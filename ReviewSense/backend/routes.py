import sqlite3
from flask import Blueprint, jsonify, request
from ml import predict
from .analysis import run, run_batch
from .database import conn

api = Blueprint("api", __name__, url_prefix="/api")
err = lambda m, c=400: (jsonify(error=m), c)

@api.errorhandler(sqlite3.Error)
def db_error(e):
    return err("Database error. Please try again.", 500)

@api.get("/health")
def health():
    return jsonify(status="ok")

@api.post("/analyze")
def analyze():
    d = request.get_json(silent=True)
    if not isinstance(d, dict): return err("Invalid JSON body.")
    text = d.get("text")
    if not isinstance(text, str) or len(text.strip()) < 3: return err("Please enter a review to analyze.")
    if len(text) > 10000: return err("Text is too long (max 10,000 characters).")
    text = text.strip()
    res = run(text)
    if d.get("save") is True:
        with conn() as c:
            res["id"] = c.execute("INSERT INTO analyses(text,label,confidence,score,word_count) VALUES(?,?,?,?,?)",
                                  (text, res["label"], res["confidence"], res["score"], res["stats"]["words"])).lastrowid
    return jsonify(res)

@api.post("/analyze-batch")
def batch():
    d = request.get_json(silent=True)
    text = d.get("text") if isinstance(d, dict) else None
    if not isinstance(text, str): return err("Invalid request.")
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) >= 3]
    if not lines: return err("Enter at least one review (one per line).")
    if len(lines) > 100: return err("Please analyze at most 100 reviews at a time.")
    if any(len(l) > 5000 for l in lines): return err("A review is too long (max 5,000 characters).")
    return jsonify(run_batch(lines))

@api.get("/history")
def history():
    with conn() as c:
        rows = c.execute("SELECT * FROM analyses ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@api.get("/history/<int:aid>")
def one(aid):
    with conn() as c:
        r = c.execute("SELECT * FROM analyses WHERE id=?", (aid,)).fetchone()
    if not r: return err("Analysis not found.", 404)
    d = dict(r); d["result"] = run(d["text"])
    return jsonify(d)

@api.delete("/history/<int:aid>")
def delete(aid):
    with conn() as c:
        n = c.execute("DELETE FROM analyses WHERE id=?", (aid,)).rowcount
    return jsonify(deleted=n) if n else err("Analysis not found.", 404)

@api.delete("/history")
def clear():
    with conn() as c:
        c.execute("DELETE FROM analyses")
    return jsonify(deleted="all")

@api.get("/analytics")
def analytics():
    with conn() as c:
        by = {r[0]: r[1] for r in c.execute("SELECT label, COUNT(*) FROM analyses GROUP BY label")}
        tot = c.execute("SELECT COUNT(*), COALESCE(ROUND(AVG(score),2),0), COALESCE(SUM(word_count),0) FROM analyses").fetchone()
        days = [dict(r) for r in c.execute("SELECT date(created_at) AS day, COUNT(*) AS n FROM analyses WHERE created_at >= date('now','-6 days') GROUP BY day ORDER BY day")]
    top = max(by, key=by.get) if by else None
    return jsonify(total=tot[0], avg_score=tot[1], total_words=tot[2], top_sentiment=top, by_label=by, per_day=days, model=predict.metrics())
