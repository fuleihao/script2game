# Script2Game：AI 剧本杀生成与陪玩系统使用说明文档

## 1. 项目简介

Script2Game 是一个面向 AI 剧本杀场景的交互式生成与游玩系统。系统支持用户输入普通案件文本、上传文档，或调用大模型随机生成案件文本，并自动转换为可玩的剧本杀内容。玩家创建房间后，可以选择一个真人角色，其余角色由 AI 自动补位。游戏过程中，AI 主持人负责控场、阶段推进、线索解锁和最终复盘；AI 角色则根据自己的身份信息、私密记忆、已解锁线索和聊天历史参与讨论。

本系统的核心目标不是简单的 AI 聊天，而是构建一个具备“剧本生成、角色权限、阶段控制、线索解锁、历史上下文记忆、AI 推理与主持人复盘”的 AI 剧本杀平台。

---

## 2. 系统功能概览

系统目前主要包括以下功能：

1. AI 随机生成案件文本
2. 普通文本自动改写为剧本杀
3. 固定格式剧本直接编译
4. 剧本杀房间创建
5. 真人玩家选择角色
6. AI 自动补位
7. AI 角色自我介绍
8. 阶段推进与线索解锁
9. 玩家与主持人、角色互动
10. AI 读取聊天历史进行回应
11. 线索板、人物说法、关系链展示
12. 全员提交最终推理
13. 主持人统一复盘评分
14. 本局结束与重新开局

系统整体流程如下：

```text
案件文本 / AI 随机文本
↓
自动生成固定格式剧本杀
↓
编译为结构化剧本
↓
创建游戏房间
↓
真人玩家选择角色
↓
AI 自动补位
↓
阶段推进与线索解锁
↓
玩家盘问角色
↓
全员提交最终推理
↓
主持人复盘评分
↓
结束本局
```

---

## 3. 项目目录结构

项目主目录示例：

```bash
/root/siton-data-guanchunxiangData/fuleihao/script2game_v3_ui
```

核心目录结构如下：

```text
script2game_v3_ui/
├── app.py
├── README.md
├── requirements.txt
├── backend/
│   ├── __init__.py
│   ├── agents.py
│   ├── document2script.py
│   ├── document_loader.py
│   ├── evidence_board.py
│   ├── game_state.py
│   ├── host_review.py
│   ├── judge.py
│   ├── knowledge_manager.py
│   ├── llm_client.py
│   ├── random_text_generator.py
│   ├── retriever.py
│   ├── script_parser.py
│   ├── spoiler_controller.py
│   └── ui_components.py
├── data/
│   ├── scripts/
│   └── compiled/
└── assets/
```

各文件作用如下：

| 文件                                 | 作用                         |
| ---------------------------------- | -------------------------- |
| `app.py`                           | Streamlit 前端主程序            |
| `backend/agents.py`                | 主持人 Agent、角色 Agent、AI 最终推理 |
| `backend/document2script.py`       | 普通文本转固定格式剧本                |
| `backend/document_loader.py`       | 读取 txt、docx、pdf 文档         |
| `backend/evidence_board.py`        | 线索板、时间线、人物说法、关系链           |
| `backend/game_state.py`            | 房间状态、阶段推进、聊天记录             |
| `backend/host_review.py`           | 主持人最终复盘评分                  |
| `backend/knowledge_manager.py`     | 构造角色可见知识                   |
| `backend/llm_client.py`            | 大模型接口调用                    |
| `backend/random_text_generator.py` | AI 随机案件文本生成                |
| `backend/retriever.py`             | 简易 RAG 检索器                 |
| `backend/script_parser.py`         | 固定格式剧本解析                   |
| `backend/spoiler_controller.py`    | 剧透控制                       |
| `backend/ui_components.py`         | 页面样式与卡片组件                  |

---

## 4. 环境配置

### 4.1 Python 环境

推荐使用 Python 3.9 及以上版本。

创建 conda 环境：

