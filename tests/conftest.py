"""Test setup.

Tests run offline and on CPU. If the heavy packages A-Mem imports at module
level (sentence-transformers, transformers, litellm) are missing, we put small
stand-ins in their place: a hashing embedder instead of MiniLM, and empty
modules for the rest. With the real packages installed, the real ones are used.
"""

import hashlib
import sys
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class HashEmbedder:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, **kwargs):
        out = np.zeros((len(texts), 64), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in str(text).lower().split():
                out[row, int(hashlib.md5(word.encode()).hexdigest(), 16) % 64] += 1.0
        return out + 1e-6

    def get_config_dict(self):
        return {"model_name": "hash"}


def _stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module


try:
    import sentence_transformers  # noqa: F401
except ImportError:
    _stub("sentence_transformers", SentenceTransformer=HashEmbedder)
    _stub("sentence_transformers.util", pytorch_cos_sim=None)
try:
    import transformers  # noqa: F401
except ImportError:
    _stub("transformers", AutoModel=None, AutoTokenizer=None)
try:
    import litellm  # noqa: F401
except ImportError:
    _stub("litellm", completion=None)
