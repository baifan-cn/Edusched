"""外部服务工厂。

用于创建和管理外部服务实例。
"""

from typing import Dict, Type, Optional, Any
import logging

from .base import BaseService, ServiceConfig, ServiceType, ExternalServiceError
from .email.service import EmailService
from .notification.service import NotificationService
from .storage.service import StorageService
from .logging.service import LoggingService
from .cache.service import CacheService


logger = logging.getLogger(__name__)


class ServiceFactory:
    """外部服务工厂。"""

    _service_registry: Dict[ServiceType, Type[BaseService]] = {
        ServiceType.EMAIL: EmailService,
        ServiceType.NOTIFICATION: NotificationService,
        ServiceType.STORAGE: StorageService,
        ServiceType.LOGGING: LoggingService,
        ServiceType.CACHE: CacheService,
    }

    _service_instances: Dict[str, BaseService] = {}

    @classmethod
    def register_service(
        cls,
        service_type: ServiceType,
        service_class: Type[BaseService]
    ) -> None:
        """注册服务类型。"""
        cls._service_registry[service_type] = service_class
        logger.info(f"已注册服务类型: {service_type.value}")

    @classmethod
    def create_service(
        cls,
        service_type: ServiceType,
        config: ServiceConfig,
        instance_name: Optional[str] = None,
        **kwargs: Any
    ) -> BaseService:
        """创建服务实例。"""
        if service_type not in cls._service_registry:
            raise ExternalServiceError(
                f"未知的服务类型: {service_type.value}",
                "ServiceFactory"
            )

        service_class = cls._service_registry[service_type]
        instance_key = f"{service_type.value}_{instance_name}" if instance_name else service_type.value

        # 检查是否已存在实例
        if instance_key in cls._service_instances:
            logger.warning(f"服务实例 {instance_key} 已存在，将返回现有实例")
            return cls._service_instances[instance_key]

        try:
            service = service_class(config, **kwargs)
            cls._service_instances[instance_key] = service
            logger.info(f"已创建服务实例: {instance_key}")
            return service

        except Exception as e:
            raise ExternalServiceError(
                f"创建服务实例失败: {str(e)}",
                "ServiceFactory",
                original_error=e
            )

    @classmethod
    def get_service(
        cls,
        service_type: ServiceType,
        instance_name: Optional[str] = None
    ) -> Optional[BaseService]:
        """获取服务实例。"""
        instance_key = f"{service_type.value}_{instance_name}" if instance_name else service_type.value
        return cls._service_instances.get(instance_key)

    @classmethod
    async def initialize_all(cls) -> None:
        """初始化所有服务实例。"""
        for service in cls._service_instances.values():
            try:
                await service.initialize()
                logger.info(f"服务 {service.service_name} 初始化成功")
            except Exception as e:
                logger.error(f"服务 {service.service_name} 初始化失败: {e}")

    @classmethod
    async def close_all(cls) -> None:
        """关闭所有服务实例。"""
        for service in cls._service_instances.values():
            try:
                await service.close()
                logger.info(f"服务 {service.service_name} 已关闭")
            except Exception as e:
                logger.error(f"关闭服务 {service.service_name} 时出错: {e}")

        cls._service_instances.clear()

    @classmethod
    def get_all_services(cls) -> Dict[str, BaseService]:
        """获取所有服务实例。"""
        return cls._service_instances.copy()

    @classmethod
    def remove_service(cls, service_type: ServiceType, instance_name: Optional[str] = None) -> bool:
        """移除服务实例。"""
        instance_key = f"{service_type.value}_{instance_name}" if instance_name else service_type.value

        if instance_key in cls._service_instances:
            service = cls._service_instances.pop(instance_key)
            logger.info(f"已移除服务实例: {instance_key}")
            return True

        return False


class ServiceManager:
    """服务管理器。

    提供统一的服务管理接口。
    """

    def __init__(self):
        self._services: Dict[str, BaseService] = {}

    async def add_service(
        self,
        service_type: ServiceType,
        config: ServiceConfig,
        name: str,
        **kwargs: Any
    ) -> BaseService:
        """添加服务。"""
        if name in self._services:
            raise ExternalServiceError(
                f"服务名称 {name} 已存在",
                "ServiceManager"
            )

        service = ServiceFactory.create_service(service_type, config, name, **kwargs)
        await service.initialize()
        self._services[name] = service
        return service

    async def remove_service(self, name: str) -> bool:
        """移除服务。"""
        if name in self._services:
            service = self._services.pop(name)
            await service.close()
            return True
        return False

    def get_service(self, name: str) -> Optional[BaseService]:
        """获取服务。"""
        return self._services.get(name)

    def get_service_by_type(self, service_type: ServiceType) -> Optional[BaseService]:
        """根据类型获取服务。"""
        for service in self._services.values():
            if service.service_type == service_type:
                return service
        return None

    async def health_check_all(self) -> Dict[str, Any]:
        """检查所有服务健康状态。"""
        results = {}
        for name, service in self._services.items():
            try:
                health = await service.health_check()
                results[name] = {
                    "status": health.status.value,
                    "message": health.message,
                    "response_time": health.response_time,
                    "error_count": health.error_count
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": str(e),
                    "error_count": service.get_health().error_count
                }
        return results

    async def close_all(self) -> None:
        """关闭所有服务。"""
        for service in self._services.values():
            try:
                await service.close()
            except Exception as e:
                logger.error(f"关闭服务 {service.service_name} 时出错: {e}")
        self._services.clear()

    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """列出所有服务信息。"""
        return {
            name: {
                "type": service.service_type.value,
                "name": service.service_name,
                "status": service.get_health().status.value,
                "metrics": {
                    "request_count": service.get_metrics().request_count,
                    "success_count": service.get_metrics().success_count,
                    "error_count": service.get_metrics().error_count,
                    "avg_response_time": (
                        service.get_metrics().total_response_time /
                        service.get_metrics().request_count
                        if service.get_metrics().request_count > 0
                        else 0
                    )
                }
            }
            for name, service in self._services.items()
        }


# 全局服务管理器实例
service_manager = ServiceManager()