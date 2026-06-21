import html
import streamlit as st



def inject_css():
    st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
}

/* 整体：复古档案桌面风 */
.stApp {
    background:
        radial-gradient(circle at 18% 8%, rgba(120,53,15,.10), transparent 26%),
        radial-gradient(circle at 88% 18%, rgba(127,29,29,.10), transparent 24%),
        linear-gradient(180deg, #F3E8D3 0%, #EAD8B8 54%, #D8BE91 100%);
    color: #2B2118;
}

/* 顶部栏 */
header[data-testid="stHeader"] {
    background: rgba(43, 29, 20, .96) !important;
    border-bottom: 1px solid rgba(120, 53, 15, .25) !important;
}
header[data-testid="stHeader"] * {
    color: #F8EEDB !important;
}
div[data-testid="stDecoration"] {
    background: linear-gradient(90deg, #7F1D1D, #B45309, #D4A017) !important;
}

/* 侧边栏：深木色控制台 */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #1C1917 0%, #292524 52%, #1C1917 100%) !important;
    border-right: 1px solid rgba(245, 222, 179, .18);
}
section[data-testid="stSidebar"] * {
    color: #F8EEDB !important;
}

/* 主内容宽度 */
.block-container {
    padding-top: 2rem;
    max-width: 1480px;
}

/* 顶部 Hero：案卷封面，不再霓虹 */
.hero {
    border: 1px solid rgba(120,53,15,.22);
    background:
        linear-gradient(135deg, rgba(43,29,20,.82), rgba(90,55,30,.54)),
        url('https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=1600&q=80');
    background-size: cover;
    background-position: center;
    border-radius: 22px;
    padding: 34px 42px;
    box-shadow: 0 18px 45px rgba(62,39,22,.28);
    margin-bottom: 20px;
}
.hero h1 {
    font-size: 44px;
    line-height: 1.1;
    font-weight: 900;
    margin: 0 0 12px 0;
    color: #FFF7ED;
    letter-spacing: .5px;
}
.hero p {
    font-size: 17px;
    color: #FDEDD3;
    max-width: 820px;
    line-height: 1.8;
}

/* 通用卡片：纸张质感 */
.card, .role-card, .evidence-card, .score-card, .room-status-card, .side-panel, .input-panel {
    border: 1px solid rgba(120,53,15,.20);
    background:
        linear-gradient(180deg, rgba(255,251,235,.95), rgba(250,240,218,.92));
    border-radius: 18px;
    padding: 18px;
    box-shadow:
        0 12px 28px rgba(92,64,32,.16),
        inset 0 0 0 1px rgba(255,255,255,.45);
    color: #2B2118;
    margin-bottom: 14px;
}

/* 剧本卡更像档案 */
.card h2, .card h3, .card p,
.role-card, .evidence-card, .score-card,
.room-status-card, .side-panel, .input-panel {
    color: #2B2118 !important;
}

.role-card {
    border-left: 5px solid #7F1D1D;
    padding: 14px;
    border-radius: 14px;
}
.role-name {
    font-size: 18px;
    font-weight: 900;
    color: #2B2118;
}

/* 标签 */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    margin: 4px 6px 4px 0;
    background: rgba(180,83,9,.12);
    border: 1px solid rgba(180,83,9,.32);
    color: #92400E !important;
    font-weight: 700;
}
.badge.ai {
    background: rgba(30,64,175,.10);
    border-color: rgba(30,64,175,.28);
    color: #1E3A8A !important;
}
.badge.human {
    background: rgba(21,128,61,.10);
    border-color: rgba(21,128,61,.28);
    color: #166534 !important;
}

/* 阶段条 */
.stage-bar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 10px 0 20px 0;
}
.stage-item {
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(255,251,235,.74);
    color: #6B4F32;
    border: 1px solid rgba(120,53,15,.18);
    font-size: 13px;
    font-weight: 700;
}
.stage-item.active {
    background: linear-gradient(135deg, #7F1D1D, #B91C1C);
    color: #FFF7ED;
    font-weight: 900;
    box-shadow: 0 8px 20px rgba(127,29,29,.25);
}

/* 聊天框：档案桌上的记录纸 */
.chat-box {
    max-height: 620px;
    overflow-y: auto;
    padding: 12px;
    border-radius: 18px;
    background:
        linear-gradient(180deg, rgba(255,251,235,.92), rgba(250,240,218,.88));
    border: 1px solid rgba(120,53,15,.20);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.45);
}
.chat-box-main {
    height: 420px !important;
    max-height: 420px !important;
    overflow-y: auto !important;
}

