"""通知服务主类。"""

from typing import Optional, Dict, Any, List
import logging

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import (
    NotificationServiceInterface,
    NotificationConfig,
    NotificationMessage,
    NotificationStatus,
    NotificationTarget,
    NotificationChannel
)
from .providers import DefaultNotificationService

logger = logging.getLogger(__name__)


class NotificationService(BaseService, NotificationServiceInterface):
    """通知服务。"""

    def __init__(self, config: ServiceConfig, notification_config: NotificationConfig):
        super().__init__("notification", config)
        self.notification_config = notification_config
        self._provider: Optional[NotificationServiceInterface] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.NOTIFICATION

    async def initialize(self) -> None:
        """初始化通知服务。"""
        try:
            # 创建默认通知服务提供商
            self._provider = DefaultNotificationService(self.config, self.notification_config)
            await self._provider.initialize()
            self.logger.info("通知服务初始化成功")

        except Exception as e:
            raise ExternalServiceError(
                f"通知服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        if not self._provider:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = "通知服务未初始化"
            self._health.last_check = datetime.now()
            return self._health

        try:
            provider_health = await self._provider.health_check()
            self._health = provider_health
            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"通知服务异常: {str(e)}"
            self._health.last_check = datetime.now()
            return self._health

    async def send_notification(self, message: NotificationMessage) -> List[Dict[str, Any]]:
        """发送通知。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.send_notification, message)

    async def send_batch_notifications(self, messages: List[NotificationMessage]) -> List[Dict[str, Any]]:
        """批量发送通知。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.send_batch_notifications, messages)

    async def schedule_notification(self, message: NotificationMessage, scheduled_at: datetime) -> str:
        """定时发送通知。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.schedule_notification,
            message,
            scheduled_at
        )

    async def cancel_notification(self, message_id: str) -> bool:
        """取消通知。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.cancel_notification, message_id)

    async def get_notification_status(self, message_id: str) -> NotificationStatus:
        """获取通知状态。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_notification_status, message_id)

    async def retry_failed_notifications(self, limit: int = 100) -> int:
        """重试失败的通知。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.retry_failed_notifications, limit)

    async def register_webhook(self, channel: NotificationChannel, url: str, secret: Optional[str] = None) -> str:
        """注册 webhook。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.register_webhook,
            channel,
            url,
            secret
        )

    async def unregister_webhook(self, webhook_id: str) -> bool:
        """注销 webhook。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.unregister_webhook, webhook_id)

    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 webhook 数据。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.parse_webhook, payload, signature)

    async def get_notification_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取通知统计信息。"""
        if not self._provider:
            raise ExternalServiceError("通知服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.get_notification_stats,
            start_date,
            end_date
        )

    async def close(self) -> None:
        """关闭服务连接。"""
        if self._provider:
            try:
                await self._provider.close()
            except Exception as e:
                self.logger.error(f"关闭通知服务提供商时出错: {e}")
            self._provider = None

    def create_simple_message(
        self,
        title: str,
        content: str,
        targets: List[str],
        channel: NotificationChannel = NotificationChannel.EMAIL,
        priority: str = "normal"
    ) -> NotificationMessage:
        """创建简单通知消息。"""
        notification_targets = [
            NotificationTarget(channel=channel, address=target)
            for target in targets
        ]

        return NotificationMessage(
            title=title,
            content=content,
            targets=notification_targets,
            priority=getattr(NotificationPriority, priority.upper(), NotificationPriority.NORMAL)
        )

    def get_provider(self) -> Optional[NotificationServiceInterface]:
        """获取当前通知服务提供商。"""
        return self._provider