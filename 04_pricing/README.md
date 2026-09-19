# 04_pricing · 期权定价

**这一层要解决的问题：从随机过程到无套利定价。**

这是我目前数理含金量最高、也最弱的一块。

## 对应的课程

东吴《財務風險管理》用的是 Hull《Options, Futures, and Other Derivatives》11e，
第 14 章 Wiener Processes and Itô's Lemma —— 这是 Hull 全书最难的一章，也是量化金融的门槛。

## 目标

- [ ] 几何布朗运动（GBM）模拟股价路径
- [ ] 蒙特卡洛欧式期权定价，与 Black-Scholes 解析解对比
- [ ] 希腊字母（Delta / Gamma / Vega / Theta）的数值计算
- [ ] 隐含波动率曲面（进阶）
- [ ] 用 A 股 50ETF 期权实盘数据校准（进阶）

## 为什么这块重要

厦大 WISE 是学术导向项目，「随机过程 + 无套利定价」是量化金融的看家本领。
这一块做出来，是作品集里**数理含金量最高**的一项。
