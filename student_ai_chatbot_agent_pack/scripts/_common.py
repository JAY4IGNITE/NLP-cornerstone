"""Shared bootstrap for scripts: makes ``backend`` importable and offers helpers.

Every script imports this first. Running ``python scripts/<name>.py`` puts the
scripts/ dir on sys.path[0]; we prepend the repo root so ``backend.app...``
resolves without installation.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.app.core.config import Settings, get_settings  # noqa: F401
from backend.app.core.logging import configure_logging  # noqa: F401


def banner(title: str) -> None:
    line = "=" * max(8, len(title) + 4)
    print(f"\n{line}\n  {title}\n{line}")


def ok(msg: str) -> None:
    print(f"[ OK ] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def artifacts_dir(sub: str | Settings | None = None) -> Path:
    """Return (creating) an artifacts directory.

    ``artifacts_dir("eval")`` -> ``artifacts/eval``. A ``Settings`` (or None)
    argument is accepted for backward compatibility and maps to ``artifacts``.
    """
    d = ROOT / "artifacts"
    if isinstance(sub, str):
        d = d / sub
    d.mkdir(parents=True, exist_ok=True)
    return d
