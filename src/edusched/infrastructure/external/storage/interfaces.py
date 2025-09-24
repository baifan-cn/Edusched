"""文件存储服务接口定义。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, AsyncIterator
from enum import Enum
from datetime import datetime, timedelta
import hashlib


class StorageProvider(Enum):
    """存储服务提供商。"""
    LOCAL = "local"
    S3 = "s3"
    ALIYUN_OSS = "aliyun_oss"
    TENCENT_COS = "tencent_cos"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    MINIO = "minio"


class StoragePermission(Enum):
    """存储权限。"""
    PRIVATE = "private"
    PUBLIC_READ = "public_read"
    PUBLIC_READ_WRITE = "public_read_write"
    AUTHENTICATED_READ = "authenticated_read"


@dataclass
class StorageObject:
    """存储对象。"""
    key: str
    size: int
    last_modified: datetime
    etag: str
    content_type: str
    metadata: Optional[Dict[str, str]] = None
    storage_class: Optional[str] = None
    version_id: Optional[str] = None


@dataclass
class UploadResult:
    """上传结果。"""
    success: bool
    key: str
    etag: Optional[str] = None
    version_id: Optional[str] = None
    location: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PresignedURL:
    """预签名 URL。"""
    url: str
    method: str  # GET, PUT, DELETE
    expires_at: datetime
    headers: Optional[Dict[str, str]] = None


@dataclass
class StorageConfig:
    """存储服务配置。"""
    provider: StorageProvider
    bucket_name: str
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    access_key_id: Optional[str] = None
    access_key_secret: Optional[str] = None
    session_token: Optional[str] = None

    # 本地存储配置
    local_path: Optional[str] = None
    base_url: Optional[str] = None

    # 安全配置
    default_permission: StoragePermission = StoragePermission.PRIVATE
    enable_versioning: bool = False
    enable_encryption: bool = True
    encryption_key: Optional[str] = None

    # 性能配置
    multipart_threshold: int = 8 * 1024 * 1024  # 8MB
    multipart_chunksize: int = 8 * 1024 * 1024  # 8MB
    max_concurrency: int = 10

    # CDN 配置
    cdn_enabled: bool = False
    cdn_domain: Optional[str] = None
    cdn_https: bool = True

    # 生命周期配置
    lifecycle_rules: Optional[List[Dict[str, Any]]] = None

    # 跨域配置
    cors_rules: Optional[List[Dict[str, Any]]] = None


class StorageServiceInterface(ABC):
    """存储服务接口。"""

    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        permission: Optional[StoragePermission] = None
    ) -> UploadResult:
        """上传文件。"""
        pass

    @abstractmethod
    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        permission: Optional[StoragePermission] = None
    ) -> UploadResult:
        """上传字节数据。"""
        pass

    @abstractmethod
    async def download_file(self, key: str, file_path: str, version_id: Optional[str] = None) -> bool:
        """下载文件。"""
        pass

    @abstractmethod
    async def download_bytes(self, key: str, version_id: Optional[str] = None) -> Optional[bytes]:
        """下载字节数据。"""
        pass

    @abstractmethod
    async def download_stream(self, key: str, version_id: Optional[str] = None) -> AsyncIterator[bytes]:
        """下载文件流。"""
        pass

    @abstractmethod
    async def delete_file(self, key: str, version_id: Optional[str] = None) -> bool:
        """删除文件。"""
        pass

    @abstractmethod
    async def copy_file(
        self,
        source_key: str,
        dest_key: str,
        source_version_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> UploadResult:
        """复制文件。"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查文件是否存在。"""
        pass

    @abstractmethod
    async def get_object_info(self, key: str, version_id: Optional[str] = None) -> Optional[StorageObject]:
        """获取对象信息。"""
        pass

    @abstractmethod
    async def list_objects(
        self,
        prefix: str = "",
        delimiter: Optional[str] = None,
        max_keys: int = 1000,
        start_after: Optional[str] = None
    ) -> List[StorageObject]:
        """列出对象。"""
        pass

    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        method: str = "GET",
        expires_in: int = 3600,
        version_id: Optional[str] = None
    ) -> PresignedURL:
        """生成预签名 URL。"""
        pass

    @abstractmethod
    async def generate_presigned_post(
        self,
        key: str,
        expires_in: int = 3600,
        conditions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """生成预签名 POST。"""
        pass

    @abstractmethod
    async def set_object_acl(self, key: str, permission: StoragePermission) -> bool:
        """设置对象 ACL。"""
        pass

    @abstractmethod
    async def get_object_acl(self, key: str) -> StoragePermission:
        """获取对象 ACL。"""
        pass

    @abstractmethod
    async def set_object_metadata(self, key: str, metadata: Dict[str, str]) -> bool:
        """设置对象元数据。"""
        pass

    @abstractmethod
    async def get_object_metadata(self, key: str) -> Dict[str, str]:
        """获取对象元数据。"""
        pass

    @abstractmethod
    async def restore_object(
        self,
        key: str,
        version_id: Optional[str] = None,
        tier: str = "Standard"
    ) -> bool:
        """恢复归档对象。"""
        pass

    @abstractmethod
    async def initiate_multipart_upload(
        self,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """初始化分片上传。"""
        pass

    @abstractmethod
    async def upload_part(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes
    ) -> str:
        """上传分片。"""
        pass

    @abstractmethod
    async def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: List[Dict[str, Any]]
    ) -> UploadResult:
        """完成分片上传。"""
        pass

    @abstractmethod
    async def abort_multipart_upload(self, key: str, upload_id: str) -> bool:
        """中止分片上传。"""
        pass

    @abstractmethod
    async def list_multipart_uploads(self, max_uploads: int = 1000) -> List[Dict[str, Any]]:
        """列出进行中的分片上传。"""
        pass

    @abstractmethod
    async def calculate_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """计算文件哈希值。"""
        pass

    @abstractmethod
    async def sync_directory(
        self,
        local_dir: str,
        remote_prefix: str = "",
        delete: bool = False
    ) -> Dict[str, Any]:
        """同步目录。"""
        pass