# Algorithm Approach Overview

## Strategy

Two‑stage hybrid:
1. Feasibility via CP‑SAT (hard constraints)
2. Optimization via weighted soft constraints with fairness

## Decision variables（文字化）

- 排课二元变量：`x[s, t, r, k] ∈ {0,1}` 表示 section `s` 在 timeslot `t` 使用房间 `r`、由教师 `k` 授课
- 辅助变量：
  - `u[s, t] ∈ {0,1}` section 是否占用时间槽 `t`（聚合到 block）
  - `g[k, d] ≥ 0` 教师 `k` 在天 `d` 的空档分钟数（用于软约束）
  - `c_i ≥ 0` 第 i 个软约束的违规计数/度量

域与参数（示例）：

- `T`：所有 time slots（含单双周）；`R`：可用房间；`K`：教师；`S`：section
- `hours[s]`：section 需授课节次数；`block_len[s]`：连堂长度；`room_ok[s, r]`：房间特性可用；`teacher_ok[s, k]`：可授课教师
- `adjacent(t, t')`：时间相邻关系；`campus(r)`/`campus_of_teacher[k, t]`

## Objective（加权软约束）

- 最小化：`Z = Σ_i w_i * c_i`
- 软约束度量 `c_i` 定义见 “Hard/Soft Constraints” 与 “Scoring and Fairness”

## Heuristics

- Warm‑start: graph coloring, largest degree first, saturation degree ordering
- Local search/Tabu for improvements; deterministic seeds

## Orchestration

- Jobs: draft → running → feasible → optimized → published
- Checkpoints, pause/resume, cancellation
- Progress events via Redis/WebSocket

## Two‑stage parameters（建议）

- Feasibility 阶段：
  - 时间预算：`feasibility_max_ms`（默认 60–180s，视规模）
  - 停止条件：找到可行解或时间用尽
  - 随机种子：`seed`（可复现）
- Optimization 阶段：
  - 时间预算：`optimization_max_ms` 或无改进停机 `no_improve_ms`
  - 停止条件：达到目标上界、无改进、外部取消
  - 初始解：来自可行解/热启动（warm start）

## Local search（邻域与禁忌）

- 邻域操作：单点移动（move）、两两交换（swap）、链式交换、连堂拆分/合并
- 禁忌策略：短期禁忌表，记录最近修改的 `(s, t, r, k)` 组合，长度 `tabu_len`（规模自适应）
- 接受准则：最优贪心 + 温和模拟退火（少量劣解接受以跳出局部最优）

## Reproducibility

- 固定随机种子；记录求解版本、参数、权重与输入快照；输出包含 `seed` 与 commit hash（若可用）
