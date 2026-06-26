"""
Langfuse tracing for governance-experiment-v2.

Tracing is **opt-in** and **silent when off**. If the Langfuse credentials are
not in the environment, every helper here is a zero-overhead no-op and nothing
from the `langfuse` package is imported — so analysis-only and offline use keep
working with no extra dependency.

Enable it by exporting:
    LANGFUSE_PUBLIC_KEY=pk-lf-...
    LANGFUSE_SECRET_KEY=sk-lf-...
    LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or us./your self-hosted URL

When enabled, every Anthropic `messages.create` (agent + judge) across the
runner and judge is auto-traced as a `generation` via the OpenTelemetry
Anthropic instrumentor, and the `@observe`-decorated `run_trial` / `score_row`
group each call into a per-trial trace carrying the experimental cell.
"""

import os
import re
from contextlib import contextmanager

_initialized = False
_enabled = False

# Conservative PII redaction applied only to exported span attributes (never to
# the values the experiment computes/stores with).
_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE = re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def _mask_otel_spans(*, params):
    """Redact card/SSN/phone-like strings from exported OpenTelemetry spans."""
    from langfuse.types import MaskOtelSpansResult, OtelSpanPatch

    patches = {}
    for identifier, span in params.spans.items():
        replacements = {}
        for key, value in span.attributes.items():
            if isinstance(value, str):
                masked = _CARD.sub("[REDACTED_CARD]", value)
                masked = _SSN.sub("[REDACTED_SSN]", masked)
                masked = _PHONE.sub("[REDACTED_PHONE]", masked)
                if masked != value:
                    replacements[key] = masked
        if replacements:
            patches[identifier] = OtelSpanPatch(set_attributes=replacements)

    return MaskOtelSpansResult(span_patches=patches) if patches else None


def init_observability():
    """Initialize Langfuse + Anthropic instrumentation once. Idempotent.

    Returns True if tracing is active, False otherwise.
    """
    global _initialized, _enabled
    if _initialized:
        return _enabled
    _initialized = True

    if not (os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        return False

    # The Langfuse SDK reads LANGFUSE_HOST; accept LANGFUSE_BASE_URL as an alias.
    if os.environ.get("LANGFUSE_BASE_URL") and not os.environ.get("LANGFUSE_HOST"):
        os.environ["LANGFUSE_HOST"] = os.environ["LANGFUSE_BASE_URL"]

    try:
        from langfuse import Langfuse
        from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

        Langfuse(mask_otel_spans=_mask_otel_spans)
        AnthropicInstrumentor().instrument()
        _enabled = True
    except Exception as exc:  # never let tracing setup break the experiment
        print(f"[observability] Langfuse tracing disabled ({type(exc).__name__}: {exc})")
        _enabled = False

    return _enabled


def observe(*d_args, **d_kwargs):
    """No-op-safe replacement for `langfuse.observe`.

    Supports bare `@observe` and `@observe(name=..., as_type=...,
    capture_input=False, ...)`. When tracing is disabled the function is returned
    unchanged (no wrapper, no warning, no overhead). Works with async functions.
    """

    def decorator(fn):
        if not _enabled:
            return fn
        from langfuse import observe as _lf_observe

        return _lf_observe(**d_kwargs)(fn)

    if len(d_args) == 1 and callable(d_args[0]) and not d_kwargs:
        return decorator(d_args[0])
    return decorator


@contextmanager
def trace_context(**attrs):
    """Attach trace attributes (session_id, tags, metadata, trace_name, ...) to
    spans created inside the block. No-op when tracing is disabled."""
    if not _enabled:
        yield
        return
    from langfuse import propagate_attributes

    with propagate_attributes(**{k: v for k, v in attrs.items() if v is not None}):
        yield


def update_trace(**kwargs):
    """Set fields (input, output, metadata, ...) on the current root observation,
    which become the trace's input/output. No-op when disabled."""
    if not _enabled:
        return
    from langfuse import get_client

    get_client().update_current_span(**{k: v for k, v in kwargs.items() if v is not None})


def flush():
    """Flush buffered spans (call before a short-lived process exits)."""
    if not _enabled:
        return
    from langfuse import get_client

    get_client().flush()


# Initialize on import so @observe decorators see the correct enabled state.
init_observability()
