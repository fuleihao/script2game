from backend.game_state import add_message
from backend.knowledge_manager import host_docs, role_docs, retrieve_context, get_role
from backend.spoiler_controller import check_spoiler


def format_recent_history(room, limit=18):
    messages = room.get("messages", [])[-limit:]

    if not messages:
        return "暂无聊天记录。"

    lines = []

    for idx, msg in enumerate(messages, start=1):
        time = msg.get("time", "")
        speaker = msg.get("speaker", "")
        target = msg.get("target", "")
        content = str(msg.get("content", "") or "").replace("\n", " ").strip()

        if not content:
            continue

        if len(content) > 220:
            content = content[:220] + "..."

        lines.append(
            "{}. {} {} 对 {} 说：{}".format(
                idx,
                time,
                speaker or "未知角色",
                target or "全体",
                content
            )
        )

    return "\n".join(lines) if lines else "暂无聊天记录。"


def latest_human_message(room):
    messages = room.get("messages", [])

    for msg in reversed(messages):
        if msg.get("role_type") == "human":
            return msg

    return None


def is_simple_greeting(text):
    text = str(text or "").strip()

    greetings = [
        "你好",
        "你们好",
        "大家好",
        "我是",
        "我来了",
        "开始吧",
        "hello",
        "hi"
    ]

    if len(text) <= 30 and any(x in text.lower() for x in greetings):
        return True

    return False


class HostAgent:
    def __init__(self, script, room, llm=None):
        self.script = script
        self.room = room
        self.llm = llm

    def opening(self):
        roles = "、".join([
            r.get("name", "")
            for r in self.script.get("roles", [])
            if r.get("name", "")
        ])

        return "欢迎来到《{}》。本局角色包括：{}。每个角色掌握的信息并不相同，请根据证据链提交推理。".format(
            self.script.get("title", "未命名剧本"),
            roles
        )

    def stage_intro(self):
        stage = self.room.get("current_stage", "")

        if "线索" in stage:
            evs = self.room.get("unlocked_evidence", [])[-4:]
            ev_text = "\n".join(["- " + str(x) for x in evs])
            return "现在进入【{}】。新的线索已经公开：\n{}".format(stage, ev_text)

        if stage == "最终推理":
            return "现在进入最终推理阶段。请提交你的判断：关键人物是谁、动机是什么、证据链是什么。"

        return "现在进入【{}】。".format(stage)

    def answer(self, question):
        block = check_spoiler(question, self.room)

        if block:
            return block

        history = format_recent_history(self.room, limit=20)

        ctx = retrieve_context(
            question + "\n" + history,
            host_docs(self.script, self.room, include_truth=False),
            top_k=10
        )

        prompt_parts = [
            "你是剧本杀主持人。",
            "请根据当前已公开信息和聊天历史回答玩家问题，不要提前透露最终真相。",
            "",
            "【当前阶段】",
            str(self.room.get("current_stage", "")),
            "",
            "【最近聊天历史】",
            history,
            "",
            "【检索到的相关资料】",
            ctx,
            "",
            "【玩家最新问题】",
            str(question),
            "",
            "【回答要求】",
            "1. 必须先看聊天历史，再回答。",
            "2. 如果玩家只是打招呼，你就自然回应并引导继续讨论，不要突然讲案件细节。",
            "3. 如果玩家追问前面某个人说过的话，要承接前文。",
            "4. 如果聊天历史里已经出现过某个说法，不要装作不知道。",
            "5. 只能基于已公开信息、已解锁线索和聊天历史回答。",
            "6. 不要提前透露最终真相。",
            "7. 语气像主持人，简洁控场。",
            "",
            "请回答："
        ]

        prompt = "\n".join(prompt_parts)

        out = self.llm.generate(prompt) if self.llm else None

        if out:
            return out

        return "主持人提示：大家已经到齐，可以先从各自昨晚的行动开始说明。"


