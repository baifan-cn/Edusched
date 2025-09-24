# 应用服务层 (Application Service Layer)

应用服务层实现了CQRS（命令查询责任分离）模式，负责协调领域服务和基础设施操作。

## 目录结构

```
src/edusched/application/
├── __init__.py                 # 包初始化
├── base.py                     # 基础抽象类定义
├── factory.py                  # 应用服务工厂
├── commands/                   # 命令定义
│   ├── __init__.py
│   ├── school_commands.py      # 学校相关命令
│   ├── teacher_commands.py     # 教师相关命令
│   ├── course_commands.py      # 课程相关命令
│   └── timetable_commands.py   # 时间表相关命令
├── queries/                    # 查询定义
│   ├── __init__.py
│   ├── school_queries.py      # 学校相关查询
│   ├── teacher_queries.py     # 教师相关查询
│   ├── course_queries.py      # 课程相关查询
│   └── timetable_queries.py   # 时间表相关查询
├── handlers/                   # 处理器实现
│   ├── __init__.py
│   ├── command_handlers.py    # 命令处理器
│   └── query_handlers.py      # 查询处理器
├── dto/                        # 数据传输对象
│   ├── __init__.py
│   ├── school_dto.py          # 学校相关DTO
│   ├── teacher_dto.py         # 教师相关DTO
│   ├── timetable_dto.py      # 时间表相关DTO
│   └── common_dto.py          # 通用DTO
├── services/                   # 应用服务
│   ├── __init__.py
│   ├── school_service.py      # 学校应用服务
│   ├── timetable_service.py   # 时间表应用服务
│   └── dispatcher.py          # 命令查询分发器
└── events/                     # 事件处理
    ├── __init__.py
    └── domain_event_handlers.py # 领域事件处理器
```

## 核心概念

### 1. CQRS模式

- **Commands（命令）**: 表示写操作，改变系统状态
- **Queries（查询）**: 表示读操作，查询系统状态
- **Handlers（处理器）**: 处理具体的命令或查询

### 2. 基础类

#### BaseCommand
所有命令的基类，包含：
- tenant_id: 租户ID
- requested_by: 请求者
- correlation_id: 关联ID
- metadata: 元数据

#### BaseQuery
所有查询的基类，包含：
- tenant_id: 租户ID
- skip/limit: 分页参数
- sort_by/sort_order: 排序参数

#### CommandResult
命令执行结果，包含：
- success: 是否成功
- data: 返回数据
- error: 错误信息
- message: 提示信息
- events: 产生的事件

#### QueryResult
查询执行结果，包含：
- success: 是否成功
- data: 返回数据
- total: 总记录数
- page/size: 分页信息

### 3. 数据传输对象（DTO）

DTO用于应用层和API层之间的数据传递，包括：
- 创建DTO（CreateDTO）
- 更新DTO（UpdateDTO）
- 详情DTO（DTO）
- 列表DTO（通常继承详情DTO）

## 使用示例

### 1. 创建学校

```python
from edusched.application.commands import CreateSchoolCommand
from edusched.application.dto import SchoolCreateDTO
from edusched.application.factory import ApplicationServiceFactory

# 创建DTO
school_dto = SchoolCreateDTO(
    name="示例学校",
    code="SCHOOL001",
    address="北京市朝阳区",
    phone="010-12345678",
    academic_year="2024-2025",
    semester="fall"
)

# 创建命令
command = CreateSchoolCommand(
    tenant_id="tenant_001",
    requested_by="admin",
    **school_dto.dict()
)

# 发送命令
factory = ApplicationServiceFactory(...)
result = await factory.send_command(command)

if result.success:
    school = result.data
    print(f"学校创建成功: {school.name}")
else:
    print(f"创建失败: {result.error}")
```

### 2. 查询学校列表

```python
from edusched.application.queries import GetSchoolsQuery

# 创建查询
query = GetSchoolsQuery(
    tenant_id="tenant_001",
    keyword="示例",
    is_active=True,
    skip=0,
    limit=20,
    sort_by="name",
    sort_order="asc"
)

# 发送查询
result = await factory.send_query(query)

if result.success:
    schools = result.data
    print(f"共找到 {result.total} 所学校")
    for school in schools:
        print(f"- {school.name}")
```

### 3. 使用应用服务

```python
# 获取学校应用服务
school_service = factory.school_service

# 创建学校
result = await school_service.create_school(
    dto=school_dto,
    tenant_id="tenant_001",
    requested_by="admin"
)

# 查询学校
result = await school_service.get_schools(
    tenant_id="tenant_001",
    keyword="示例",
    page=1,
    size=20
)
```

## 事件处理

应用服务层支持领域事件处理：

1. **事件类型**:
   - 学校事件：创建、更新、删除、激活、停用
   - 教师事件：创建、更新、删除、工作量更新
   - 时间表事件：创建、更新、发布、调度完成等

2. **事件处理器**:
   - 处理事件后的业务逻辑
   - 更新缓存
   - 发送通知
   - 记录日志

## 依赖注入

应用服务层通过依赖注入获取所需的服务：

- 领域服务：SchoolService, TeacherService, TimetableService等
- 基础设施服务：CacheService, NotificationService
- 仓储：各种Repository实现

## 最佳实践

1. **保持应用服务轻量**:
   - 只协调，不包含业务逻辑
   - 业务逻辑放在领域层

2. **使用DTO隔离**:
   - 领域模型不直接暴露给API层
   - 通过DTO进行数据转换

3. **错误处理**:
   - 使用统一的错误返回格式
   - 记录详细的错误日志

4. **事件驱动**:
   - 通过事件解耦组件
   - 异步处理非关键路径

5. **性能优化**:
   - 合理使用缓存
   - 批量操作支持
   - 分页查询优化