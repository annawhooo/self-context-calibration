"""
Provider adapters for the convergence collection runner.

Three client shapes cover five providers:
  anthropic      native Messages API (thinking blocks in the response).
  openai_compat  one chat-completions client parameterized by base url and
                 key, serving openai, deepseek, and zai. Reasoning control
                 differs per provider and is pinned in the tables below, not
                 inferred.
  google         native generateContent. Arm B only: Gemini 3.x exposes no
                 way to disable internal reasoning, so no Arm A
                 configuration exists for it.

Reasoning-off mechanism per provider, pinned (do not tune without a
pre-registration deviation note):
  anthropic  omit the thinking parameter entirely.
  openai     reasoning_effort "none". A model that rejects it fails the call
             with a non-retryable error; it is excluded, never silently
             downgraded.
  deepseek   the documented V4-line thinking toggle: thinking {type disabled}.
  zai        enable_thinking false. NEVER thinking {type disabled}: that form
             has been reported to be silently ignored on Z.ai while
             enable_thinking works, and a silent ignore would corrupt Arm A.
  google     not applicable, Arm B only.

Reasoning-presence detection per provider (verification mode and per-row
reasoning_detected):
  anthropic  thinking or redacted_thinking blocks in content.
  openai     usage.completion_tokens_details.reasoning_tokens (count 0 is a
             positive "off" signal; a missing count is undetectable, not
             success).
  deepseek   choices[0].message.reasoning_content.
  zai        choices[0].message.reasoning_content.
  google     usageMetadata.thoughtsTokenCount, falling back to parts flagged
             thought: true.
An undetectable state is reported as None, never as success, because the
pre-registration's void condition requires positive verification.

Temperature: 1.0 sent where the API accepts it, omitted where it rejects it
(anthropic 4.7+ deprecated the parameter; the openai gpt-5 line rejects
non-default values). Which was done is pinned per model in the roster config
(temperature_mode) and reported per row as temperature_sent. Never 0 and
never a near-0 default: the measurement depends on natural sampling variance.

Credentials enter build_request as an argument and land only in headers.
Nothing here logs, stores, or serializes a key.
"""

import os
import sys
import json
import time

import requests

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))

# Reuse the faithful harness's pinned call constants: same endpoint and API
# version for anthropic, same generation token budget, same retry bounds and
# linear backoff. Reusing the constants keeps the convergence retry semantics
# identical to the harness's call_model by construction.
from confab_harness_faithful import (  # noqa: E402
    API_URL as ANTHROPIC_API_URL,
    API_VERSION as ANTHROPIC_API_VERSION,
    GEN_MAX_TOKENS,
    MAX_RETRIES,
    RETRY_BACKOFF_SECONDS,
    REQUEST_TIMEOUT,
)


class ProviderConfigError(ValueError):
    """A model config, arm, or provider combination that must never reach the
    network. Raised at request-build time, before any call."""


# Retryable HTTP statuses, mapped explicitly per provider:
#   anthropic  429 rate limit, 500/502/503 server, 529 overloaded (the same
#              set call_model retries in the faithful harness).
#   openai     429 rate limit, 500 server, 502/503 gateway/overload. 400-level
#              errors (including a rejected reasoning_effort) are never
#              retried: they mean the pinned config is wrong for the model.
#   deepseek   429 rate limit, 500 server, 502/503 gateway/overload (DeepSeek
#              documents 429/500/503; 502 observed from its gateway).
#   zai        429 rate limit, 500 server, 502/503 gateway/overload.
#   google     429 RESOURCE_EXHAUSTED, 500 INTERNAL, 503 UNAVAILABLE,
#              504 DEADLINE_EXCEEDED.
PROVIDERS = {
    "anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "url": ANTHROPIC_API_URL,
        "shape": "anthropic",
        "retryable": (429, 500, 502, 503, 529),
    },
    "openai": {
        "env": "OPENAI_API_KEY",
        "url": "https://api.openai.com/v1/chat/completions",
        "shape": "openai_compat",
        "retryable": (429, 500, 502, 503),
    },
    "deepseek": {
        "env": "DEEPSEEK_API_KEY",
        "url": "https://api.deepseek.com/chat/completions",
        "shape": "openai_compat",
        "retryable": (429, 500, 502, 503),
    },
    "zai": {
        "env": "ZAI_API_KEY",
        "url": "https://api.z.ai/api/paas/v4/chat/completions",
        "shape": "openai_compat",
        "retryable": (429, 500, 502, 503),
    },
    "google": {
        "env": "GOOGLE_API_KEY",
        "url_template": ("https://generativelanguage.googleapis.com/v1beta/"
                         "models/{model}:generateContent"),
        "shape": "google",
        "retryable": (429, 500, 503, 504),
    },
}

