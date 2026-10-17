from harness.metrics import bleu1, f1, summarise


def test_f1_matches_amem_definition():
    assert f1("7 May 2023", "7 May 2023") == 1.0
    assert f1("May 2023", "7 May 2023") == 0.8  # set-based tokens, as in A-Mem
    assert f1("", "anything") == 0.0
    assert f1("Paris.", "paris") == 1.0  # lower-cased, punctuation stripped


def test_bleu1_range():
    assert bleu1("7 May 2023", "7 May 2023") > 0.99
    assert bleu1("nothing in common", "7 May 2023") < 0.01


def test_summarise_per_category():
    rows = [{"category": 2, "f1": 1.0, "bleu1": 1.0}, {"category": 4, "f1": 0.0, "bleu1": 0.0}]
    s = summarise(rows)
    assert s["Temporal"]["f1"] == 100 and s["Single-hop"]["f1"] == 0 and s["Overall"]["f1"] == 50
