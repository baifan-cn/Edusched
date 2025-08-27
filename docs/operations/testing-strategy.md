# Testing Strategy

## Levels

- Unit tests (backend/frontend)
- Integration tests (API, DB)
- E2E (Playwright)
- Algorithm regression suite with seed datasets
- Load and performance tests

## Policies

- Deterministic seeds for solver
- Test data fixtures per domain

## 算法回归与基线（草案）

- 基线数据集：small（<50 节/周）、medium（50–200）、large（200+）
- 指标：可行率、求解时间（p50/p95/p99）、评分（越低越好）
- 固定随机种子与超时阈值，保证可重复性
- 回归流水线：遇到评分回退时输出差异报告与热图

## 负载与性能

- API：并发读写与速率限制验证
- Worker：多作业并行与队列深度；CPU 亲和与内存占用监控
