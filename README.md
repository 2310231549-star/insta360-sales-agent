# 🌐 跨境电商智能多源销售数据看板 Agent

> **一句话价值主张**：用 Python + 大模型打造的全自动销售数据分析 Agent，把运营 3 小时的人工分析 + 写周报流程，缩短到 **10 秒全自动生成**，附带库存预警与运营建议。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎬 Demo 视频

▶️ **[点击观看 Demo 视频](demo_output.mp4)** (21 秒，右键下载)

> 标题卡 → KPI 看板 → 图表滚动 → AI 报告生成 → 运营建议输出

---

## 🎯 痛点场景

跨境电商运营每天面对 Amazon、Shopify 等多个渠道的分散数据：
- ❌ 手动合并 Excel → 耗时 2-3 小时，易出错
- ❌ 缺乏实时库存预警 → 爆款断货不知，滞销品积压无感
- ❌ 周报靠人写 → 主观性强，没有数据驱动的洞察
- ❌ 业务决策滞后 → CEO 问"本周最该补货什么"，运营只能苦笑

**本 Demo 用 AI Agent 一键解决以上所有问题。**

---

## 🚀 核心功能

| 模块 | 说明 |
|---|---|
| 📥 **多源数据合并** | 自动合并 Amazon + Shopify 双渠道订单数据 |
| 📊 **核心 KPI 看板** | 总收入、订单数、客单价、利润率、库存周转率、环比增长 |
| 📈 **趋势可视化** | 周度销售趋势、渠道/区域分布、SKU 排行榜 |
| 🤖 **AI 智能洞察** | LLM 自动生成爆款分析 + 滞销预警 + 运营策略建议 |
| 🔄 **一键刷新** | 新数据进来，10 秒全流程自动化输出 |

---

## 🖥️ Demo 预览

```
streamlit run app.py
```

打开后你将看到：
1. **顶部**：6 个核心 KPI 指标卡片（收入、订单、利润率、环比等）
2. **中部**：4 张交互式图表（周度趋势 / 渠道占比 / 区域分布 / SKU 排行）
3. **底部**：AI Agent 自动生成的分析报告（爆款/滞销/建议）

---

## 🛠️ 技术架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Amazon CSV  │───▶│  Pandas ETL   │───▶│  Streamlit   │
│  Shopify CSV │    │  合并/清洗/指标  │    │  可视化看板   │
└─────────────┘    └──────┬───────┘    └──────┬──────┘
                          │                    │
                          ▼                    ▼
                   ┌──────────────┐    ┌─────────────┐
                   │  Data Context │───▶│   LLM Agent  │
                   │  结构化数据摘要  │    │  Agnes AI    │
                   └──────────────┘    │  生成分析报告  │
                                       └─────────────┘
```

| 层级 | 技术选型 | 选型理由 |
|---|---|---|
| 数据处理 | **Pandas + NumPy** | 高性能 DataFrame 操作，支持复杂聚合 |
| 可视化 | **Streamlit + Plotly** | 纯 Python 写前端，交互式图表 |
| AI 引擎 | **Agnes AI (OpenAI 兼容)** | 低成本 LLM，可替换为任何兼容 API |
| 数据模拟 | **NumPy random** | 真实分布采样，模拟多渠道订单 |

---

## 📦 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动 AI 代理（可选，但推荐）
```bash
# 启动 Agnes AI Proxy（或其他 OpenAI-compatible API）
python agnes_proxy.py
```

> AI 模块可替换为任何 OpenAI 兼容 API，修改 `src/config.py` 即可。

### 3. 启动看板
```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501` 即可看到看板。

---

## 📂 项目结构

```
insta360-sales-agent/
├── data/
│   ├── generate_data.py    # 模拟多渠道销售数据生成
│   ├── amazon_sales.csv    # Amazon 渠道数据（自动生成）
│   └── shopify_sales.csv   # Shopify 渠道数据（自动生成）
├── src/
│   ├── config.py           # LLM 配置 + 数据路径
│   ├── data_processor.py   # 数据合并、清洗、KPI 计算
│   └── ai_insights.py      # LLM 调用 + 分析报告生成
├── app.py                  # Streamlit 主看板
├── requirements.txt
└── README.md
```

---

## 🧠 AI Prompt 设计思路

本项目的核心灵魂是 **System Prompt**（见 `src/ai_insights.py`），它定义了 AI Agent 作为"跨境电商数据分析专家"的角色：

1. **角色设定**：全球化消费电子品牌的数据分析师
2. **输出约束**：4 个固定板块（概览、爆款、滞销、建议）
3. **风格要求**：简洁有力、建议具体可执行、金额用美元
4. **降级方案**：LLM 不可用时自动切换规则引擎，保证可用性

这就是 JD 中要求的"沉淀运营 SOP 和 AI Prompt"的具体实践。

---

## 🎤 面试陈述建议

> "我做了一个跨境电商智能销售看板 Agent。它能自动合并 Amazon 和 Shopify 的多源数据，计算核心 KPI，然后用大模型自动生成分析报告。
>
> 传统运营每周至少花 3 小时做数据整理和写周报，这个 Agent 把这个流程自动化到 10 秒以内，而且分析质量更稳定、更数据驱动。
>
> 技术栈是 Python + Pandas + Streamlit + LLM，代码已经开源在 GitHub 上，你可以直接跑起来看效果。"

---

## 📝 License

MIT © 张睿 (Zhang Rui)

---

*Built for 影石 Insta360 跨境电商运营实习岗位 Demo*
