from backend.host_review import host_final_review
from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from backend.ui_components import inject_css, hero, stage_bar, role_card, chat_bubble, evidence_card, chat_panel, role_profile_card, clue_case_card
from backend.ui_components import claim_note_card, relation_edge_card
from backend.llm_client import LLMClient
from backend.document_loader import load_document_text
from backend.document2script import document_to_script, save_generated_script
from backend.random_text_generator import generate_random_case_text
from backend.script_parser import compile_script
from backend.game_state import create_room, add_message, next_stage, STAGES
from backend.agents import HostAgent, RoleAgent, ai_all_intro, ai_stage_speak, ai_submit_final_answers, ai_react_to_latest_user, ai_submit_final_answers
from backend.evidence_board import build_timeline, build_claims, build_relation_edges
from backend.judge import JudgeAgent


def _script2game_force_stage(room, target_index):
    """强制设置房间阶段，避免 AI 自我介绍后还停留在准备阶段。"""
    stage_names = [
        "准备阶段",
        "开场介绍",
        "第一幕线索",
        "第二幕线索",
        "第三幕线索",
        "最终推理",
        "复盘结算"
    ]

    target_index = max(0, min(int(target_index), len(stage_names) - 1))
    room["current_stage_index"] = target_index
    room["current_stage"] = stage_names[target_index]
    return room["current_stage"]


