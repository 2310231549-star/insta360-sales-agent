"""跨境电商智能多源销售数据看板 — Streamlit App."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_processor import (
    load_data, compute_kpi_summary, weekly_trend, channel_breakdown,
    region_breakdown, sku_performance, build_context_for_llm,
)
from src.ai_insights import generate_insights
from src.config import AMAZON_FILE, SHOPIFY_FILE

st.set_page_config(page_title="Insta360 跨境电商销售看板", page_icon="��", layout="wide")

# ── Sidebar ──
with st.sidebar:
    st.image("https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/insta360.svg", width=80)
    st.title("智能销售看板")
    st.caption("Powered by Python + LLM")

    st.divider()
    st.markdown("### 📥 数据源")
    st.caption(f"Amazon: `{AMAZON_FILE}`")
    st.caption(f"Shopify: `{SHOPIFY_FILE}`")

    regenerate = st.button("🔄 重新生成模拟数据", use_container_width=True)
    if regenerate:
        with st.spinner("生成中..."):
            os.system(f"cd data && python generate_data.py")
        st.rerun()

    st.divider()
    st.markdown("### ⚙️ 关于")
    st.caption(
        "本 Demo 展示 AI Agent 如何自动化跨境电商运营分析：\n"
        "多源数据合并 → 指标计算 → AI 洞察 → 可视化看板\n"
        "全流程 10 秒内完成，替代传统 3 小时人工分析。"
    )

# ── Main ──
st.title("🌐 跨境电商多源销售数据智能看板")
st.caption("Amazon + Shopify 双渠道 | 实时 KPI | AI 智能洞察 | 自动预警")

# Check data
if not os.path.exists(AMAZON_FILE) or not os.path.exists(SHOPIFY_FILE):
    st.warning("⚠️ 未找到数据文件，正在自动生成模拟数据...")
    os.system(f"cd data && python generate_data.py")
    st.rerun()

# Load & process
df = load_data()
kpi = compute_kpi_summary(df)
trend = weekly_trend(df)
channel = channel_breakdown(df)
region = region_breakdown(df)
sku_df = sku_performance(df)

# ═══ KPI Row ═══
st.divider()
st.subheader("📈 核心经营指标")

cols = st.columns(6)
metrics = [
    ("总收入", f"${kpi['total_revenue']:,.0f}", None),
    ("订单数", f"{kpi['total_orders']:,}", None),
    ("销量", f"{kpi['total_units']:,} 件", None),
    ("客单价", f"${kpi['avg_order_value']:.0f}", None),
    ("利润率", f"{kpi['profit_margin']}%", f"{kpi['wow_growth_pct']:+.1f}% WoW"),
    ("库存周转率", f"{kpi['inventory_turnover']}", None),
]

for col, (label, value, delta) in zip(cols, metrics):
    with col:
        st.metric(label=label, value=value, delta=delta)

# ═══ Charts Row 1 ═══
st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📅 周度销售趋势")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=trend["week"].astype(str), y=trend["revenue"],
                         name="收入", marker_color="#3B82F6", yaxis="y1"))
    fig.add_trace(go.Scatter(x=trend["week"].astype(str), y=trend["profit"],
                             name="利润", mode="lines+markers", line=dict(color="#10B981", width=3),
                             yaxis="y2"))
    fig.update_layout(
        legend=dict(orientation="h", y=1.12),
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
        yaxis=dict(title="收入 ($)", side="left"),
        yaxis2=dict(title="利润 ($)", overlaying="y", side="right"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📦 渠道对比")
    fig = go.Figure(data=[
        go.Pie(labels=channel.index, values=channel["revenue"], hole=0.5,
               marker_colors=["#FF9900", "#96BF48"], textinfo="label+percent")
    ])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

# ═══ Charts Row 2 ═══
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🌍 区域分布")
    region_plot = region.reset_index()
    fig = px.bar(region_plot, x="region", y="revenue", color="channel", barmode="group",
                 color_discrete_map={"Amazon": "#FF9900", "Shopify": "#96BF48"})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350,
                      xaxis_title="", yaxis_title="收入 ($)")
    st.plotly_chart(fig, use_container_width=True)

with col_right2:
    st.subheader("🏷️ SKU 排行榜")
    fig = px.bar(sku_df.reset_index().head(8), x="revenue", y="sku", orientation="h",
                 color="sku", text_auto=".2s")
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350,
                      showlegend=False, xaxis_title="收入 ($)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# ═══ AI Insights ═══
st.divider()
st.subheader("🤖 AI 智能洞察报告")
st.caption("LLM 自动分析数据 → 生成爆款/滞销分析 → 输出运营建议")

if st.button("🚀 生成 AI 分析报告", type="primary", use_container_width=True):
    with st.spinner("AI Agent 正在分析多渠道数据..."):
        context = build_context_for_llm(kpi, sku_df, trend, channel, region)
        report = generate_insights(context)
        st.markdown(report)
else:
    st.info("👆 点击上方按钮，让 AI Agent 自动分析本周销售数据并生成运营建议")

# ── Footer ──
st.divider()
st.caption(
    "Built for Insta360 跨境电商运营岗位 Demo | "
    "技术栈: Python · Pandas · Streamlit · Plotly · LLM (Agnes AI) | "
    "作者: 张睿"
)
