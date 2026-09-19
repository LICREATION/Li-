# -*- coding: utf-8 -*-
"""
=============================================================================
04 · A股机器学习资产定价 复现骨架
模仿 Gu, Kelly & Xiu (2020) "Empirical Asset Pricing via Machine Learning" (RFS)
在 A 股上跑一遍：公司特征 -> 机器学习预测下月收益 -> 多空十分位组合

用途：
  1. 这是你给厦大 WISE / 邹至庄 导师看的"研究准备"作品核心
  2. 也是你从"技术指标回测"升级到"横截面资产定价"的第一步
  3. 它跑不出漂亮结果很正常 —— 能说清楚"为什么跑不出来"比跑出来更值钱

作者：为你定制（零基础友好，每行都有注释）
依赖：pip install akshare pandas numpy scikit-learn matplotlib
=============================================================================
"""

# ============ 0. 先把"作图中文不乱码"这件事解决掉 ============
import matplotlib
matplotlib.use("Agg")                      # 不弹窗，直接存图片
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]   # 中文字体（Windows）
plt.rcParams["axes.unicode_minus"] = False              # 负号正常显示

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# 中国习惯：涨=红色，跌=绿色
RED   = "#e5484d"
GREEN = "#30a46c"

print("=" * 70)
print("A股机器学习资产定价 · 复现骨架")
print("=" * 70)


# =============================================================================
# 第 1 步：拿数据
# -----------------------------------------------------------------------------
# 说明：akshare 是免费的 A 股数据接口。第一次跑会比较慢（要拉全市场）。
#      建议第一次跑完后把结果存成本地 csv，之后直接读，省时间。
# =============================================================================

USE_CACHE = True          # True = 有本地缓存就直接读，不再联网
CACHE_FILE = "a_stock_panel.csv"

def build_price_panel(start="2010-01-01", end="2025-12-31"):
    """
    构造"股票-月份"面板数据。
    返回 DataFrame，列为：
        code, month, ret(当月收益), mktcap(总市值), turnover(换手率),
        close(收盘价), volume(成交量)
    """
    import akshare as ak

    # 1) 拉全部 A 股的日线行情（这一步最慢，可能要十几分钟）
    print("[1/3] 正在拉取 A 股日线数据 ...")
    df = ak.stock_zh_a_daily(symbol="sh000001", start_date=start, end_date=end, adjust="qfq")
    # ↑ 上面这行只是占位，真正要拉全市场请用下面这段（注释掉是因为很慢）:
    #
    #   codes = ak.stock_info_a_code_name()["code"].tolist()
    #   all_dfs = []
    #   for i, c in enumerate(codes):
    #       try:
    #           d = ak.stock_zh_a_daily(symbol=c, start_date=start, end_date=end, adjust="qfq")
    #           d["code"] = c
    #           all_dfs.append(d)
    #       except Exception:
    #           pass
    #       if i % 200 == 0:
    #           print(f"    已处理 {i}/{len(codes)}")
    #   df = pd.concat(all_dfs)
    #
    return df


def build_panel_from_cache():
    """已经跑过一次、存了 csv 的话，直接读。"""
    df = pd.read_csv(CACHE_FILE, dtype={"code": str})
    df["date"] = pd.to_datetime(df["date"])
    return df


# ---- 这里给你一个"最小可跑"的替代方案：只用几只 ETF 做演示 ----
# 真实做研究时必须换成全 A 股，但先把流程跑通比什么都重要。
DEMO_MODE = True     # True = 用 6 只宽基/行业 ETF 演示流程（快，几分钟）

