"""Generates the small SYNTHETIC demo dataset ml/data/seed_reviews.csv (template-based, first-run only).
Replace it with real reviews: save as ml/data/reviews.csv (text,label or text,rating) and run: python -m ml.train"""
import csv, os, random
R = random.Random(5); P = R.choice
PROD = ["phone", "laptop", "headphones", "blender", "backpack", "vacuum cleaner", "smartwatch", "camera"]
ASP = ["battery life", "build quality", "price", "delivery", "customer service", "design", "sound quality", "packaging", "performance", "screen"]
POS = ["excellent", "fantastic", "amazing", "superb", "impressive", "great", "perfect", "outstanding", "wonderful", "reliable"]
NEG = ["terrible", "awful", "disappointing", "poor", "horrible", "useless", "cheap", "unreliable", "dreadful", "faulty"]
NEU = ["average", "okay", "mediocre", "ordinary", "standard", "so-so", "acceptable", "typical"]
DAY = ["Monday", "Tuesday", "Friday", "Saturday"]
def f(t, **k): return t.format(p=P(PROD), a=P(ASP), d=P(DAY), n=R.randint(2, 9), **k)
def pos(): return f(P(["The {a} is {j}.", "I love this {p}, the {a} is {j}!", "Highly recommend this {p}, {j} {a}.", "Best {p} I have bought, {j} {a}.", "Five stars! The {a} is {j} and the {p} arrived quickly.", "Very happy with the {p}, works perfectly."]), j=P(POS))
def neg(): return f(P(["The {a} is {j}.", "Do not buy this {p}, the {a} is {j}.", "I regret buying this {p}, {j} {a}.", "One star. The {a} is {j} and the {p} stopped working.", "Very disappointed with the {p}, total waste of money.", "The {p} broke after {n} days, {j} {a}."]), j=P(NEG))
def neu(): return f(P(["The {p} arrived on {d}.", "The {a} is {j}, nothing special.", "It is an {j} {p} for the price.", "The {p} does what it says, no more, no less.", "I used the {p} for {n} weeks. The {a} is {j}."]), j=P(NEU))
def neg_t(): return f(P(["The {a} is not {j}.", "The {p} is not {j} at all.", "I don't think the {a} is {j}."]), j=P(POS)), "negative"
def pos_t(): return f(P(["The {a} is not {j}.", "The {p} is not {j} at all."]), j=P(["terrible", "bad", "poor", "awful"])), "positive"
rows = set()
for lab, fn in (("positive", pos), ("negative", neg), ("neutral", neu)):
    while sum(r[1] == lab for r in rows) < 220: rows.add((fn(), lab))
rows |= {neg_t() for _ in range(40)} | {pos_t() for _ in range(25)}
rows = sorted(rows); R.shuffle(rows)
with open(os.path.join(os.path.dirname(__file__), "data", "seed_reviews.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["text", "label"]); w.writerows(rows)
