"""RAG baseline: same harness and tools as A-Mem, no LLM calls on write."""

import json

from harness.run_locomo import run
from tsom.contracts import RunConfig
from tsom.llm import LLM
from tsom.rag import RagMemory
from tsom.tools import MemoryTools


def test_rag_retrieves_raw_turns():
    llm = LLM("fake", "fake")
    memory = RagMemory(RunConfig(run_name="t", system="rag", backend="fake", model="fake"), llm)
    tools = MemoryTools(memory)
    tools.call("write_memory", turn="Speaker Ali says : I live in Karachi", time="1 May 2023")
    tools.call("write_memory", turn="Speaker Ali says : My cat is called Mano", time="2 May 2023")
    assert "Karachi" in tools.call("search_memory", query="Karachi", k=1)["notes"]
    assert llm.usage.calls == 0


def test_rag_smoke(tmp_path):
    config = RunConfig(run_name="rag_smoke", system="rag", backend="fake", model="fake",
                       max_samples=1, max_sessions=2, max_questions=10, output_dir=str(tmp_path))
    summary = run(config)
    ops = [json.loads(l) for l in (tmp_path / "rag_smoke" / "ops_sample_0.jsonl").read_text().splitlines()]
    writes = [op for op in ops if op["op_type"] == "write"]
    assert writes and all(op["llm_calls"] == 0 for op in writes)
    assert summary["scores"]["Overall"]["n"] == 10