```bash
conda create -n script2game python=3.9 -y
conda activate script2game
```

进入项目目录：

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/script2game_v3_ui
```

安装依赖：

```bash
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

`requirements.txt` 推荐内容如下：

```text
streamlit==1.39.0
pandas==2.0.3
requests==2.32.3
python-docx==1.1.2
pypdf==4.3.1
```

---

## 5. 大模型配置

系统支持 OpenAI-compatible 格式的大模型接口，因此可以接入：

* 本地 Qwen3
* DeepSeek
* OpenAI
* 其他兼容 `/v1/chat/completions` 的模型服务

### 5.1 使用本地 Qwen3

本地 Qwen3 接口示例地址：

```text
http://127.0.0.1:8001/v1/chat/completions
```

前端左侧模型设置填写：

```text
Provider：openai
模型名：Qwen3-8B
接口地址：http://127.0.0.1:8001/v1/chat/completions
API Key：可留空
max_tokens：4096
temperature：0.20
```

启动本地 Qwen3 API 服务示例：

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/rag_ie_system_full

conda activate /root/siton-data-guanchunxiangData/Miniconda3/envs/qwen3_tf

nohup uvicorn qwen3_api_server:app \
  --host 127.0.0.1 \
  --port 8001 \
  > qwen3_api.log 2>&1 &
```

检查服务是否正常：

```bash
curl http://127.0.0.1:8001/v1/models
```

---

### 5.2 使用 DeepSeek API

前端左侧模型设置填写：

```text
Provider：openai
模型名：deepseek-chat
接口地址：https://api.deepseek.com/chat/completions
API Key：填写你的 DeepSeek API Key
max_tokens：4096
temperature：0.20
```

API Key 可以直接填在前端，也可以配置到服务器环境变量中。

配置环境变量：

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

永久保存：

```bash
echo 'export DEEPSEEK_API_KEY="你的 DeepSeek API Key"' >> ~/.bashrc
source ~/.bashrc
```

前端填写 API Key 的方式适合本地测试和内测；正式部署时建议使用服务器环境变量，避免 API Key 暴露。

---

## 6. 启动系统

进入项目目录：

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/script2game_v3_ui
```

启动 Streamlit：

```bash
streamlit run app.py --server.fileWatcherType none
```

外部访问启动方式：

```bash
streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.fileWatcherType none
```

后台运行方式：

```bash
nohup streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.fileWatcherType none \
  > script2game.log 2>&1 &
```

访问地址示例：

```text
http://服务器IP:8501
```

---

## 7. 页面使用说明

### 7.1 剧本大厅

剧本大厅用于生成或导入剧本。

当前支持三种输入模式：

```text
AI随机生成文本
普通文本自动生成剧本杀
固定格式剧本直接编译
```

---

### 7.2 AI 随机生成文本

该功能用于让系统从零生成一段普通案件材料。

用户可以设置：

* 题材类型
* 推理难度
* 推理风格
* 额外要求
* 生成角色数量

示例额外要求：

```text
发生在研究生实验室，和论文、项目、代码有关。
```

点击：

```text
生成随机案件文本
```

系统会生成一段普通案件材料。用户确认后，再点击：

```text
生成 / 编译剧本
```

系统会将普通案件文本改写为可玩的固定格式剧本杀。

---

### 7.3 普通文本自动生成剧本杀

用户可以直接粘贴普通案件文本，例如：

```text
星河学院数字媒体实验室正在准备一次校级创新项目展示。展示当天上午，原本应该播放的宣传短片突然变成了旧版本……
```

点击：

```text
生成 / 编译剧本
```

系统会调用大模型生成固定格式剧本。

---

### 7.4 固定格式剧本直接编译

如果用户已经有符合系统格式的剧本，可以直接粘贴固定格式内容：

