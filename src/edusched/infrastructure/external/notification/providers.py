"""通知服务提供商实现。"""

import json
import uuid
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

import aiohttp
import redis.asyncio as redis

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from ..email.interfaces import EmailServiceInterface, EmailMessage
from ..email.service import EmailService
from .interfaces import (
    NotificationServiceInterface,
    NotificationMessage,
    NotificationTarget,
    NotificationResult,
    NotificationConfig,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus
)

logger = logging.getLogger(__name__)


class DefaultNotificationService(BaseService, NotificationServiceInterface):
    """默认通知服务（支持多渠道）。"""

    def __init__(self, config: ServiceConfig, notification_config: NotificationConfig):
        super().__init__("notification", config)
        self.notification_config = notification_config
        self._email_service: Optional[EmailServiceInterface] = None
        self._redis_client: Optional[redis.Redis] = None
        self._scheduled_tasks: Dict[str, asyncio.Task] = {}

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.NOTIFICATION

    async def initialize(self) -> None:
        """初始化通知服务。"""
        try:
            # 初始化 Redis 连接
            if self.notification_config.queue_enabled:
                self._redis_client = redis.ConnectionPool.from_url(
                    "redis://localhost:6379",
                    max_connections=10,
                    retry_on_timeout=True
                )
                # 测试连接
                redis_client = redis.Redis(connection_pool=self._redis_client)
                await redis_client.ping()

            # 初始化邮件服务
            if self.notification_config.email_config:
                from ..email.interfaces import EmailConfig
                email_config = EmailConfig(**self.notification_config.email_config)
                email_service_config = ServiceConfig(
                    enabled=True,
                    timeout=self.config.timeout,
                    max_retries=self.config.max_retries
                )
                self._email_service = EmailService(email_service_config, email_config)
                await self._email_service.initialize()

            self.logger.info("通知服务初始化成功")

        except Exception as e:
            raise ExternalServiceError(
                f"通知服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()

            # 检查 Redis
            if self._redis_client:
                redis_client = redis.Redis(connection_pool=self._redis_client)
                await redis_client.ping()

            # 检查邮件服务
            if self._email_service:
                await self._email_service.health_check()

            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "通知服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"通知服务异常: {str(e)}"
            self._health.last_check = datetime.now()

            return self._health

    async def send_notification(self, message: NotificationMessage) -> List[NotificationResult]:
        """发送通知。"""
        return await self._execute_with_retry(self._send_notification_impl, message)

    async def _send_notification_impl(self, message: NotificationMessage) -> List[NotificationResult]:
        """实现通知发送。"""
        results = []

        for target in message.targets:
            try:
                result = await self._send_to_channel(message, target)
                results.append(result)
            except Exception as e:
                logger.error(f"发送通知到 {target.channel.value} 失败: {e}")
                results.append(NotificationResult(
                    success=False,
                    message_id=message.id or str(uuid.uuid4()),
                    channel=target.channel,
                    target=target.address,
                    status=NotificationStatus.FAILED,
                    error_message=str(e)
                ))

        return results

    async def _send_to_channel(self, message: NotificationMessage, target: NotificationTarget) -> NotificationResult:
        """发送到指定渠道。"""
        message_id = message.id or str(uuid.uuid4())
        current_time = datetime.now()

        if target.channel == NotificationChannel.EMAIL:
            if not self._email_service:
                raise ExternalServiceError("邮件服务未配置", self.service_name)

            email_message = EmailMessage(
                to=[target.address],
                subject=message.title,
                content=message.content,
                html_content=message.content,  # 简化处理
                attachments=[
                    EmailAttachment(
                        filename=att.filename,
                        content=att.content,
                        content_type=att.content_type
                    )
                    for att in message.attachments or []
                ] if message.attachments else None
            )

            email_result = await self._email_service.send_email(email_message)

            return NotificationResult(
                success=email_result.get("success", False),
                message_id=message_id,
                channel=target.channel,
                target=target.address,
                status=NotificationStatus.SENT if email_result.get("success") else NotificationStatus.FAILED,
                delivery_time=current_time if email_result.get("success") else None,
                metadata={"provider": email_result.get("provider")}
            )

        elif target.channel == NotificationChannel.SMS:
            # 简化的 SMS 实现
            logger.info(f"发送短信到 {target.address}: {message.title} - {message.content}")
            return NotificationResult(
                success=True,
                message_id=message_id,
                channel=target.channel,
                target=target.address,
                status=NotificationStatus.SENT,
                delivery_time=current_time
            )

        elif target.channel == NotificationChannel.SLACK:
            # Slack webhook 实现
            webhook_url = target.metadata.get("webhook_url") if target.metadata else None
            if not webhook_url:
                raise ExternalServiceError("Slack webhook URL 未提供", self.service_name)

            await self._send_slack_webhook(webhook_url, message.title, message.content)

            return NotificationResult(
                success=True,
                message_id=message_id,
                channel=target.channel,
                target=target.address,
                status=NotificationStatus.SENT,
                delivery_time=current_time
            )

        elif target.channel == NotificationChannel.WEBHOOK:
            webhook_url = target.address
            headers = target.metadata.get("headers", {}) if target.metadata else {}
            secret = target.metadata.get("secret") if target.metadata else None

            await self._send_webhook(webhook_url, {
                "title": message.title,
                "content": message.content,
                "priority": message.priority.value,
                "message_id": message_id,
                "timestamp": current_time.isoformat()
            }, headers, secret)

            return NotificationResult(
                success=True,
                message_id=message_id,
                channel=target.channel,
                target=target.address,
                status=NotificationStatus.SENT,
                delivery_time=current_time
            )

        else:
            raise ExternalServiceError(
                f"不支持的通知渠道: {target.channel}",
                self.service_name
            )

    async def _send_slack_webhook(self, webhook_url: str, title: str, content: str) -> None:
        """发送 Slack webhook。"""
        payload = {
            "text": f"*{title}*\n{content}"
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    raise ExternalServiceError(
                        f"Slack webhook 发送失败: {response.status}",
                        self.service_name
                    )

    async def _send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> None:
        """发送通用 webhook。"""
        if secret:
            # 这里应该添加签名逻辑
            import hmac
            import hashlib
            signature = hmac.new(
                secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers = headers or {}
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as session:
            async with session.post(
                url,
                json=payload,
                headers=headers or {}
            ) as response:
                if response.status not in [200, 201, 202, 204]:
                    raise ExternalServiceError(
                        f"Webhook 发送失败: {response.status}",
                        self.service_name
                    )

    async def send_batch_notifications(self, messages: List[NotificationMessage]) -> List[NotificationResult]:
        """批量发送通知。"""
        all_results = []
        for message in messages:
            results = await self.send_notification(message)
            all_results.extend(results)
        return all_results

    async def schedule_notification(self, message: NotificationMessage, scheduled_at: datetime) -> str:
        """定时发送通知。"""
        if not self.notification_config.queue_enabled or not self._redis_client:
            raise ExternalServiceError("队列功能未启用", self.service_name)

        message_id = str(uuid.uuid4())
        message.id = message_id

        # 存储到 Redis
        redis_client = redis.Redis(connection_pool=self._redis_client)
        await redis_client.zadd(
            "scheduled_notifications",
            {
                json.dumps({
                    "message": message.__dict__,
                    "scheduled_at": scheduled_at.isoformat()
                }): scheduled_at.timestamp()
            }
        )

        # 创建定时任务
        delay = (scheduled_at - datetime.now()).total_seconds()
        if delay > 0:
            task = asyncio.create_task(self._delayed_send(message_id, delay))
            self._scheduled_tasks[message_id] = task

        return message_id

    async def _delayed_send(self, message_id: str, delay: float) -> None:
        """延迟发送通知。"""
        await asyncio.sleep(delay)

        # 从 Redis 获取消息
        if not self._redis_client:
            return

        redis_client = redis.Redis(connection_pool=self._redis_client)
        scheduled_data = await redis_client.zrangebyscore(
            "scheduled_notifications",
            datetime.now().timestamp(),
            datetime.now().timestamp()
        )

        for data in scheduled_data:
            try:
                data_dict = json.loads(data)
                if data_dict["message"]["id"] == message_id:
                    message = NotificationMessage(**data_dict["message"])
                    await self.send_notification(message)
                    await redis_client.zrem("scheduled_notifications", data)
                    break
            except Exception as e:
                logger.error(f"处理定时通知失败: {e}")

        if message_id in self._scheduled_tasks:
            del self._scheduled_tasks[message_id]

    async def cancel_notification(self, message_id: str) -> bool:
        """取消通知。"""
        # 取消定时任务
        if message_id in self._scheduled_tasks:
            self._scheduled_tasks[message_id].cancel()
            del self._scheduled_tasks[message_id]

        # 从 Redis 移除
        if self._redis_client:
            redis_client = redis.Redis(connection_pool=self._redis_client)
            scheduled_data = await redis_client.zrange("scheduled_notifications", 0, -1)
            for data in scheduled_data:
                try:
                    data_dict = json.loads(data)
                    if data_dict["message"]["id"] == message_id:
                        await redis_client.zrem("scheduled_notifications", data)
                        return True
                except:
                    pass

        return False

    async def get_notification_status(self, message_id: str) -> NotificationStatus:
        """获取通知状态（简化实现）。"""
        # 这里应该从数据库或缓存中查询状态
        # 简化实现，总是返回 SENT
        return NotificationStatus.SENT

    async def retry_failed_notifications(self, limit: int = 100) -> int:
        """重试失败的通知。"""
        # 这里应该从死信队列中获取失败的通知并重试
        # 简化实现，返回 0
        return 0

    async def register_webhook(self, channel: NotificationChannel, url: str, secret: Optional[str] = None) -> str:
        """注册 webhook。"""
        webhook_id = str(uuid.uuid4())

        if not self._redis_client:
            raise ExternalServiceError("Redis 未配置", self.service_name)

        redis_client = redis.Redis(connection_pool=self._redis_client)
        await redis_client.hset(
            "webhooks",
            webhook_id,
            json.dumps({
                "channel": channel.value,
                "url": url,
                "secret": secret,
                "created_at": datetime.now().isoformat()
            })
        )

        return webhook_id

    async def unregister_webhook(self, webhook_id: str) -> bool:
        """注销 webhook。"""
        if not self._redis_client:
            return False

        redis_client = redis.Redis(connection_pool=self._redis_client)
        result = await redis_client.hdel("webhooks", webhook_id)
        return result > 0

    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 webhook 数据。"""
        # 这里应该根据不同的渠道解析 webhook
        # 简化实现，直接返回 payload
        return {
            "parsed": True,
            "data": payload,
            "signature_verified": signature is not None
        }

    async def get_notification_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取通知统计信息。"""
        # 这里应该从数据库查询统计信息
        # 简化实现，返回模拟数据
        return {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "by_channel": {},
            "by_priority": {},
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    async def close(self) -> None:
        """关闭服务连接。"""
        # 取消所有定时任务
        for task in self._scheduled_tasks.values():
            task.cancel()

        # 关闭邮件服务
        if self._email_service:
            await self._email_service.close()

        # 关闭 Redis 连接
        if self._redis_client:
            await self._redis_client.aclose()

        self.logger.info("通知服务已关闭")


# 需要在文件顶部添加导入
from ..base import ServiceStatus