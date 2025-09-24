"""邮件服务提供商实现。"""

import smtplib
import aiohttp
import json
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import (
    EmailServiceInterface,
    EmailMessage,
    EmailAttachment,
    EmailConfig,
    EmailProvider
)

logger = logging.getLogger(__name__)


class SMTPEmailService(BaseService, EmailServiceInterface):
    """SMTP 邮件服务。"""

    def __init__(self, config: ServiceConfig, email_config: EmailConfig):
        super().__init__("smtp_email", config)
        self.email_config = email_config
        self._smtp_client = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.EMAIL

    async def initialize(self) -> None:
        """初始化 SMTP 连接。"""
        try:
            # 验证配置
            if not self.email_config.smtp_host:
                raise ExternalServiceError("SMTP 主机未配置", self.service_name)

            if not self.email_config.smtp_username or not self.email_config.smtp_password:
                raise ExternalServiceError("SMTP 用户名或密码未配置", self.service_name)

            # 测试连接
            await self._test_connection()
            self.logger.info("SMTP 邮件服务初始化成功")

        except Exception as e:
            raise ExternalServiceError(
                f"SMTP 邮件服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def _test_connection(self) -> None:
        """测试 SMTP 连接。"""
        try:
            with smtplib.SMTP(
                self.email_config.smtp_host,
                self.email_config.smtp_port,
                timeout=self.config.timeout
            ) as smtp:
                if self.email_config.smtp_use_tls:
                    smtp.starttls()

                smtp.login(
                    self.email_config.smtp_username,
                    self.email_config.smtp_password
                )
        except Exception as e:
            raise ExternalServiceError(f"SMTP 连接测试失败: {str(e)}", self.service_name)

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()
            await self._test_connection()
            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "SMTP 服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"SMTP 服务异常: {str(e)}"
            self._health.last_check = datetime.now()

            return self._health

    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """发送邮件。"""
        return await self._execute_with_retry(self._send_email_impl, message)

    async def _send_email_impl(self, message: EmailMessage) -> Dict[str, Any]:
        """实现邮件发送。"""
        try:
            # 构建邮件
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = self._format_address(
                message.from_name or self.email_config.default_from_name,
                message.from_email or self.email_config.default_from_email
            )
            msg["To"] = ", ".join(message.to)

            if message.cc:
                msg["Cc"] = ", ".join(message.cc)
            if message.reply_to:
                msg["Reply-To"] = message.reply_to

            # 添加内容
            if message.html_content:
                msg.attach(MIMEText(message.html_content, "html", "utf-8"))
            else:
                msg.attach(MIMEText(message.content, "plain", "utf-8"))

            # 添加附件
            if message.attachments:
                for attachment in message.attachments:
                    part = MIMEBase(
                        attachment.content_type.split("/")[0],
                        attachment.content_type.split("/")[1]
                    )
                    part.set_payload(attachment.content)
                    encoders.encode_base64(part)

                    filename = attachment.filename
                    if attachment.content_id:
                        part.add_header(
                            "Content-ID",
                            f"<{attachment.content_id}>"
                        )
                        part.add_header(
                            "Content-Disposition",
                            "inline",
                            filename=filename
                        )
                    else:
                        part.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=filename
                        )

                    msg.attach(part)

            # 发送邮件
            with smtplib.SMTP(
                self.email_config.smtp_host,
                self.email_config.smtp_port,
                timeout=self.config.timeout
            ) as smtp:
                if self.email_config.smtp_use_tls:
                    smtp.starttls()

                smtp.login(
                    self.email_config.smtp_username,
                    self.email_config.smtp_password
                )

                recipients = message.to[:]
                if message.cc:
                    recipients.extend(message.cc)
                if message.bcc:
                    recipients.extend(message.bcc)

                smtp.send_message(msg, to_addrs=recipients)

            return {
                "success": True,
                "message_id": f"smtp_{datetime.now().timestamp()}",
                "provider": "smtp"
            }

        except Exception as e:
            raise ExternalServiceError(
                f"发送邮件失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def send_batch_emails(self, messages: List[EmailMessage]) -> List[Dict[str, Any]]:
        """批量发送邮件。"""
        tasks = [self.send_email(msg) for msg in messages]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def send_template_email(
        self,
        template_id: str,
        to: List[str],
        template_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """发送模板邮件（SMTP 不支持，直接发送普通邮件）。"""
        message = EmailMessage(
            to=to,
            subject=kwargs.get("subject", "来自 Edusched 的邮件"),
            content=str(template_data),
            **{k: v for k, v in kwargs.items() if k in ["from_email", "from_name", "cc", "bcc"]}
        )
        return await self.send_email(message)

    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """获取投递状态（SMTP 不支持）。"""
        return {
            "message_id": message_id,
            "status": "unknown",
            "provider": "smtp",
            "message": "SMTP 不支持投递状态查询"
        }

    async def validate_email(self, email: str) -> bool:
        """验证邮箱地址格式。"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 webhook（SMTP 不支持）。"""
        return {
            "provider": "smtp",
            "message": "SMTP 不支持 webhook"
        }

    def _format_address(self, name: Optional[str], email: Optional[str]) -> str:
        """格式化邮件地址。"""
        if name and email:
            return f"{name} <{email}>"
        return email or ""

    async def close(self) -> None:
        """关闭连接。"""
        if self._smtp_client:
            try:
                self._smtp_client.quit()
            except:
                pass
            self._smtp_client = None


class SendGridEmailService(BaseService, EmailServiceInterface):
    """SendGrid 邮件服务。"""

    def __init__(self, config: ServiceConfig, email_config: EmailConfig):
        super().__init__("sendgrid_email", config)
        self.email_config = email_config
        self._api_key = email_config.api_key
        self._base_url = "https://api.sendgrid.com/v3"

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.EMAIL

    async def initialize(self) -> None:
        """初始化 SendGrid 服务。"""
        if not self._api_key:
            raise ExternalServiceError("SendGrid API Key 未配置", self.service_name)

        # 测试 API 连接
        await self._test_api_connection()
        self.logger.info("SendGrid 邮件服务初始化成功")

    async def _test_api_connection(self) -> None:
        """测试 API 连接。"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                }
                async with session.get(f"{self._base_url}/user/account", headers=headers) as response:
                    if response.status != 200:
                        raise ExternalServiceError(
                            f"SendGrid API 认证失败: {response.status}",
                            self.service_name
                        )
        except Exception as e:
            raise ExternalServiceError(
                f"SendGrid API 连接失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()
            await self._test_api_connection()
            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "SendGrid 服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"SendGrid 服务异常: {str(e)}"
            self._health.last_check = datetime.now()

            return self._health

    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """发送邮件。"""
        return await self._execute_with_retry(self._send_email_impl, message)

    async def _send_email_impl(self, message: EmailMessage) -> Dict[str, Any]:
        """实现邮件发送。"""
        try:
            personalizations = [{
                "to": [{"email": email} for email in message.to]
            }]

            if message.cc:
                personalizations[0]["cc"] = [{"email": email} for email in message.cc]

            if message.bcc:
                personalizations[0]["bcc"] = [{"email": email} for email in message.bcc]

            email_data = {
                "personalizations": personalizations,
                "from": {
                    "email": message.from_email or self.email_config.default_from_email,
                    "name": message.from_name or self.email_config.default_from_name
                },
                "subject": message.subject,
                "content": []
            }

            # 添加内容
            if message.html_content:
                email_data["content"].append({
                    "type": "text/html",
                    "value": message.html_content
                })
            else:
                email_data["content"].append({
                    "type": "text/plain",
                    "value": message.content
                })

            # 添加附件
            if message.attachments:
                email_data["attachments"] = []
                for attachment in message.attachments:
                    email_data["attachments"].append({
                        "content": attachment.content.decode('latin-1'),
                        "filename": attachment.filename,
                        "type": attachment.content_type,
                        "disposition": "attachment",
                        "content_id": attachment.content_id
                    })

            # 发送请求
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                }
                async with session.post(
                    f"{self._base_url}/mail/send",
                    headers=headers,
                    json=email_data
                ) as response:
                    if response.status == 202:
                        result = await response.json()
                        return {
                            "success": True,
                            "message_id": result.get("headers", {}).get("X-Message-Id"),
                            "provider": "sendgrid"
                        }
                    else:
                        error_data = await response.json()
                        raise ExternalServiceError(
                            f"SendGrid API 错误: {error_data}",
                            self.service_name
                        )

        except aiohttp.ClientError as e:
            raise ExternalServiceError(
                f"发送邮件失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def send_batch_emails(self, messages: List[EmailMessage]) -> List[Dict[str, Any]]:
        """批量发送邮件。"""
        tasks = [self.send_email(msg) for msg in messages]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def send_template_email(
        self,
        template_id: str,
        to: List[str],
        template_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """发送模板邮件。"""
        try:
            personalizations = [{
                "to": [{"email": email} for email in to],
                "dynamic_template_data": template_data
            }]

            email_data = {
                "personalizations": personalizations,
                "from": {
                    "email": kwargs.get("from_email", self.email_config.default_from_email),
                    "name": kwargs.get("from_name", self.email_config.default_from_name)
                },
                "template_id": template_id
            }

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                }
                async with session.post(
                    f"{self._base_url}/mail/send",
                    headers=headers,
                    json=email_data
                ) as response:
                    if response.status == 202:
                        result = await response.json()
                        return {
                            "success": True,
                            "message_id": result.get("headers", {}).get("X-Message-Id"),
                            "provider": "sendgrid"
                        }
                    else:
                        error_data = await response.json()
                        raise ExternalServiceError(
                            f"SendGrid 模板邮件错误: {error_data}",
                            self.service_name
                        )

        except Exception as e:
            raise ExternalServiceError(
                f"发送模板邮件失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """获取投递状态。"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self._base_url}/messages/{message_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "message_id": message_id,
                            "status": data.get("status"),
                            "provider": "sendgrid",
                            "opens_count": data.get("opens_count", 0),
                            "clicks_count": data.get("clicks_count", 0),
                            "last_event_time": data.get("last_event_time")
                        }
                    else:
                        return {
                            "message_id": message_id,
                            "status": "unknown",
                            "provider": "sendgrid",
                            "error": "无法获取状态"
                        }

        except Exception as e:
            raise ExternalServiceError(
                f"获取投递状态失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def validate_email(self, email: str) -> bool:
        """验证邮箱地址。"""
        # SendGrid 提供邮箱验证 API，这里简化处理
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 SendGrid webhook。"""
        try:
            # 这里应该验证签名
            # if signature and not self._verify_webhook_signature(payload, signature):
            #     raise ExternalServiceError("Webhook 签名验证失败", self.service_name)

            events = payload.get("events", [])
            parsed_events = []

            for event in events:
                parsed_events.append({
                    "message_id": event.get("sg_message_id"),
                    "event": event.get("event"),
                    "email": event.get("email"),
                    "timestamp": event.get("timestamp"),
                    "ip": event.get("ip"),
                    "useragent": event.get("useragent"),
                    "url": event.get("url"),
                    "reason": event.get("reason")
                })

            return {
                "provider": "sendgrid",
                "events": parsed_events
            }

        except Exception as e:
            raise ExternalServiceError(
                f"解析 webhook 失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def close(self) -> None:
        """关闭连接。"""
        pass


# 需要在文件顶部添加导入
from ..base import ServiceStatus