```text
【剧本标题】
午夜打印记录

【故事背景】
……

【角色列表】
许川
沈宁
陆遥

【角色：许川】
公开信息：
……
私密信息：
……
目标：
……
不能主动透露的信息：
……

【第一幕线索】
1. ……
2. ……

【第二幕线索】
1. ……
2. ……

【第三幕线索】
1. ……
2. ……

【最终真相】
……

【评分标准】
指出真正关键人物：40分
说明关键动机：20分
解释误导人物或排除错误嫌疑：20分
引用关键证据支撑推理：20分
```

点击：

```text
生成 / 编译剧本
```

系统会直接解析剧本并进入可创建房间状态。

---

## 8. 创建房间

剧本生成成功后，进入“创建房间”页面。

用户需要：

1. 选择自己扮演的角色。
2. 设置是否允许 AI 补位。
3. 点击创建房间。

创建成功后，系统会生成：

* 房间 ID
* 当前剧本
* 真人玩家角色
* AI 补位角色
* 初始阶段
* 聊天记录

---

## 9. 游戏房间

游戏房间是主要游玩区域。

主要包含：

* 房间状态
* 当前阶段
* 阶段进度条
* 玩家发言区
* 聊天记录
* 阶段控制
* 当前线索
* 角色状态
* 最终推理与主持人复盘
* 本局结束操作

---

### 9.1 发言方式

系统支持三种发言方式：

```text
全体公开发言
询问主持人
询问角色
```

#### 全体公开发言

玩家向所有角色公开发言。AI 会根据玩家最新发言进行回应。

例如玩家说：

```text
我是许川，你们好。
```

AI 应自然回应打招呼，而不是突然进入案件分析。

#### 询问主持人

玩家向主持人提问。主持人会基于当前阶段、已解锁线索和聊天历史进行回答。

#### 询问角色

玩家选择某个角色进行提问。该角色会基于自己的角色信息、私密信息、已解锁线索和聊天历史回答。

---

### 9.2 AI 自我介绍

开局后点击：

```text
AI角色自我介绍
```

系统会自动进入开场介绍阶段，并让 AI 角色依次进行自我介绍。

---

### 9.3 阶段推进

点击：

```text
进入下一阶段
```

系统会自动完成：

1. 推进阶段。
2. 主持人宣布当前阶段。
3. 解锁对应线索。
4. AI 角色根据阶段主动发言。

阶段顺序如下：

```text
准备阶段
↓
开场介绍
↓
第一幕线索
↓
第二幕线索
↓
第三幕线索
↓
最终推理
↓
复盘结算
```

---

### 9.4 当前线索

当前线索区域展示已解锁的证据卡片。

示例：

```text
证据卡 #01
门禁记录显示，许川 22:10 进入打印室，22:14 离开。

证据卡 #02
门禁记录显示，陆遥 22:18 进入打印室，22:27 离开。
```

线索会随着阶段推进逐步公开。

---

### 9.5 角色状态

角色状态区域展示当前房间中的所有角色，包括：

* 真人玩家
* AI 补位
* 角色目标
* 当前状态

---

## 10. 线索板

线索板用于辅助玩家推理。

包括：

### 10.1 已解锁证据

展示当前已公开的所有线索。

### 10.2 时间线

系统会从线索和聊天记录中提取时间点，形成时间线。

示例：

```text
22:10：许川进入打印室。
22:18：陆遥进入打印室。
22:27：陆遥离开打印室。
```

### 10.3 人物说法

系统会整理聊天记录中的人物发言，形成证词卡片。

### 10.4 关系链

系统会基于角色、线索和聊天内容生成简单关系链。

示例：

```text
许川 —— 相关 —— 沈宁
陆遥 —— 发表说法 —— 我昨晚确实去过打印室
```

---

## 11. 最终推理与主持人复盘

进入最终推理阶段后，玩家需要填写自己的最终推理。

最终推理应包括：

1. 关键人物是谁。
2. 动机是什么。
3. 证据链是什么。
4. 如何排除其他可疑人物。

点击：

```text
提交最终推理，开始全员复盘
```

系统会自动执行：

