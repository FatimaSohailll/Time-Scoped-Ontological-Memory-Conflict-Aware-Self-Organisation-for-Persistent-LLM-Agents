"""F1 and BLEU-1, computed exactly as in A-Mem's utils.py.

We copy the two functions instead of importing utils.py because that file also
loads BERTScore and other models we do not report.
"""

from collections import defaultdict
from statistics import mean
from typing import Dict, List

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

for _pkg in ("punkt", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{_pkg}")
    except LookupError:
        nltk.download(_pkg, quiet=True)

CATEGORY_NAMES ={1: "Multi-hop", 2: "Temporal", 3: "Open-domain", 4: "Single-hop", 5: "Adversarial"}


def simple_tokenize(text) -> List[str]:
    text = str(text)
    return text.lower().replace('.', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ').split()


def f1(prediction: str, reference: str) -> float:
    if not prediction or not reference:
        return 0.0
    pred = set(simple_tokenize(str(prediction).strip()))
    ref = set(simple_tokenize(str(reference).strip()))
    if not pred or not ref:
        return 0.0
    common = pred & ref
    p, r = len(common) / len(pred), len(common) / len(ref)
    return 2 * p * r / (p + r) if p + r > 0 else 0.0


def bleu1(prediction: str, reference: str) -> float:
    if not prediction or not reference:
        return 0.0
    pred = nltk.word_tokenize(str(prediction).strip().lower())
    ref = [nltk.word_tokenize(str(reference).strip().lower())]
    try:
        return sentence_bleu(ref, pred, weights=(1, 0, 0, 0),
                             smoothing_function=SmoothingFunction().method1)
    except Exception:
        return 0.0


def summarise(rows: List[Dict]) -> Dict:
    """rows: dicts with category, f1, bleu1. Returns mean scores per category and overall."""
    by_cat = defaultdict(list)
    for row in rows:
        by_cat[row["category"]].append(row)
    out = {}
    for cat in sorted(by_cat):
        items = by_cat[cat]
        out[CATEGORY_NAMES[cat]] = {"n": len(items),
                                    "f1": 100 * mean(r["f1"] for r in items),
                                    "bleu1": 100 * mean(r["bleu1"] for r in items)}
    if rows:
        out["Overall"] = {"n": len(rows), "f1": 100 * mean(r["f1"] for r in rows),
                          "bleu1": 100 * mean(r["bleu1"] for r in rows)}
    return out
