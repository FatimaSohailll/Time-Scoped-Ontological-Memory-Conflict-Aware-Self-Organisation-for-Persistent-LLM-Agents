from tsom.contracts import Fact, MemoryOp, Note
from tsom.store import Store


def test_note_round_trip():
    store = Store()
    note = Note(content="I moved to Lahore", timestamp="1 May 2023", keywords=["move"], links=["abc"])
    store.upsert_note(note)
    assert store.get_note(note.id) == note


def test_supersede_keeps_history():
    store = Store()
    old = Fact(subject="ali", predicate="lives_in", object="Karachi", valid_from="2023-01-01")
    store.add_fact(old)
    new = Fact(subject="ali", predicate="lives_in", object="Lahore", valid_from="2023-05-01")
    store.supersede(old.id, new)

    active = store.active_facts("ali", "lives_in")
    assert [f.object for f in active] == ["Lahore"]
    history = store.fact_history("ali", "lives_in")
    assert [f.object for f in history] == ["Karachi", "Lahore"]
    assert history[0].status == "retired" and history[0].valid_to == "2023-05-01"
    assert history[1].supersedes == old.id


def test_revert_supersession():
    store = Store()
    old = Fact(subject="ali", predicate="lives_in", object="Karachi", valid_from="2023-01-01")
    store.add_fact(old)
    new = Fact(subject="ali", predicate="lives_in", object="Lahore", valid_from="2023-05-01")
    store.supersede(old.id, new)

    restored = store.revert_supersession(new.id)
    assert restored.object == "Karachi" and restored.status == "active" and restored.valid_to is None
    assert store.get_fact(new.id).status == "rejected"


def test_op_log():
    store = Store()
    store.log_op(MemoryOp(op_type="write", system="amem", llm_calls=3, latency_s=1.5))
    ops = store.ops()
    assert len(ops) == 1 and ops[0].llm_calls == 3
