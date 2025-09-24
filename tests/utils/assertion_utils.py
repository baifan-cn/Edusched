"""断言工具类"""

import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import json


class AssertionUtils:
    """断言工具类"""

    @staticmethod
    def assert_uuid_format(uuid_str: str):
        """断言UUID格式正确"""
        try:
            uuid.UUID(uuid_str)
        except ValueError:
            raise AssertionError(f"Invalid UUID format: {uuid_str}")

    @staticmethod
    def assert_email_format(email: str):
        """断言邮箱格式正确"""
        assert '@' in email, f"Invalid email format: {email}"
        assert '.' in email.split('@')[1], f"Invalid email format: {email}"

    @staticmethod
    def assert_phone_format(phone: str):
        """断言电话号码格式正确"""
        assert len(phone) >= 10, f"Phone number too short: {phone}"
        assert phone.isdigit(), f"Phone number contains non-digits: {phone}"

    @staticmethod
    def assert_date_format(date_str: str, format: str = "%Y-%m-%d"):
        """断言日期格式正确"""
        try:
            datetime.strptime(date_str, format)
        except ValueError:
            raise AssertionError(f"Invalid date format: {date_str}")

    @staticmethod
    def assert_datetime_format(datetime_str: str, format: str = "%Y-%m-%d %H:%M:%S"):
        """断言日期时间格式正确"""
        try:
            datetime.strptime(datetime_str, format)
        except ValueError:
            raise AssertionError(f"Invalid datetime format: {datetime_str}")

    @staticmethod
    def assert_time_format(time_str: str, format: str = "%H:%M"):
        """断言时间格式正确"""
        try:
            datetime.strptime(time_str, format)
        except ValueError:
            raise AssertionError(f"Invalid time format: {time_str}")

    @staticmethod
    def assert_json_format(json_str: str):
        """断言JSON格式正确"""
        try:
            json.loads(json_str)
        except json.JSONDecodeError:
            raise AssertionError(f"Invalid JSON format: {json_str}")

    @staticmethod
    def assert_dict_keys(data: Dict[str, Any], required_keys: List[str]):
        """断言字典包含必需的键"""
        missing_keys = [key for key in required_keys if key not in data]
        assert not missing_keys, f"Missing required keys: {missing_keys}"

    @staticmethod
    def assert_dict_no_extra_keys(data: Dict[str, Any], allowed_keys: List[str]):
        """断言字典没有额外的键"""
        extra_keys = [key for key in data.keys() if key not in allowed_keys]
        assert not extra_keys, f"Unexpected keys: {extra_keys}"

    @staticmethod
    def assert_dict_values_type(data: Dict[str, Any], expected_types: Dict[str, type]):
        """断言字典值的类型"""
        for key, expected_type in expected_types.items():
            if key in data:
                actual_value = data[key]
                assert isinstance(actual_value, expected_type), \
                    f"Key '{key}' should be {expected_type}, got {type(actual_value)}: {actual_value}"

    @staticmethod
    def assert_list_items_type(items: List[Any], expected_type: type):
        """断言列表项的类型"""
        for i, item in enumerate(items):
            assert isinstance(item, expected_type), \
                f"Item at index {i} should be {expected_type}, got {type(item)}: {item}"

    @staticmethod
    def assert_list_length(items: List[Any], expected_length: int):
        """断言列表长度"""
        assert len(items) == expected_length, \
            f"Expected list length {expected_length}, got {len(items)}"

    @staticmethod
    def assert_list_contains(items: List[Any], expected_item: Any):
        """断言列表包含指定项"""
        assert expected_item in items, f"List does not contain {expected_item}"

    @staticmethod
    def assert_list_not_contains(items: List[Any], unexpected_item: Any):
        """断言列表不包含指定项"""
        assert unexpected_item not in items, f"List contains unexpected {unexpected_item}"

    @staticmethod
    def assert_list_unique(items: List[Any]):
        """断言列表项唯一"""
        seen = set()
        duplicates = set()
        for item in items:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)
        assert not duplicates, f"List contains duplicate items: {duplicates}"

    @staticmethod
    def assert_string_length(text: str, min_length: int = 0, max_length: Optional[int] = None):
        """断言字符串长度"""
        length = len(text)
        assert length >= min_length, f"String length {length} is less than minimum {min_length}"
        if max_length is not None:
            assert length <= max_length, f"String length {length} exceeds maximum {max_length}"

    @staticmethod
    def assert_string_matches_pattern(text: str, pattern: str):
        """断言字符串匹配模式"""
        import re
        assert re.match(pattern, text), f"String '{text}' does not match pattern '{pattern}'"

    @staticmethod
    def assert_string_contains(text: str, substring: str):
        """断言字符串包含子串"""
        assert substring in text, f"String '{text}' does not contain '{substring}'"

    @staticmethod
    def assert_string_not_contains(text: str, substring: str):
        """断言字符串不包含子串"""
        assert substring not in text, f"String '{text}' contains '{substring}'"

    @staticmethod
    def assert_number_range(number: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]):
        """断言数值在指定范围内"""
        assert min_val <= number <= max_val, \
            f"Number {number} is not in range [{min_val}, {max_val}]"

    @staticmethod
    def assert_number_positive(number: Union[int, float]):
        """断言数值为正数"""
        assert number > 0, f"Number {number} is not positive"

    @staticmethod
    def assert_number_non_negative(number: Union[int, float]):
        """断言数值为非负数"""
        assert number >= 0, f"Number {number} is negative"

    @staticmethod
    def assert_number_non_positive(number: Union[int, float]):
        """断言数值为非正数"""
        assert number <= 0, f"Number {number} is positive"

    @staticmethod
    def assert_boolean_true(value: bool):
        """断言布尔值为True"""
        assert value is True, f"Expected True, got {value}"

    @staticmethod
    def assert_boolean_false(value: bool):
        """断言布尔值为False"""
        assert value is False, f"Expected False, got {value}"

    @staticmethod
    def assert_not_none(value: Any):
        """断言值不为None"""
        assert value is not None, f"Expected not None, got {value}"

    @staticmethod
    def assert_is_none(value: Any):
        """断言值为None"""
        assert value is None, f"Expected None, got {value}"

    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: str = ""):
        """断言值相等"""
        assert actual == expected, f"{message}: Expected {expected}, got {actual}"

    @staticmethod
    def assert_not_equal(actual: Any, expected: Any, message: str = ""):
        """断言值不相等"""
        assert actual != expected, f"{message}: Expected not equal to {expected}, got {actual}"

    @staticmethod
    def assert_dict_equal(actual: Dict[str, Any], expected: Dict[str, Any]):
        """断言字典相等"""
        assert actual == expected, f"Dictionaries are not equal. Expected: {expected}, Actual: {actual}"

    @staticmethod
    def assert_list_equal(actual: List[Any], expected: List[Any]):
        """断言列表相等"""
        assert actual == expected, f"Lists are not equal. Expected: {expected}, Actual: {actual}"

    @staticmethod
    def assert_datetime_in_range(dt: datetime, start_dt: datetime, end_dt: datetime):
        """断言日期时间在指定范围内"""
        assert start_dt <= dt <= end_dt, \
            f"Datetime {dt} is not in range [{start_dt}, {end_dt}]"

    @staticmethod
    def assert_date_in_range(d: date, start_d: date, end_d: date):
        """断言日期在指定范围内"""
        assert start_d <= d <= end_d, \
            f"Date {d} is not in range [{start_d}, {end_d}]"

    @staticmethod
    def assert_future_datetime(dt: datetime):
        """断言日期时间是未来时间"""
        assert dt > datetime.now(), f"Datetime {dt} is not in the future"

    @staticmethod
    def assert_past_datetime(dt: datetime):
        """断言日期时间是过去时间"""
        assert dt < datetime.now(), f"Datetime {dt} is not in the past"

    @staticmethod
    def assert_valid_status_code(status_code: int):
        """断言HTTP状态码有效"""
        assert 100 <= status_code <= 599, f"Invalid status code: {status_code}"

    @staticmethod
    def assert_success_status_code(status_code: int):
        """断言HTTP状态码表示成功"""
        assert 200 <= status_code < 300, f"Expected success status code, got {status_code}"

    @staticmethod
    def assert_client_error_status_code(status_code: int):
        """断言HTTP状态码表示客户端错误"""
        assert 400 <= status_code < 500, f"Expected client error status code, got {status_code}"

    @staticmethod
    def assert_server_error_status_code(status_code: int):
        """断言HTTP状态码表示服务器错误"""
        assert 500 <= status_code < 600, f"Expected server error status code, got {status_code}"

    @staticmethod
    def assert_response_structure(response_data: Dict[str, Any], required_keys: List[str]):
        """断言响应数据结构正确"""
        AssertionUtils.assert_dict_keys(response_data, required_keys)

    @staticmethod
    def assert_response_contains_data(response_data: Dict[str, Any]):
        """断言响应包含数据"""
        AssertionUtils.assert_dict_keys(response_data, ['data'])

    @staticmethod
    def assert_response_contains_message(response_data: Dict[str, Any]):
        """断言响应包含消息"""
        AssertionUtils.assert_dict_keys(response_data, ['message'])

    @staticmethod
    def assert_response_success(response_data: Dict[str, Any]):
        """断言响应表示成功"""
        AssertionUtils.assert_dict_keys(response_data, ['success'])
        AssertionUtils.assert_boolean_true(response_data['success'])

    @staticmethod
    def assert_response_error(response_data: Dict[str, Any]):
        """断言响应表示错误"""
        AssertionUtils.assert_dict_keys(response_data, ['success'])
        AssertionUtils.assert_boolean_false(response_data['success'])

    @staticmethod
    def assert_tenant_id_consistency(data: Dict[str, Any], tenant_id: str):
        """断言租户ID一致性"""
        if 'tenant_id' in data:
            AssertionUtils.assert_equal(data['tenant_id'], tenant_id)

    @staticmethod
    def assert_created_timestamp(timestamp: datetime):
        """断言创建时间戳合理"""
        AssertionUtils.assert_past_datetime(timestamp)
        AssertionUtils.assert_datetime_in_range(
            timestamp,
            datetime.now().replace(year=datetime.now().year - 1),
            datetime.now()
        )

    @staticmethod
    def assert_updated_timestamp_after_created(updated_at: datetime, created_at: datetime):
        """断言更新时间在创建时间之后"""
        AssertionUtils.assert_datetime_in_range(updated_at, created_at, datetime.now())

    @staticmethod
    def assert_active_flag_consistency(data: Dict[str, Any]):
        """断言活跃标志一致性"""
        if 'is_active' in data:
            AssertionUtils.assert_boolean_type(data['is_active'])

    @staticmethod
    def assert_boolean_type(value: Any):
        """断言值是布尔类型"""
        assert isinstance(value, bool), f"Expected boolean, got {type(value)}: {value}"

    @staticmethod
    def assert_integer_type(value: Any):
        """断言值是整数类型"""
        assert isinstance(value, int), f"Expected integer, got {type(value)}: {value}"

    @staticmethod
    def assert_float_type(value: Any):
        """断言值是浮点数类型"""
        assert isinstance(value, (int, float)), f"Expected float, got {type(value)}: {value}"

    @staticmethod
    def assert_string_type(value: Any):
        """断言值是字符串类型"""
        assert isinstance(value, str), f"Expected string, got {type(value)}: {value}"

    @staticmethod
    def assert_list_type(value: Any):
        """断言值是列表类型"""
        assert isinstance(value, list), f"Expected list, got {type(value)}: {value}"

    @staticmethod
    def assert_dict_type(value: Any):
        """断言值是字典类型"""
        assert isinstance(value, dict), f"Expected dict, got {type(value)}: {value}"

    @staticmethod
    def assert_positive_integer(value: Any):
        """断言值是正整数"""
        AssertionUtils.assert_integer_type(value)
        AssertionUtils.assert_number_positive(value)

    @staticmethod
    def assert_non_negative_integer(value: Any):
        """断言值是非负整数"""
        AssertionUtils.assert_integer_type(value)
        AssertionUtils.assert_number_non_negative(value)

    @staticmethod
    def assert_percentage_value(value: Any):
        """断言值是百分比（0-1之间）"""
        AssertionUtils.assert_float_type(value)
        AssertionUtils.assert_number_range(value, 0.0, 1.0)