st.set_page_config(page_title="Script2Game V3", page_icon="🎭", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("## 🎮 游戏控制台")
    role_count = st.slider("生成角色数量", 3, 6, 3)
    ai_enabled = st.checkbox("允许 AI 补位", value=True)
    spoiler_strict = st.checkbox("严格剧透控制", value=True)
    ai_power = st.select_slider("AI 推理强度", options=["低", "中", "高"], value="中")

    st.divider()
    with st.expander("🤖 模型设置", expanded=True):
        provider = st.selectbox("Provider", ["openai", "ollama", "none"], index=0)
        model_name = st.text_input("模型名", value="Qwen3-8B")
        base_url = st.text_input("接口地址", value="http://127.0.0.1:8001/v1/chat/completions")

        api_key = st.text_input(
            "API Key",
            value="",
            type="password",
            placeholder="DeepSeek / OpenAI API Key，可留空使用服务器环境变量"
        )

        max_tokens = st.number_input("max_tokens", 512, 8192, 4096, step=512)
        temperature = st.slider("temperature", 0.0, 1.0, 0.2, step=0.05)
        if st.button("测试大模型连接"):
            llm = LLMClient(provider, model_name, base_url, max_tokens=max_tokens, temperature=temperature, api_key=api_key)
            res = llm.generate("请只回复：大模型连接成功。")
            if res:
                st.success("连接成功")
                st.write(res)
            else:
                st.error("连接失败，当前会走规则兜底。")



def end_current_game():
    """结束当前房间，但保留当前剧本，方便重新开局。"""
    for key in [
        "room",
        "host_final_review_text",
        "game_room_final_reasoning",
        "jump_to_game_room"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.game_ended_notice = True



_GAME_OVER_CONTROL_RENDER_COUNT = 0

def render_game_over_controls(position="top"):
    """本局结束后的顶部操作区。"""
    global _GAME_OVER_CONTROL_RENDER_COUNT
    _GAME_OVER_CONTROL_RENDER_COUNT += 1

    room = st.session_state.get("room", {})
    room_id = room.get("room_id", "no_room")
    key_suffix = f"{position}_{room_id}_{_GAME_OVER_CONTROL_RENDER_COUNT}"

    st.markdown("#### 🎬 本局已结束")
    st.success("主持人已经完成最终复盘，本局剧本杀已结束。")

    end_col1, end_col2 = st.columns(2)

    with end_col1:
        clicked_end = st.button(
            "结束本局，返回创建房间",
            type="primary",
            use_container_width=True,
            key=f"end_game_{key_suffix}"
        )

    with end_col2:
        clicked_restart = st.button(
            "保留剧本，重新开一局",
            use_container_width=True,
            key=f"restart_game_{key_suffix}"
        )

    if clicked_end or clicked_restart:
        # 清空当前房间，但保留当前 script 和 fixed_text
        for key in [
            "room",
            "host_final_review_text",
            "game_room_final_reasoning",
            "jump_to_game_room"
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.game_ended_notice = True
        st.session_state.jump_to_create_room = True
        st.rerun()


def get_llm():
    if provider == "none":
        return None
    return LLMClient(
        provider,
        model_name,
        base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        api_key=api_key
    )


def empty_script():
    return {
        "title": "尚未生成剧本",
        "background": "请在剧本大厅中上传文本、粘贴故事，或导入固定格式剧本。",
        "roles": [],
        "stages": [],
        "truth": "",
        "scoring": "",
        "raw_text": ""
    }, ""


if "script" not in st.session_state:
    st.session_state.script, st.session_state.fixed_text = empty_script()

script = st.session_state.script
hero()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎬 剧本大厅", "🚪 创建房间", "💬 游戏房间", "🧷 线索板", "🏆 复盘评分"])


if st.session_state.get("jump_to_create_room", False):
    components.html("""
    <script>
    setTimeout(function() {
        const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
        if (tabs && tabs.length >= 2) {
            tabs[1].click();
        }
    }, 150);
    </script>
    """, height=0)
    st.session_state.jump_to_create_room = False



if st.session_state.get("jump_to_game_room", False):
    components.html("""
    <script>
    setTimeout(function() {
        const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
        if (tabs && tabs.length >= 3) {
            tabs[2].click();
        }
    }, 120);
    </script>
    """, height=0)
    st.session_state.jump_to_game_room = False


with tab1:
    st.markdown("### 剧本生成 / 编译")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        mode = st.radio("输入类型", ["AI随机生成文本", "普通文本自动生成剧本杀", "固定格式剧本直接编译"], horizontal=True)
        uploaded = st.file_uploader("上传 TXT / DOCX / PDF", type=["txt", "docx", "pdf"])
        default_text = st.session_state.get(
            "random_case_text",
            "可以在这里粘贴普通案件文本，也可以选择“AI随机生成文本”后自动生成一段案件材料。"
        )

        if mode == "AI随机生成文本":
            st.markdown("#### 🎲 AI 随机案件生成")

            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                random_theme = st.selectbox(
                    "题材类型",
                    ["校园", "公司", "实验室", "民国", "古风", "科幻", "密室", "家庭", "医院", "艺术馆"],
                    index=0
                )
            with rc2:
                random_difficulty = st.selectbox(
                    "推理难度",
                    ["新手", "普通", "硬核"],
                    index=1
                )
            with rc3:
                random_style = st.selectbox(
                    "推理风格",
                    ["证据链推理", "角色博弈", "强反转", "轻推理", "时间线推理"],
                    index=0
                )

            random_extra = st.text_input(
                "额外要求",
                value="",
                placeholder="例如：发生在研究生实验室，和论文、项目、代码有关"
            )

            if st.button("🎲 生成随机案件文本", type="primary"):
                try:
                    llm = get_llm()
                    if not llm:
                        st.error("AI随机生成文本需要大模型，请先在左侧连接模型。")
                        st.stop()

                    with st.spinner("AI 正在生成随机案件文本..."):
                        generated_text = generate_random_case_text(
                            llm,
                            theme=random_theme,
                            role_count=role_count,
                            difficulty=random_difficulty,
                            style=random_style,
                            extra_requirements=random_extra
                        )

                    st.session_state.random_case_text = generated_text
                    st.success("随机案件文本已生成。你可以检查后点击“生成 / 编译剧本”。")
                    st.rerun()

                except Exception as e:
                    st.error(f"随机案件文本生成失败：{e}")

        raw_text = st.text_area(
            "输入文本",
            value=default_text,
            height=300,
            help="AI随机生成的内容会出现在这里。确认没问题后，再点击下面的“生成 / 编译剧本”。"
        )
        if uploaded:
            temp = Path("data/scripts") / uploaded.name
            temp.parent.mkdir(parents=True, exist_ok=True)
            temp.write_bytes(uploaded.getbuffer())
            try:
                raw_text = load_document_text(temp)
                st.success("文件读取成功")
            except Exception as e:
                st.error(f"读取失败：{e}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("生成 / 编译剧本", type="primary"):
                try:
                    if mode == "固定格式剧本直接编译":
                        fixed_text = raw_text
                        script = compile_script(fixed_text)
                    else:
                        llm = get_llm()
                        if not llm:
                            st.error("普通文本生成剧本需要大模型，请先连接 Qwen。")
                            st.stop()
                        result = document_to_script(raw_text, llm, role_count=role_count)
                        fixed_text = result["fixed_text"]
                        script = result["json"]
                        save_generated_script(fixed_text, "data/scripts/generated_from_document.txt")
                    st.session_state.script = script
                    st.session_state.fixed_text = fixed_text
                    if "room" in st.session_state:
                        del st.session_state.room
                    st.success("剧本准备完成。")
                except Exception as e:
                    st.error(f"生成/编译失败：{e}")
        with col_b:
            if st.button("查看/隐藏固定格式剧本"):
                st.session_state.show_fixed = not st.session_state.get("show_fixed", False)

        if st.session_state.get("show_fixed"):
            st.text_area("固定格式剧本", value=st.session_state.get("fixed_text", ""), height=360)

    with c2:
        st.markdown("### 当前剧本卡")
        st.markdown(f"""
<div class="card">
  <h2>《{script.get('title', '未命名剧本')}》</h2>
  <p>{script.get('background', '')[:220]}...</p>
  <span class="badge human">{len(script.get('roles', []))} 人本</span>
  <span class="badge ai">AI补位</span>
  <span class="badge">推理本</span>
</div>
""", unsafe_allow_html=True)
        st.markdown("### 👤 角色档案")

        roles = script.get("roles", [])
        room = st.session_state.get("room", {})
        player_role = room.get("player_role", "")

        if roles:
            for role in roles:
                role_profile_card(
                    role,
                    is_player=(role.get("name") == player_role)
                )
        else:
            st.info("当前剧本还没有解析到角色。")

        st.markdown("### 🗂️ 三幕卷宗")

        stages = script.get("stages", [])

        if stages:
            for idx, stage in enumerate(stages, start=1):
                title = stage.get("name", f"第{idx}幕线索")
                clues = stage.get("evidence", [])

                if idx == 1:
                    summary = "事件初始阶段，建立人物关系、基础时间线与第一批疑点。"
                elif idx == 2:
                    summary = "矛盾升级阶段，动机冲突与行动轨迹逐渐浮现。"
                else:
                    summary = "真相收束阶段，关键证据链与误导信息逐渐清晰。"

                clue_case_card(
                    title,
                    clues,
                    unlocked=True,
                    summary=summary
                )
        else:
            st.info("当前剧本还没有解析到线索。")

with tab2:
    st.markdown("### 创建游戏房间")
    roles = [r["name"] for r in script.get("roles", [])]
    if not roles:
        st.warning("当前剧本没有角色，请先生成/编译剧本。")
    else:
        player_role = st.selectbox("选择你的角色", roles)
        if st.button("创建房间", type="primary"):
            room = create_room(script, player_role, ai_enabled=ai_enabled)
            st.session_state.room = room
            add_message(room, "主持人", "全体", HostAgent(script, room, get_llm()).opening(), "host")
            st.success("房间创建成功。")
        room = st.session_state.get("room")
        if room:
            st.markdown(f"房间 ID：`{room['room_id']}`")
            stage_bar(STAGES, room.get("current_stage_index", 0))

            if room.get("game_over", False):
                render_game_over_controls("top")

            cols = st.columns(max(1, len(room.get("players", []))))
            role_map = {r["name"]: r for r in script.get("roles", [])}
            for i, p in enumerate(room.get("players", [])):
                with cols[i]:
                    rr = role_map.get(p["role"], {})
                    role_card(p["role"], p["type"], p["status"], rr.get("goal", ""))
            if st.button("AI角色自我介绍", type="primary"):
                # AI 自我介绍后，不应该还停留在准备阶段，直接进入开场介绍
                if room.get("current_stage_index", 0) == 0:
                    _script2game_force_stage(room, 1)
                    add_message(
                        room,
                        "主持人",
                        "全体",
                        HostAgent(script, room, get_llm()).stage_intro(),
                        "host"
                    )

                if not room.get("ai_intro_done", False):
                    ai_all_intro(script, room, get_llm())
                    room["ai_intro_done"] = True
                else:
                    add_message(
                        room,
                        "主持人",
                        "全体",
                        "AI角色已经完成过自我介绍，现在可以开始盘问。",
                        "host"
                    )

                st.session_state.jump_to_game_room = True
                st.success("AI角色已自我介绍，已自动进入开场介绍。")
                st.rerun()



with tab3:
    st.markdown("### 💬 游戏房间")
    room = st.session_state.get("room")

    if not room:
        st.warning("请先创建房间。")
    else:
        # 顶部状态栏
        st.markdown(f"""
<div class="room-status-card">
  <div>
    <span class="room-title">房间 #{room.get('room_id', '')}</span>
    <span class="room-subtitle">《{script.get('title', '未命名剧本')}》</span>
  </div>
  <div>
    <span class="badge human">你：{room.get('player_role', '玩家')}</span>
    <span class="badge ai">当前：{room.get('current_stage', '')}</span>
  </div>
</div>
""", unsafe_allow_html=True)

        stage_bar(STAGES, room.get("current_stage_index", 0))

        if room.get("game_over", False):
            render_game_over_controls("top")


        chat_col, side_col = st.columns([1.75, 0.95])

        with chat_col:
            # 输入框放到最上面
            st.markdown("#### 你的发言")

            st.markdown('<div class="input-panel">', unsafe_allow_html=True)

            ai_roles = [
                p["role"] for p in room.get("players", [])
                if p["role"] != room.get("player_role")
            ]

            speak_mode = st.radio(
                "发言方式",
                ["全体公开发言", "询问主持人", "询问角色"],
                horizontal=True
            )

            target = "全体"

            if speak_mode == "询问角色":
                if ai_roles:
                    target = st.selectbox("选择询问角色", ai_roles)
                else:
                    st.info("当前没有可询问的其他角色。")
                    target = "全体"

            elif speak_mode == "询问主持人":
                target = "主持人"

            question = st.text_area(
                "输入你的发言",
                height=110,
                placeholder="例如：沈宁，你说自己 21:30 后离开了，那 22:25 回来取移动硬盘这件事怎么解释？"
            )

            send_clicked = st.button("发送", type="primary", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

            if send_clicked:
                if not question.strip():
                    st.warning("先输入一句话再发送。")
                else:
                    # 玩家发言先进入聊天记录
                    add_message(
                        room,
                        room.get("player_role", "玩家"),
                        target,
                        question,
                        "human"
                    )

                    # 全体公开发言：只记录，不强制 AI 回复
                    if speak_mode == "全体公开发言":
                        ai_react_to_latest_user(script, room, get_llm(), max_roles=2)

                    # 问主持人：主持人回复
                    elif speak_mode == "询问主持人":
                        ans = HostAgent(script, room, get_llm()).answer(question)
                        add_message(
                            room,
                            "主持人",
                            room.get("player_role", "玩家"),
                            ans,
                            "host"
                        )

                    # 问角色：对应角色回复
                    elif speak_mode == "询问角色" and target != "全体":
                        ans = RoleAgent(script, room, target, get_llm()).answer(question)
                        add_message(
                            room,
                            target,
                            room.get("player_role", "玩家"),
                            ans,
                            "ai"
                        )

                    st.rerun()

            st.markdown("#### 聊天记录（最新在上）")

            # 最新消息倒序显示，并一次性渲染到聊天框中，避免出现空白大框
            messages_to_show = list(reversed(room.get("messages", [])[-40:]))
            chat_panel(messages_to_show)

        with side_col:
            st.markdown("#### 阶段控制")

            st.markdown(f"""
<div class="side-panel">
  <div class="side-title">当前任务</div>
  <div class="side-content">当前处于 <b>{room.get('current_stage', '')}</b>。你可以公开发言、询问某个角色，或推进阶段解锁新线索。</div>
</div>
""", unsafe_allow_html=True)

            control_col1, control_col2 = st.columns(2)

            with control_col1:
                if st.button("进入下一阶段", type="primary", use_container_width=True):
                    if room.get("game_over", False):
                        st.warning("本局已经结束，请点击结束本局或重新开局。")
                    elif room.get("current_stage") == "复盘结算":
                        st.warning("已经进入复盘结算阶段，不能再继续推进。")
                    else:
                        next_stage(room, script)

                        add_message(
                            room,
                            "主持人",
                            "全体",
                            HostAgent(script, room, get_llm()).stage_intro(),
                            "host"
                        )

                        if room.get("current_stage") not in ["最终推理", "复盘结算"]:
                            ai_stage_speak(script, room, get_llm())

                        st.rerun()

            with control_col2:
                if st.button("AI主动发言", use_container_width=True):
                    if room.get("game_over", False):
                        st.warning("本局已经结束，AI角色不会继续发言。")
                    elif room.get("current_stage") in ["最终推理", "复盘结算"]:
                        st.warning("当前是最终推理/复盘阶段，请提交最终推理，由主持人复盘，不再让角色继续自由发言。")
                    else:
                        ai_react_to_latest_user(script, room, get_llm(), max_roles=2)
                        st.rerun()

            # ===== 最终推理 / 全员复盘 =====
            if room.get("current_stage") in ["最终推理", "复盘结算"]:
                st.markdown("#### 🧑‍⚖️ 最终推理与主持人复盘")

                final_reasoning = st.text_area(
                    "提交你的最终推理",
                    key="game_room_final_reasoning",
                    height=140,
                    placeholder="请写出：关键人物是谁、动机是什么、证据链是什么、你如何排除其他人。"
                )

                if st.button("提交最终推理，开始全员复盘", type="primary", use_container_width=True):
                    if not str(final_reasoning or "").strip():
                        st.warning("请先填写你的最终推理。")
                    else:
                        room.setdefault("final_answers", {})

                        player_role_name = room.get("player_role", "真人玩家")
                        room["final_answers"][player_role_name] = final_reasoning

                        add_message(
                            room,
                            player_role_name,
                            "主持人",
                            "【最终推理】\n" + str(final_reasoning),
                            "human"
                        )

                        ai_submit_final_answers(script, room, get_llm())

                        review = host_final_review(
                            get_llm(),
                            script,
                            room,
                            final_reasoning
                        )

                        st.session_state.host_final_review_text = review

                        room["current_stage_index"] = 6
                        room["current_stage"] = "复盘结算"
                        room["game_over"] = True

                        add_message(
                            room,
                            "主持人",
                            "全体",
                            review,
                            "host"
                        )

                        st.rerun()

                if st.session_state.get("host_final_review_text"):
                    st.markdown("##### 复盘结果")
                    st.markdown(st.session_state.host_final_review_text)

            st.markdown("#### 当前线索")

            if room.get("unlocked_evidence"):
                for i, ev in enumerate(room["unlocked_evidence"][-6:], 1):
                    evidence_card(i, ev)
            else:
                st.info("暂无公开线索。推进到第一幕后会解锁。")

            st.markdown("#### 角色状态")

            role_map = {r["name"]: r for r in script.get("roles", [])}

            for p in room.get("players", []):
                rr = role_map.get(p["role"], {})
                role_card(
                    p["role"],
                    p["type"],
                    p["status"],
                    rr.get("goal", "")
                )

with tab4:
    st.markdown("### 线索板 / 关系图")
    room = st.session_state.get("room")
    if not room:
        st.warning("请先创建房间。")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 已解锁证据")
            for i, ev in enumerate(room.get("unlocked_evidence", []), 1):
                evidence_card(i, ev)
            st.markdown("#### 时间线")
            timeline = build_timeline(script, room)
            if timeline:
                for t in timeline:
                    st.write("⏱️ " + t)
            else:
                st.info("暂无时间线。")
        with c2:
            st.markdown("#### 📝 人物说法")
            claims = build_claims(room)

            if claims:
                for idx, item in enumerate(claims, start=1):
                    claim_note_card(
                        idx,
                        item.get("角色", ""),
                        item.get("说法", "")
                    )
            else:
                st.info("暂无发言。")

            st.markdown("#### 🔗 关系链")
            edges = build_relation_edges(script, room)

            if edges:
                for idx, item in enumerate(edges, start=1):
                    relation_edge_card(
                        idx,
                        item.get("头实体", ""),
                        item.get("关系", ""),
                        item.get("尾实体", ""),
                        item.get("来源", "")
                    )
            else:
                st.info("暂无关系。")

with tab5:
    st.markdown("### 最终推理 / 裁判评分")
    room = st.session_state.get("room")
    if not room:
        st.warning("请先创建房间。")
    else:
        answer = st.text_area("提交你的最终推理", value="我认为真正关键人物是……因为……证据包括……", height=180)
        if st.button("提交并评分", type="primary"):
            result = JudgeAgent(script, room, get_llm()).judge(answer)
            st.markdown('<div class="score-card">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
