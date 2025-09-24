"""存储服务提供商实现。"""

import os
import shutil
import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncIterator, BinaryIO
import aiofiles
import aiohttp
from datetime import datetime, timedelta

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

logger = logging.getLogger(__name__)


class LocalStorageService(BaseService, StorageServiceInterface):
    """本地文件存储服务。"""

    def __init__(self, config: ServiceConfig, storage_config: StorageConfig):
        super().__init__("local_storage", config)
        self.storage_config = storage_config
        self._base_path = Path(storage_config.local_path or "/tmp/storage")
        self._base_url = storage_config.base_url or "http://localhost:8000/files"

    @property
    def service_type(self) -> ServiceType:
        return ServiceType.STORAGE

    async def initialize(self) -> None:
        """初始化本地存储。"""
        try:
            # 创建基础目录
            self._base_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"本地存储初始化成功: {self._base_path}")

        except Exception as e:
            raise ExternalServiceError(
                f"本地存储初始化失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def health_check(self):
        """健康检查。"""
        try:
            start_time = datetime.now()

            # 检查目录权限
            test_file = self._base_path / "health_check.tmp"
            test_file.write_text("health check")
            test_file.unlink()

            response_time = (datetime.now() - start_time).total_seconds()

            self._health.status = ServiceStatus.HEALTHY
            self._health.message = "本地存储服务正常"
            self._health.response_time = response_time
            self._health.last_check = datetime.now()

            return self._health

        except Exception as e:
            self._health.status = ServiceStatus.UNAVAILABLE
            self._health.message = f"本地存储服务异常: {str(e)}"
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
        return await self._execute_with_retry(
            self._upload_file_impl,
            file_path,
            key,
            content_type,
            metadata,
            permission
        )

    async def _upload_file_impl(
        self,
        file_path: str,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        permission: Optional[StoragePermission] = None
    ) -> UploadResult:
        """实现文件上传。"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                raise ExternalServiceError(f"源文件不存在: {file_path}", self.service_name)

            target_path = self._base_path / key
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(source_path, target_path)

            # 计算文件哈希
            file_hash = await self.calculate_file_hash(file_path)

            # 保存元数据
            if metadata:
                metadata_file = target_path.with_suffix(target_path.suffix + ".meta")
                async with aiofiles.open(metadata_file, "w") as f:
                    await f.write(str(metadata))

            return UploadResult(
                success=True,
                key=key,
                etag=file_hash,
                location=f"{self._base_url}/{key}"
            )

        except Exception as e:
            raise ExternalServiceError(
                f"上传文件失败: {str(e)}",
                self.service_name,
                original_error=e
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
        return await self._execute_with_retry(
            self._upload_bytes_impl,
            data,
            key,
            content_type,
            metadata,
            permission
        )

    async def _upload_bytes_impl(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        permission: Optional[StoragePermission] = None
    ) -> UploadResult:
        """实现字节数据上传。"""
        try:
            target_path = self._base_path / key
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            async with aiofiles.open(target_path, "wb") as f:
                await f.write(data)

            # 计算哈希
            file_hash = hashlib.md5(data).hexdigest()

            # 保存元数据
            if metadata:
                metadata_file = target_path.with_suffix(target_path.suffix + ".meta")
                async with aiofiles.open(metadata_file, "w") as f:
                    await f.write(str(metadata))

            return UploadResult(
                success=True,
                key=key,
                etag=file_hash,
                location=f"{self._base_url}/{key}"
            )

        except Exception as e:
            raise ExternalServiceError(
                f"上传字节数据失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def download_file(self, key: str, file_path: str, version_id: Optional[str] = None) -> bool:
        """下载文件。"""
        return await self._execute_with_retry(self._download_file_impl, key, file_path, version_id)

    async def _download_file_impl(self, key: str, file_path: str, version_id: Optional[str] = None) -> bool:
        """实现文件下载。"""
        try:
            source_path = self._base_path / key
            if not source_path.exists():
                raise ExternalServiceError(f"文件不存在: {key}", self.service_name)

            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source_path, target_path)
            return True

        except Exception as e:
            raise ExternalServiceError(
                f"下载文件失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def download_bytes(self, key: str, version_id: Optional[str] = None) -> Optional[bytes]:
        """下载字节数据。"""
        return await self._execute_with_retry(self._download_bytes_impl, key, version_id)

    async def _download_bytes_impl(self, key: str, version_id: Optional[str] = None) -> Optional[bytes]:
        """实现字节数据下载。"""
        try:
            file_path = self._base_path / key
            if not file_path.exists():
                return None

            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()

        except Exception as e:
            raise ExternalServiceError(
                f"下载字节数据失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def download_stream(self, key: str, version_id: Optional[str] = None) -> AsyncIterator[bytes]:
        """下载文件流。"""
        file_path = self._base_path / key
        if not file_path.exists():
            return

        chunk_size = 8192
        async with aiofiles.open(file_path, "rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def delete_file(self, key: str, version_id: Optional[str] = None) -> bool:
        """删除文件。"""
        return await self._execute_with_retry(self._delete_file_impl, key, version_id)

    async def _delete_file_impl(self, key: str, version_id: Optional[str] = None) -> bool:
        """实现文件删除。"""
        try:
            file_path = self._base_path / key
            if file_path.exists():
                file_path.unlink()

                # 删除元数据文件
                metadata_file = file_path.with_suffix(file_path.suffix + ".meta")
                if metadata_file.exists():
                    metadata_file.unlink()

                return True
            return False

        except Exception as e:
            raise ExternalServiceError(
                f"删除文件失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def copy_file(
        self,
        source_key: str,
        dest_key: str,
        source_version_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> UploadResult:
        """复制文件。"""
        return await self._execute_with_retry(
            self._copy_file_impl,
            source_key,
            dest_key,
            source_version_id,
            metadata
        )

    async def _copy_file_impl(
        self,
        source_key: str,
        dest_key: str,
        source_version_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> UploadResult:
        """实现文件复制。"""
        try:
            source_path = self._base_path / source_key
            dest_path = self._base_path / dest_key

            if not source_path.exists():
                raise ExternalServiceError(f"源文件不存在: {source_key}", self.service_name)

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

            # 更新元数据
            if metadata:
                metadata_file = dest_path.with_suffix(dest_path.suffix + ".meta")
                async with aiofiles.open(metadata_file, "w") as f:
                    await f.write(str(metadata))

            # 计算文件哈希
            file_hash = await self.calculate_file_hash(str(source_path))

            return UploadResult(
                success=True,
                key=dest_key,
                etag=file_hash,
                location=f"{self._base_url}/{dest_key}"
            )

        except Exception as e:
            raise ExternalServiceError(
                f"复制文件失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def exists(self, key: str) -> bool:
        """检查文件是否存在。"""
        file_path = self._base_path / key
        return file_path.exists()

    async def get_object_info(self, key: str, version_id: Optional[str] = None) -> Optional[StorageObject]:
        """获取对象信息。"""
        try:
            file_path = self._base_path / key
            if not file_path.exists():
                return None

            stat = file_path.stat()

            # 读取元数据
            metadata = {}
            metadata_file = file_path.with_suffix(file_path.suffix + ".meta")
            if metadata_file.exists():
                async with aiofiles.open(metadata_file, "r") as f:
                    metadata_content = await f.read()
                    try:
                        metadata = eval(metadata_content)
                    except:
                        pass

            return StorageObject(
                key=key,
                size=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                etag=str(stat.st_mtime),  # 使用修改时间作为简单ETag
                content_type="application/octet-stream",
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"获取对象信息失败: {e}")
            return None

    async def list_objects(
        self,
        prefix: str = "",
        delimiter: Optional[str] = None,
        max_keys: int = 1000,
        start_after: Optional[str] = None
    ) -> List[StorageObject]:
        """列出对象。"""
        objects = []
        search_path = self._base_path / prefix

        for file_path in search_path.rglob("*") if prefix else self._base_path.glob("*"):
            if file_path.is_file() and not file_path.name.endswith(".meta"):
                # 跳过元数据文件
                if start_after and file_path.name <= start_after:
                    continue

                obj = await self.get_object_info(str(file_path.relative_to(self._base_path)))
                if obj:
                    objects.append(obj)

                if len(objects) >= max_keys:
                    break

        return objects

    async def generate_presigned_url(
        self,
        key: str,
        method: str = "GET",
        expires_in: int = 3600,
        version_id: Optional[str] = None
    ) -> PresignedURL:
        """生成预签名 URL（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持预签名 URL", self.service_name)

    async def generate_presigned_post(
        self,
        key: str,
        expires_in: int = 3600,
        conditions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """生成预签名 POST（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持预签名 POST", self.service_name)

    async def set_object_acl(self, key: str, permission: StoragePermission) -> bool:
        """设置对象 ACL（本地存储不支持）。"""
        # 本地存储总是返回成功
        return True

    async def get_object_acl(self, key: str) -> StoragePermission:
        """获取对象 ACL。"""
        return StoragePermission.PRIVATE

    async def set_object_metadata(self, key: str, metadata: Dict[str, str]) -> bool:
        """设置对象元数据。"""
        try:
            file_path = self._base_path / key
            metadata_file = file_path.with_suffix(file_path.suffix + ".meta")

            async with aiofiles.open(metadata_file, "w") as f:
                await f.write(str(metadata))

            return True

        except Exception as e:
            logger.error(f"设置对象元数据失败: {e}")
            return False

    async def get_object_metadata(self, key: str) -> Dict[str, str]:
        """获取对象元数据。"""
        file_path = self._base_path / key
        metadata_file = file_path.with_suffix(file_path.suffix + ".meta")

        if metadata_file.exists():
            async with aiofiles.open(metadata_file, "r") as f:
                content = await f.read()
                try:
                    return eval(content)
                except:
                    return {}
        return {}

    async def restore_object(
        self,
        key: str,
        version_id: Optional[str] = None,
        tier: str = "Standard"
    ) -> bool:
        """恢复归档对象（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持对象归档", self.service_name)

    async def initiate_multipart_upload(
        self,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """初始化分片上传（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持分片上传", self.service_name)

    async def upload_part(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes
    ) -> str:
        """上传分片（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持分片上传", self.service_name)

    async def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: List[Dict[str, Any]]
    ) -> UploadResult:
        """完成分片上传（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持分片上传", self.service_name)

    async def abort_multipart_upload(self, key: str, upload_id: str) -> bool:
        """中止分片上传（本地存储不支持）。"""
        raise ExternalServiceError("本地存储不支持分片上传", self.service_name)

    async def list_multipart_uploads(self, max_uploads: int = 1000) -> List[Dict[str, Any]]:
        """列出进行中的分片上传（本地存储不支持）。"""
        return []

    async def calculate_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """计算文件哈希值。"""
        hash_func = getattr(hashlib, algorithm)()
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    async def sync_directory(
        self,
        local_dir: str,
        remote_prefix: str = "",
        delete: bool = False
    ) -> Dict[str, Any]:
        """同步目录。"""
        results = {
            "uploaded": 0,
            "deleted": 0,
            "skipped": 0,
            "errors": 0
        }

        local_path = Path(local_dir)
        if not local_path.exists():
            raise ExternalServiceError(f"本地目录不存在: {local_dir}", self.service_name)

        try:
            # 上传文件
            for file_path in local_path.rglob("*"):
                if file_path.is_file():
                    remote_key = f"{remote_prefix}/{file_path.relative_to(local_path)}".lstrip("/")
                    if await self.exists(remote_key):
                        results["skipped"] += 1
                    else:
                        try:
                            await self.upload_file(str(file_path), remote_key)
                            results["uploaded"] += 1
                        except Exception as e:
                            logger.error(f"同步文件失败 {file_path}: {e}")
                            results["errors"] += 1

            # 删除远程多余的文件
            if delete:
                remote_objects = await self.list_objects(prefix=remote_prefix)
                for obj in remote_objects:
                    local_file = local_path / obj.key[len(remote_prefix):].lstrip("/")
                    if not local_file.exists():
                        try:
                            await self.delete_file(obj.key)
                            results["deleted"] += 1
                        except Exception as e:
                            logger.error(f"删除远程文件失败 {obj.key}: {e}")
                            results["errors"] += 1

            return results

        except Exception as e:
            raise ExternalServiceError(
                f"同步目录失败: {str(e)}",
                self.service_name,
                original_error=e
            )

    async def close(self) -> None:
        """关闭服务连接。"""
        pass


# 需要在文件顶部添加导入
from ..base import ServiceStatus