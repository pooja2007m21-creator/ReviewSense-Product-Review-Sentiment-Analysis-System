import re
from ml import predict

# Rule-based topic lexicon; the sentiment of each topic comes from the ML model applied to the clauses mentioning it.
ASPECTS = {"battery": ["battery", "charge", "charging"], "price & value": ["price", "cost", "value", "expensive", "cheap", "worth", "money"],
           "quality": ["quality", "build", "material", "durable", "sturdy", "broke", "broken"], "delivery": ["delivery", "shipping", "arrived", "courier", "late"],
           "customer service": ["service", "support", "refund", "return", "seller"], "design": ["design", "look", "looks", "color", "size", "weight"],
           "performance": ["performance", "speed", "fast", "slow", "lag", "works", "working"], "sound & display": ["sound", "audio", "screen", "display", "camera", "picture"],
           "packaging": ["packaging", "package", "box"]}
CLAUSE = re.compile(r"(?<=[.!?])\s+|\n+|\s*[;,]?\s+\b(?:but|however|although|though|yet)\b\s*", re.I)

def clauses(text):
    return [c.strip() for c in CLAUSE.split(text) if c and len(c.strip()) > 2]

def word_label(score):
    return "positive" if score >= 0.2 else "negative" if score <= -0.2 else "neutral"

def aspects_of(text):
    """{aspect: [scores of clauses mentioning it]}"""
    out = {}
    for c in clauses(text):
        words = set(re.findall(r"[a-z]+", c.lower()))
        hit = [a for a, ws in ASPECTS.items() if words & set(ws)]
        if hit:
            sc = predict.classify(c, False)["score"]
            for a in hit:
                out.setdefault(a, []).append(sc)
    return out

def aspect_list(d):
    rows = [{"aspect": a, "mentions": len(v), "score": round(sum(v) / len(v), 2), "label": word_label(sum(v) / len(v))} for a, v in d.items()]
    return sorted(rows, key=lambda r: -r["mentions"])

def stats(text):
    words = re.findall(r"\S+", text)
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    return {"words": len(words), "characters": len(text), "sentences": len(sents),
            "avg_words_per_sentence": round(len(words) / len(sents), 1) if sents else 0,
            "exclamation_marks": text.count("!"), "question_marks": text.count("?")}

def insight(res, asp):
    pr = [a["aspect"] for a in asp if a["label"] == "positive"]; ng = [a["aspect"] for a in asp if a["label"] == "negative"]
    s = f"This review is mostly {res['label']}."
    if pr: s += " Praised: " + ", ".join(pr) + "."
    if ng: s += " Criticised: " + ", ".join(ng) + "."
    if pr and ng: s += " It is mixed: it contains both praise and complaints."
    return s

def run(text):
    res = predict.classify(text)
    res["stats"] = stats(text)
    res["low_confidence"] = res["confidence"] < 50
    res["estimated_stars"] = max(1, min(5, round(3 + 2 * res["score"])))
    cl = clauses(text)
    res["clauses"] = [dict(text=c, **{k: v for k, v in predict.classify(c, False).items() if k in ("label", "score")}) for c in cl[:30]] if len(cl) > 1 else []
    res["aspects"] = aspect_list(aspects_of(text))
    res["insight"] = insight(res, res["aspects"])
    return res

def run_batch(texts):
    items, counts, agg = [], {"positive": 0, "negative": 0, "neutral": 0}, {}
    for t in texts:
        r = predict.classify(t, False)
        counts[r["label"]] = counts.get(r["label"], 0) + 1
        items.append({"text": t[:200], "label": r["label"], "score": r["score"], "confidence": r["confidence"]})
        for a, v in aspects_of(t).items():
            agg.setdefault(a, []).extend(v)
    n = len(items)
    asp = aspect_list(agg)
    return {"total": n, "counts": counts, "avg_score": round(sum(i["score"] for i in items) / n, 2), "aspects": asp, "reviews": items,
            "insight": ("Praised most: " + ", ".join(a["aspect"] for a in asp if a["label"] == "positive")[:200] + ". " if any(a["label"] == "positive" for a in asp) else "")
                       + ("Criticised most: " + ", ".join(a["aspect"] for a in asp if a["label"] == "negative")[:200] + "." if any(a["label"] == "negative" for a in asp) else "")}
