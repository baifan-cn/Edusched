"""存储服务主类。"""

from typing import Optional, Dict, Any, List
import logging

from ..base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .interfaces import (
    StorageServiceInterface,
    StorageConfig,
    StorageObject,
    UploadResult,
    PresignedURL,
    StorageProvider,
    StoragePermission
)
from .providers import LocalStorageService

logger = logging.getLogger(__name__)


class StorageService(BaseService, StorageServiceInterface):
    """存储服务。"""

    def __init__(self, config: ServiceConfig, storage_config: StorageConfig):
        super().__init__("storage", config)
        self.storage_config = storage_config
        self._provider: Optional[StorageServiceInterface] = None

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.STORAGE

    async def initialize(self) -> None:
        """初始化存储服务。"""
        try:
            # 根据配置创建提供商实例
            if self.storage_config.provider == StorageProvider.LOCAL:
                self._provider = LocalStorageService(self.config, self.storage_config)
            elif self.storage_config.provider == StorageProvider.S3:
                # TODO: 实现 S3 存储服务
                raise ExternalServiceError("S3 存储服务尚未实现", self.service_name)
            elif self.storage_config.provider == StorageProvider.ALIYUN_OSS:
                # TODO: 实现阿里云 OSS 服务
                raise ExternalServiceError("阿里云 OSS 服务尚未实现", self.service_name)
            else:
                raise ExternalServiceError(
                    f"不支持的存储服务提供商: {self.storage_config.provider}",
                    self.service_name
                )

            await self._provider.initialize()
            self.logger.info(f"存储服务初始化成功，提供商: {self.storage_config.provider.value}")

        except Exception as e:
            raise ExternalServiceError(
                f"存储服务初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        if not self._provider:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = "存储服务未初始化"
            self._health.last_check = datetime.now()
            return self._health

        try:
            provider_health = await self._provider.health_check()
            self._health = provider_health
            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"存储服务异常: {str(e)}"
            self._health.last_check = datetime.now()
            return self._health

    async def upload_file(
        self,
        file_path: str,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        permission: Optional[StoragePermission] = None
    ) -> UploadResult:
        """上传文件。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.upload_file,
            file_path,
            key,
            content_type,
            metadata,
            permission
        )

    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        permission: Optional[StoragePermission] = None
    ) -> UploadResult:
        """上传字节数据。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.upload_bytes,
            data,
            key,
            content_type,
            metadata,
            permission
        )

    async def download_file(self, key: str, file_path: str, version_id: Optional[str] = None) -> bool:
        """下载文件。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.download_file, key, file_path, version_id)

    async def download_bytes(self, key: str, version_id: Optional[str] = None) -> Optional[bytes]:
        """下载字节数据。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.download_bytes, key, version_id)

    async def download_stream(self, key: str, version_id: Optional[str] = None):
        """下载文件流。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        # 对于流式下载，直接调用提供商方法
        return self._provider.download_stream(key, version_id)

    async def delete_file(self, key: str, version_id: Optional[str] = None) -> bool:
        """删除文件。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.delete_file, key, version_id)

    async def copy_file(
        self,
        source_key: str,
        dest_key: str,
        source_version_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> UploadResult:
        """复制文件。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.copy_file,
            source_key,
            dest_key,
            source_version_id,
            metadata
        )

    async def exists(self, key: str) -> bool:
        """检查文件是否存在。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.exists, key)

    async def get_object_info(self, key: str, version_id: Optional[str] = None) -> Optional[StorageObject]:
        """获取对象信息。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_object_info, key, version_id)

    async def list_objects(
        self,
        prefix: str = "",
        delimiter: Optional[str] = None,
        max_keys: int = 1000,
        start_after: Optional[str] = None
    ) -> List[StorageObject]:
        """列出对象。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.list_objects,
            prefix,
            delimiter,
            max_keys,
            start_after
        )

    async def generate_presigned_url(
        self,
        key: str,
        method: str = "GET",
        expires_in: int = 3600,
        version_id: Optional[str] = None
    ) -> PresignedURL:
        """生成预签名 URL。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.generate_presigned_url,
            key,
            method,
            expires_in,
            version_id
        )

    async def generate_presigned_post(
        self,
        key: str,
        expires_in: int = 3600,
        conditions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """生成预签名 POST。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.generate_presigned_post,
            key,
            expires_in,
            conditions
        )

    async def set_object_acl(self, key: str, permission: StoragePermission) -> bool:
        """设置对象 ACL。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.set_object_acl, key, permission)

    async def get_object_acl(self, key: str) -> StoragePermission:
        """获取对象 ACL。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_object_acl, key)

    async def set_object_metadata(self, key: str, metadata: Dict[str, str]) -> bool:
        """设置对象元数据。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.set_object_metadata, key, metadata)

    async def get_object_metadata(self, key: str) -> Dict[str, str]:
        """获取对象元数据。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.get_object_metadata, key)

    async def restore_object(
        self,
        key: str,
        version_id: Optional[str] = None,
        tier: str = "Standard"
    ) -> bool:
        """恢复归档对象。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.restore_object,
            key,
            version_id,
            tier
        )

    async def initiate_multipart_upload(
        self,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """初始化分片上传。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.initiate_multipart_upload,
            key,
            content_type,
            metadata
        )

    async def upload_part(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes
    ) -> str:
        """上传分片。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.upload_part,
            key,
            upload_id,
            part_number,
            data
        )

    async def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: List[Dict[str, Any]]
    ) -> UploadResult:
        """完成分片上传。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.complete_multipart_upload,
            key,
            upload_id,
            parts
        )

    async def abort_multipart_upload(self, key: str, upload_id: str) -> bool:
        """中止分片上传。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.abort_multipart_upload, key, upload_id)

    async def list_multipart_uploads(self, max_uploads: int = 1000) -> List[Dict[str, Any]]:
        """列出进行中的分片上传。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.list_multipart_uploads, max_uploads)

    async def calculate_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """计算文件哈希值。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(self._provider.calculate_file_hash, file_path, algorithm)

    async def sync_directory(
        self,
        local_dir: str,
        remote_prefix: str = "",
        delete: bool = False
    ) -> Dict[str, Any]:
        """同步目录。"""
        if not self._provider:
            raise ExternalServiceError("存储服务未初始化", self.service_name)

        return await self._execute_with_retry(
            self._provider.sync_directory,
            local_dir,
            remote_prefix,
            delete
        )

    async def close(self) -> None:
        """关闭服务连接。"""
        if self._provider:
            try:
                await self._provider.close()
            except Exception as e:
                self.logger.error(f"关闭存储服务提供商时出错: {e}")
            self._provider = None

    def get_provider(self) -> Optional[StorageServiceInterface]:
        """获取当前存储服务提供商。"""
        return self._provider

    def change_provider(self, new_config: StorageConfig) -> None:
        """切换存储服务提供商。"""
        if self._provider:
            raise ExternalServiceError(
                "请先关闭当前提供商再切换",
                self.service_name
            )

        self.storage_config = new_config
        self.logger.info(f"已切换存储服务提供商配置: {new_config.provider.value}")


# 需要在文件顶部添加导入
from datetime import datetime
from ..base import ServiceStatus