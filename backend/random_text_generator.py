import re


def clean_random_text(text: str) -> str:
    text = text or ""
    text = text.strip()

    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.I).strip()
    text = re.sub(r"^```text\s*", "", text, flags=re.I).strip()
    text = re.sub(r"^```markdown\s*", "", text, flags=re.I).strip()
    text = re.sub(r"^```\s*", "", text).strip()
    text = re.sub(r"\s*```$", "", text).strip()

    return text


def build_random_case_prompt(
    theme="校园",
    role_count=3,
    difficulty="普通",
    style="证据链推理",
    extra_requirements=""
):
    return f"""
README.md app.py backend data requirements.>

README.md app.py backend data requirements.txt 


"{theme}
"{role_count}
"{difficulty}
#
"{style}
"{extra_requirements or "无"}


1. 不要输出固定格式剧本。
2. 不要输出 JSON。
3. 不要写“角色列表、第一幕线索、最终真相”等标题。
4. 只输出一段完整的案件故事文本。
5. 文本中必须自然包含人物、地点、时间线、关键物品、矛盾、动机、误导信息和关键证据。
6. 必须有一个真正的关键人物，但不要直接用“凶手是xxx”这种方式提前揭晓。
7. 每个主要人物都要有可疑点或隐瞒内容。
8. 至少包含 3 个时间点，例如 21:40、22:10、22:25。
9. 至少包含 3 条可用于推理的证据，例如门禁、聊天记录、监控、文件记录、物品痕迹等。
10. 故事应该能被改写成 {role_count} 人剧本杀。
11. 字数控制在 900 到 1400 字之间。
12. 语言要自然，像一段案件材料，不要像提纲。


""".strip()


def generate_random_case_text(
    llm,
    theme="校园",
    role_count=3,
    difficulty="普通",
    style="证据链推理",
    extra_requirements=""
):
    if not llm:
        raise RuntimeError("随机生成案件文本需要先连接大模型。")

    prompt = build_random_case_prompt(
        theme=theme,
        role_count=role_count,
        difficulty=difficulty,
        style=style,
        extra_requirements=extra_requirements
    )

    text = llm.generate(prompt)

    if not text:
        raise RuntimeError("大模型没有返回内容，请检查模型接口或 API Key。")

    text = clean_random_text(text)

    if len(text) < 200:
        raise RuntimeError("随机案件文本太短，生成质量不合格，请重新生成。")

    return text
