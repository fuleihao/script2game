import json
import re


def _is_empty_or_placeholder(answer):
    answer = (answer or "").strip()
    if len(answer) < 20:
        return True
    bad_patterns = ["……", "...", "某人", "不知道", "不清楚", "证据包括……", "因为……", "关键人物是……"]
    if any(p in answer for p in bad_patterns):
        concrete_chars = re.sub(r"[.。…，,、\s]", "", answer)
        if len(concrete_chars) < 45:
            return True
    return False


def _extract_json(text):
    if not text:
        return None
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.I).strip()
    text = text.replace("```json", "").replace("```", "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    raw = text[start:end + 1]
    try:
        return json.loads(raw)
    except Exception:
        try:
            from json_repair import repair_json
            return json.loads(repair_json(raw))
        except Exception:
            return None


class JudgeAgent:
    def __init__(self, script, room, llm=None):
        self.script = script
        self.room = room
        self.llm = llm

    def judge(self, answer):
        answer = (answer or "").strip()
        if _is_empty_or_placeholder(answer):
            return self._format({
                "method": "规则预检",
                "total_score": 0,
                "hit_items": [],
                "miss_items": [{"item": "玩家答案不完整", "reason": "答案中存在省略号、占位符或缺少具体人物/证据。", "score": 0}],
                "comment": "请写出明确的关键人物、动机、证据和排除理由后再提交。"
            })
        if self.llm:
            data = self._llm_judge(answer)
            if data:
                return self._format(data)
        return self._format(self._rule_judge(answer))

    def _llm_judge(self, answer):
        evidence = []
        for stage in self.script.get("stages", []):
            evidence.extend(stage.get("evidence", []))
        prompt = f"""
你是严格剧本杀裁判。只能根据【玩家答案】中明确写出的内容给分，不能用最终真相替玩家补全答案。

【最终真相】
{self.script.get('truth', '')}

【评分标准】
{self.script.get('scoring', '')}

【可用证据】
{chr(10).join(['- ' + x for x in evidence])}

【玩家答案】
{answer}

输出严格 JSON：
{{
  "method": "大模型严格裁判",
  "total_score": 0,
  "hit_items": [
    {{"item": "评分项", "reason": "为什么命中", "score": 0}}
  ],
  "miss_items": [
    {{"item": "评分项", "reason": "为什么未命中", "score": 0}}
  ],
  "comment": "简短复盘"
}}
"""
        data = _extract_json(self.llm.generate(prompt))
        if not data:
            return None
        try:
            data["total_score"] = max(0, min(100, int(data.get("total_score", 0))))
        except Exception:
            data["total_score"] = 0
        data.setdefault("method", "大模型严格裁判")
        data.setdefault("hit_items", [])
        data.setdefault("miss_items", [])
        data.setdefault("comment", "")
        return data

    def _rule_judge(self, answer):
        roles = [r.get("name", "") for r in self.script.get("roles", []) if r.get("name")]
        truth_roles = [r for r in roles if r in self.script.get("truth", "")]
        answer_roles = [r for r in roles if r in answer]
        hit_items, miss_items, total = [], [], 0

        if any(r in answer_roles for r in truth_roles):
            total += 40
            hit_items.append({"item": "指出真正关键人物", "reason": "答案中出现了真相相关角色。", "score": 40})
        else:
            miss_items.append({"item": "指出真正关键人物", "reason": "没有明确写出正确关键人物。", "score": 0})

        motive_words = ["不满", "动机", "贡献", "突出", "替换", "利益", "报复", "展示"]
        if any(w in answer for w in motive_words):
            total += 20
            hit_items.append({"item": "说明关键动机", "reason": "答案中包含动机相关表述。", "score": 20})
        else:
            miss_items.append({"item": "说明关键动机", "reason": "没有说明清楚动机。", "score": 0})

        if len(answer_roles) >= 2:
            total += 20
            hit_items.append({"item": "解释误导人物或排除错误嫌疑", "reason": "答案中提到了多个角色，有排除嫌疑基础。", "score": 20})
        else:
            miss_items.append({"item": "解释误导人物或排除错误嫌疑", "reason": "没有解释其他角色为什么不是关键人物。", "score": 0})

        ev_keywords = ["门禁", "记录", "修改", "打开", "文件", "监控", "聊天", "时间", "证据", "指纹", "旧报告"]
        hits = [w for w in ev_keywords if w in answer]
        if len(hits) >= 2:
            total += 20
            hit_items.append({"item": "引用关键证据支撑推理", "reason": "引用证据关键词：{}".format("、".join(hits)), "score": 20})
        else:
            miss_items.append({"item": "引用关键证据支撑推理", "reason": "证据引用不足。", "score": 0})

        return {"method": "规则兜底裁判", "total_score": total, "hit_items": hit_items, "miss_items": miss_items, "comment": "当前为规则兜底评分。"}

    def _format(self, result):
        lines = ["评测方式：{}".format(result.get("method", "未知")), "", "总分：{}分".format(result.get("total_score", 0)), "", "---", "", "## 命中项："]
        if result.get("hit_items"):
            for x in result.get("hit_items", []):
                lines.append("- {}：✅ {}分".format(x.get("item", ""), x.get("score", 0)))
                if x.get("reason"):
                    lines.append("  - {}".format(x["reason"]))
        else:
            lines.append("- 无")
        lines += ["", "---", "", "## 错误项 / 未命中项："]
        if result.get("miss_items"):
            for x in result.get("miss_items", []):
                lines.append("- {}：❌ 0分".format(x.get("item", "")))
                if x.get("reason"):
                    lines.append("  - {}".format(x["reason"]))
        else:
            lines.append("- 无")
        if result.get("comment"):
            lines += ["", "---", "", "## 复盘：", result.get("comment", "")]
        return "\n".join(lines)
