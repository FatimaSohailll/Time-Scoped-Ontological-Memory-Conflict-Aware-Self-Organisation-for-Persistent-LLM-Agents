"""The memory module: A-Mem notes plus our fact layer, behind one class.

Phase 1 runs A-Mem unchanged (system="amem") and records cost and latency
for every operation. The fact layer, classifier, gate and validity steps
(system="tsom") have their interfaces here and are filled in during Phase 2.
"""

from __future__ import annotations

import time
from typing import List, Optional

from .amem_bridge import RobustAgenticMemorySystem
from .contracts import Fact, MemoryOp, Note, RunConfig
from .llm import LLM
from .store import Store


class MemorySystem:
    def __init__(self, config: RunConfig, llm: LLM, db_path: str = ":memory:",
                 sample_id: Optional[str] = None):
        if config.system == "tsom" and (config.use_classifier or config.use_gate or config.use_validity):
            raise NotImplementedError("classifier, gate and validity are Phase 2 work")
        self.config = config
        self.llm = llm
        self.sample_id = sample_id
        self.store = Store(db_path)
        # Build A-Mem with a backend that needs no network at start-up,
        # then hand it our instrumented LLM so every call is counted.
        self.amem = RobustAgenticMemorySystem(model_name=config.embedder, llm_backend="ollama",
                                              llm_model=config.model)
        self.amem.llm_controller.llm = llm

    # ---- write path ----

    def write(self, content: str, time_str: str) -> str:
        before = self.llm.usage.snapshot()
        evo_before = self.amem.evo_cnt
        start = time.perf_counter()
        note_id = self.amem.add_note(content, time=time_str)
        latency = time.perf_counter() - start
        used = self.llm.usage.since(before)
        self._sync_note(note_id)
        self.store.log_op(MemoryOp(
            op_type="write", system=self.config.system, sample_id=self.sample_id,
            ids_touched=[note_id], llm_calls=used.calls, prompt_tokens=used.prompt_tokens,
            completion_tokens=used.completion_tokens, latency_s=latency,
            evolved=self.amem.evo_cnt > evo_before,
        ))
        return note_id

    # Phase 2 hooks. Each one is a single, separately switchable step.

    def extract_facts(self, note: Note) -> List[Fact]:
        """Turn a note into typed facts against tsom.schema.PREDICATES."""
        raise NotImplementedError("Phase 2")

    def classify(self, fact: Fact) -> str:
        """Gap 1: label a fact additive, corrective, contradictory or redundant."""
        raise NotImplementedError("Phase 2")

    def gate(self, labels: List[str], neighbour_similarity: float) -> bool:
        """Gap 2: True means run A-Mem evolution for this write."""
        return any(lbl in ("corrective", "contradictory") for lbl in labels) or \
            neighbour_similarity >= self.config.tau

    # ---- read path ----

    def search(self, query: str, k: int) -> dict:
        start = time.perf_counter()
        context = self.amem.find_related_memories_raw(query, k=k)
        self.store.log_op(MemoryOp(op_type="search", system=self.config.system,
                                   sample_id=self.sample_id, latency_s=time.perf_counter() - start))
        return {"notes": context, "facts": []}  # facts filled once the fact layer exists

    def fact_history(self, entity: str, predicate: Optional[str] = None) -> List[Fact]:
        self.store.log_op(MemoryOp(op_type="fact_history", system=self.config.system,
                                   sample_id=self.sample_id))
        return self.store.fact_history(entity, predicate)

    def inspect(self, entity: str) -> dict:
        facts = self.store.fact_history(entity)
        return {
            "entity": entity,
            "current": [f.model_dump() for f in facts if f.status == "active"],
            "retired": [f.model_dump() for f in facts if f.status != "active"],
        }

    # ---- helpers ----

    def _sync_note(self, note_id: str):
        """Copy an A-Mem note (and any neighbours evolution changed) into SQLite."""
        ids = list(self.amem.memories.keys())
        targets = [note_id] + self._neighbour_ids(note_id, ids)
        for nid in targets:
            n = self.amem.memories[nid]
            links = [ids[i] for i in n.links if isinstance(i, int) and 0 <= i < len(ids)]
            self.store.upsert_note(Note(id=n.id, content=n.content, timestamp=n.timestamp,
                                        keywords=list(n.keywords), tags=list(n.tags),
                                        context=n.context, links=links))

    def _neighbour_ids(self, note_id: str, ids: List[str]) -> List[str]:
        n = self.amem.memories[note_id]
        return [ids[i] for i in n.links if isinstance(i, int) and 0 <= i < len(ids) and ids[i] != note_id]

    def sync_all(self):
        for nid in self.amem.memories:
            self._sync_note(nid)
        self.store.conn.commit()
