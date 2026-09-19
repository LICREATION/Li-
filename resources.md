# resources.md · 精选资源清单

> 原则：**只放我用过或正在用的**。链接坟场没有价值，能用上的三五个才有用。
> 每加一条，写一句「我用它做什么」。

---

## 数据源

| 资源 | 用途 | 备注 |
|---|---|---|
| [akshare](https://github.com/akfamily/akshare) | A股行情、财务、宏观数据 | 主线项目全部数据来源，免费 |
| [Tushare Pro](https://tushare.pro/) | 备用，财务数据质量更高 | 需要积分，学生可申请 |
| [CSMAR / Wind](https://www.gtarsc.com/) | 学术论文级数据 | 研究生阶段再说，本科拿不到 |
| [WRDS](https://wrds-www.wharton.upenn.edu/) | 美股与 CRSP/Compustat | Gu-Kelly-Xiu 原文数据，机构订阅 |

## 关键论文（主线相关）

| 论文 | 为什么重要 |
|---|---|
| Gu, Kelly & Xiu (2020), *Empirical Asset Pricing via Machine Learning*, RFS | 主线复现对象，ML 资产定价奠基之作 |
| 姜富伟等《基于自编码机器学习的资产定价研究》，管理科学学报 | A股对标版本 |
| 姜富伟等《投资者预期协同的资产定价研究》，管理世界 2025(12) | 目标导师最新中文成果 |
| Kelly, Pruitt & Su (2019), *Characteristics are Covariances*, JFE | IPCA，特征与因子结构的桥梁 |
| Cochrane, *Asset Pricing*（教材） | 资产定价的地基 |

> 完整精读清单与进度见 `notes/README.md`。

## 工具与项目（照着 README 跑，比刷课有用）

| 项目 | 学什么 |
|---|---|
| [akshare](https://github.com/akfamily/akshare) | 中文金融数据 API 的组织方式 |
| [qlib](https://github.com/microsoft/qlib) | 微软量化平台，工业级流水线长什么样 |
| [backtesting.py](https://github.com/kernc/backtesting.py) | 轻量回测框架，代码可读性极佳 |
| [VeighNa](https://github.com/vnpy/vnpy) | 实盘/模拟盘框架，我的模拟盘基于它 |

## 课程

| 课程 | 来源 | 对应模块 |
|---|---|---|
| 金融大数据（东吴大学 · 栗嘉良） | TronClass | `01_data` / `03_backtest` |
| 金融计量（东吴大学） | TronClass | `02_factor`（时变 Beta） |
| 财务风险管理（东吴大学 · Hull 教材） | TronClass | `04_pricing` |
| Machine Learning（Andrew Ng, Coursera） | 已学 | 全部 |

## 方法论备忘（踩过的坑）

- **金融数据绝不能用 `train_test_split` 随机切分** —— 未来函数泄漏。必须用 `TimeSeriesSplit` 或滚动窗口。
- **`cross_val_score` 默认 KFold 同样泄漏** —— 必须显式传入时序切分器。
- 回测必须含佣金、滑点、涨跌停与 T+1，否则收益全是假的。
- 样本外 R² 在资产定价里是个位数百分比量级，0.5% 就已经很强，不要拿房价预测的 R²=0.85 当参照。

---

最后更新：2026-09-19