1. 保存真人玩家最终答案。
2. AI 角色提交各自的最终推理。
3. 主持人读取最终真相、评分标准、已解锁线索、聊天历史和所有角色答案。
4. 主持人分别给真人玩家和 AI 角色评分。
5. 主持人揭示完整真相。
6. 系统进入复盘结算阶段。

---

## 12. 本局结束

主持人完成复盘后，系统会显示：

```text
本局已结束
主持人已经完成最终复盘，本局剧本杀已结束。
```

此时可以选择：

```text
结束本局，返回创建房间
保留剧本，重新开一局
```

含义如下：

* **结束本局，返回创建房间**：清空当前房间，保留当前剧本，返回创建房间页面。
* **保留剧本，重新开一局**：清空当前房间，保留剧本，重新创建新房间。

---

## 13. 系统中的 RAG 思路

当前系统属于轻量级 RAG 原型。AI 角色回答时，并不是完全凭空生成，而是会基于角色可见信息检索相关上下文。

角色回答流程：

```text
玩家发言
↓
判断发言对象
↓
构造角色可见资料
↓
加入已解锁线索
↓
加入最近聊天历史
↓
检索相关上下文
↓
拼接 Prompt
↓
调用大模型
↓
生成回答
```

不同身份可见内容不同：

```text
真人玩家：自己看到的公开内容和线索
AI 角色：自己的公开信息、私密信息、目标、已解锁线索、聊天历史
主持人：剧本背景、角色信息、已解锁线索、聊天历史
复盘主持人：最终真相、评分标准、全部线索、所有最终答案
```

这体现了系统的核心设计：

```text
角色权限控制 + 动态线索解锁 + 历史上下文检索 + Agent 生成
```

后续可以升级为正式 RAG：

```text
Embedding
向量数据库
Chroma / FAISS
metadata 权限过滤
证据引用
相似度召回
```

---

## 14. 剧透控制

系统包含基础剧透控制逻辑。

如果玩家在早期直接询问：

```text
凶手是谁？
最终真相是什么？
谁干的？
直接告诉我答案。
```

系统会阻止主持人或角色直接透露答案。

AI 角色也会遵守：

* 不读取最终真相。
* 不主动自爆。
* 不提前揭示关键结论。
* 只基于当前可见信息回答。

---

## 15. 常见问题与解决方法

### 15.1 页面启动失败

先检查语法：

```bash
python -m py_compile app.py
```

如果提示缩进错误，通常是修改 `app.py` 时破坏了 `if / elif / else / with` 结构。

可以查看备份：

```bash
ls app.py.bak*
```

恢复备份：

```bash
cp app.py.bak_xxx app.py
```

再次检查：

```bash
python -m py_compile app.py
```

---

### 15.2 大模型没有回复

检查左侧模型设置：

```text
Provider 是否为 openai
模型名是否正确
接口地址是否正确
API Key 是否填写
```

本地 Qwen3 检查：

```bash
curl http://127.0.0.1:8001/v1/models
```

DeepSeek 检查：

```text
接口地址：https://api.deepseek.com/chat/completions
API Key：必须填写或配置环境变量
```

---

### 15.3 AI 不看历史消息

检查 `backend/agents.py` 中是否包含：

```python
format_recent_history(room, limit=...)
```

并确认角色回答 Prompt 中包含：

```text
【最近聊天历史】
```

同时检查 `backend/knowledge_manager.py` 是否将聊天记录加入检索资料。

---

### 15.4 AI 打招呼时突然讲案件细节

检查 `RoleAgent.react_to_player()` 和 `is_simple_greeting()` 是否存在。

玩家说：

```text
我是许川，你们好。
```

AI 应该自然回应，而不是直接讲案件细节。

---

### 15.5 复盘后还能继续让 AI 发言

应确保复盘完成后设置：

```python
room["game_over"] = True
```

按钮逻辑中应判断：

```python
if room.get("game_over", False):
    st.warning("本局已经结束，AI角色不会继续发言。")
```

