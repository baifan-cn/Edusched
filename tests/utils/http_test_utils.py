"""HTTP测试工具"""

import json
from typing import Any, Dict, List, Optional, Union
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest


class HttpTestUtils:
    """HTTP测试工具类"""

    def __init__(self, test_client: TestClient = None):
        self.test_client = test_client

    def set_test_client(self, test_client: TestClient):
        """设置测试客户端"""
        self.test_client = test_client

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        response = self.test_client.get(url, headers=headers, **kwargs)
        return self._process_response(response)

    def post(self, url: str, json_data: Optional[Dict[str, Any]] = None,
             data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        if json_data:
            response = self.test_client.post(url, json=json_data, headers=headers, **kwargs)
        else:
            response = self.test_client.post(url, data=data, headers=headers, **kwargs)
        return self._process_response(response)

    def put(self, url: str, json_data: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送PUT请求"""
        if json_data:
            response = self.test_client.put(url, json=json_data, headers=headers, **kwargs)
        else:
            response = self.test_client.put(url, data=data, headers=headers, **kwargs)
        return self._process_response(response)

    def patch(self, url: str, json_data: Optional[Dict[str, Any]] = None,
              data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送PATCH请求"""
        if json_data:
            response = self.test_client.patch(url, json=json_data, headers=headers, **kwargs)
        else:
            response = self.test_client.patch(url, data=data, headers=headers, **kwargs)
        return self._process_response(response)

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送DELETE请求"""
        response = self.test_client.delete(url, headers=headers, **kwargs)
        return self._process_response(response)

    def _process_response(self, response) -> Dict[str, Any]:
        """处理响应"""
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"text": response.text}

        return {
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers),
            "response": response
        }

    def assert_status_code(self, response: Dict[str, Any], expected_status_code: int):
        """断言状态码"""
        assert response["status_code"] == expected_status_code, \
            f"Expected status code {expected_status_code}, got {response['status_code']}"

    def assert_success_response(self, response: Dict[str, Any]):
        """断言成功响应"""
        self.assert_status_code(response, 200)
        if "success" in response["data"]:
            assert response["data"]["success"], f"Response indicates failure: {response['data']}"

    def assert_error_response(self, response: Dict[str, Any], expected_status_code: int = 400):
        """断言错误响应"""
        self.assert_status_code(response, expected_status_code)
        if "success" in response["data"]:
            assert not response["data"]["success"], f"Response indicates success: {response['data']}"

    def assert_response_contains(self, response: Dict[str, Any], key: str, expected_value: Any = None):
        """断言响应包含指定键"""
        assert key in response["data"], f"Response does not contain key '{key}'"
        if expected_value is not None:
            assert response["data"][key] == expected_value, \
                f"Expected {key}={expected_value}, got {response['data'][key]}"

    def assert_response_structure(self, response: Dict[str, Any], required_keys: List[str]):
        """断言响应结构"""
        for key in required_keys:
            assert key in response["data"], f"Response does not contain required key '{key}'"

    def assert_response_data_type(self, response: Dict[str, Any], key: str, expected_type: type):
        """断言响应数据类型"""
        assert key in response["data"], f"Response does not contain key '{key}'"
        actual_value = response["data"][key]
        assert isinstance(actual_value, expected_type), \
            f"Expected {key} to be {expected_type}, got {type(actual_value)}: {actual_value}"

    def assert_response_list_length(self, response: Dict[str, Any], key: str, expected_length: int):
        """断言响应列表长度"""
        assert key in response["data"], f"Response does not contain key '{key}'"
        actual_list = response["data"][key]
        assert isinstance(actual_list, list), f"Expected {key} to be a list, got {type(actual_list)}"
        assert len(actual_list) == expected_length, \
            f"Expected {key} length {expected_length}, got {len(actual_list)}"

    def assert_response_dict_contains(self, response: Dict[str, Any], dict_key: str, required_subkeys: List[str]):
        """断言响应字典包含子键"""
        assert dict_key in response["data"], f"Response does not contain dict key '{dict_key}'"
        actual_dict = response["data"][dict_key]
        assert isinstance(actual_dict, dict), f"Expected {dict_key} to be a dict, got {type(actual_dict)}"
        for subkey in required_subkeys:
            assert subkey in actual_dict, f"Dict {dict_key} does not contain subkey '{subkey}'"

    def get_response_data(self, response: Dict[str, Any]) -> Any:
        """获取响应数据"""
        return response["data"]

    def get_response_headers(self, response: Dict[str, Any]) -> Dict[str, str]:
        """获取响应头"""
        return response["headers"]

    def get_response_status_code(self, response: Dict[str, Any]) -> int:
        """获取响应状态码"""
        return response["status_code"]

    def create_auth_headers(self, token: str) -> Dict[str, str]:
        """创建认证头"""
        return {"Authorization": f"Bearer {token}"}

    def create_tenant_headers(self, tenant_id: str) -> Dict[str, str]:
        """创建租户头"""
        return {"X-Tenant-ID": tenant_id}

    def create_content_type_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """创建内容类型头"""
        return {"Content-Type": content_type}

    def create_standard_headers(self, token: str = None, tenant_id: str = None) -> Dict[str, str]:
        """创建标准头"""
        headers = {}
        if token:
            headers.update(self.create_auth_headers(token))
        if tenant_id:
            headers.update(self.create_tenant_headers(tenant_id))
        return headers

    def test_pagination(self, url: str, headers: Optional[Dict[str, str]] = None,
                       page: int = 1, size: int = 20) -> Dict[str, Any]:
        """测试分页"""
        params = {"page": page, "size": size}
        response = self.test_client.get(url, headers=headers, params=params)
        return self._process_response(response)

    def test_filtering(self, url: str, filters: Dict[str, Any],
                      headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试过滤"""
        response = self.test_client.get(url, headers=headers, params=filters)
        return self._process_response(response)

    def test_sorting(self, url: str, sort_field: str, sort_order: str = "asc",
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试排序"""
        params = {"sort": f"{sort_field}:{sort_order}"}
        response = self.test_client.get(url, headers=headers, params=params)
        return self._process_response(response)

    def test_search(self, url: str, search_term: str,
                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试搜索"""
        params = {"search": search_term}
        response = self.test_client.get(url, headers=headers, params=params)
        return self._process_response(response)

    def test_file_upload(self, url: str, file_path: str, field_name: str = "file",
                        headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试文件上传"""
        with open(file_path, "rb") as file:
            files = {field_name: file}
            response = self.test_client.post(url, files=files, headers=headers)
        return self._process_response(response)

    def test_form_data(self, url: str, form_data: Dict[str, Any],
                      headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试表单数据"""
        response = self.test_client.post(url, data=form_data, headers=headers)
        return self._process_response(response)


class AsyncHttpTestUtils:
    """异步HTTP测试工具类"""

    def __init__(self, async_client: AsyncClient = None):
        self.async_client = async_client

    def set_async_client(self, async_client: AsyncClient):
        """设置异步客户端"""
        self.async_client = async_client

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送异步GET请求"""
        response = await self.async_client.get(url, headers=headers, **kwargs)
        return self._process_response(response)

    async def post(self, url: str, json_data: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送异步POST请求"""
        if json_data:
            response = await self.async_client.post(url, json=json_data, headers=headers, **kwargs)
        else:
            response = await self.async_client.post(url, data=data, headers=headers, **kwargs)
        return self._process_response(response)

    async def put(self, url: str, json_data: Optional[Dict[str, Any]] = None,
                  data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送异步PUT请求"""
        if json_data:
            response = await self.async_client.put(url, json=json_data, headers=headers, **kwargs)
        else:
            response = await self.async_client.put(url, data=data, headers=headers, **kwargs)
        return self._process_response(response)

    async def patch(self, url: str, json_data: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送异步PATCH请求"""
        if json_data:
            response = await self.async_client.patch(url, json=json_data, headers=headers, **kwargs)
        else:
            response = await self.async_client.patch(url, data=data, headers=headers, **kwargs)
        return self._process_response(response)

    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
        """发送异步DELETE请求"""
        response = await self.async_client.delete(url, headers=headers, **kwargs)
        return self._process_response(response)

    def _process_response(self, response) -> Dict[str, Any]:
        """处理响应"""
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"text": response.text}

        return {
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers),
            "response": response
        }

    # 断言方法与HttpTestUtils相同
    def assert_status_code(self, response: Dict[str, Any], expected_status_code: int):
        """断言状态码"""
        assert response["status_code"] == expected_status_code, \
            f"Expected status code {expected_status_code}, got {response['status_code']}"

    def assert_success_response(self, response: Dict[str, Any]):
        """断言成功响应"""
        self.assert_status_code(response, 200)
        if "success" in response["data"]:
            assert response["data"]["success"], f"Response indicates failure: {response['data']}"

    def assert_error_response(self, response: Dict[str, Any], expected_status_code: int = 400):
        """断言错误响应"""
        self.assert_status_code(response, expected_status_code)
        if "success" in response["data"]:
            assert not response["data"]["success"], f"Response indicates success: {response['data']}"

    # 其他断言方法与HttpTestUtils相同，省略...


# 创建pytest fixture
@pytest.fixture
def http_utils(test_client: TestClient):
    """HTTP测试工具fixture"""
    utils = HttpTestUtils(test_client)
    return utils


@pytest.fixture
async def async_http_utils(async_client: AsyncClient):
    """异步HTTP测试工具fixture"""
    utils = AsyncHttpTestUtils(async_client)
    return utils