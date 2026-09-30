"""Fine-tune the DistilBERT intent classifier (MODEL_PLAN.md §5).

Trains a sequence-classification head over the 24 canonical intents from the
CampusFAQ splits (preprocessed ``intent_*.jsonl`` if present, else the raw
``campus_faq.*.jsonl``) and saves a HuggingFace model dir that
``services/intent.IntentClassifier`` auto-loads at runtime.

This is the one *optional*, *online* step in the pack: the app ships working on
the deterministic lexical fallback (zero training, fully offline), and only
upgrades to DistilBERT when a trained model is present here. First run needs
network (or a warm HF cache) to fetch the base model.

Deterministic (seed=42). Use ``--smoke`` for a fast wiring check that writes to a
throwaway dir instead of the app's model dir.
"""

from __future__ import annotations

import argparse
import json
import random

import _common

from backend.app.models.intents import INTENTS, NUM_INTENTS


def _load(split: str) -> list[tuple[str, int]]:
    base = _common.ROOT / "data" / "processed"
    for name in (f"intent_{split}.jsonl", f"campus_faq.{split}.jsonl"):
        p = base / name
        if p.exists():
            rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
            return [((r.get("text") or r.get("question") or ""), int(r["label_id"])) for r in rows]
    return []


def _parse() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Fine-tune DistilBERT intent classifier")
    ap.add_argument("--base-model", default="distilbert-base-uncased")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--max-train", type=int, default=None, help="cap training rows")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--smoke", action="store_true", help="tiny/fast wiring check")
    return ap.parse_args()


def main() -> int:
    args = _parse()
    _common.configure_logging("WARNING")
    _common.banner("Train intent classifier")

    try:
        import numpy as np
        import torch
        from torch.utils.data import DataLoader, TensorDataset
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            set_seed,
        )
    except ImportError as exc:
        _common.fail(f"training deps missing ({exc.name}); install extras: pip install -e .[ml]")
        _common.warn("the app still runs on the offline lexical fallback without a trained model")
        return 2

    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    set_seed(seed)

    train = _load("train")
    val = _load("val")
    if not train:
        _common.fail("no training data — run scripts/build_dataset.py (and optionally preprocess.py)")
        return 1

    if args.smoke:
        train, val = train[:64], val[:64]
        args.epochs = 1
    if args.max_train:
        train = train[: args.max_train]

    out_dir = args.output_dir or (
        "artifacts/models/intent_smoke" if args.smoke else "artifacts/models/intent"
    )
    out_path = _common.ROOT / out_dir
    device = "cuda" if torch.cuda.is_available() else "cpu"
    id2label = {i: INTENTS[i] for i in range(NUM_INTENTS)}
    label2id = {v: k for k, v in id2label.items()}
    print(f"  base={args.base_model} | device={device} | train={len(train)} val={len(val)} | "
          f"epochs={args.epochs} -> {out_dir}\n")

    tok = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model, num_labels=NUM_INTENTS, id2label=id2label, label2id=label2id
    ).to(device)

    def _encode(rows: list[tuple[str, int]]) -> TensorDataset:
        enc = tok([t for t, _ in rows], truncation=True, padding="max_length",
                  max_length=args.max_length, return_tensors="pt")
        labels = torch.tensor([y for _, y in rows], dtype=torch.long)
        return TensorDataset(enc["input_ids"], enc["attention_mask"], labels)

    dl = DataLoader(_encode(train), batch_size=args.batch_size, shuffle=True)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)

    model.train()
    for epoch in range(args.epochs):
        running = 0.0
        for ids, mask, y in dl:
            ids, mask, y = ids.to(device), mask.to(device), y.to(device)
            opt.zero_grad()
            loss = model(input_ids=ids, attention_mask=mask, labels=y).loss
            loss.backward()
            opt.step()
            running += loss.item()
        _common.ok(f"epoch {epoch + 1}/{args.epochs} mean_loss={running / max(1, len(dl)):.4f}")

    val_acc = 0.0
    if val:
        model.eval()
        correct = 0
        with torch.no_grad():
            for ids, mask, y in DataLoader(_encode(val), batch_size=args.batch_size):
                ids, mask = ids.to(device), mask.to(device)
                pred = model(input_ids=ids, attention_mask=mask).logits.argmax(-1).cpu()
                correct += int((pred == y).sum())
        val_acc = round(correct / len(val), 4)
        _common.ok(f"val_accuracy={val_acc} ({correct}/{len(val)})")

    out_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out_path))
    tok.save_pretrained(str(out_path))
    report = {"base_model": args.base_model, "epochs": args.epochs, "train_rows": len(train),
              "val_rows": len(val), "val_accuracy": val_acc, "output_dir": out_dir, "smoke": args.smoke}
    (_common.artifacts_dir("eval") / "train_intent_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    _common.ok(f"saved model to {out_dir}"
               + ("  (smoke dir; app model dir untouched)" if args.smoke else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
