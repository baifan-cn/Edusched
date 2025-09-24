"""邮件服务主类。"""

from typing import Optional, Dict, Any
import logging

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import EmailServiceInterface, EmailConfig, EmailMessage, EmailProvider
from .providers import SMTPEmailService, SendGridEmailService

logger = logging.getLogger(__name__)


class EmailService(BaseService, EmailServiceInterface):
    """邮件服务。"""

    def __init__(self, config: ServiceConfig, email_config: EmailConfig):
        super().__init__("email", config)
        self.email_config = email_config
        self._provider: Optional[EmailServiceInterface] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.EMAIL

    async def initialize(self) -> None:
        """初始化邮件服务。"""
        try:
            # 根据配置创建提供商实例
            if self.email_config.provider == EmailProvider.SMTP:
                self._provider = SMTPEmailService(self.config, self.email_config)
            elif self.email_config.provider == EmailProvider.SENDGRID:
                self._provider = SendGridEmailService(self.config, self.email_config)
            else:
                raise ExternalServiceError(
                    f"不支持的邮件服务提供商: {self.email_config.provider}",
                    self.service_name
                )

            await self._provider.initialize()
            self.logger.info(f"邮件服务初始化成功，提供商: {self.email_config.provider.value}")

        except Exception as e:
            raise ExternalServiceError(
                f"邮件服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        if not self._provider:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = "邮件服务未初始化"
            self._health.last_check = datetime.now()
            return self._health

        try:
            provider_health = await self._provider.health_check()
            self._health = provider_health
            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"邮件服务异常: {str(e)}"
            self._health.last_check = datetime.now()
            return self._health

    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """发送邮件。"""
        if not self._provider:
            raise ExternalServiceError("邮件服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.send_email, message)

    async def send_batch_emails(self, messages: list[EmailMessage]) -> list[Dict[str, Any]]:
        """批量发送邮件。"""
        if not self._provider:
            raise ExternalServiceError("邮件服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.send_batch_emails, messages)

    async def send_template_email(
        self,
        template_id: str,
        to: list[str],
        template_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """发送模板邮件。"""
        if not self._provider:
            raise ExternalServiceError("邮件服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.send_template_email,
            template_id,
            to,
            template_data,
            **kwargs
        )

    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """获取邮件投递状态。"""
        if not self._provider:
            raise ExternalServiceError("邮件服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_delivery_status, message_id)

    async def validate_email(self, email: str) -> bool:
        """验证邮箱地址。"""
        if not self._provider:
            raise ExternalServiceError("邮件服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.validate_email, email)

    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 webhook 数据。"""
        if not self._provider:
            raise ExternalServiceError("邮件服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.parse_webhook, payload, signature)

    async def close(self) -> None:
        """关闭服务连接。"""
        if self._provider:
            try:
                await self._provider.close()
            except Exception as e:
                self.logger.error(f"关闭邮件服务提供商时出错: {e}")
            self._provider = None

    def get_provider(self) -> Optional[EmailServiceInterface]:
        """获取当前邮件服务提供商。"""
        return self._provider

    def change_provider(self, new_config: EmailConfig) -> None:
        """切换邮件服务提供商。"""
        if self._provider:
            raise ExternalServiceError(
                "请先关闭当前提供商再切换",
                self.service_name
            )

        self.email_config = new_config
        self.logger.info(f"已切换邮件服务提供商配置: {new_config.provider.value}")


# 需要在文件顶部添加导入
from datetime import datetime