import re
from typing import Dict, Any, List


def get_section(text: str, title: str) -> str:
    pattern = r"【{}】([\s\S]*?)(?=\n【|$)".format(re.escape(title))
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""


def split_numbered_lines(text: str) -> List[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d+[.、]\s*", "", line)
        lines.append(line)
    return lines


def parse_role_block(role_name: str, block: str) -> Dict[str, Any]:
    def field(name: str) -> str:
        pattern = r"{}：([\s\S]*?)(?=\n\S+：|$)".format(re.escape(name))
        m = re.search(pattern, block)
        return m.group(1).strip() if m else ""
    return {
        "name": role_name,
        "public_profile": field("公开信息"),
        "private_memory": field("私密信息"),
        "goal": field("目标"),
        "forbidden": field("不能主动透露的信息")
    }


def compile_script(text: str) -> Dict[str, Any]:
    title = get_section(text, "剧本标题") or "未命名剧本"
    background = get_section(text, "故事背景")
    role_names = [x.strip() for x in get_section(text, "角色列表").splitlines() if x.strip()]
    roles = []
    for name in role_names:
        pattern = r"【角色：{}】([\s\S]*?)(?=\n【角色：|\n【第一幕线索】|\n【第二幕线索】|\n【第三幕线索】|\n【最终真相】|$)".format(re.escape(name))
        m = re.search(pattern, text)
        roles.append(parse_role_block(name, m.group(1).strip() if m else ""))

    stages = []
    for stage_name in ["第一幕线索", "第二幕线索", "第三幕线索"]:
        content = get_section(text, stage_name)
        if content:
            stages.append({"name": stage_name, "evidence": split_numbered_lines(content)})

    return {
        "title": title,
        "background": background,
        "roles": roles,
        "stages": stages,
        "truth": get_section(text, "最终真相"),
        "scoring": get_section(text, "评分标准"),
        "raw_text": text
    }
