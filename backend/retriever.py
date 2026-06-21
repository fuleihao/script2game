import re
import math


def tokenize(text):
    text = text or ""
    chinese = re.findall(r"[\u4e00-\u9fff]", text)
    words = re.findall(r"[A-Za-z0-9_./:：]+", text.lower())
    bigrams = [chinese[i] + chinese[i + 1] for i in range(len(chinese) - 1)]
    return chinese + bigrams + words


def score(query, doc):
    q, d = set(tokenize(query)), set(tokenize(doc))
    if not q or not d:
        return 0.0
    return len(q & d) / math.sqrt(len(q) * len(d))


def simple_search(query, docs, top_k=6):
    arr = []
    for d in docs:
        s = score(query, d.get("text", ""))
        if s > 0:
            x = dict(d)
            x["score"] = s
            arr.append(x)
    arr.sort(key=lambda x: x["score"], reverse=True)
    return arr[:top_k]
