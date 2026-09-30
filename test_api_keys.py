"""Standalone API-key connectivity probe (stdlib only).

Reads .env, reports which secret keys are configured, and for any that ARE set
makes a minimal authenticated request to verify it actually works. Key values are
never printed — only a masked length. Safe to run with an empty .env.

    python test_api_keys.py
"""
import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
TIMEOUT = 12
_ctx = ssl.create_default_context()


def load_env(path):
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def mask(val):
    return f"set (len={len(val)})" if val else "EMPTY"


def http(method, url, headers=None):
    """Return (status_code, short_body) or (None, error_string)."""
    req = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=_ctx) as r:
            return r.status, r.read(300).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(300).decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def verdict(status):
    if status == 200:
        return "WORKING"
    if status in (401, 403):
        return "INVALID KEY (auth rejected)"
    if status == 404:
        return "AUTH OK, resource missing (404)"  # token valid, index not created yet
    if status is None:
        return "NETWORK ERROR"
    return f"UNEXPECTED (HTTP {status})"


def test_nvidia(env):
    key = env.get("NVIDIA_API_KEY", "")
    base = env.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
    if not key:
        return "NVIDIA NIM (NVIDIA_API_KEY)", mask(key), "SKIPPED -- not configured, backend uses offline fallback"
    status, body = http("GET", f"{base}/models", {"Authorization": f"Bearer {key}"})
    return "NVIDIA NIM (NVIDIA_API_KEY)", mask(key), f"{verdict(status)} | {body[:120]}"


def test_gemini(env):
    key = env.get("GEMINI_API_KEY", "")
    label = "Gemini (GEMINI_API_KEY) [note: unused by current backend]"
    if not key:
        return label, mask(key), "SKIPPED -- not configured"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    status, body = http("GET", url)
    return label, mask(key), f"{verdict(status)} | {body[:120]}"


def test_cloudflare(env):
    acct = env.get("CLOUDFLARE_ACCOUNT_ID", "")
    token = env.get("CLOUDFLARE_API_TOKEN", "")
    index = env.get("CLOUDFLARE_VECTORIZE_INDEX", "student-curriculum-index")
    label = "Cloudflare Vectorize (CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN)"
    cfg = f"account_id={mask(acct)}, api_token={mask(token)}"
    if not (acct and token):
        return label, cfg, "SKIPPED -- not configured, backend uses local edge emulator"
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/vectorize/v2/indexes/{index}"
    status, body = http("GET", url, {"Authorization": f"Bearer {token}"})
    return label, cfg, f"{verdict(status)} | {body[:120]}"


def main():
    env = load_env(ENV_PATH)
    print(f"Loaded {ENV_PATH} ({'exists' if ENV_PATH.exists() else 'MISSING'})\n")
    print("=" * 78)
    for name, cfg, result in (test_nvidia(env), test_gemini(env), test_cloudflare(env)):
        print(f"{name}\n   config : {cfg}\n   result : {result}")
        print("-" * 78)
    configured = [k for k in ("NVIDIA_API_KEY", "GEMINI_API_KEY",
                              "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN") if env.get(k)]
    print(f"\nSummary: {len(configured)}/4 secret keys configured -> "
          + (", ".join(configured) if configured else "NONE (full offline fallback mode)"))


if __name__ == "__main__":
    main()
