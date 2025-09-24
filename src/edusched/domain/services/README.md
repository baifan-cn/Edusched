# 领域服务层使用指南

## 概述

领域服务层封装了Edusched系统的核心业务逻辑，遵循领域驱动设计（DDD）原则。每个服务都负责特定的业务领域，确保业务规则的一致性。

## 服务架构

```
domain/services/
├── base.py              # 基础服务类和抽象接口
├── school_service.py    # 学校管理服务
├── teacher_service.py   # 教师管理服务
├── course_service.py    # 课程管理服务
├── timetable_service.py # 时间表管理服务
└── scheduling_domain_service.py # 调度领域服务
```

## 使用示例

### 1. 创建服务实例

```python
from edusched.domain.services import SchoolService, TeacherService

# 创建服务实例（需要传入租户ID）
tenant_id = "school_001"
school_service = SchoolService(tenant_id)
teacher_service = TeacherService(tenant_id)
```

### 2. 基本CRUD操作

```python
from uuid import uuid4
from edusched.domain.models import School

# 创建学校
school = School(
    name="示例学校",
    code="SCH001",
    academic_year="2024-2025",
    semester="fall",
    tenant_id=tenant_id
)

result = await school_service.create(school)
if result.success:
    print(f"学校创建成功: {result.data.id}")
else:
    print(f"创建失败: {result.error}")
```

### 3. 业务规则验证

```python
from edusched.domain.models import Teacher

# 创建教师
teacher = Teacher(
    employee_id="T001",
    name="张老师",
    email="zhang@example.com",
    department="数学系",
    max_hours_per_day=8,
    max_hours_per_week=40,
    tenant_id=tenant_id
)

# 服务会自动验证业务规则
result = await teacher_service.create(teacher)
```

### 4. 复杂业务操作

```python
# 激活学校
result = await school_service.activate_school(school_id)

# 计算教师工作负荷
workload = await teacher_service.calculate_teacher_workload(teacher_id)

# 发布时间表
result = await timetable_service.publish_timetable(timetable_id, user_id)

# 开始调度任务
job = await scheduling_service.start_scheduling(timetable_id)
```

### 5. 处理服务结果

```python
# 检查操作是否成功
if result.success:
    # 操作成功
    data = result.data
    message = result.message
    print(f"成功: {message}")
else:
    # 操作失败
    error = result.error
    validation_errors = result.metadata.get("validation_errors", [])
    print(f"失败: {error}")
    if validation_errors:
        print("验证错误:", validation_errors)
```

## 最佳实践

1. **始终使用服务层**：所有业务逻辑都应该通过服务层执行，而不是直接操作存储库

2. **处理服务结果**：总是检查ServiceResult的success字段

3. **事务管理**：复杂操作应该使用事务确保数据一致性

4. **错误处理**：提供有意义的错误信息，帮助用户理解问题

5. **业务规则验证**：在服务层实现所有业务规则验证

## 服务依赖

领域服务依赖于存储库（Repository）来访问持久化数据。存储库应该在服务实例化时注入：

```python
# 示例：依赖注入
school_service = SchoolService(
    tenant_id=tenant_id,
    school_repository=school_repository,
    campus_repository=campus_repository
)
```