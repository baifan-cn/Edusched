# Routes and Navigation

- Public: /login, /callback
- Tenant selector: /tenants
- Dashboard: /dashboard
- Data: /teachers, /rooms, /subjects, /offerings, /sections, /constraints
- Jobs: /jobs
- Timetable: /timetable
- Reports: /reports
- Settings: /settings
 
## 私有化与多校区导航考虑

- 多校区过滤：在主要数据视图与课表工作台提供校区筛选器
- 身份与授权：基于 OIDC/JWT 的租户与角色守卫（SchoolAdmin/Scheduler 等）
