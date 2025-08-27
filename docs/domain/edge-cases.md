# Edge Cases

- Alternating weeks and block schedules
- Fixed periods and assemblies
- Shared teachers and partial availability
- Labs/equipment dependencies
- Max consecutive lessons; lunch breaks
- Multi‑campus travel times
  - 教师跨校区课程需满足行程耗时与缓冲：`travel_time(src,dst) + buffer <= timeslot_gap`
  - 行程矩阵空缺时视为不可达（硬约束冲突）
- Split or combined classes; bilingual/co‑teach
- Exam weeks and special events
- Last‑minute changes and overrides

### Timeslot/Period 细节

- 单双周（odd/even/both）与块排（block_length>1）组合可能导致边界冲突；需在生成 Timeslot 与校验 Assignment 时处理。

### 并发与乐观锁

- 多人协同编辑同一 `timetable/assignment` 时，使用 `ETag/If-Match` 或 `lock_version` 防止覆盖。
- 批量操作需按资源粒度返回冲突集合，避免部分成功导致状态不一致。

## Risks and mitigations

- Data quality variability → strong import validation and dry‑run
- Large instance runtime → timeouts, progressive relaxation, warm starts, parallelization
- Change management → training materials and manual override UX
- Complex timetables → flexible constraint DSL with JSONB extensions
