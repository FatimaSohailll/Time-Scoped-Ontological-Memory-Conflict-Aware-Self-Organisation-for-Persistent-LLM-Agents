"""The only place that imports A-Mem's vendored code (third_party/amem)."""

import sys
from pathlib import Path

AMEM_DIR = Path(__file__).resolve().parent.parent / "third_party" / "amem"
if str(AMEM_DIR) not in sys.path:
    sys.path.insert(0, str(AMEM_DIR))

from memory_layer_robust import RobustAgenticMemorySystem  # noqa: E402
from memory_layer import SimpleEmbeddingRetriever  # noqa: E402
from llm_text_parsers import (  # noqa: E402
    parse_keywords_response,
    parse_plain_text_answer,
)
from load_dataset import load_locomo_dataset  # noqa: E402

__all__ = [
    "RobustAgenticMemorySystem",
    "SimpleEmbeddingRetriever",
    "parse_keywords_response",
    "parse_plain_text_answer",
    "load_locomo_dataset",
]
