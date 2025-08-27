# Hard and Soft Constraints

## Hard

- Teacher conflict‑free scheduling
- Room conflict‑free; feature compatibility
- Teacher availability and fixed periods respected
- Course hour totals met; student group clash‑free
- Travel time buffers across campuses

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
