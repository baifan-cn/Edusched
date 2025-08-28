# Engine Orchestration

## Lifecycle

- draft → running → feasible → optimized → published
- Idempotency keys; retries
- Checkpoints for pause/resume; rollback on cancel

## Components

- Worker (RQ) running OR‑Tools CP‑SAT and local search
- Redis queue and pub/sub for progress
- DB for inputs/outputs and audit

## Events

- Progress updates, conflict alerts, publish notifications via WS

### 事件 schema（版本化）

参考 `backend/api-design.md` 与 `algorithms/feasibility-and-diagnostics.md` 的消息体；包含 `version`, `event`, `job_id`, `phase`, `percent`, `metrics`, `conflicts?`。

## 状态机与重入（草案）

- 触发：`POST /v1/jobs` 创建作业（携带 `idempotency-key`）
- 状态：`draft -> running(feasibility) -> feasible -> running(optimization) -> optimized -> published`
- 重入：根据 `idempotency-key` 与 `checkpoint` 实现幂等与断点续跑
- 取消：`cancelled`（触发回滚到最近稳定快照）

### 重试与退避

- 最大重试：`max_retries=N`（默认 3）
- 退避：指数退避 `base=2`，加抖动；对可恢复错误（网络/资源暂不可用）适用
- 不可重试：业务逻辑冲突/输入无效

## Checkpoint 策略

- 粒度：输入快照（经过规范化/排序）、部分解（已分配集合）、随机种子
- 存储：`job.checkpoint (jsonb)` + 对应 `timetable` 版本号
- 频率：阶段性进度（例如每 N 次改进或时间片）

### 大实例处理

- 分片：按 resource/time 切片为子任务；父任务聚合得分与可行性
- 并行：多 worker 并发；控制 Redis 队列长度与优先级（`high/default/low`）
- 内存与时间预算：任务入队时根据规模估算预算（timeslots × sections × teachers）

## 进度与指标

- 进度：`{ percent, phase, elapsed_ms, eta_ms }`
- 指标：当前最优得分、可行/不可行标记、改进次数、邻域搜索步数
- 事件：`progress`, `feasible_found`, `improved`, `conflict`, `completed`

### 连接健壮性

- WebSocket/SSE 客户端断线重连：携带 `Last-Event-Id` 或 offset，请求补发未读事件
- 服务器端事件缓冲：按 `job_id` 保存最近 N 条事件（带自增 offset），超时淘汰
