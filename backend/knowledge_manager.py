from backend.retriever import simple_search


def get_role(script, role_name):
    for r in script.get("roles", []):
        if r.get("name") == role_name:
            return r
    return {}


def _short_text(text, max_len=220):
    text = str(text or "").replace("\n", " ").strip()
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def recent_message_docs(room, limit=30):
    """
    把最近聊天记录也作为可检索资料。
    这样 AI 回答问题时，不只看剧本和线索，也会看前面谁说过什么。
    """
    docs = []
    messages = room.get("messages", [])[-limit:]

    for msg in messages:
        speaker = msg.get("speaker", "")
        target = msg.get("target", "")
        content = msg.get("content", "")
        time = msg.get("time", "")

        if not content:
            continue

        text = "{} {} 对 {} 说：{}".format(
            time,
            speaker or "未知角色",
            target or "全体",
            _short_text(content)
        )

        docs.append({
            "scope": "聊天记录",
            "text": text
        })

    return docs


def host_docs(script, room, include_truth=False):
    docs = [{"scope": "故事背景", "text": script.get("background", "")}]

    for r in script.get("roles", []):
        docs.append({
            "scope": "角色信息",
            "text": "角色{}：公开信息：{} 私密信息：{} 目标：{} 禁止主动透露：{}".format(
                r.get("name", ""),
                r.get("public_profile", ""),
                r.get("private_memory", ""),
                r.get("goal", ""),
                r.get("forbidden", "")
            )
        })

    for ev in room.get("unlocked_evidence", []):
        docs.append({
            "scope": "已解锁证据",
            "text": ev
        })

    docs.extend(recent_message_docs(room, limit=30))

    if include_truth:
        docs.append({
            "scope": "最终真相",
            "text": script.get("truth", "")
        })
        docs.append({
            "scope": "评分标准",
            "text": script.get("scoring", "")
        })

    return docs


def role_docs(script, room, role_name):
    r = get_role(script, role_name)

    docs = [
        {"scope": "故事背景", "text": script.get("background", "")},
        {"scope": "我的公开信息", "text": r.get("public_profile", "")},
        {"scope": "我的私密信息", "text": r.get("private_memory", "")},
        {"scope": "我的目标", "text": r.get("goal", "")},
        {"scope": "不能主动透露", "text": r.get("forbidden", "")},
    ]

    for ev in room.get("unlocked_evidence", []):
        docs.append({
            "scope": "已解锁证据",
            "text": ev
        })

    docs.extend(recent_message_docs(room, limit=30))

    return docs


def retrieve_context(query, docs, top_k=8):
    results = simple_search(query, docs, top_k=top_k)

    if not results:
        results = docs[:top_k]

    lines = []
    for x in results:
        text = x.get("text", "")
        if text:
            lines.append("- [{}] {}".format(x.get("scope", ""), text))

    return "\n".join(lines)