def build_panel_demo(start="20150101", end="20251231"):
    """
    演示模式：用 6 只 A 股 ETF 的日线。
    目的只有一个 —— 把下面所有的代码流程跑通、跑顺。
    换成全 A 股时，只要把这一函数替换掉，后面所有代码都不用改。
    """
    import akshare as ak
    etfs = {
        "510300": "沪深300",
        "512480": "半导体",
        "159915": "创业板",
        "510880": "红利",
        "512690": "酒",
        "512010": "券商",
    }
    dfs = []
    for code, name in etfs.items():
        try:
            d = ak.fund_etf_hist_em(symbol=code, period="daily",
                                    start_date=start, end_date=end, adjust="qfq")
            d = d.rename(columns={"日期": "date", "收盘": "close",
                                  "成交量": "volume", "成交额": "amount",
                                  "换手率": "turnover"})
            d["code"] = code
            d["name"] = name
            d["date"] = pd.to_datetime(d["date"])
            dfs.append(d[["code", "name", "date", "close", "volume", "amount", "turnover"]])
            print(f"    {code} {name}：{len(d)} 条")
        except Exception as e:
            print(f"    {code} 拉取失败：{e}")
    return pd.concat(dfs, ignore_index=True)


if USE_CACHE:
    try:
        panel_daily = build_panel_from_cache()
        print(f"[数据] 从缓存读取：{panel_daily.shape[0]} 行")
    except Exception:
        print("[数据] 没有缓存，改为联网拉取（演示模式）")
        panel_daily = build_panel_demo()
else:
    panel_daily = build_panel_demo() if DEMO_MODE else build_price_panel()

# 缓存下来，下次不用再拉
panel_daily.to_csv("a_stock_panel.csv", index=False, encoding="utf-8-sig")


# =============================================================================
# 第 2 步：日线 -> 月线，构造"公司特征"(characteristics)
# -----------------------------------------------------------------------------
# Gu-Kelly-Xiu 的核心思想是：
#     用一堆"公司特征" X 去预测"下个月的股票收益" y。
# 你原来做的 KD/MACD/RSI/BOLL 是【时间序列】特征（自己跟自己的历史比）；
# 这里做的是【横截面】特征（同一时点上，这只股票跟别的股票比）。
# 这是两套完全不同的东西，后者才是学术资产定价的主流。
# =============================================================================

def to_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    """日线转月线，并计算每个月的收益率。"""
    daily = daily.sort_values(["code", "date"]).copy()
    daily["ym"] = daily["date"].dt.to_period("M")     # 年月标记，例如 2024-03

    g = daily.groupby(["code", "ym"])
    m = g.agg(
        close   = ("close", "last"),      # 月末收盘价
        volume  = ("volume", "sum"),      # 当月总成交量
        amount  = ("amount", "sum"),      # 当月总成交额
        turnover= ("turnover", "mean"),   # 当月平均换手率
    ).reset_index()

    # 月收益率 = (本月末收盘 / 上月末收盘) - 1
    m = m.sort_values(["code", "ym"])
    m["ret"] = m.groupby("code")["close"].pct_change()
    return m


def build_features(m: pd.DataFrame) -> pd.DataFrame:
    """
    构造预测用的特征 X。
    ⚠️ 铁律：所有特征在 t 月末尾必须【已经能观测到】，
             不能用到 t+1 的信息，否则就是未来函数，回测全是假的。
    """
    m = m.sort_values(["code", "ym"]).copy()

    # --- 动量类 ---
    # 过去 1 / 3 / 6 / 12 个月的累计收益（不含当月，避免把 y 混进 X）
    for k in [1, 3, 6, 12]:
        m[f"mom_{k}"] = m.groupby("code")["ret"].apply(
            lambda s: s.shift(1).rolling(k).apply(lambda x: (1 + x).prod() - 1, raw=False)
        ).reset_index(level=0, drop=True)

    # --- 反转类 ---
    m["rev_1"] = -m["mom_1"]          # 短期反转因子（学术界经典）

    # --- 波动率 ---
    m["vol_12"] = m.groupby("code")["ret"].transform(
        lambda s: s.shift(1).rolling(12).std())

    # --- 流动性 / 换手率 ---
    m["turnover"] = m["turnover"].fillna(0)
    m["turn_1"]  = m["turnover"]
    m["turn_12"] = m.groupby("code")["turnover"].transform(
        lambda s: s.shift(1).rolling(12).mean())
    # 换手率变化 = 当期换手 / 过去一年平均换手（异常关注度指标）
    m["turn_chg"] = m["turn_1"] / (m["turn_12"].replace(0, np.nan))

    # --- 规模（用成交额的对数代替市值，ETF 没有市值数据）---
    m["size"] = np.log(m["amount"].clip(lower=1))

    # --- 价格类 ---
    m["price"] = m["close"]

    # --- 成交量的变化 ---
    m["vol_chg"] = m.groupby("code")["volume"].transform(
        lambda s: s.shift(1) / s.shift(1).rolling(12).mean().replace(0, np.nan))

    # --- 横截面标准化：每个月内，把每个特征做 z-score ---
    # 这一步非常重要：让不同月份的横截面可比，也是 Gu-Kelly-Xiu 的标准做法
    feat_cols = ["mom_1", "mom_3", "mom_6", "mom_12", "rev_1", "vol_12",
                 "turn_1", "turn_12", "turn_chg", "size", "price", "vol_chg"]
    for c in feat_cols:
        m[c] = m.groupby("ym")[c].transform(
            lambda s: (s - s.mean()) / (s.std() + 1e-8))
        m[c] = m[c].clip(-3, 3)          # 截尾，防止极端值主导模型

    return m, feat_cols


