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

## Caching and rate limiting

- ETags and conditional requests; rate limits per tenant
