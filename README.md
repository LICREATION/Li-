# Quant Portfolio · 量化研究作品集

> **一个量化金融学习过程的公开账本** —— 记录我从 2026 年 9 月起，为考研与研究生阶段研究做准备的全部工作。

**作者**：郑州大学 金融科技本科（2024 级） · 东吴大学财务工程与精算数学系交换（2026.09–2027.01）
**目标**：厦门大学 王亚南经济研究院（WISE）/ 邹至庄经济研究院，金融硕士 · 量化金融 / AI 金融方向

---

## 一、现在能跑什么（先看这个）

理念说得再好，也要能被检验。以下是仓库里**当前真实可运行**的东西：

```bash
git clone https://github.com/<你的用户名>/quant-portfolio.git
cd quant-portfolio
pip install -r requirements.txt

# 主线项目：A股机器学习资产定价（当前为 6 只 ETF 演示模式）
python 05_ml_asset_pricing/04_A股机器学习资产定价_复现骨架.py
```

| 模块 | 状态 | 能跑出什么 |
|---|---|---|
| `05_ml_asset_pricing/` | ✅ 骨架可运行 | 月频面板 → 12 个横截面特征 → 滚动窗口训练 → 样本外 R² → 多空十分位收益 |
| `03_backtest/` | 🔧 迁移中 | 存量 36 组回测（6 策略 × 6 ETF），桌面代码整理中 |
| `01_data/` ·`02_factor/` ·`04_pricing/` | 📋 规划中 | 仅有设计文档 |

> 状态说明：**✅ 可运行 / 🔧 迁移中 / 📋 规划中**。我不把规划中的东西写成已完成。

---

## 二、目录结构

```text
quant-portfolio/
├── README.md                 项目总览
├── 学习日志.md                每周记录：做了什么 / 卡在哪 / 下一步（最新在最前）
├── resources.md              精选资源清单（数据源 / 课程 / 工具 / 论文入口）
├── requirements.txt          依赖清单
│
├── notes/                    论文精读笔记卡（目标：一年 10 篇）
│   ├── README.md             阅读进度与命名规范
│   └── 论文精读笔记卡_模板.md
│
├── 01_data/                  数据管道：akshare → SQLite 增量更新
├── 02_factor/                因子构造：时变 Beta、横截面公司特征
├── 03_backtest/              回测引擎：多策略对比 + 真实成本（佣金/滑点/T+1）
├── 04_pricing/               期权定价：GBM + 蒙特卡洛
└── 05_ml_asset_pricing/      主线：复现 Gu, Kelly & Xiu (2020) 于 A 股
```

主线研究问题：**机器学习能否在 A 股横截面上预测个股下月收益？样本外表现如何？哪些特征在起作用？**

---

## 三、已有的基础工作（正在迁移进仓库）

- **郑州二手房价格预测模型**：单变量 → 多变量线性回归，R² = 0.85
- **36 组策略批量回测**：6 个策略 × 6 个 ETF 板块，含夏普比率与最大回撤对比
- **历史回放模拟盘**：数据库日线逐 bar 回放 + 模拟撮合（佣金万三 + 滑点 + T+1）
- **交易决策可视化**：47 次买入 / 32 次卖出 / 10 次止盈 / 3 次止损的完整记录与复盘

---

## 四、环境与复现

```
Python 3.13  ·  Windows 11
核心依赖见 requirements.txt
可选：VeighNa 4.4（模拟盘部分，不影响其余模块）
```

所有脚本默认**不写绝对路径、不含任何密钥**。数据通过 akshare 实时拉取，不入库分发。

---

## 五、为什么是公开的（以及为什么长这样）

我选择公开，是因为我认为**可被检验**比**看起来厉害**更重要。

具体做法：

- **早期提交里的笨拙写法我刻意保留** —— 那正是我真实的学习轨迹
- **跑不出好结果也照实记录** —— 能说清「样本外 R² 是 X，比原文低一个数量级，我怀疑原因是 Y」，比一个漂亮但说不清的数字有价值
- **不隐瞒不会的东西** —— 不会 Git、学术阅读量接近零、数学基础不足，这些都写在 `学习日志.md` 里

这个仓库的目标不是构建一个完美的作品集，而是记录一个真实、可验证的学习过程。

> The goal is not to build a perfect portfolio, but to document a genuine and verifiable learning process.

---

## About This Repository (English)

I am an undergraduate in Financial Technology at Zhengzhou University, currently on exchange at Soochow University (Taiwan). I am preparing for the Master of Finance program at Xiamen University (WISE / Chow Institute), with a focus on quantitative finance and AI in finance.

This repository evolves alongside my learning journey. As I study academic papers and explore new topics, I document my reflections, summarize key findings and methodologies, and organize the code and resources related to my work. Relevant papers and references are linked in `resources.md`. I also keep track of the challenges I encounter, the mistakes I make, and the improvements I achieve along the way — see `学习日志.md`.

**My main project** is a replication of Gu, Kelly & Xiu (2020), *Empirical Asset Pricing via Machine Learning* (RFS), on Chinese A-share data: monthly panel → cross-sectional characteristics → rolling-window training → out-of-sample R² → long-short decile portfolios → feature importance.

If you are working on something similar, feel free to reach out.

---

最后更新：2026-09-19