/* 聊天气泡 */
.bubble {
    padding: 12px 14px;
    border-radius: 15px;
    margin: 10px 0;
    border: 1px solid rgba(120,53,15,.14);
    background: rgba(255,255,255,.58);
    color: #2B2118;
}
.bubble.player {
    background: #DCFCE7;
    border-color: rgba(22,101,52,.25);
}
.bubble.host {
    background: #FEE2E2;
    border-color: rgba(127,29,29,.25);
}
.bubble.ai {
    background: #DBEAFE;
    border-color: rgba(30,64,175,.22);
}
.bubble .meta {
    font-size: 12px;
    color: #6B7280;
    margin-bottom: 6px;
    font-weight: 700;
}
.bubble .content {
    color: #1F2937;
    line-height: 1.75;
    font-weight: 600;
}

/* 空聊天 */
.empty-chat {
    color: #78716C;
    padding: 20px;
    text-align: center;
    border: 1px dashed rgba(120,53,15,.25);
    border-radius: 14px;
    background: rgba(255,255,255,.35);
}

/* 线索卡 */
.evidence-card {
    border-left: 5px solid #B45309;
    border-radius: 14px;
    padding: 14px;
}
.evidence-card .tag {
    font-size: 12px;
    color: #92400E;
    margin-bottom: 6px;
    font-weight: 900;
}

/* 评分卡 */
.score-card {
    border-left: 6px solid #7F1D1D;
    border-radius: 18px;
    padding: 24px;
    background:
        linear-gradient(180deg, rgba(255,251,235,.98), rgba(254,226,226,.80));
    color: #2B2118 !important;
}
.score-card * {
    color: #2B2118 !important;
}

/* 房间状态栏 */
.room-status-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}
.room-title {
    font-weight: 900;
    font-size: 18px;
    color: #2B2118;
}
.room-subtitle {
    margin-left: 10px;
    font-size: 14px;
    color: #6B4F32;
}

/* 右侧任务面板 */
.side-title {
    font-weight: 900;
    color: #7F1D1D;
    margin-bottom: 8px;
}
.side-content {
    color: #3F2E22;
    font-size: 14px;
    line-height: 1.7;
}

/* 输入框 */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] > div {
    background: rgba(255,251,235,.92) !important;
    color: #2B2118 !important;
    border: 1px solid rgba(120,53,15,.26) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 2px rgba(92,64,32,.10);
}

/* 数字输入按钮 */
div[data-testid="stNumberInput"] button {
    background: #F5E6C8 !important;
    color: #2B2118 !important;
    border: 1px solid rgba(120,53,15,.22) !important;
}

/* 上传框 */
section[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,251,235,.78) !important;
    border: 1px dashed rgba(120,53,15,.35) !important;
    border-radius: 14px !important;
}
section[data-testid="stFileUploaderDropzone"] * {
    color: #3F2E22 !important;
}

