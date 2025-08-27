# API Design

## Standards

- REST with OpenAPI; JSON
- Versioning: `/v1`
- Pagination, filtering (RSQL-like), sorting
- Idempotency keys for mutating operations
- Errors use `application/problem+json`

## AuthN/AuthZ

- OIDC + JWT
- RBAC roles: SuperAdmin, SchoolAdmin, Scheduler, Teacher, Student, Viewer
- Tenant scoping via claims

## Resources (high-level)

- Auth/session
- Tenants/Schools
- Terms/Calendars
- Rooms/Features
- Teachers/Availabilities/Contracts
- Grades/ClassGroups/StudentGroups
- Subjects/CourseOfferings/Sections
- Constraints/WeightProfiles
- Timetables/Assignments
- Jobs (run/stop/status)
- Imports/Exports
- Notifications
- Audit

## CRUD 与 DTO 关键字段（示例选段）

- Teachers
  - Create: `first_name`, `last_name`, `code`, `email`, `campus_id?`
  - Read: `id`, `code`, `name`, `campus_id`, `metadata`
  - Constraints: `code` 唯一（tenant+school）
- Rooms
  - Create: `campus_id`, `name`, `code`, `capacity`, `features?`
  - Constraints: `code` 唯一（tenant+campus）
- Timeslots
  - Read: `term_id`, `day_of_week`, `period_index`, `week_parity`
- Timetables
  - Update: `If-Match` 头（ETag），`lock_version` 乐观锁
- Assignments
  - Create: `timetable_id`, `section_id`, `timeslot_id`, `room_id`, `teacher_id`, `block_length?`
  - Validation: 冲突检查（教师/房间/学生组）

## 资源草案与路径（示例）

- `/v1/schools`，`/v1/campuses`
- `/v1/terms`，`/v1/calendars`，`/v1/period-templates`
- `/v1/teachers`，`/v1/teacher-availabilities`，`/v1/teacher-contracts`
- `/v1/rooms`，`/v1/room-features`
- `/v1/grades`，`/v1/class-groups`，`/v1/student-groups`
- `/v1/subjects`，`/v1/course-offerings`，`/v1/sections`
- `/v1/constraints`，`/v1/weight-profiles`
- `/v1/timetables`，`/v1/assignments`
- `/v1/jobs`（POST run/stop；GET status/stream）
- `/v1/imports`，`/v1/exports`
- `/v1/notifications`，`/v1/audit-events`

## 查询与过滤

- 分页：`page`, `page_size`
- 过滤：RSQL 风格或 `filter[field]=op:value` 简化语法
- 排序：`sort=field,-field2`

### 过滤运算符白名单（建议）

- 比较：`eq`, `ne`, `lt`, `lte`, `gt`, `gte`
- 集合：`in`, `out`
- 模糊：`like`, `ilike`
- 布尔：`isnull`

字段白名单示例：`teacher.code`, `room.code`, `room.capacity`, `timeslot.day_of_week`, `section.offering_id`。

### 示例

```
GET /v1/teachers?page=1&page_size=50&sort=last_name,-first_name&filter[campus_id]==:uuid&filter[subject]==eq:Math

200 OK
{
  "data": [ {"id": "...", "first_name": "...", "last_name": "..."} ],
  "page": 1,
  "page_size": 50,
  "total": 1234
}
```

## 幂等与并发

- `Idempotency-Key` 头部支持创建/启动类操作
- 乐观锁：`If-Match` + `ETag`（如编辑 `timetable`）

缓存/代理兼容性：确保响应头含 `ETag` 与 `Cache-Control: no-store`（对敏感资源），避免代理缓存带来一致性问题。

### 错误响应（problem+json）

```
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "https://edusched.dev/problems/version-conflict",
  "title": "Version conflict",
  "status": 409,
  "detail": "ETag does not match current resource version",
  "instance": "/v1/timetables/abc-123"
}
```

## 实时与事件

- WebSocket：`/ws/jobs/{job_id}` 推送进度与冲突告警
- Webhook（可选）：`schedule_published`, `job_completed`

消息 schema（版本化，示意）：

```
{
  "version": "1.0",
  "event": "progress|conflict|published",
  "job_id": "...",
  "data": { "percent": 42, "conflicts": [ ... ] }
}
```

### WebSocket 消息示例

```
{
  "event": "progress",
  "job_id": "job-123",
  "phase": "optimization",
  "percent": 42,
  "metrics": {"best_score": 12345, "improvements": 17}
}
```

## Real-time

- WebSocket channels for job progress and alerts

## Webhooks

- Optional outbound events: `schedule_published`, `job_completed`
 - 重试与签名：HMAC-SHA256 签名头（时效 5 分钟），最多重试 5 次指数退避

## Caching and rate limiting

- ETags and conditional requests; rate limits per tenant

## 错误码与 problem+json 目录（建议）

- 400 `invalid_request`：参数或 DTO 校验失败
- 401 `unauthorized`：缺少/无效令牌
- 403 `forbidden`：权限不足或越权的租户/校区访问
- 404 `not_found`：资源不存在或无访问权
- 409 `version_conflict`：ETag/lock_version 冲突
- 409 `idempotency_conflict`：幂等键重复冲突
- 422 `business_rule_violation`：硬约束冲突（教师/房间/学生组）
- 429 `rate_limited`：超过速率限制
- 503 `job_capacity_exceeded`：队列满或暂不可受理

错误响应统一采用 `application/problem+json`，`type` 指向文档链接，`instance` 为资源或作业路径。

## OIDC Claims 映射与租户切换

- 必要声明：`sub`, `iss`, `aud`, `exp`；自定义：`tenant_id`, `campus_ids`, `roles`
- 租户切换：允许用户在拥有多个租户授权时通过 `X-Act-As-Tenant` 请求头切换；服务端校验 `sub` 对该租户是否有角色绑定。