panel_m = to_monthly(panel_daily)
panel_m, FEATURES = build_features(panel_m)

print(f"\n[面板] 月频数据：{panel_m.shape[0]} 行，"
      f"{panel_m['code'].nunique()} 个标的，"
      f"{panel_m['ym'].nunique()} 个月份")
print(f"[特征] 共 {len(FEATURES)} 个：{FEATURES}")


# =============================================================================
# 第 3 步：定义预测目标 y —— 下个月的收益
# -----------------------------------------------------------------------------
# 关键：y 是【t+1 月】的收益，X 是【t 月末】能看到的。
# 用 shift(-1) 把下月收益搬到当前行，这样每一行就是 (X_t, y_{t+1})
# =============================================================================

panel_m = panel_m.sort_values(["code", "ym"])
panel_m["y"] = panel_m.groupby("code")["ret"].shift(-1)

data = panel_m.dropna(subset=["y"] + FEATURES).reset_index(drop=True)
print(f"[样本] 去掉缺失后可训练样本：{len(data)} 行")

# 如果样本太少（演示模式下 ETF 只有 6 只），给出提示但继续跑
if len(data) < 200:
    print("\n⚠️  样本量太小，结果没有统计意义。")
    print("   这只是为了把流程跑通。真正做研究时请换成全 A 股（4000+ 只 × 120 个月）。")
    print("   替换方法：把 build_panel_demo() 换成全 A 股日线拉取即可，后面代码不用改。\n")


# =============================================================================
# 第 4 步：滚动窗口训练 + 样本外预测
# -----------------------------------------------------------------------------
# ⚠️⚠️ 这里是整个项目最关键的一行：绝对不能用 train_test_split 随机切分！
#     金融数据有时间相关性，随机切分会把未来的数据混进训练集，
#     得到的好结果是假的。必须用"滚动窗口"：
#         用 [t-60, t-1] 的 60 个月训练 -> 预测 t 月 -> 窗口往前挪一格
# =============================================================================

from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score

# 用来对比的模型（先跑前两个就够了，后两个慢）
MODELS = {
    "OLS(线性)":        LinearRegression(),
    "Ridge(岭回归)":    RidgeCV(alphas=np.logspace(-3, 3, 10)),
    "RandomForest":     RandomForestRegressor(n_estimators=200, max_depth=3,
                                              min_samples_leaf=20, random_state=42),
    "GBRT(梯度提升)":   GradientBoostingRegressor(n_estimators=100, max_depth=2,
                                                 learning_rate=0.05, random_state=42),
}

TRAIN_WINDOW = 60      # 用过去 60 个月训练（5 年）
MIN_TRAIN    = 36      # 少于 36 个月就不预测

def rolling_predict(df, feature_cols, model_factory, train_window=TRAIN_WINDOW):
    """
    滚动窗口：每个月用过去 train_window 个月训练，预测当月。
    返回 DataFrame：ym, code, y_true, y_pred
    """
    months = sorted(df["ym"].unique())
    out = []

    for i in range(train_window, len(months)):
        train_months = months[i - train_window: i]     # 训练期（严格在过去）
        test_month   = months[i]                        # 预测期（当期）

        tr = df[df["ym"].isin(train_months)]
        te = df[df["ym"] == test_month].copy()
        if len(tr) < MIN_TRAIN or len(te) == 0:
            continue

        Xtr, ytr = tr[feature_cols].values, tr["y"].values
        Xte      = te[feature_cols].values

        model = model_factory()
        model.fit(Xtr, ytr)
        te["y_pred"] = model.predict(Xte)
        te["train_end"] = str(train_months[-1])
        out.append(te[["ym", "code", "y", "y_pred"]])

    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