/* 按钮：酒红印章 */
.stButton button {
    border-radius: 999px !important;
    background: linear-gradient(135deg, #7F1D1D, #B91C1C) !important;
    color: #FFF7ED !important;
    font-weight: 900 !important;
    border: none !important;
    padding: .62rem 1.15rem !important;
    box-shadow: 0 8px 18px rgba(127,29,29,.25);
}
.stButton button:hover {
    background: linear-gradient(135deg, #991B1B, #DC2626) !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #5B4636 !important;
    font-weight: 800 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #7F1D1D !important;
    border-bottom-color: #7F1D1D !important;
}

/* 标题正文 */
h1, h2, h3, h4 {
    color: #2B2118 !important;
    font-weight: 900 !important;
}
p, li, label, span, div {
    color: inherit;
}

/* dataframe 不要刺眼 */
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* radio/checkbox */
label[data-baseweb="radio"] span,
label[data-baseweb="checkbox"] span {
    color: #2B2118 !important;
}

/* 侧边栏里的 radio/checkbox 仍保持浅色 */
section[data-testid="stSidebar"] label[data-baseweb="radio"] span,
section[data-testid="stSidebar"] label[data-baseweb="checkbox"] span {
    color: #F8EEDB !important;
}

/* ===== 侧边栏输入框可读性强制修复 ===== */

/* 侧边栏普通输入框、数字框、文本框 */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: #FFF7ED !important;
    color: #1C1917 !important;
    border: 1px solid rgba(120,53,15,.35) !important;
    border-radius: 12px !important;
    caret-color: #7F1D1D !important;
    -webkit-text-fill-color: #1C1917 !important;
}

/* 侧边栏输入框 placeholder */
section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
    color: #78716C !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #78716C !important;
}

/* 侧边栏 selectbox 外壳 */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: #FFF7ED !important;
    color: #1C1917 !important;
    border: 1px solid rgba(120,53,15,.35) !important;
    border-radius: 12px !important;
}

/* selectbox 内部文字 */
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] div {
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
}

/* selectbox 右侧箭头 */
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #1C1917 !important;
    color: #1C1917 !important;
}

/* number_input 的 + - 按钮 */
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] button {
    background: #F5E6C8 !important;
    color: #1C1917 !important;
    border: 1px solid rgba(120,53,15,.35) !important;
}

section[data-testid="stSidebar"] div[data-testid="stNumberInput"] button svg {
    fill: #1C1917 !important;
    color: #1C1917 !important;
}

/* 禁用态也要能看清，不要白字 */
section[data-testid="stSidebar"] input:disabled,
section[data-testid="stSidebar"] button:disabled {
    background: #F5E6C8 !important;
    color: #57534E !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #57534E !important;
}

/* 聚焦状态 */
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
    border-color: #B45309 !important;
    box-shadow: 0 0 0 2px rgba(180,83,9,.22) !important;
}

/* 侧边栏 label 保持浅色，输入内容保持深色 */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #F8EEDB !important;
}

/* slider 数值和说明文字 */
section[data-testid="stSidebar"] div[data-testid="stSlider"] * {
    color: #F8EEDB !important;
}

/* slider 轨道 */
section[data-testid="stSidebar"] div[data-testid="stSlider"] [role="slider"] {
    background: #EF4444 !important;
}


/* ===== 全局可读性兜底修复：浅色框必须深色字 ===== */

/* 主内容区文字统一深色，避免米色背景白字 */
div[data-testid="stAppViewContainer"] main,
div[data-testid="stAppViewContainer"] main p,
div[data-testid="stAppViewContainer"] main span,
div[data-testid="stAppViewContainer"] main label,
div[data-testid="stAppViewContainer"] main div,
div[data-testid="stAppViewContainer"] main li {
    color: #2B2118 !important;
}

/* 主内容区标题 */
div[data-testid="stAppViewContainer"] main h1,
div[data-testid="stAppViewContainer"] main h2,
div[data-testid="stAppViewContainer"] main h3,
div[data-testid="stAppViewContainer"] main h4 {
    color: #2B2118 !important;
}

/* 所有浅色输入框：深色文字 */
div[data-testid="stAppViewContainer"] main input,
div[data-testid="stAppViewContainer"] main textarea,
div[data-testid="stAppViewContainer"] main div[data-baseweb="input"] input,
div[data-testid="stAppViewContainer"] main div[data-baseweb="textarea"] textarea,
div[data-testid="stAppViewContainer"] main div[data-baseweb="select"] > div {
    background: #FFF7ED !important;
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
    border: 1px solid rgba(120,53,15,.35) !important;
    border-radius: 12px !important;
}

/* placeholder 也要看得见 */
div[data-testid="stAppViewContainer"] main input::placeholder,
div[data-testid="stAppViewContainer"] main textarea::placeholder {
    color: #78716C !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #78716C !important;
}

/* selectbox 内部文字、箭头 */
div[data-testid="stAppViewContainer"] main div[data-baseweb="select"] span,
div[data-testid="stAppViewContainer"] main div[data-baseweb="select"] div {
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
}