class RoleAgent:
    def __init__(self, script, room, role_name, llm=None):
        self.script = script
        self.room = room
        self.role_name = role_name
        self.llm = llm

    def intro(self):
        r = get_role(self.script, self.role_name)

        return "我是{}。{}".format(
            self.role_name,
            r.get("public_profile", "我会根据自己知道的信息参与讨论。")
        )

    def react_to_player(self, player_message):
        r = get_role(self.script, self.role_name)
        history = format_recent_history(self.room, limit=22)
        player_message = str(player_message or "").strip()

        if is_simple_greeting(player_message):
            prompt_parts = [
                "你正在剧本杀中扮演【{}】。".format(self.role_name),
                "现在玩家刚刚公开打招呼，你要自然回应。",
                "",
                "【你的角色公开信息】",
                str(r.get("public_profile", "")),
                "",
                "【你的目标】",
                str(r.get("goal", "")),
                "",
                "【最近聊天历史】",
                history,
                "",
                "【玩家刚才说】",
                player_message,
                "",
                "【回应要求】",
                "1. 只做自然回应，不要突然讲案件细节。",
                "2. 不要重复完整自我介绍。",
                "3. 不要说自己是 AI。",
                "4. 语气像真实玩家。",
                "5. 控制在 1-2 句话。",
                "",
                "请回应："
            ]

            prompt = "\n".join(prompt_parts)
            out = self.llm.generate(prompt) if self.llm else None

            if out:
                return out

            return "{}：你好，先看看大家都怎么说吧。".format(self.role_name)

        query = "玩家公开发言：{}\n角色：{}\n聊天历史：{}".format(
            player_message,
            self.role_name,
            history
        )

        ctx = retrieve_context(
            query,
            role_docs(self.script, self.room, self.role_name),
            top_k=8
        )

        prompt_parts = [
            "你正在剧本杀中扮演【{}】。".format(self.role_name),
            "你要回应玩家刚刚的公开发言。",
            "你不是全知上帝，只能根据自己的角色信息、已解锁线索和聊天历史回应。",
            "不要说自己是 AI。不要提前透露最终真相。",
            "",
            "【当前阶段】",
            str(self.room.get("current_stage", "")),
            "",
            "【你的角色公开信息】",
            str(r.get("public_profile", "")),
            "",
            "【你的私密信息】",
            str(r.get("private_memory", "")),
            "",
            "【你的目标】",
            str(r.get("goal", "")),
            "",
            "【不能主动透露的信息】",
            str(r.get("forbidden", "")),
            "",
            "【最近聊天历史】",
            history,
            "",
            "【检索到的相关资料】",
            ctx,
            "",
            "【玩家刚才说】",
            player_message,
            "",
            "【回应要求】",
            "1. 必须回应玩家刚才这句话，不要自顾自推进案件。",
            "2. 如果玩家只是聊天，就自然聊天。",
            "3. 如果玩家质疑你，你可以辩解、回避或反问。",
            "4. 如果玩家质疑别人，你可以附和、怀疑或转移话题。",
            "5. 不要重复自我介绍。",
            "6. 不要提前透露最终真相。",
            "7. 控制在 1-3 句话。",
            "",
            "请回应："
        ]

        prompt = "\n".join(prompt_parts)

        out = self.llm.generate(prompt) if self.llm else None

        if out:
            return out

        return "{}：我先听听大家怎么说。".format(self.role_name)

    def stage_speak(self):
        r = get_role(self.script, self.role_name)
        history = format_recent_history(self.room, limit=20)

        query = "当前阶段主动发言\n角色：{}\n聊天历史：{}".format(
            self.role_name,
            history
        )

        ctx = retrieve_context(
            query,
            role_docs(self.script, self.room, self.role_name),
            top_k=10
        )

        prompt_parts = [
            "你正在剧本杀中扮演【{}】。".format(self.role_name),
            "你只能根据自己的角色信息、已解锁线索和最近聊天历史发言。",
            "你不是全知上帝，不能自爆，不能提前透露最终真相。",
            "",
            "【当前阶段】",
            str(self.room.get("current_stage", "")),
            "",
            "【你的角色公开信息】",
            str(r.get("public_profile", "")),
            "",
            "【你的私密信息】",
            str(r.get("private_memory", "")),
            "",
            "【你的目标】",
            str(r.get("goal", "")),
            "",
            "【不能主动透露的信息】",
            str(r.get("forbidden", "")),
            "",
            "【最近聊天历史】",
            history,
            "",
            "【检索到的相关资料】",
            ctx,
            "",
            "【发言要求】",
            "1. 这是阶段主动发言，不是回应打招呼。",
            "2. 必须参考最近聊天历史，不要像第一次发言。",
            "3. 如果有人刚刚质疑你、提到你、或者提到与你有关的线索，你要回应。",
            "4. 不要重复自我介绍。",
            "5. 不要说自己是 AI。",
            "6. 发言要像真实玩家，1-3句话。",
            "7. 可以辩解、反问、转移怀疑，但不能违反你的角色设定。",
            "",
            "请用第一人称主动发言："
        ]

        prompt = "\n".join(prompt_parts)

        out = self.llm.generate(prompt) if self.llm else None

        if out:
            return out

        return "{}：我现在只能根据已公开线索判断，事情还需要继续问清楚。".format(self.role_name)

    def answer(self, question):
        block = check_spoiler(question, self.room)

        if block:
            return "{}：{}".format(self.role_name, block)

        r = get_role(self.script, self.role_name)
        history = format_recent_history(self.room, limit=22)

        query = "玩家问题：{}\n角色：{}\n聊天历史：{}".format(
            question,
            self.role_name,
            history
        )

        ctx = retrieve_context(
            query,
            role_docs(self.script, self.room, self.role_name),
            top_k=10
        )

        prompt_parts = [
            "你正在剧本杀中扮演【{}】。".format(self.role_name),
            "你不是全知上帝，只能根据自己的角色信息、已解锁线索和聊天历史回答。",
            "不要说自己是 AI。不要提前透露最终真相。",
            "",
            "【当前阶段】",
            str(self.room.get("current_stage", "")),
            "",
            "【你的角色公开信息】",
            str(r.get("public_profile", "")),
            "",
            "【你的私密信息】",
            str(r.get("private_memory", "")),
            "",
            "【你的目标】",
            str(r.get("goal", "")),
            "",
            "【不能主动透露的信息】",
            str(r.get("forbidden", "")),
            "",
            "【最近聊天历史】",
            history,
            "",
            "【检索到的相关资料】",
            ctx,
            "",
            "【玩家最新问题】",
            str(question),
            "",
            "【回答要求】",
            "1. 必须先看最近聊天历史，再回答最新问题。",
            "2. 如果玩家的问题承接前文，你要承接前文回答。",
            "3. 如果你前面已经说过某句话，现在被追问，要解释、补充或辩解，不能当作没发生过。",
            "4. 如果其他角色前面说法与你矛盾，可以反驳、回避、辩解或提出反问。",
            "5. 回答必须符合你的角色身份、目标和已知信息。",
            "6. 不要提前透露最终真相。",
            "7. 用第一人称，像真实玩家一样说话。",
            "8. 回答控制在 1-4 句话。",
            "",
            "请回答："
        ]

        prompt = "\n".join(prompt_parts)

        out = self.llm.generate(prompt) if self.llm else None

        if out:
            return out

        return "{}：我能确认的信息是：{}".format(self.role_name, ctx)