# Reasoning request fragments per provider and arm (A = off, B = on), merged
# into the openai_compat body. anthropic and google are handled structurally
# in build_request (thinking parameter present or absent; google has no off
# form at all).
_OPENAI_COMPAT_REASONING = {
    "openai": {"A": {"reasoning_effort": "none"},
               "B": {}},   # Arm B: the provider's default effort, per pre-reg
    "deepseek": {"A": {"thinking": {"type": "disabled"}},
                 "B": {"thinking": {"type": "enabled"}}},
    "zai": {"A": {"enable_thinking": False},
            "B": {"enable_thinking": True}},
}

# Token-limit parameter name per openai_compat provider. The openai gpt-5
# line requires max_completion_tokens; deepseek and zai use max_tokens.
_OPENAI_COMPAT_MAX_TOKENS_PARAM = {
    "openai": "max_completion_tokens",
    "deepseek": "max_tokens",
    "zai": "max_tokens",
}


def build_request(model_cfg, arm, prompt, api_key):
    """Construct the full request for one single-turn call. Returns
    (url, headers, body, temperature_sent). Pure: no network, no environment
    reads. temperature_sent is 1.0 when the body carries temperature, else
    None, and is recorded on the row by the caller."""
    provider = model_cfg.get("provider")
    if provider not in PROVIDERS:
        raise ProviderConfigError("unknown provider {!r}; valid: {}".format(
            provider, ", ".join(sorted(PROVIDERS))))
    if arm not in ("A", "B"):
        raise ProviderConfigError("unknown arm {!r}; valid: A, B".format(arm))
    if provider == "google" and arm == "A":
        raise ProviderConfigError(
            "google runs Arm B only: Gemini 3.x exposes no way to disable "
            "reasoning, so no Arm A configuration exists for it")

    p = PROVIDERS[provider]
    model = model_cfg["model"]
    send_temperature = model_cfg.get("temperature_mode") == "send"
    temperature_sent = 1.0 if send_temperature else None

    if p["shape"] == "anthropic":
        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            "content-type": "application/json",
        }
        body = {
            "model": model,
            "max_tokens": GEN_MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        }
        if arm == "B":
            thinking_on = model_cfg.get("thinking_on")
            if not thinking_on:
                raise ProviderConfigError(
                    "anthropic Arm B requires a thinking_on config for "
                    "{} (adaptive, or enabled with a budget)".format(model))
            body["thinking"] = thinking_on
        if send_temperature:
            body["temperature"] = 1.0
        return p["url"], headers, body, temperature_sent

    if p["shape"] == "openai_compat":
        headers = {
            "Authorization": "Bearer {}".format(api_key),
            "content-type": "application/json",
        }
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            _OPENAI_COMPAT_MAX_TOKENS_PARAM[provider]: GEN_MAX_TOKENS,
        }
        body.update(_OPENAI_COMPAT_REASONING[provider][arm])
        if send_temperature:
            body["temperature"] = 1.0
        return p["url"], headers, body, temperature_sent

    # google
    headers = {
        "x-goog-api-key": api_key,
        "content-type": "application/json",
    }
    generation_config = {"maxOutputTokens": GEN_MAX_TOKENS}
    if send_temperature:
        generation_config["temperature"] = 1.0
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }
    url = p["url_template"].format(model=model)
    return url, headers, body, temperature_sent