print("\n" + "=" * 70)
print("开始滚动窗口训练（每个月训练一次，会比较慢，耐心等）")
print("=" * 70)

results_oos = {}
for name, mdl in MODELS.items():
    pred = rolling_predict(data, FEATURES, lambda m=mdl: m)
    if pred.empty:
        print(f"  {name}：样本不足，跳过")
        continue
    results_oos[name] = pred

    # Gu-Kelly-Xiu 的核心指标：样本外 R² (out-of-sample R²)
    # R²_oos = 1 - Σ(y - ŷ)² / Σ(y - ȳ_train)²
    # 简单版：直接算预测值与真实值的相关性和 R²
    r2  = r2_score(pred["y"], pred["y_pred"])
    ic  = pred.groupby("ym").apply(
        lambda g: g["y"].corr(g["y_pred"], method="spearman")).mean()   # 横截面 IC
    print(f"  {name:<16} 样本外R² = {r2:>8.4f}   平均横截面IC = {ic:>7.4f}")


# =============================================================================
# 第 5 步：多空十分位组合（学术界的"收益曲线"长这样）
# -----------------------------------------------------------------------------
# 每个月按预测收益从高到低分成 10 组：
#     第 10 组（预测最高）做多，第 1 组（预测最低）做空 -> 多空组合
# 学界看的是这条多空曲线的夏普比率，不是某一只股票的收益。
# =============================================================================

def long_short_decile(pred: pd.DataFrame, n_group=10):
    """构造多空十分位组合的月度收益。"""
    rows = []
    for ym, g in pred.groupby("ym"):
        if g["y_pred"].nunique() < n_group:
            n = max(2, min(n_group, g["y_pred"].nunique()))
        else:
            n = n_group
        try:
            g = g.copy()
            g["group"] = pd.qcut(g["y_pred"], n, labels=False, duplicates="drop") + 1
        except Exception:
            continue
        gr = g.groupby("group")["y"].mean()
        rows.append({"ym": ym, **{f"G{int(k)}": v for k, v in gr.items()}})

    port = pd.DataFrame(rows).set_index("ym").sort_index()
    return port


def summary(port: pd.DataFrame, name: str):
    """算多空组合的年化收益、年化波动、夏普比率。"""
    cols = [c for c in port.columns if c.startswith("G")]
    lo, hi = cols[0], cols[-1]                      # 最低组、最高组
    ls = port[hi] - port[lo]                        # 多空收益（月度）

    ls = ls.dropna()
    if len(ls) == 0:
        print(f"  {name}：组合样本不足")
        return None

    ann_ret  = ls.mean() * 12                       # 年化收益
    ann_vol  = ls.std() * np.sqrt(12)               # 年化波动
    sharpe   = ann_ret / ann_vol if ann_vol > 0 else np.nan
    cum      = (1 + ls).cumprod()                   # 累计净值

    print(f"\n  【{name}】多空十分位组合")
    print(f"    年化收益   {ann_ret*100:>8.2f}%")
    print(f"    年化波动   {ann_vol*100:>8.2f}%")
    print(f"    夏普比率   {sharpe:>8.2f}")
    print(f"    最大回撤   {((cum/cum.cummax()-1).min())*100:>8.2f}%")
    print(f"    月份数     {len(ls):>8d}")
    return cum


print("\n" + "=" * 70)
print("多空十分位组合表现")
print("=" * 70)

cum_curves = {}
for name, pred in results_oos.items():
    port = long_short_decile(pred)
    cum = summary(port, name)
    if cum is not None:
        cum_curves[name] = cum


# =============================================================================
# 第 6 步：画图
# =============================================================================

