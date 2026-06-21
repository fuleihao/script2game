SPOILER_WORDS = ["真相", "凶手", "答案", "谁干的", "谁做的", "最终", "幕后", "直接告诉我", "是不是你", "谁替换", "谁修改"]


def is_spoiler_question(question):
    q = question or ""
    return any(w in q for w in SPOILER_WORDS)


def check_spoiler(question, room):
    stage_idx = room.get("current_stage_index", 0)
    if is_spoiler_question(question) and stage_idx < 5:
        return "这个问题可能涉及最终真相。当前阶段还不能直接确认。你可以继续追问行动时间线、动机或已经解锁的证据。"
    return ""
