"""AI-powered sales insights via LLM (OpenAI-compatible API)."""
import json
import requests

from src.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_MAX_TOKENS


SYSTEM_PROMPT = """你是一个跨境电商数据分析专家，服务于一家全球化消费电子品牌（类似 Insta360 / DJI）。
你的任务是：根据提供的销售数据摘要，用中文生成一份简洁、专业的"本周销售分析报告"。

报告必须包含以下四个板块：
1. **📊 核心数据概览**：用 2-3 句话总结本周整体表现（收入、利润、环比）
2. **🔥 爆款分析**：指出 TOP3 畅销品及原因推测
3. **⚠️ 滞销预警**：指出 BOTTOM3 滞销品，给出具体的促销/清仓建议
4. **🎯 运营建议**：给出 2-3 条具体可执行的运营策略（如补货、广告调整、区域重点）

注意：
- 语言简洁有力，每条建议不超过 2 句话
- 数据金额用美元 $ 表示
- 建议要具体可执行，不要泛泛而谈"""


def generate_insights(context: str) -> str:
    """Send data context to LLM, return markdown report."""
    url = f"{LLM_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": LLM_MODEL,
        "max_tokens": LLM_MAX_TOKENS,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"请根据以下数据生成分析报告：\n\n{context}"},
        ],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return _fallback_insights(context)
    except Exception as e:
        return f"⚠️ AI 分析暂不可用 ({e})\n\n---\n\n请确保 Agnes AI Proxy 已启动：`python agnes_proxy.py`"


def _fallback_insights(context: str) -> str:
    """Rule-based fallback when LLM is unreachable."""
    lines = context.split("\n")
    revenue = next((l for l in lines if "总收入" in l), "")
    wow = next((l for l in lines if "环比" in l), "")
    best = next((l for l in lines if "本周爆款" in l), "")
    worst = next((l for l in lines if "本周滞销" in l), "")

    return f"""## 📊 AI 分析报告（离线规则模式）

### 📊 核心数据概览
{revenue.strip()}，{wow.strip()}。整体销售表现符合预期，建议关注库存周转效率。

### 🔥 爆款分析
{best.strip()} 为本周期表现最佳单品，建议优先补货并加大广告投放。

### ⚠️ 滞销预警
{worst.strip()} 销售低迷，建议考虑捆绑销售或限时折扣清仓。

### 🎯 运营建议
1. 针对爆款产品增加广告预算 15-20%，抢占搜索排名
2. 滞销品启动"满减捆绑"促销，搭配热销配件销售
3. 关注美国站库存深度，避免断货影响排名

> ⚠️ 离线模式 — 启动 Agnes AI Proxy 可获取更精准的 AI 分析
"""
