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

## Real-time

- WebSocket channels for job progress and alerts

## Webhooks

- Optional outbound events: `schedule_published`, `job_completed`

## Caching and rate limiting

- ETags and conditional requests; rate limits per tenant
