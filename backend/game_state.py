import uuid
from datetime import datetime

STAGES = ["准备阶段", "开场介绍", "第一幕线索", "第二幕线索", "第三幕线索", "最终推理", "复盘结算"]


def now_time():
    return datetime.now().strftime("%H:%M:%S")


def create_room(script, player_role, ai_enabled=True):
    roles = [r["name"] for r in script.get("roles", [])]
    players = []
    for role in roles:
        players.append({
            "role": role,
            "type": "human" if role == player_role else ("ai" if ai_enabled else "empty"),
            "status": "真人玩家" if role == player_role else ("AI补位" if ai_enabled else "空位")
        })
    return {
        "room_id": str(uuid.uuid4())[:8],
        "script_title": script.get("title", "未命名剧本"),
        "current_stage_index": 0,
        "current_stage": STAGES[0],
        "player_role": player_role,
        "players": players,
        "messages": [],
        "unlocked_evidence": [],
        "submitted_answers": {},
        "created_at": now_time()
    }


def add_message(room, speaker, target, content, role_type="system"):
    room.setdefault("messages", []).append({
        "speaker": speaker,
        "target": target,
        "content": content,
        "role_type": role_type,
        "time": now_time()
    })


def unlock_stage(room, script, stage_index):
    stage_index = max(0, min(stage_index, len(STAGES) - 1))
    room["current_stage_index"] = stage_index
    room["current_stage"] = STAGES[stage_index]
    if stage_index in [2, 3, 4]:
        ev_idx = stage_index - 2
        stages = script.get("stages", [])
        if 0 <= ev_idx < len(stages):
            for ev in stages[ev_idx].get("evidence", []):
                if ev not in room["unlocked_evidence"]:
                    room["unlocked_evidence"].append(ev)


def next_stage(room, script):
    unlock_stage(room, script, room.get("current_stage_index", 0) + 1)
