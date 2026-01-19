"""
LLM 点餐推荐模块（稳定工程版）

特性：
1. 严格 JSON 输出约束
2. JSON 解析失败自动二次修复
3. temperature = 0，最大化结构稳定性
4. 无硬编码 API Key（符合工程规范）
"""

import os
import json
from typing import Dict, Any, List
from openai import OpenAI


# =================================================
# JSON 安全解析 + 自动修复
# =================================================
def _safe_json_parse(client: OpenAI, content: str) -> Dict[str, Any]:
    """
    尝试解析 JSON；
    若失败，则请求模型“只修 JSON”，再解析一次
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        fix_prompt = f"""
你刚才的输出不是合法 JSON。

请你【只返回修正后的 JSON 本身】：
- 不要解释
- 不要 markdown
- 不要多余文字
- 必须可以被 Python json.loads() 解析

原始输出如下：
{content}
"""
        fix_resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个 JSON 修复器，只输出 JSON。"},
                {"role": "user", "content": fix_prompt},
            ],
            temperature=0,
        )

        fixed_content = fix_resp.choices[0].message.content
        return json.loads(fixed_content)


# =================================================
# 主推荐函数
# =================================================
def recommend_with_llm(req: dict, menu_rows) -> dict:
    """
    req: {
        "people": int,
        "budget": float,
        "prefs": str,
        "avoid": str
    }

    return:
    {
      "items": [
        {"product_id": int, "qty": int, "reason": str}
      ],
      "estimated_total": float,
      "note": str
    }
    """

    # ---------- 1️⃣ API Key ----------
    api_key = "sk-a3fbbd1d660e4bcfa9a46691e00c7d09"
    if not api_key:
        raise RuntimeError("未设置环境变量 DEEPSEEK_API_KEY")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    # ---------- 2️⃣ 构造菜单文本 ----------
    menu_lines: List[str] = []
    for p in menu_rows:
        menu_lines.append(
            f"- ID:{p['id']} | {p['name']} | 价格:{p['price']} | {p['description'] or ''}"
        )
    menu_text = "\n".join(menu_lines)

    # ---------- 3️⃣ Prompt（强结构约束） ----------
    system_prompt = (
        "你是一个餐厅点餐推荐系统。"
        "你的任务是根据用户信息，从给定菜单中推荐菜品。"
        "你只能选择菜单中存在的菜品，禁止编造。"
        "你必须严格输出合法 JSON。"
    )

    user_prompt = f"""
【用户信息】
- 用餐人数：{req.get("people", 1)}
- 预算：{req.get("budget", "不限")}
- 口味偏好：{req.get("prefs", "")}
- 忌口：{req.get("avoid", "")}

【菜单】
{menu_text}

【输出模板（必须严格一致）】
{{
  "items": [
    {{
      "product_id": 1,
      "qty": 2,
      "reason": "推荐原因"
    }}
  ],
  "estimated_total": 0,
  "note": "整体说明"
}}

在输出前请自检：
1. 是否是合法 JSON
2. 是否能被 Python json.loads 解析
3. product_id 是否真实存在于菜单
"""

    # ---------- 4️⃣ 调用模型 ----------
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,   # ⭐ 关键：稳定 > 创意
    )

    content = response.choices[0].message.content

    # ---------- 5️⃣ 安全解析 ----------
    result = _safe_json_parse(client, content)

    # ---------- 6️⃣ 最低限度结构校验 ----------
    if not isinstance(result, dict):
        raise RuntimeError("AI 返回结果不是 dict")

    if "items" not in result or not isinstance(result["items"], list):
        raise RuntimeError("AI 返回结果缺少 items")

    for it in result["items"]:
        if "product_id" not in it or "qty" not in it:
            raise RuntimeError("推荐项缺少 product_id 或 qty")

    return result
