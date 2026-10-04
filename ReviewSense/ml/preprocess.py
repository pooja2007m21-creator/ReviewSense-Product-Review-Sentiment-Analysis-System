"""Text cleaning: lowercase, tokenize, mark negation ("not happy" -> "not_happy"), remove stop words (keeping negators)."""
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

NEG = {"not", "no", "never", "wont", "dont", "isnt", "wasnt", "arent", "didnt", "doesnt", "hardly"}
STOP = set(ENGLISH_STOP_WORDS) - NEG - {"very", "so", "too", "but", "nothing", "more", "less"}

def tokens(text):
    """Return [(token, display_word)]; negated words get a 'not_' prefix."""
    t = text.lower().replace("’", "'").replace("can't", "cannot").replace("won't", "will not")
    t = re.sub(r"(\w)n't\b", r"\1 not", t)
    out, neg = [], 0
    for w in re.findall(r"[a-z]{2,}", t):
        if w in NEG:
            neg = 2; continue
        if w in STOP:
            continue
        out.append(("not_" + w, "not " + w) if neg else (w, w))
        neg = max(0, neg - 1)
    return out

def analyzer(text):
    return [t for t, _ in tokens(text)]