div[data-testid="stAppViewContainer"] main div[data-baseweb="select"] svg {
    fill: #1C1917 !important;
    color: #1C1917 !important;
}

/* number_input 的 + - */
div[data-testid="stAppViewContainer"] main div[data-testid="stNumberInput"] button {
    background: #F5E6C8 !important;
    color: #1C1917 !important;
    border: 1px solid rgba(120,53,15,.35) !important;
}

div[data-testid="stAppViewContainer"] main div[data-testid="stNumberInput"] button svg {
    fill: #1C1917 !important;
}

/* 文件上传区域 */
section[data-testid="stFileUploaderDropzone"] {
    background: #FFF7ED !important;
    border: 1px dashed rgba(120,53,15,.42) !important;
    border-radius: 14px !important;
}

section[data-testid="stFileUploaderDropzone"] * {
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
}

/* Browse files 按钮单独处理 */
section[data-testid="stFileUploaderDropzone"] button {
    background: #7F1D1D !important;
    color: #FFF7ED !important;
    -webkit-text-fill-color: #FFF7ED !important;
    border-radius: 12px !important;
}

/* 卡片内所有文字强制深色 */
.card *,
.role-card *,
.evidence-card *,
.score-card *,
.room-status-card *,
.side-panel *,
.input-panel * {
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
}

/* badge 颜色单独恢复，否则会被上面覆盖 */
.badge {
    color: #92400E !important;
    -webkit-text-fill-color: #92400E !important;
}
.badge.ai {
    color: #1E3A8A !important;
    -webkit-text-fill-color: #1E3A8A !important;
}
.badge.human {
    color: #166534 !important;
    -webkit-text-fill-color: #166534 !important;
}

/* 聊天气泡内容 */
.bubble .meta {
    color: #6B7280 !important;
    -webkit-text-fill-color: #6B7280 !important;
}
.bubble .content {
    color: #1F2937 !important;
    -webkit-text-fill-color: #1F2937 !important;
}

/* 线索 tag */
.evidence-card .tag {
    color: #92400E !important;
    -webkit-text-fill-color: #92400E !important;
}

/* 按钮必须白字 */
.stButton button,
.stButton button * {
    color: #FFF7ED !important;
    -webkit-text-fill-color: #FFF7ED !important;
}

/* 侧边栏：label 保持浅色 */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] span {
    color: #F8EEDB !important;
}

/* 侧边栏输入框内部仍然深色字 */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"] input {
    background: #FFF7ED !important;
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
    border: 1px solid rgba(120,53,15,.35) !important;
}

/* 侧边栏 select 内部文字 */
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] div {
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
}

/* 侧边栏 select 箭头 */
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #1C1917 !important;
    color: #1C1917 !important;
}

/* 侧边栏 number_input 加减按钮 */
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] button,
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] button * {
    background: #F5E6C8 !important;
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
}

/* 下拉菜单弹出层，有些会挂到 body 根部，不在 sidebar/main 内 */
div[data-baseweb="popover"] *,
ul[role="listbox"] *,
li[role="option"] * {
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
}

div[data-baseweb="popover"],
ul[role="listbox"],
li[role="option"] {
    background: #FFF7ED !important;
    color: #1C1917 !important;
}

/* dataframe 区域尽量保持白底黑字 */
div[data-testid="stDataFrame"] * {
    color: #1C1917 !important;
    -webkit-text-fill-color: #1C1917 !important;
}


/* ===== 角色档案卡：替代 dataframe ===== */
.dossier-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin: 12px 0 22px 0;
}

.dossier-card {
    background: linear-gradient(180deg, #FFF7ED 0%, #F7E7C6 100%);
    border: 1px solid rgba(120,53,15,.24);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 8px 20px rgba(92,64,32,.12);
    margin-bottom: 14px;
    color: #2B2118 !important;
}

.dossier-card * {
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
}

.dossier-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    border-bottom: 1px dashed rgba(120,53,15,.22);
    padding-bottom: 10px;
}

.dossier-name {
    font-size: 20px;
    font-weight: 900;
    color: #2B2118 !important;
}

