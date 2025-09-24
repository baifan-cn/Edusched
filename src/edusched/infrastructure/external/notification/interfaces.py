"""通知服务接口定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime


class NotificationChannel(Enum):
    """通知渠道。"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    WECHAT = "wechat"
    DINGTALK = "dingtalk"


class NotificationPriority(Enum):
    """通知优先级。"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """通知状态。"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class NotificationAttachment:
    """通知附件。"""
    filename: str
    content: bytes
    content_type: str
    size: int


@dataclass
class NotificationTarget:
    """通知目标。"""
    channel: NotificationChannel
    address: str  # 邮箱、手机号、设备ID等
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationMessage:
    """通知消息。"""
    title: str
    content: str
    targets: List[NotificationTarget]
    priority: NotificationPriority = NotificationPriority.NORMAL
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    attachments: Optional[List[NotificationAttachment]] = None
    scheduled_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = field(default=None, init=False)


@dataclass
class NotificationResult:
    """通知结果。"""
    success: bool
    message_id: str
    channel: NotificationChannel
    target: str
    status: NotificationStatus
    error_message: Optional[str] = None
    delivery_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationConfig:
    """通知服务配置。"""
    # 通用配置
    default_channel: NotificationChannel = NotificationChannel.EMAIL
    retry_attempts: int = 3
    retry_delay: int = 60
    batch_size: int = 100
    rate_limit: int = 1000  # 每分钟限制

    # 各渠道配置
    email_config: Optional[Dict[str, Any]] = None
    sms_config: Optional[Dict[str, Any]] = None
    push_config: Optional[Dict[str, Any]] = None
    webhook_config: Optional[Dict[str, Any]] = None
    slack_config: Optional[Dict[str, Any]] = None
    wechat_config: Optional[Dict[str, Any]] = None
    dingtalk_config: Optional[Dict[str, Any]] = None

    # 队列配置
    queue_enabled: bool = True
    queue_name: str = "notifications"
    dead_letter_queue: str = "notifications_dead"

    # 模板配置
    template_dir: Optional[str] = None

    # 回调配置
    callback_url: Optional[str] = None
    callback_secret: Optional[str] = None


class NotificationServiceInterface(ABC):
    """通知服务接口。"""

    @abstractmethod
    async def send_notification(self, message: NotificationMessage) -> List[NotificationResult]:
        """发送通知。"""
        pass

    @abstractmethod
    async def send_batch_notifications(self, messages: List[NotificationMessage]) -> List[NotificationResult]:
        """批量发送通知。"""
        pass

    @abstractmethod
    async def schedule_notification(self, message: NotificationMessage, scheduled_at: datetime) -> str:
        """定时发送通知。"""
        pass

    @abstractmethod
    async def cancel_notification(self, message_id: str) -> bool:
        """取消通知。"""
        pass

    @abstractmethod
    async def get_notification_status(self, message_id: str) -> NotificationStatus:
        """获取通知状态。"""
        pass

    @abstractmethod
    async def retry_failed_notifications(self, limit: int = 100) -> int:
        """重试失败的通知。"""
        pass

    @abstractmethod
    async def register_webhook(self, channel: NotificationChannel, url: str, secret: Optional[str] = None) -> str:
        """注册 webhook。"""
        pass

    @abstractmethod
    async def unregister_webhook(self, webhook_id: str) -> bool:
        """注销 webhook。"""
        pass

    @abstractmethod
    async def parse_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> Dict[str, Any]:
        """解析 webhook 数据。"""
        pass

    @abstractmethod
    async def get_notification_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取通知统计信息。"""
        pass