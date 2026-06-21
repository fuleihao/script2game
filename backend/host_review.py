from backend.agents import format_recent_history


def _join_evidence(room):
    evs = room.get("unlocked_evidence", [])

    if not evs:
        return "暂无已解锁线索。"

    return "\n".join(["- " + str(x) for x in evs])


def _format_final_answers(room, player_answer=""):
    final_answers = dict(room.get("final_answers", {}))

    player_role = room.get("player_role", "真人玩家")

    if player_answer:
        final_answers[player_role] = player_answer

    if not final_answers:
        return "暂无角色提交最终推理。"

    lines = []

    for role, answer in final_answers.items():
        lines.append("【{} 的最终推理】".format(role))
        lines.append(str(answer))
        lines.append("")

    return "\n".join(lines)


def host_final_review(llm, script, room, player_answer):
    """
    主持人最终复盘：
    对真人玩家和 AI 角色的最终推理一起评分。
    """
    player_answer = str(player_answer or "").strip()

    if not player_answer:
        return "你还没有提交最终推理。请先写出：关键人物是谁、动机是什么、证据链是什么。"

    history = format_recent_history(room, limit=50)
    evidence_text = _join_evidence(room)
    final_answers_text = _format_final_answers(room, player_answer)

    truth = script.get("truth", "")
    scoring = script.get("scoring", "")

    prompt_parts = [
        "你是剧本杀主持人，现在进入最终复盘。",
        "你可以查看最终真相、评分标准、全部已解锁线索、聊天记录，以及每位角色提交的最终推理。",
        "请对真人玩家和 AI 角色分别评分，并进行完整复盘。",
        "",
        "【剧本标题】",
        str(script.get("title", "未命名剧本")),
        "",
        "【最终真相】",
        str(truth),
        "",
        "【评分标准】",
        str(scoring),
        "",
        "【已解锁线索】",
        evidence_text,
        "",
        "【最近聊天记录】",
        history,
        "",
        "【所有角色最终推理】",
        final_answers_text,
        "",
        "【复盘要求】",
        "1. 对每个提交最终推理的角色分别给出 0-100 分。",
        "2. 真人玩家必须单独重点评价。",
        "3. 说明每个角色命中了哪些点、遗漏了哪些点。",
        "4. 说明正确证据链应该如何串联。",
        "5. 最后以主持人口吻揭示完整真相。",
        "6. 不要只给结论，要像剧本杀主持人复盘一样。",
        "",
        "【输出格式】",
        "【全员得分】",
        "- 角色名：分数，简短评价",
        "",
        "【真人玩家评价】",
        "",
        "【AI角色评价】",
        "",
        "【证据链复盘】",
        "",
        "【完整真相】",
        "",
        "请开始复盘："
    ]

    prompt = "\n".join(prompt_parts)

    out = llm.generate(prompt) if llm else None

    if out:
        return out

    return "\n".join([
        "【最终得分】",
        "无法调用大模型评分。",
        "",
        "【主持人提示】",
        "请检查模型连接，或在左侧填写正确 API Key。",
        "",
        "【所有角色最终推理】",
        final_answers_text
    ])
