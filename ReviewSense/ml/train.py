"""Train the sentiment classifier.  Usage: python -m ml.train [path/to/reviews.csv]
CSV columns: text,label (positive|negative|neutral) OR text,rating (1-2 negative, 3 neutral, 4-5 positive)."""
import csv, json, os, sys
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from .preprocess import analyzer

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL, METRICS = os.path.join(HERE, "model.joblib"), os.path.join(HERE, "metrics.json")
USER_DATA, SEED_DATA = os.path.join(HERE, "data", "reviews.csv"), os.path.join(HERE, "data", "seed_reviews.csv")
ALIAS = {"pos": "positive", "neg": "negative", "neu": "neutral"}
LABELS = {"positive", "negative", "neutral"}

def _label(r):
    lab = (r.get("label") or "").strip().lower()
    if lab:
        return ALIAS.get(lab, lab)
    try:
        v = float(r.get("rating"))
    except (TypeError, ValueError):
        return ""
    return "negative" if v <= 2 else "neutral" if v < 4 else "positive"

def train(path=None):
    path = path or (USER_DATA if os.path.exists(USER_DATA) else SEED_DATA)
    X, y = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lab = _label(r)
            if lab in LABELS and (r.get("text") or "").strip():
                X.append(r["text"]); y.append(lab)
    if len(set(y)) < 2 or len(y) < 60:
        raise ValueError("Need at least 60 labeled rows and 2 classes (columns: text,label or text,rating).")
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    pipe = Pipeline([("tfidf", TfidfVectorizer(analyzer=analyzer, sublinear_tf=True, min_df=1)),
                     ("clf", LogisticRegression(max_iter=3000, class_weight="balanced", C=5))])
    pipe.fit(Xtr, ytr)
    rep = classification_report(yte, pipe.predict(Xte), output_dict=True, zero_division=0)
    metrics = {"dataset": os.path.basename(path), "train_size": len(Xtr), "test_size": len(Xte),
               "accuracy": round(rep["accuracy"], 4), "labels": list(pipe.classes_),
               "per_class_f1": {k: round(rep[k]["f1-score"], 3) for k in pipe.classes_}}
    joblib.dump(pipe, MODEL)
    with open(METRICS, "w") as f:
        json.dump(metrics, f)
    return metrics

if __name__ == "__main__":
    print(json.dumps(train(sys.argv[1] if len(sys.argv) > 1 else None), indent=2))