.dossier-tag {
    background: #92400E;
    color: #FFF7ED !important;
    -webkit-text-fill-color: #FFF7ED !important;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
}

.dossier-tag.player {
    background: #166534;
}

.dossier-block {
    margin-top: 10px;
}

.dossier-label {
    font-size: 13px;
    font-weight: 900;
    color: #92400E !important;
    -webkit-text-fill-color: #92400E !important;
    margin-bottom: 4px;
}

.dossier-text {
    font-size: 14px;
    line-height: 1.7;
    color: #2B2118 !important;
}

.dossier-detail {
    margin-top: 12px;
    border-top: 1px dashed rgba(120,53,15,.20);
    padding-top: 10px;
}

.dossier-detail summary {
    cursor: pointer;
    font-size: 13px;
    font-weight: 800;
    color: #7F1D1D !important;
    -webkit-text-fill-color: #7F1D1D !important;
}

.dossier-secret {
    margin-top: 8px;
    font-size: 13px;
    line-height: 1.7;
    color: #3F2E22 !important;
}

/* ===== 三幕卷宗卡：替代 expander ===== */
.case-card {
    background: linear-gradient(180deg, #FFF7ED 0%, #F4DFB7 100%);
    border: 1px solid rgba(120,53,15,.24);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 8px 20px rgba(92,64,32,.10);
    margin-bottom: 16px;
    color: #2B2118 !important;
}

.case-card * {
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
}

.case-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 12px;
}

.case-title {
    font-size: 20px;
    font-weight: 900;
    color: #2B2118 !important;
}

.case-summary {
    font-size: 13px;
    color: #6B4F32 !important;
    -webkit-text-fill-color: #6B4F32 !important;
    margin-top: 5px;
    line-height: 1.6;
}

.case-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
    white-space: nowrap;
}

.case-status {
    font-size: 12px;
    font-weight: 900;
    padding: 4px 10px;
    border-radius: 999px;
}

.case-status.open {
    background: rgba(21,128,61,.12);
    color: #166534 !important;
    -webkit-text-fill-color: #166534 !important;
    border: 1px solid rgba(21,128,61,.28);
}

.case-status.locked {
    background: rgba(107,114,128,.12);
    color: #4B5563 !important;
    -webkit-text-fill-color: #4B5563 !important;
    border: 1px solid rgba(107,114,128,.24);
}

.case-count {
    font-size: 12px;
    color: #92400E !important;
    -webkit-text-fill-color: #92400E !important;
    font-weight: 800;
}

.case-body {
    border-top: 1px dashed rgba(120,53,15,.22);
    padding-top: 12px;
}

.case-list {
    margin: 0;
    padding-left: 18px;
}

.case-list li {
    margin-bottom: 8px;
    line-height: 1.7;
    color: #2B2118 !important;
}

.case-empty {
    color: #78716C !important;
    -webkit-text-fill-color: #78716C !important;
    font-size: 14px;
}

@media (max-width: 1100px) {
    .dossier-grid {
        grid-template-columns: 1fr;
    }
}


/* ===== 修复卷宗卡布局：防止标题竖排 / meta 区挤压 ===== */
.case-top {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    gap: 18px !important;
    width: 100% !important;
}

.case-main {
    flex: 1 !important;
    min-width: 0 !important;
}

.case-title {
    display: block !important;
    white-space: normal !important;
    word-break: keep-all !important;
    writing-mode: horizontal-tb !important;
    min-width: 160px !important;
}

.case-summary {
    display: block !important;
    white-space: normal !important;
    word-break: normal !important;
}

.case-meta {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-end !important;
    gap: 8px !important;
    min-width: 86px !important;
    white-space: nowrap !important;
}

.case-status,
.case-count {
    display: inline-block !important;
    white-space: nowrap !important;
}

.case-body {
    width: 100% !important;
}


