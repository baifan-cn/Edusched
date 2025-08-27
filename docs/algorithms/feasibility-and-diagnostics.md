# Feasibility and Diagnostics

## Feasibility

- Minimal unsat cores and explanations for violated constraints
- Relaxation strategies for near‑feasible cases

### 最小不可满足核心（MUS）输出示例（草案）

```
{
  "status": "infeasible",
  "unsat_core": [
    {"type": "teacher_conflict", "teacher_id": "t-1", "timeslot_id": "ts-0900-mon"},
    {"type": "room_feature_mismatch", "room_id": "r-302", "feature": "lab:chem"}
  ],
  "explanations": [
    "Teacher t-1 assigned to two sections at 09:00 Monday",
    "Room r-302 lacks required feature lab:chem"
  ]
}
```

## Diagnostics

- Constraint heatmaps; conflict graphs
- What‑if simulations; scenario comparisons
- Deterministic runs with seed control for reproducibility

### 诊断视图（草案）

- 冲突热力图：按时间/资源维度聚合冲突密度
- 约束命中榜：列出高频触发的硬/软约束
- What-if：在副本上调整权重/可用性并评估影响