def ai_all_intro(script, room, llm=None):
    for p in room.get("players", []):
        if p.get("type") == "ai":
            add_message(
                room,
                p["role"],
                "全体",
                RoleAgent(script, room, p["role"], llm).intro(),
                "ai"
            )


def ai_stage_speak(script, room, llm=None):
    for p in room.get("players", []):
        if p.get("type") == "ai":
            add_message(
                room,
                p["role"],
                "全体",
                RoleAgent(script, room, p["role"], llm).stage_speak(),
                "ai"
            )


def ai_react_to_latest_user(script, room, llm=None, max_roles=2):
    latest = latest_human_message(room)

    if not latest:
        ai_stage_speak(script, room, llm)
        return

    player_message = latest.get("content", "")

    count = 0

    for p in room.get("players", []):
        if p.get("type") == "ai":
            add_message(
                room,
                p["role"],
                "全体",
                RoleAgent(script, room, p["role"], llm).react_to_player(player_message),
                "ai"
            )

            count += 1

            if count >= max_roles:
                break


def ai_submit_final_answers(script, room, llm=None):
    """
    最终推理阶段：所有 AI 角色提交自己的最终答案。
    注意：AI 只能根据自己可见的信息、已解锁线索和聊天历史推理，不能直接读取最终真相。
    """
    if room.get("ai_final_answers_done", False):
        return

    room.setdefault("final_answers", {})

    history = format_recent_history(room, limit=40)

    for p in room.get("players", []):
        if p.get("type") != "ai":
            continue

        role_name = p.get("role", "")
        r = get_role(script, role_name)

        query = "最终推理\n角色：{}\n聊天历史：{}".format(
            role_name,
            history
        )

        ctx = retrieve_context(
            query,
            role_docs(script, room, role_name),
            top_k=12
        )

        prompt_parts = [
            "你正在剧本杀中扮演【{}】。".format(role_name),
            "现在已经进入最终推理阶段，你需要给出自己的最终判断。",
            "你不能读取最终真相，只能根据自己的角色信息、已解锁线索和聊天历史进行推理。",
            "不要说自己是 AI。",
            "",
            "【你的角色公开信息】",
            str(r.get("public_profile", "")),
            "",
            "【你的私密信息】",
            str(r.get("private_memory", "")),
            "",
            "【你的目标】",
            str(r.get("goal", "")),
            "",
            "【最近聊天历史】",
            history,
            "",
            "【你可见的相关资料】",
            ctx,
            "",
            "【最终答案要求】",
            "请你像真实玩家一样提交最终推理，必须包含：",
            "1. 你认为的关键人物是谁。",
            "2. 你认为的动机是什么。",
            "3. 你依据的证据链是什么。",
            "4. 你如何排除其他可疑人物。",
            "5. 如果你不确定，也要给出最可能的判断。",
            "",
            "请用第一人称提交最终推理："
        ]

        prompt = "\n".join(prompt_parts)

        answer = llm.generate(prompt) if llm else None

        if not answer:
            answer = "{}：我认为还需要更多证据，但我会根据目前线索给出判断。".format(role_name)

        room["final_answers"][role_name] = answer

        add_message(
            room,
            role_name,
            "主持人",
            "【最终推理】\n" + answer,
            "ai"
        )

    room["ai_final_answers_done"] = True