/* ===== 人物说法卡：替代表格 ===== */
.claim-card {
    background: linear-gradient(180deg, #FFF7ED 0%, #F6E6C9 100%);
    border: 1px solid rgba(120,53,15,.24);
    border-left: 5px solid #1E3A8A;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 8px 18px rgba(92,64,32,.10);
}

.claim-card * {
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
}

.claim-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.claim-index {
    font-size: 12px;
    font-weight: 900;
    color: #1E3A8A !important;
    -webkit-text-fill-color: #1E3A8A !important;
}

.claim-role {
    font-size: 13px;
    font-weight: 900;
    background: rgba(30,64,175,.10);
    border: 1px solid rgba(30,64,175,.24);
    color: #1E3A8A !important;
    -webkit-text-fill-color: #1E3A8A !important;
    padding: 4px 10px;
    border-radius: 999px;
}

.claim-content {
    font-size: 14px;
    line-height: 1.75;
    color: #2B2118 !important;
}

/* ===== 关系链卡：替代表格 ===== */
.relation-card {
    background: linear-gradient(180deg, #FFF7ED 0%, #F4DFB7 100%);
    border: 1px solid rgba(120,53,15,.24);
    border-left: 5px solid #7F1D1D;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 8px 18px rgba(92,64,32,.10);
}

.relation-card * {
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
}

.relation-index {
    font-size: 12px;
    font-weight: 900;
    color: #7F1D1D !important;
    -webkit-text-fill-color: #7F1D1D !important;
    margin-bottom: 8px;
}

.relation-line {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    font-size: 15px;
    line-height: 1.8;
}

.relation-entity {
    font-weight: 900;
    background: rgba(120,53,15,.10);
    border: 1px solid rgba(120,53,15,.22);
    padding: 4px 10px;
    border-radius: 10px;
}

.relation-arrow {
    font-weight: 900;
    color: #92400E !important;
    -webkit-text-fill-color: #92400E !important;
}

.relation-source {
    margin-top: 8px;
    font-size: 12px;
    color: #78716C !important;
    -webkit-text-fill-color: #78716C !important;
}

/* 线索板右侧卡片排版 */
.board-card-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}


/* ===== 统一角色卡高度 ===== */
.role-card-fixed {
    height: 190px !important;
    min-height: 190px !important;
    max-height: 190px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    overflow: hidden !important;
}

.role-card-fixed .role-name {
    font-size: 18px !important;
    line-height: 1.35 !important;
    margin-bottom: 8px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

.role-card-fixed .badge {
    width: fit-content !important;
    margin-bottom: 8px !important;
}

.role-goal-text {
    font-size: 14px !important;
    line-height: 1.65 !important;
    color: #2B2118 !important;
    -webkit-text-fill-color: #2B2118 !important;
    overflow: hidden !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 5 !important;
    -webkit-box-orient: vertical !important;
}

/* 如果一排角色太多，让卡片不要被挤得太窄 */
div[data-testid="column"] .role-card-fixed {
    min-width: 150px !important;
}


/* ===== 隐藏顶部单独的“复盘评分”Tab，复盘改为游戏房间内由主持人完成 ===== */
div[data-baseweb="tab-list"] button:nth-of-type(5) {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

def hero():
    st.markdown("""
<div class="hero">
  <h1>Script2Game</h1>
  <p>上传故事、案件材料或剧本文档，生成一局可推进、可盘问、可评分的 AI 增强剧本杀房间。真人负责博弈，AI 负责主持、补位、控流程和复盘。</p>
</div>
""", unsafe_allow_html=True)


def stage_bar(stages, current_index):
    parts = ['<div class="stage-bar">']
    for i, s in enumerate(stages):
        cls = "stage-item active" if i == current_index else "stage-item"
        parts.append(f'<span class="{cls}">{i+1}. {html.escape(s)}</span>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def role_card(role, role_type="ai", status="AI补位", goal=""):
    badge_cls = "human" if role_type == "human" else "ai"
    icon = "🧑‍💼" if role_type == "human" else "🤖"
    st.markdown(f"""
<div class="role-card">
  <div class="role-name">{icon} {html.escape(role)}</div>
  <span class="badge {badge_cls}">{html.escape(status)}</span>
  <div style="font-size:13px;color:rgba(255,255,255,.70);margin-top:6px;">{html.escape(goal or "等待发言")}</div>
</div>
""", unsafe_allow_html=True)


def chat_bubble(speaker, content, role_type="ai", time=""):
    cls = "player" if role_type == "human" else ("host" if speaker == "主持人" else "ai")
    safe = html.escape(content).replace(chr(10), "<br>")
    st.markdown(f"""
<div class="bubble {cls}">
  <div class="meta">{html.escape(time)} · {html.escape(speaker)}</div>
  <div class="content">{safe}</div>
</div>
""", unsafe_allow_html=True)


def evidence_card(idx, text, tag="证据卡"):
    st.markdown(f"""
<div class="evidence-card">
  <div class="tag">{tag} #{idx:02d}</div>
  <div>{html.escape(text)}</div>
</div>
""", unsafe_allow_html=True)



def chat_panel(messages):
    """一次性渲染聊天面板，避免 Streamlit HTML div 空壳问题。"""
    parts = ['<div class="chat-box chat-box-main">']

    if not messages:
        parts.append('<div class="empty-chat">暂无发言。创建房间后，主持人会先开场。</div>')
    else:
        for msg in messages:
            speaker = html.escape(msg.get("speaker", ""))
            content = html.escape(msg.get("content", "")).replace(chr(10), "<br>")
            role_type = msg.get("role_type", "ai")
            time = html.escape(msg.get("time", ""))

            cls = "player" if role_type == "human" else ("host" if speaker == "主持人" else "ai")

            parts.append(f"""
<div class="bubble {cls}">
  <div class="meta">{time} · {speaker}</div>
  <div class="content">{content}</div>
</div>
""")

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)



def role_profile_card(role, is_player=False):
    """角色档案卡：替代 dataframe 表格。"""
    name = role.get("name", "")
    public_profile = role.get("public_profile", "")
    private_memory = role.get("private_memory", "")
    goal = role.get("goal", "")

    tag = "真人玩家" if is_player else "角色档案"
    tag_cls = "player" if is_player else "normal"

    st.markdown(f"""
<div class="dossier-card">
  <div class="dossier-head">
    <div class="dossier-name">👤 {html.escape(name)}</div>
    <div class="dossier-tag {tag_cls}">{html.escape(tag)}</div>
  </div>

  <div class="dossier-block">
    <div class="dossier-label">公开身份</div>
    <div class="dossier-text">{html.escape(public_profile)}</div>
  </div>

  <div class="dossier-block">
    <div class="dossier-label">角色目标</div>
    <div class="dossier-text">{html.escape(goal)}</div>
  </div>

  <details class="dossier-detail">
    <summary>查看私密信息</summary>
    <div class="dossier-secret">{html.escape(private_memory)}</div>
  </details>
</div>
""", unsafe_allow_html=True)


def clue_case_card(title, clues, unlocked=True, summary=""):
    """三幕卷宗卡：替代普通 expander。"""
    status = "已解锁" if unlocked else "未解锁"
    status_cls = "open" if unlocked else "locked"

    clues = clues or []
    count = len(clues)

    if not summary:
        if "第一幕" in title:
            summary = "建立人物关系、基础时间线和初始疑点。"
        elif "第二幕" in title:
            summary = "动机冲突升级，关键行动轨迹开始浮现。"
        else:
            summary = "证据链收束，真相与误导信息逐渐清晰。"

    if clues:
        items = "".join(f"<li>{html.escape(str(x))}</li>" for x in clues)
        clue_html = f"<ul class='case-list'>{items}</ul>"
    else:
        clue_html = "<div class='case-empty'>暂无线索</div>"

    st.markdown(f"""
<div class="case-card">
  <div class="case-top">
    <div>
      <div class="case-title">🗂️ {html.escape(title)}</div>
      <div class="case-summary">{html.escape(summary)}</div>
    </div>

    <div class="case-meta">
      <span class="case-status {status_cls}">{status}</span>
      <span class="case-count">{count} 条线索</span>
    </div>
  </div>

  <div class="case-body">
    {clue_html}
  </div>
</div>
""", unsafe_allow_html=True)

# ===== 修正版：角色档案卡 / 三幕卷宗卡 =====
# 说明：这两个函数会覆盖前面同名函数，解决 HTML 被 Streamlit 当代码块显示的问题。

def role_profile_card(role, is_player=False):
    """角色档案卡：替代 dataframe 表格。"""
    name = role.get("name", "")
    public_profile = role.get("public_profile", "")
    private_memory = role.get("private_memory", "")
    goal = role.get("goal", "")

    tag = "真人玩家" if is_player else "角色档案"
    tag_cls = "player" if is_player else "normal"

    html_str = f"""<div class="dossier-card">
<div class="dossier-head">
<div class="dossier-name">👤 {html.escape(name)}</div>
<div class="dossier-tag {tag_cls}">{html.escape(tag)}</div>
</div>

<div class="dossier-block">
<div class="dossier-label">公开身份</div>
<div class="dossier-text">{html.escape(public_profile)}</div>
</div>

<div class="dossier-block">
<div class="dossier-label">角色目标</div>
<div class="dossier-text">{html.escape(goal)}</div>
</div>

<details class="dossier-detail">
<summary>查看私密信息</summary>
<div class="dossier-secret">{html.escape(private_memory)}</div>
</details>
</div>"""

    st.markdown(html_str, unsafe_allow_html=True)


def clue_case_card(title, clues, unlocked=True, summary=""):
    """三幕卷宗卡：替代普通 expander。"""
    status = "已解锁" if unlocked else "未解锁"
    status_cls = "open" if unlocked else "locked"

    clues = clues or []
    count = len(clues)

    if not summary:
        if "第一幕" in title:
            summary = "建立人物关系、基础时间线和初始疑点。"
        elif "第二幕" in title:
            summary = "动机冲突升级，关键行动轨迹开始浮现。"
        else:
            summary = "证据链收束，真相与误导信息逐渐清晰。"

    if clues:
        items = "".join(
            f"<li>{html.escape(str(x))}</li>"
            for x in clues
        )
        clue_html = f"<ul class='case-list'>{items}</ul>"
    else:
        clue_html = "<div class='case-empty'>暂无线索</div>"

    html_str = f"""<div class="case-card">
<div class="case-top">
<div class="case-main">
<div class="case-title">🗂️ {html.escape(title)}</div>
<div class="case-summary">{html.escape(summary)}</div>
</div>

<div class="case-meta">
<span class="case-status {status_cls}">{status}</span>
<span class="case-count">{count} 条线索</span>
</div>
</div>

<div class="case-body">
{clue_html}
</div>
</div>"""

    st.markdown(html_str, unsafe_allow_html=True)

# ===== 修正版：人物说法卡 / 关系链卡 =====

def claim_note_card(idx, role, claim):
    """人物说法卡：替代人物说法 dataframe。"""
    html_str = f"""<div class="claim-card">
<div class="claim-head">
<span class="claim-index">证词 #{idx:02d}</span>
<span class="claim-role">👤 {html.escape(str(role))}</span>
</div>
<div class="claim-content">{html.escape(str(claim))}</div>
</div>"""
    st.markdown(html_str, unsafe_allow_html=True)


def relation_edge_card(idx, head, relation, tail, source=""):
    """关系链卡：替代关系图 dataframe。"""
    html_str = f"""<div class="relation-card">
<div class="relation-index">关系 #{idx:02d}</div>
<div class="relation-line">
<span class="relation-entity">{html.escape(str(head))}</span>
<span class="relation-arrow">── {html.escape(str(relation))} ──▶</span>
<span class="relation-entity">{html.escape(str(tail))}</span>
</div>
<div class="relation-source">来源：{html.escape(str(source or "未知"))}</div>
</div>"""
    st.markdown(html_str, unsafe_allow_html=True)

# ===== 修正版：统一高度角色卡 =====
# 会覆盖前面同名 role_card 函数

def role_card(role, role_type="ai", status="AI补位", goal=""):
    badge_cls = "human" if role_type == "human" else "ai"
    icon = "🧑‍💼" if role_type == "human" else "🤖"

    html_str = f"""<div class="role-card role-card-fixed">
<div class="role-name">{icon} {html.escape(str(role))}</div>
<span class="badge {badge_cls}">{html.escape(str(status))}</span>
<div class="role-goal-text">{html.escape(str(goal or "等待发言"))}</div>
</div>"""

    st.markdown(html_str, unsafe_allow_html=True)
