"""Multi-channel sales data pipeline — merge, clean, compute KPIs."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.config import AMAZON_FILE, SHOPIFY_FILE


def load_data() -> pd.DataFrame:
    amazon = pd.read_csv(AMAZON_FILE, parse_dates=["date"])
    shopify = pd.read_csv(SHOPIFY_FILE, parse_dates=["date"])
    amazon["channel"] = "Amazon"
    shopify["channel"] = "Shopify"
    df = pd.concat([amazon, shopify], ignore_index=True)
    df["gross_profit"] = df["revenue"] - df["cost"] - df["shipping_cost"] - df["platform_fee"] - df["ad_spend"]
    df["profit_margin"] = df["gross_profit"] / df["revenue"]
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    return df


def compute_kpi_summary(df: pd.DataFrame) -> dict:
    now = df["date"].max()
    current_week = df[df["week"] == df["week"].max()]
    prev_week = df[df["week"] == df["week"].max() - 1]

    def _gp(df_chunk):
        return df_chunk["gross_profit"].sum()

    cur_gp = _gp(current_week)
    prv_gp = _gp(prev_week)
    gp_wow = (cur_gp - prv_gp) / prv_gp * 100 if prv_gp else 0

    # Inventory turnover (simplified: revenue / avg_cost → higher = faster sell)
    avg_inventory_cost = df["cost"].sum() / df["date"].nunique() * 7  # rough avg weekly
    turnover = df["revenue"].sum() / max(avg_inventory_cost, 1)

    return {
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_orders": df["order_id"].nunique(),
        "total_units": int(df["units_sold"].sum()),
        "avg_order_value": round(df["revenue"].sum() / max(df["order_id"].nunique(), 1), 2),
        "gross_profit": round(cur_gp, 2),
        "profit_margin": round(df["gross_profit"].sum() / df["revenue"].sum() * 100, 2),
        "wow_growth_pct": round(gp_wow, 1),
        "inventory_turnover": round(turnover, 2),
        "best_sku": str(current_week.groupby("sku")["revenue"].sum().idxmax()),
        "worst_sku": str(current_week.groupby("sku")["revenue"].sum().idxmin()),
        "data_period": f"{df['date'].min().date()} ~ {df['date'].max().date()}",
    }


def weekly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("week").agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        profit=("gross_profit", "sum"),
        margin=("profit_margin", "mean"),
    ).round(2).reset_index()


def channel_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("channel").agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        avg_order=("revenue", lambda x: round(x.sum() / max(x.count(), 1), 2)),
        margin=("profit_margin", "mean"),
    ).round(2)


def region_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["channel", "region"]).agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        units=("units_sold", "sum"),
    ).round(2)


def sku_performance(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["sku", "category"]).agg(
        revenue=("revenue", "sum"),
        units=("units_sold", "sum"),
        profit=("gross_profit", "sum"),
        margin=("profit_margin", "mean"),
    ).sort_values("revenue", ascending=False).round(2)


def build_context_for_llm(kpi: dict, sku_df: pd.DataFrame, trend_df: pd.DataFrame,
                          channel_df: pd.DataFrame, region_df: pd.DataFrame) -> str:
    top3 = sku_df.head(3)
    bot3 = sku_df.tail(3)

    return f"""## 跨境电商多渠道销售数据摘要

### 核心KPI
- 总收入: ${kpi['total_revenue']:,.2f}
- 总订单: {kpi['total_orders']}
- 总销量: {kpi['total_units']} 件
- 客单价: ${kpi['avg_order_value']:.2f}
- 毛利润: ${kpi['gross_profit']:,.2f}
- 利润率: {kpi['profit_margin']}%
- 环比增长: {kpi['wow_growth_pct']}%
- 库存周转率: {kpi['inventory_turnover']}
- 数据周期: {kpi['data_period']}

### 本周表现
- 本周爆款: {kpi['best_sku']}
- 本周滞销: {kpi['worst_sku']}

### TOP3 畅销品
{top3.to_string()}

### BOTTOM3 滞销品
{bot3.to_string()}

### 渠道对比
{channel_df.to_string()}

### 区域分布
{region_df.to_string()}
"""
