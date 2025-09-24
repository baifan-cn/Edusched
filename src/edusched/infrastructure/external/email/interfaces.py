"""邮件服务接口定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class EmailProvider(Enum):
    """邮件服务提供商。"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    MAILGUN = "mailgun"
    POSTMARK = "postmark"


@dataclass
class EmailAttachment:
    """邮件附件。"""
    filename: str
    content: bytes
    content_type: str
    content_id: Optional[str] = None


@dataclass
class EmailMessage:
    """邮件消息。"""
    to: List[str]
    subject: str
    content: str
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    reply_to: Optional[str] = None
    attachments: Optional[List[EmailAttachment]] = None
    html_content: Optional[str] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    tracking: bool = True


@dataclass
class EmailConfig:
    """邮件服务配置。"""
    provider: EmailProvider
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    region: Optional[str] = None
    domain: Optional[str] = None

    # SMTP 配置
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    # 发送配置
    default_from_email: Optional[str] = None
    default_from_name: Optional[str] = None
    batch_size: int = 100
    rate_limit: int = 100  # 每分钟发送限制

    # 模板配置
    template_dir: Optional[str] = None

    # 回调配置
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None


class EmailServiceInterface(ABC):
    """邮件服务接口。"""

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """发送邮件。"""
        pass

    @abstractmethod
    async def send_batch_emails(self, messages: List[EmailMessage]) -> List[Dict[str, Any]]:
        """批量发送邮件。"""
        pass

    @abstractmethod
    async def send_template_email(
        self,
        template_id: str,
        to: List[str],
        template_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """发送模板邮件。"""
        pass

    @abstractmethod
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """获取邮件投递状态。"""
        pass

    @abstractmethod
    async def validate_email(self, email: str) -> bool:
        """验证邮箱地址。"""
        pass

    @abstractmethod
    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 webhook 数据。"""
        pass