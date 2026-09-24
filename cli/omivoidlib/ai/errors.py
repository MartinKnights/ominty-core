"""Stable provider error codes (docs/ai/10 §11, docs/ai/01).

These codes are returned through the structured error envelope:

    PROVIDER_NOT_FOUND    provider name is not registered
    PROVIDER_UNAVAILABLE  provider binary/server is not usable
    PROVIDER_FAILED       provider invocation failed
    PROVIDER_TIMEOUT      provider did not respond in time
"""

PROVIDER_ERRORS = {
    "PROVIDER_NOT_FOUND",
    "PROVIDER_UNAVAILABLE",
    "PROVIDER_FAILED",
    "PROVIDER_TIMEOUT",
}