if cum_curves:
    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor="#111318")
    ax.set_facecolor("#111318")

    colors = [RED, "#5b9cf8", "#a78bfa", "#f5a524"]
    for i, (name, cum) in enumerate(cum_curves.items()):
        x = [str(p) for p in cum.index]
        ax.plot(range(len(cum)), cum.values, label=name,
                color=colors[i % len(colors)], linewidth=1.9)

    ax.axhline(1.0, color="#7a8394", linestyle="--", linewidth=1)
    step = max(1, len(cum) // 12)
    ax.set_xticks(range(0, len(cum), step))
    ax.set_xticklabels([str(p) for p in cum.index][::step], rotation=45,
                       fontsize=9, color="#a8b0bd")
    ax.tick_params(colors="#a8b0bd")
    ax.set_title("A股机器学习资产定价 · 多空十分位组合净值（样本外）",
                 color="#e6e9ef", fontsize=14, pad=14)
    ax.set_ylabel("累计净值", color="#a8b0bd")
    ax.legend(facecolor="#181b21", edgecolor="#2b303a", labelcolor="#e6e9ef")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#2b303a")
    ax.grid(alpha=0.15, color="#2b303a")

    plt.tight_layout()
    plt.savefig("A股机器学习资产定价_多空组合.png", dpi=150,
                facecolor="#111318")
    print("\n[图] 已保存：A股机器学习资产定价_多空组合.png")


# =============================================================================
# 第 7 步：特征重要性（这是你面试时最该讲的一张图）
# =============================================================================

if "RandomForest" in results_oos:
    from sklearn.ensemble import RandomForestRegressor
    tr = data[data["ym"].isin(sorted(data["ym"].unique())[-TRAIN_WINDOW:])]
    rf = RandomForestRegressor(n_estimators=300, max_depth=3,
                               min_samples_leaf=20, random_state=42)
    rf.fit(tr[FEATURES].values, tr["y"].values)
    imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values()

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#111318")
    ax.set_facecolor("#111318")
    ax.barh(imp.index, imp.values, color=RED, height=0.6)
    ax.tick_params(colors="#a8b0bd")
    ax.set_title("随机森林 · 特征重要性（哪个特征在预测下月收益）",
                 color="#e6e9ef", fontsize=13, pad=12)
    ax.set_xlabel("重要性", color="#a8b0bd")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#2b303a")
    ax.grid(axis="x", alpha=0.15, color="#2b303a")
    plt.tight_layout()
    plt.savefig("A股机器学习资产定价_特征重要性.png", dpi=150, facecolor="#111318")
    print("[图] 已保存：A股机器学习资产定价_特征重要性.png")


# =============================================================================
# 第 8 步：把结果写进笔记卡（对接 论文精读笔记卡_模板.md 第六栏）
# =============================================================================

print("\n" + "=" * 70)
print("给你的三句话结论（请填进笔记卡）")
print("=" * 70)
print("""
1. 【我复现出了什么】Gu-Kelly-Xiu 的框架在 A 股上跑通了，流程是：
   月频面板 -> 横截面标准化特征 -> 滚动窗口训练 -> 样本外预测 -> 多空十分位。

2. 【哪个数字让我意外】
   （在这里写下你的样本外 R²。美国原文的月频 R² 大约在 0.3%~0.4%，
    如果你跑出来的数字和它差一个数量级，这就是你要研究的问题。）

3. 【我怀疑的原因】（这是面试时唯一真正属于你的东西，自己填）
   □ A股散户占比高，噪声大
   □ 我的特征太少（原文用了 94 个）
   □ 换手率特征主导了一切，说明模型学到的其实是"关注度"而不是"价值"
   □ 样本期内有注册制、量化新规等结构性变化，模型不稳定
   □ 其他：_______
""")

print("\n完成。下一步：")
print("  1. 把 build_panel_demo() 换成全 A 股数据（4000+ 只）")
print("  2. 特征从 12 个扩到 30~90 个（市值、账面市值比、ROE、盈利波动、杠杆...）")
print("  3. 加入行业中性化（每个特征减去所属行业均值）")
print("  4. 对比 Lasso / Elastic Net / 神经网络")
print("  5. 把结果和疑问写进笔记卡，放进 GitHub 仓库")