def post_with_retries(url, headers, body, retryable):
    """Bounded linear-backoff POST, reusing the faithful harness's retry
    semantics through its imported constants: MAX_RETRIES attempts, a sleep of
    RETRY_BACKOFF_SECONDS * attempt after a retryable failure, REQUEST_TIMEOUT
    per attempt, exactly as call_model does. retryable is the per-provider
    status set from PROVIDERS (each provider returns different rate-limit and
    error shapes; the mapping and its rationale are recorded on the table
    above). Raises RuntimeError on a non-retryable status or on exhaustion;
    error text carries only the status and a truncated response body, never
    request headers, so key material cannot reach a log line."""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(body),
                                 timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in retryable:
                last_err = "http {} {}".format(resp.status_code, resp.text[:300])
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise RuntimeError("http {} {}".format(resp.status_code,
                                                   resp.text[:500]))
        except requests.exceptions.RequestException as exc:
            last_err = str(exc)
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError("request failed after {} attempts: {}".format(
        MAX_RETRIES, last_err))


def parse_response(provider, data):
    """Extract from one provider response: the answer text, the
    reasoning-presence signal, and the exact model id the provider reports.
    Returns {"text": str, "reasoning_present": True/False/None,
    "model_id_exact": str or None}.

    reasoning_present is tri-state on purpose. True: reasoning content
    appeared. False: a positive off signal on that provider's pinned
    detection surface (see the module docstring). None: the response exposes
    no detection surface at all; the caller must report that as undetectable,
    never as success. Structurally empty responses degrade to empty text so
    the row records an unparsed sample instead of crashing the run."""
    if provider not in PROVIDERS:
        raise ProviderConfigError("unknown provider {!r}; valid: {}".format(
            provider, ", ".join(sorted(PROVIDERS))))
    shape = PROVIDERS[provider]["shape"]

    if shape == "anthropic":
        text_parts, reasoning = [], False
        for block in data.get("content") or []:
            btype = block.get("type")
            if btype == "text":
                text_parts.append(block.get("text", ""))
            elif btype in ("thinking", "redacted_thinking"):
                reasoning = True
        return {"text": "".join(text_parts),
                "reasoning_present": reasoning,
                "model_id_exact": data.get("model")}

    if shape == "openai_compat":
        choices = data.get("choices") or []
        message = (choices[0].get("message") or {}) if choices else {}
        text = message.get("content") or ""
        has_reasoning_content = bool(message.get("reasoning_content"))
        details = (data.get("usage") or {}).get("completion_tokens_details")
        has_token_count = details is not None and "reasoning_tokens" in details
        if provider == "openai":
            # Pinned surface: the reasoning token count. Count 0 is a
            # positive off signal; a missing count with no reasoning_content
            # either is undetectable, reported None, never success.
            if has_token_count:
                reasoning = details["reasoning_tokens"] > 0 or has_reasoning_content
            elif has_reasoning_content:
                reasoning = True
            else:
                reasoning = None
        else:
            # deepseek, zai. Pinned surface: reasoning_content, whose
            # documented off state is an absent or empty field, so absence is
            # a positive off signal, not an undetectable state. A nonzero
            # reasoning token count still counts as reasoning if a host
            # reports one without content.
            reasoning = has_reasoning_content or (
                has_token_count and details["reasoning_tokens"] > 0)
        return {"text": text,
                "reasoning_present": reasoning,
                "model_id_exact": data.get("model")}

    # google
    candidates = data.get("candidates") or []
    parts = (((candidates[0].get("content") or {}).get("parts") or [])
             if candidates else [])
    text = "".join(part.get("text", "") for part in parts
                   if not part.get("thought"))
    thought_parts = any(part.get("thought") for part in parts)
    usage = data.get("usageMetadata")
    if usage is not None:
        # The API omits zero-valued fields, so a present usageMetadata with
        # no thoughtsTokenCount is a positive zero.
        reasoning = usage.get("thoughtsTokenCount", 0) > 0 or thought_parts
    elif thought_parts:
        reasoning = True
    else:
        reasoning = None
    return {"text": text,
            "reasoning_present": reasoning,
            "model_id_exact": data.get("modelVersion")}
