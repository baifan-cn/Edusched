# Engine Orchestration

## Lifecycle

- draft → running → feasible → optimized → published
- Idempotency keys; retries
- Checkpoints for pause/resume; rollback on cancel

## Components

- Worker (Celery/RQ) running OR‑Tools CP‑SAT and local search
- Redis queue and pub/sub for progress
- DB for inputs/outputs and audit

## Events

- Progress updates, conflict alerts, publish notifications via WS

## 状态机与重入（草案）

- 触发：`POST /v1/jobs` 创建作业（携带 `idempotency-key`）
- 状态：`draft -> running(feasibility) -> feasible -> running(optimization) -> optimized -> published`
- 重入：根据 `idempotency-key` 与 `checkpoint` 实现幂等与断点续跑
- 取消：`cancelled`（触发回滚到最近稳定快照）

## Checkpoint 策略

- 粒度：输入快照（经过规范化/排序）、部分解（已分配集合）、随机种子
- 存储：`job.checkpoint (jsonb)` + 对应 `timetable` 版本号
- 频率：阶段性进度（例如每 N 次改进或时间片）

## 进度与指标

- 进度：`{ percent, phase, elapsed_ms, eta_ms }`
- 指标：当前最优得分、可行/不可行标记、改进次数、邻域搜索步数
- 事件：`progress`, `feasible_found`, `improved`, `conflict`, `completed`
