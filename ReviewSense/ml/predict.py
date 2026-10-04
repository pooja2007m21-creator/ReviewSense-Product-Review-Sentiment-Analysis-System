import json, os
import joblib
from .preprocess import tokens
from .train import MODEL, METRICS, train

_pipe = None

def load():
    global _pipe
    if _pipe is None:
        if not os.path.exists(MODEL):
            train()
        _pipe = joblib.load(MODEL)
    return _pipe

def metrics():
    load()
    with open(METRICS) as f:
        return json.load(f)

def classify(text, with_keywords=True):
    """Returns label, confidence, probabilities, sentiment score (P(positive) - P(negative), range -1..1) and keywords."""
    pipe = load()
    proba = pipe.predict_proba([text])[0]
    classes = list(pipe.classes_)
    P = {c: float(p) for c, p in zip(classes, proba)}
    i = int(proba.argmax())
    res = {"label": classes[i], "confidence": round(float(proba[i]) * 100, 1),
           "probabilities": {c: round(p * 100, 1) for c, p in P.items()},
           "score": round(P.get("positive", 0) - P.get("negative", 0), 2), "keywords": {"positive": [], "negative": []}}
    if with_keywords:
        vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
        X = vec.transform([text]).tocoo()
        names = vec.get_feature_names_out()
        disp = dict(tokens(text))
        for cls in ("positive", "negative"):
            if cls in classes:
                k = classes.index(cls)
                sc = sorted(((float(v * clf.coef_[k][j]), disp.get(names[j], names[j])) for j, v in zip(X.col, X.data)), reverse=True)
                res["keywords"][cls] = [w for s, w in sc[:6] if s > 0]
    return res
