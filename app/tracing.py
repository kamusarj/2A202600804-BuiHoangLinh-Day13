from __future__ import annotations

from contextlib import nullcontext
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

if os.getenv("LANGFUSE_BASE_URL"):
    os.environ["LANGFUSE_HOST"] = os.environ["LANGFUSE_BASE_URL"]

try:
    from langfuse import get_client, observe

    langfuse_client = get_client()
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyClient:
        def start_as_current_span(self, **kwargs: Any):
            return nullcontext(self)

        def start_as_current_generation(self, **kwargs: Any):
            return nullcontext(self)

        def update(self, **kwargs: Any) -> None:
            return None

        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    langfuse_client = _DummyClient()


def tracing_enabled() -> bool:
    return bool(
        os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
        and (os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL"))
    )
