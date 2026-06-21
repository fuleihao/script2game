import re


def build_timeline(script, room):
    texts = list(room.get("unlocked_evidence", []))
    for msg in room.get("messages", []):
        if msg.get("content"):
            texts.append(msg["content"])
    items = []
    for text in texts:
        for t in re.findall(r"\d{1,2}[:：]\d{2}", text):
            items.append(f"{t}：{text}")
    out, seen = [], set()
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out[:20]


def build_claims(room):
    claims = []
    for msg in room.get("messages", []):
        speaker = msg.get("speaker", "")
        content = msg.get("content", "")
        if not speaker or not content or speaker in ["玩家", "主持人"]:
            continue
        claims.append({"角色": speaker, "说法": content[:160] + ("..." if len(content) > 160 else "")})
    return claims[-30:]


def build_relation_edges(script, room):
    roles = [r.get("name", "") for r in script.get("roles", []) if r.get("name")]
    raw_text = script.get("raw_text", "") or ""
    edges = []
    for i, a in enumerate(roles):
        for b in roles[i + 1:]:
            if a in raw_text and b in raw_text:
                edges.append({"头实体": a, "关系": "相关", "尾实体": b, "来源": "剧本文本"})
    for ev in room.get("unlocked_evidence", []):
        for role in roles:
            if role in ev:
                edges.append({"头实体": role, "关系": "关联线索", "尾实体": ev[:50] + ("..." if len(ev) > 50 else ""), "来源": "已解锁证据"})
    for msg in room.get("messages", []):
        speaker = msg.get("speaker", "")
        content = msg.get("content", "")
        if speaker in roles and content:
            edges.append({"头实体": speaker, "关系": "发表说法", "尾实体": content[:50] + ("..." if len(content) > 50 else ""), "来源": "聊天记录"})
    out, seen = [], set()
    for e in edges:
        key = (e["头实体"], e["关系"], e["尾实体"])
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out[:50]
