# Scoring and Fairness

## Scoring model

- Weighted penalties per soft constraint
- School‑specific `WeightProfile`
- Pareto fronts for trade‑offs where appropriate

## Explainability

- Per‑assignment score breakdowns
- Aggregate fairness metrics by teacher/class

## Fairness

- Balance workload and time‑of‑day equity
- Configurable caps and distributions

## WeightProfile（示例草案）

```
{
  "min_idle_gap": 10,
  "limit_consecutive": 8,
  "late_day": 6,
  "early_day": 4,
  "teacher_time_pref": 5,
  "class_time_pref": 4,
  "spread_across_week": 3,
  "preferred_room": 2,
  "room_utilization": 1
}
```

- 权重单位：越大表示违规代价越高
- 归一化：将不同量纲的软约束转换为统一惩罚尺度（例如每次违规、每分钟空档、每节偏移）
- 可配置：为每个学校维护独立 `WeightProfile`，支持场景/版本化

## 评分聚合与对比

- 总分：Σ(软约束惩罚 × 权重)
- 维度化评分：教师维度、班级维度、时间段维度
- 方案对比：支持并行求解多方案，按 Pareto 支配与关键指标排序

## 公平性指标（草案）

- 教师课时分布方差/极差
- 早晚课占比差异（按教师/班级）
- 连堂/空档分布公平性（Gini/方差）