---

### 15.6 按钮点击没反应

常见原因：

1. Streamlit 按钮 key 重复。
2. 按钮 key 每次刷新都变化。
3. 状态写入后没有 `st.rerun()`。
4. 页面上存在旧按钮残留。

可以搜索按钮位置：

```bash
grep -n "保留剧本" app.py
grep -n "结束本局" app.py
```

---

## 16. 推荐演示流程

### 第一步：启动模型

使用本地 Qwen3 或 DeepSeek。

### 第二步：启动系统

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/script2game_v3_ui

streamlit run app.py --server.fileWatcherType none
```

### 第三步：配置模型

左侧填写模型配置，并测试连接。

### 第四步：生成剧本

进入剧本大厅：

```text
输入类型：AI随机生成文本
题材：校园 / 实验室
难度：普通
风格：证据链推理
```

点击生成随机案件文本，再点击生成 / 编译剧本。

### 第五步：创建房间

选择真人玩家角色，允许 AI 补位，创建房间。

### 第六步：开场介绍

点击 AI 角色自我介绍，进入游戏房间。

### 第七步：盘问角色

通过公开发言、询问主持人、询问角色推进讨论。

### 第八步：推进阶段

点击进入下一阶段，逐步解锁线索。

### 第九步：最终推理

玩家提交最终推理，AI 角色也自动提交答案。

### 第十步：主持人复盘

主持人统一评分并揭示完整真相。

### 第十一步：结束本局

点击结束本局或保留剧本重新开局。

---

## 17. 项目亮点

本系统的主要亮点包括：

1. **AI 随机案件生成**
   用户可以通过题材、难度、风格控制生成案件文本。

2. **非结构化文本自动剧本化**
   普通案件文本可以自动转换为固定格式剧本杀。

3. **AI 多角色补位**
   单人也能体验多人剧本杀流程。

4. **角色权限控制**
   每个 AI 角色只知道自己该知道的内容。

5. **阶段式线索解锁**
   线索随着阶段推进逐步公开，避免开局剧透。

6. **历史上下文记忆**
   AI 回答会参考最近聊天记录，不再像失忆 NPC。

7. **轻量级 RAG 检索**
   根据角色权限构造可见知识，并检索相关上下文。

8. **全员最终推理**
   不仅真人玩家提交答案，AI 角色也会提交自己的推理。

9. **主持人统一复盘评分**
   主持人对真人和 AI 角色分别评分，并揭示完整真相。

10. **游戏化界面**
    包含角色卡、线索卡、证词卡、关系链、阶段条等视觉组件。

---

## 18. 一键运行命令参考

### 18.1 启动本地 Qwen3 API

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/rag_ie_system_full

conda activate /root/siton-data-guanchunxiangData/Miniconda3/envs/qwen3_tf

nohup uvicorn qwen3_api_server:app \
  --host 127.0.0.1 \
  --port 8001 \
  > qwen3_api.log 2>&1 &
```

### 18.2 启动 Script2Game

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/script2game_v3_ui

conda activate script2game

streamlit run app.py --server.fileWatcherType none
```

### 18.3 后台运行

```bash
cd /root/siton-data-guanchunxiangData/fuleihao/script2game_v3_ui

nohup streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.fileWatcherType none \
  > script2game.log 2>&1 &
```

---

## 19. 总结

Script2Game 当前已经形成一个完整的 AI 剧本杀系统闭环：

```text
AI 生成案件文本
↓
案件文本转剧本杀
↓
创建房间
↓
AI 角色补位
↓
玩家盘问
↓
阶段推进
↓
线索解锁
↓
全员最终推理
↓
主持人复盘评分
↓
结束本局
```

该系统可以作为课程设计、项目展示、AI 应用 Demo 或后续产品原型继续扩展。后续重点可以放在正式 RAG 检索、多用户房间、数据库持久化和更稳定的游戏流程控制上。
::: 
