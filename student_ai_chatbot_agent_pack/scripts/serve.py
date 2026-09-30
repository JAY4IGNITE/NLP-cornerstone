"""Run the API server (uvicorn) with settings-driven host/port."""

from __future__ import annotations

import _common


def main() -> int:
    settings = _common.get_settings()
    _common.banner("Serve API")
    print(f"  http://{settings.api_host}:{settings.api_port}  (provider={settings.llm_provider})")
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
