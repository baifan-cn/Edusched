"""Mock工具类"""

import uuid
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import json


class MockUtils:
    """Mock工具类"""

    @staticmethod
    def create_mock_redis():
        """创建模拟Redis客户端"""
        mock_redis = MagicMock()

        # 模拟Redis方法
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.exists.return_value = False
        mock_redis.keys.return_value = []
        mock_redis.hget.return_value = None
        mock_redis.hset.return_value = 1
        mock_redis.hdel.return_value = 1
        mock_redis.hgetall.return_value = {}
        mock_redis.lpush.return_value = 1
        mock_redis.rpush.return_value = 1
        mock_redis.lpop.return_value = None
        mock_redis.llen.return_value = 0
        mock_redis.expire.return_value = True

        return mock_redis

    @staticmethod
    def create_mock_http_client():
        """创建模拟HTTP客户端"""
        mock_client = MagicMock()

        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.text = ""
        mock_response.content = b""
        mock_response.headers = {}

        mock_client.get.return_value = mock_response
        mock_client.post.return_value = mock_response
        mock_client.put.return_value = mock_response
        mock_client.delete.return_value = mock_response
        mock_client.patch.return_value = mock_response

        return mock_client

    @staticmethod
    def create_mock_async_http_client():
        """创建模拟异步HTTP客户端"""
        mock_client = MagicMock()

        # 模拟异步响应
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.text = ""
        mock_response.content = b""
        mock_response.headers = {}

        mock_client.get.return_value = mock_response
        mock_client.post.return_value = mock_response
        mock_client.put.return_value = mock_response
        mock_client.delete.return_value = mock_response
        mock_client.patch.return_value = mock_response

        return mock_client

    @staticmethod
    def create_mock_email_service():
        """创建模拟邮件服务"""
        mock_service = MagicMock()

        # 模拟邮件发送
        mock_service.send_email.return_value = {"message_id": str(uuid.uuid4())}
        mock_service.send_template_email.return_value = {"message_id": str(uuid.uuid4())}
        mock_service.send_bulk_email.return_value = {"sent_count": 1}

        return mock_service

    @staticmethod
    def create_mock_file_storage():
        """创建模拟文件存储服务"""
        mock_storage = MagicMock()

        # 模拟文件操作
        mock_storage.upload_file.return_value = {"file_id": str(uuid.uuid4()), "url": "http://example.com/file"}
        mock_storage.download_file.return_value = b"file content"
        mock_storage.delete_file.return_value = True
        mock_storage.file_exists.return_value = True
        mock_storage.get_file_info.return_value = {
            "size": 1024,
            "content_type": "application/octet-stream",
            "created_at": datetime.now()
        }

        return mock_storage

    @staticmethod
    def create_mock_logger():
        """创建模拟日志器"""
        mock_logger = MagicMock()

        # 模拟日志方法
        mock_logger.debug.return_value = None
        mock_logger.info.return_value = None
        mock_logger.warning.return_value = None
        mock_logger.error.return_value = None
        mock_logger.critical.return_value = None

        return mock_logger

    @staticmethod
    def create_mock_scheduler():
        """创建模拟调度器"""
        mock_scheduler = MagicMock()

        # 模拟调度方法
        mock_scheduler.add_job.return_value = str(uuid.uuid4())
        mock_scheduler.remove_job.return_value = True
        mock_scheduler.pause_job.return_value = True
        mock_scheduler.resume_job.return_value = True
        mock_scheduler.get_jobs.return_value = []

        return mock_scheduler

    @staticmethod
    def create_mock_cache():
        """创建模拟缓存"""
        mock_cache = MagicMock()

        # 模拟缓存方法
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        mock_cache.delete.return_value = True
        mock_cache.clear.return_value = True
        mock_cache.exists.return_value = False
        mock_cache.ttl.return_value = 3600

        return mock_cache

    @staticmethod
    def create_mock_external_api():
        """创建模拟外部API"""
        mock_api = MagicMock()

        # 模拟API响应
        mock_api.call.return_value = {
            "success": True,
            "data": {},
            "message": "Success"
        }

        return mock_api

    @staticmethod
    def create_mock_database_session():
        """创建模拟数据库会话"""
        mock_session = MagicMock()

        # 模拟数据库方法
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.rollback.return_value = None
        mock_session.close.return_value = None
        mock_session.query.return_value = MagicMock()
        mock_session.execute.return_value = MagicMock()
        mock_session.flush.return_value = None

        # 模拟查询
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.first.return_value = None
        mock_query.count.return_value = 0
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        mock_session.query.return_value = mock_query

        return mock_session

    @staticmethod
    def patch_redis():
        """Patch Redis"""
        return patch('redis.Redis', return_value=MockUtils.create_mock_redis())

    @staticmethod
    def patch_http_client():
        """Patch HTTP客户端"""
        return patch('httpx.Client', return_value=MockUtils.create_mock_http_client())

    @staticmethod
    def patch_async_http_client():
        """Patch异步HTTP客户端"""
        return patch('httpx.AsyncClient', return_value=MockUtils.create_mock_async_http_client())

    @staticmethod
    def patch_email_service():
        """Patch邮件服务"""
        return patch('edusched.infrastructure.external.email.EmailService',
                    return_value=MockUtils.create_mock_email_service())

    @staticmethod
    def patch_file_storage():
        """Patch文件存储"""
        return patch('edusched.infrastructure.external.storage.FileStorage',
                    return_value=MockUtils.create_mock_file_storage())

    @staticmethod
    def patch_logger():
        """Patch日志器"""
        return patch('logging.getLogger', return_value=MockUtils.create_mock_logger())

    @staticmethod
    def patch_scheduler():
        """Patch调度器"""
        return patch('apscheduler.schedulers.background.BackgroundScheduler',
                    return_value=MockUtils.create_mock_scheduler())

    @staticmethod
    def patch_cache():
        """Patch缓存"""
        return patch('edusched.infrastructure.cache.Cache',
                    return_value=MockUtils.create_mock_cache())

    @staticmethod
    def patch_external_api():
        """Patch外部API"""
        return patch('edusched.infrastructure.external.api.ExternalAPI',
                    return_value=MockUtils.create_mock_external_api())

    @staticmethod
    def patch_database_session():
        """Patch数据库会话"""
        return patch('edusched.infrastructure.database.connection.get_db',
                    return_value=MockUtils.create_mock_database_session())

    @staticmethod
    def create_mock_response(
        status_code: int = 200,
        json_data: Optional[Dict] = None,
        text: Optional[str] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict] = None
    ) -> MagicMock:
        """创建模拟HTTP响应"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = text or ""
        mock_response.content = content or b""
        mock_response.headers = headers or {}
        return mock_response

    @staticmethod
    def create_mock_exception(exception_type: type, message: str) -> Exception:
        """创建模拟异常"""
        return exception_type(message)

    @staticmethod
    def create_mock_model(model_class, **kwargs):
        """创建模拟模型"""
        mock_model = MagicMock(spec=model_class)
        mock_model.__dict__.update(kwargs)
        return mock_model

    @staticmethod
    def setup_mock_side_effects(mock_obj, side_effects: Dict[str, Any]):
        """设置mock对象的side effects"""
        for method_name, side_effect in side_effects.items():
            getattr(mock_obj, method_name).side_effect = side_effect

    @staticmethod
    def setup_mock_return_values(mock_obj, return_values: Dict[str, Any]):
        """设置mock对象的return values"""
        for method_name, return_value in return_values.items():
            getattr(mock_obj, method_name).return_value = return_value

    @staticmethod
    def assert_mock_called_with(mock_obj, method_name: str, *args, **kwargs):
        """断言mock方法被调用"""
        getattr(mock_obj, method_name).assert_called_with(*args, **kwargs)

    @staticmethod
    def assert_mock_called_once(mock_obj, method_name: str):
        """断言mock方法被调用一次"""
        getattr(mock_obj, method_name).assert_called_once()

    @staticmethod
    def assert_mock_not_called(mock_obj, method_name: str):
        """断言mock方法未被调用"""
        getattr(mock_obj, method_name).assert_not_called()

    @staticmethod
    def reset_mock(mock_obj):
        """重置mock对象"""
        mock_obj.reset_mock()