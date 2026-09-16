"""Download 100% Pure Education and Academic Datasets from Hugging Face.
All datasets are strictly academic: university coursework, computer science, mathematics,
physics, chemistry, biology, statistics, and academic admissions/regulations.
Zero non-educational datasets.
"""
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "cache" / "hf_downloads"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

HF_BASE_URL = "https://huggingface.co/datasets/flax-sentence-embeddings/stackexchange_title_body_jsonl/resolve/main/"

DATASETS_TO_DOWNLOAD = [
    ("cs.stackexchange.com.jsonl.gz", "cs.jsonl.gz", "Computer Science Education"),
    ("cstheory.stackexchange.com.jsonl.gz", "cstheory.jsonl.gz", "Theoretical Computer Science"),
    ("chemistry.stackexchange.com.jsonl.gz", "chemistry.jsonl.gz", "Chemistry Education"),
    ("biology.stackexchange.com.jsonl.gz", "biology.jsonl.gz", "Biology Education"),
    ("physics.stackexchange.com.jsonl.gz", "physics.jsonl.gz", "Physics Education"),
    ("stats.stackexchange.com.jsonl.gz", "stats.jsonl.gz", "Statistics & Probability"),
    ("math.stackexchange.com.jsonl.gz", "math.jsonl.gz", "College Mathematics & Calculus"),
]

def download_file(src_name: str, dst_name: str, desc: str):
    dst_path = CACHE_DIR / dst_name
    if dst_path.exists() and dst_path.stat().st_size > 100_000:
        print(f"[Skip] {dst_name} already exists ({dst_path.stat().st_size / (1024*1024):.1f} MB) - {desc}")
        return

    url = HF_BASE_URL + src_name
    print(f"\n[Download] Fetching {desc} ({src_name})...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req) as resp, open(dst_path, "wb") as out_f:
            dl = 0
            while True:
                chunk = resp.read(2 * 1024 * 1024)
                if not chunk:
                    break
                out_f.write(chunk)
                dl += len(chunk)
                elapsed = max(0.01, time.time() - t0)
                speed = (dl / (1024 * 1024)) / elapsed
                print(f"\r  Downloaded {dl / (1024*1024):.1f} MB @ {speed:.2f} MB/s", end="", flush=True)
        print(f"\n  Finished {dst_name} in {time.time() - t0:.1f}s")
    except Exception as e:
        print(f"\n  Error downloading {src_name}: {e}")
        if dst_path.exists():
            dst_path.unlink()

def main():
    print("=" * 70)
    print("DOWNLOADING 100% PURE ACADEMIC & EDUCATION DATASETS FROM HUGGING FACE")
    print("=" * 70)
    for src, dst, desc in DATASETS_TO_DOWNLOAD:
        download_file(src, dst, desc)
    print("\nAll pure educational dataset downloads complete.")

if __name__ == "__main__":
    main()
