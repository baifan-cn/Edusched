# Hard and Soft Constraints

## Hard

- Teacher conflict‑free scheduling
- Room conflict‑free; feature compatibility
- Teacher availability and fixed periods respected
- Course hour totals met; student group clash‑free
- Travel time buffers across campuses

### 线性化/CP 表达（示例）

- 教师冲突：`∀k,t: Σ_{s,r} x[s,t,r,k] ≤ 1`
- 房间冲突：`∀r,t: Σ_{s,k} x[s,t,r,k] ≤ 1`
- 课时满足：`∀s: Σ_{t,r,k} x[s,t,r,k] = hours[s]`（或按 block 聚合）
- 房间特性：`x[s,t,r,k] ≤ room_ok[s,r]`
- 教师资质：`x[s,t,r,k] ≤ teacher_ok[s,k]`
- 固定节次：对固定 `(s,t)` 约束 `Σ_{r,k} x[s,t,r,k] = 1`，其他 t 为 0
- 行程缓冲：禁止 `gap(t_prev,t_next) < travel_time(campus_prev,campus_next)+buffer` 的相邻分配（以蕴含/冲突对实现）

## Soft

- Preferences (teacher, class, room)
- Balance across week; spread of lessons
- Minimize idle gaps; limit consecutive lessons
- Fair workload; room utilization
- Minimize late‑day/early‑day sessions

## 细化（草案）

### 硬约束细化

- 教师冲突：任意时间槽内同一教师仅可被分配到一个班级
- 房间冲突：任意时间槽内同一房间只能被一个教学单元占用
- 房间特性：教学单元所需特性必须被房间满足（如实验室/设备）
- 固定节次：固定的会议/校会/升旗等必须占用指定节次
- 学生组无冲突：同一学生组同一时间不可被分配到多个教学单元
- 出行时间缓冲：跨校区课间必须留足缓冲

### 软约束细化

- 教师偏好：不偏好早/晚档、周一/周五等
- 班级偏好：避免连续重课、分散到不同日
- 均匀分布：将同一课程时段均匀分布在一周
- 连堂限制：限制连续上课节数与跨午休连堂
- 空档最小化：降低教师或班级在一天内的空档
- 房间偏好：优先分配偏好房间或近距离房间

### 软约束度量示例（与评分函数对齐）

- `min_idle_gap`：`g[k,d]` 聚合为分钟数，计入 `c_idle = Σ g[k,d]`
- `limit_consecutive`：超过阈值的连续节数产生惩罚 `c_cons`
- `spread_across_week`：与理想分布差异的 L1/L2 误差 `c_spread`
- `preferred_room`：非偏好房间计次 `c_roompref`
