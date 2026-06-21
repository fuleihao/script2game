import re
from pathlib import Path
from typing import Dict, Any
from backend.llm_client import LLMClient
from backend.script_parser import compile_script

DEBUG_DIR = Path("data/compiled")
DEBUG_DIR.mkdir(parents=True, exist_ok=True)


class Document2ScriptError(Exception):
    pass


def save_debug_file(name: str, content: str) -> str:
    path = DEBUG_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content or "", encoding="utf-8")
    return str(path)


def clean_model_output(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.I).strip()
    text = re.sub(r"^```text\s*", "", text, flags=re.I).strip()
    text = re.sub(r"^```markdown\s*", "", text, flags=re.I).strip()
    text = re.sub(r"^```\s*", "", text).strip()
    text = re.sub(r"\s*```$", "", text).strip()
    return text


def extract_fixed_script(text: str) -> str:
    text = clean_model_output(text)
    start = text.find("【剧本标题】")
    if start == -1:
        save_debug_file("bad_fixed_script_raw.txt", text)
        raise Document2ScriptError("模型没有输出【剧本标题】开头的固定格式剧本。")
    return text[start:].strip()


def build_document2script_prompt(raw_text: str, role_count: int = 3) -> str:
    raw_text = (raw_text or "").strip()
    if len(raw_text) > 9000:
        raw_text = raw_text[:9000]
    return f"""
你是一个剧本杀编剧系统。

请把【原始非结构化文本】改写成一个可以被程序解析的固定格式剧本杀文本。

重要要求：
1. 必须尽量保留原文中的人物、事件、地点、物品、时间线和因果关系。
2. 不要凭空编造与原文无关的关键事实。
3. 可以为了剧本杀玩法补充角色目标、隐藏信息和误导线索，但必须与原文逻辑一致。
4. 生成 {role_count} 个主要角色。
5. 每个角色必须有：公开信息、私密信息、目标、不能主动透露的信息。
6. 必须生成三幕线索，每幕 2 到 4 条。
7. 最终真相必须明确说明：关键人物、关键行为、动机、证据链、误导角色为什么不是最终关键人物。
8. 评分标准总分必须为 100 分。
9. 不要输出 JSON，不要输出解释，不要输出 markdown。
10. 必须严格按照下面固定格式输出。

固定格式如下：

【剧本标题】
这里写剧本标题

【故事背景】
这里写故事背景

【角色列表】
角色1
角色2
角色3

【角色：角色1】
公开信息：
这里写公开信息
私密信息：
这里写私密信息
目标：
这里写角色目标
不能主动透露的信息：
这里写该角色不能主动透露的信息

【第一幕线索】
1. 线索1
2. 线索2

【第二幕线索】
1. 线索1
2. 线索2

【第三幕线索】
1. 线索1
2. 线索2

【最终真相】
这里写完整最终真相

【评分标准】
指出真正关键人物：40分
说明关键动机：20分
解释误导人物或排除错误嫌疑：20分
引用关键证据支撑推理：20分

【原始非结构化文本】
{raw_text}
""".strip()


def build_repair_prompt(bad_output: str, error_message: str) -> str:
    bad_output = (bad_output or "").strip()
    if len(bad_output) > 9000:
        bad_output = bad_output[:9000]
    return f"""
你刚才输出的剧本格式不符合程序要求。
请把下面内容修复成严格固定格式剧本。

要求：
1. 必须以【剧本标题】开头。
2. 必须包含【故事背景】、【角色列表】、【第一幕线索】、【第二幕线索】、【第三幕线索】、【最终真相】、【评分标准】。
3. 每个角色必须使用【角色：角色名】格式。
4. 每个角色必须包含公开信息、私密信息、目标、不能主动透露的信息。
5. 三幕线索都不能为空。
6. 不要输出解释，不要输出 JSON，不要输出 markdown。

格式错误原因：
{error_message}

需要修复的内容：
{bad_output}
""".strip()


def validate_fixed_script(fixed_text: str) -> None:
    required = ["【剧本标题】", "【故事背景】", "【角色列表】", "【第一幕线索】", "【第二幕线索】", "【第三幕线索】", "【最终真相】", "【评分标准】"]
    missing = [s for s in required if s not in fixed_text]
    if missing:
        raise Document2ScriptError("缺少必要章节：{}".format("、".join(missing)))
    role_blocks = re.findall(r"【角色：(.+?)】", fixed_text)
    if len(role_blocks) < 3:
        raise Document2ScriptError("角色数量不足，至少需要 3 个角色。")
    for stage in ["第一幕线索", "第二幕线索", "第三幕线索"]:
        m = re.search(r"【{}】([\s\S]*?)(?=\n【|$)".format(stage), fixed_text)
        content = m.group(1).strip() if m else ""
        numbered = re.findall(r"^\s*\d+[.、]\s*", content, flags=re.M)
        if len(numbered) < 2:
            raise Document2ScriptError("{} 线索不足，至少需要 2 条。".format(stage))


def document_to_script(raw_text: str, llm: LLMClient, role_count: int = 3, allow_llm_repair: bool = True) -> Dict[str, Any]:
    raw_text = (raw_text or "").strip()
    if not raw_text:
        raise Document2ScriptError("输入文本为空。")

    output = llm.generate(build_document2script_prompt(raw_text, role_count=role_count))
    if not output:
        raise Document2ScriptError("大模型没有返回结果，请检查接口是否启动。")
    save_debug_file("document2script_raw_output.txt", output)

    try:
        fixed_text = extract_fixed_script(output)
        validate_fixed_script(fixed_text)
        repair_output = ""
    except Exception as e:
        if not allow_llm_repair:
            raise
        repair_output = llm.generate(build_repair_prompt(output, str(e)))
        if not repair_output:
            raise Document2ScriptError("首次生成格式错误，并且大模型修复没有返回结果。")
        save_debug_file("document2script_repair_output.txt", repair_output)
        fixed_text = extract_fixed_script(repair_output)
        validate_fixed_script(fixed_text)

    save_debug_file("document2script_fixed_text.txt", fixed_text)
    return {"json": compile_script(fixed_text), "fixed_text": fixed_text, "raw_output": output, "repair_output": repair_output}


def save_generated_script(fixed_text: str, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(fixed_text, encoding="utf-8")
    return str(path)
