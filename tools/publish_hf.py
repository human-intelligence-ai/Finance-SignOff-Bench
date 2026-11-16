#!/usr/bin/env python3
"""Upload this repository to the Hugging Face dataset repo as one commit.

The Hugging Face copy gets README.md with the dataset-card front matter below prepended;
everything else is uploaded as-is. Requires `hf auth login` with write access to the org.

Usage:
    python3 tools/publish_hf.py                    # creates the repo as private if it does not exist
    python3 tools/publish_hf.py --message "Add task 012"
"""
from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi

REPO_ID = "human-intelligence-ai/Finance-SignOff-Bench"
ROOT = Path(__file__).resolve().parent.parent
CARD_HEADER = """---
pretty_name: "Finance SignOff Bench"
license: cc-by-nc-sa-4.0
language:
  - zh
tags:
  - finance
  - agentic
  - expert-authored
  - knowledge-work
  - harbor
  - benchmark
  - chinese
task_categories:
  - other
size_categories:
  - n<1K
configs:
  - config_name: default
    data_files:
      - split: public
        path: metadata.jsonl
---

"""
SKIP_DIRS = {".git", "jobs", "__pycache__"}
SKIP_NAMES = {".DS_Store"}


def files_to_upload() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if path.is_dir() or rel.parts[0] in SKIP_DIRS or any(p in SKIP_DIRS for p in rel.parts) or path.name in SKIP_NAMES:
            continue
        out.append(rel)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--message", default="Update Finance SignOff Bench")
    ap.add_argument("--dry-run", action="store_true", help="list what would be uploaded")
    args = ap.parse_args()
    rels = files_to_upload()
    if args.dry_run:
        for rel in rels:
            print(rel)
        return 0
    api = HfApi()
    api.create_repo(REPO_ID, repo_type="dataset", private=True, exist_ok=True)
    ops = []
    for rel in rels:
        if rel.as_posix() == "README.md":
            card = CARD_HEADER + (ROOT / rel).read_text(encoding="utf-8")
            ops.append(CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=card.encode("utf-8")))
        else:
            ops.append(CommitOperationAdd(path_in_repo=rel.as_posix(), path_or_fileobj=str(ROOT / rel)))
    info = api.create_commit(REPO_ID, repo_type="dataset", operations=ops, commit_message=args.message)
    print(f"uploaded {len(ops)} files: {info.commit_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
