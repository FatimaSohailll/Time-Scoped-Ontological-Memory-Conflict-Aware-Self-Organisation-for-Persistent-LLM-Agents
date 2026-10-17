"""NetworkX view over the SQLite store, for graph queries and plots."""

import networkx as nx

from .store import Store


def to_graph(store: Store) -> nx.DiGraph:
    g = nx.DiGraph()
    for note in store.list_notes():
        g.add_node(note.id, kind="note", content=note.content, timestamp=note.timestamp)
        for target in note.links:
            g.add_edge(note.id, target, kind="link")
    for subject in store.subjects():
        for fact in store.fact_history(subject):
            g.add_node(fact.id, kind="fact", status=fact.status,
                       label=f"{fact.subject} {fact.predicate} {fact.object}")
            if fact.source_note_id:
                g.add_edge(fact.source_note_id, fact.id, kind="states")
            if fact.supersedes:
                g.add_edge(fact.id, fact.supersedes, kind="supersedes")
    return g
