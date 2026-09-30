"""Command-line chat client (offline, no server needed).

Builds the full pipeline in-process and answers questions from the terminal.
Use ``--query`` for a one-shot answer, or run with no args for an interactive
REPL. Demonstrates grounded answers with citations and safe abstention.
"""

from __future__ import annotations

import argparse

import _common

from backend.app.runtime import build_state


def _render(outcome) -> None:
    print(f"\nstatus : {outcome.status}   (intent={outcome.intent_label} "
          f"@ {outcome.intent_confidence}, provider={outcome.provider})")
    print(f"answer : {outcome.answer}")
    if outcome.citations:
        print("sources:")
        for c in outcome.citations:
            loc = f" — {c.location}" if c.location else ""
            print(f"   • [{c.chunk_id}] {c.title}{loc}")
    if outcome.status == "abstained":
        print(f"(reason: {outcome.reason})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Grounded campus chatbot (CLI)")
    parser.add_argument("--query", "-q", help="one-shot question; omit for interactive mode")
    args = parser.parse_args()

    settings = _common.get_settings()
    _common.configure_logging("WARNING")  # keep the REPL clean
    _common.banner("Campus Chatbot (CLI)")
    state = build_state(settings)
    print(f"  kb={state.kb.size} chunks | provider={state.provider.name} | "
          f"index={state.index_source}")

    if args.query:
        _render(state.orchestrator.answer(args.query))
        return 0

    print("  Type a question (blank line or Ctrl-C to quit).")
    try:
        while True:
            q = input("\n> ").strip()
            if not q:
                break
            _render(state.orchestrator.answer(q))
    except (EOFError, KeyboardInterrupt):
        pass
    print("\nbye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
