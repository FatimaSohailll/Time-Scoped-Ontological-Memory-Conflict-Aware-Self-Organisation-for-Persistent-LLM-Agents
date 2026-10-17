"""Inspection script for humans.

    python scripts/inspect_memory.py results/<run>/memory_sample_0.sqlite --notes 5
    python scripts/inspect_memory.py <db> --entity Caroline
    python scripts/inspect_memory.py <db> --revert <fact_id>

Shows current and retired facts for an entity, and can undo a supersession.
The fact table stays empty until the fact layer is added in Phase 2.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tsom.store import Store  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("db")
    parser.add_argument("--entity")
    parser.add_argument("--revert", metavar="FACT_ID")
    parser.add_argument("--notes", type=int, metavar="N", help="print the first N notes")
    args = parser.parse_args()
    store = Store(args.db)

    if args.notes:
        for note in store.list_notes()[: args.notes]:
            print(f"[{note.timestamp}] {note.content}\n  keywords: {note.keywords}\n  "
                  f"tags: {note.tags}\n  context: {note.context}\n  links: {len(note.links)}")
    if args.entity:
        for fact in store.fact_history(args.entity):
            until = fact.valid_to or "now"
            print(f"{fact.status:8} {fact.subject} {fact.predicate} {fact.object}  "
                  f"({fact.valid_from} to {until})  id={fact.id}")
    if args.revert:
        restored = store.revert_supersession(args.revert)
        print(f"reverted. current again: {restored.subject} {restored.predicate} {restored.object}")
    store.close()


if __name__ == "__main__":
    main()
