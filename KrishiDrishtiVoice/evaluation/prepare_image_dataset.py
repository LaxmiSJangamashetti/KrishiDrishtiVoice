"""Dry-run dataset acquisition and manifest verification helper.

No network download is performed by this script. Acquisition requires a future
explicit source, license, and human-review decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="IMAGE_DATASET_MANIFEST.json")
    parser.add_argument("--verify-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if args.verify_file:
        print(json.dumps({"file": str(args.verify_file), "sha256": sha256(args.verify_file)}))
    if args.dry_run:
        print(json.dumps({"status": "dry_run", "records": len(manifest.get("records", [])),
                          "downloads_performed": 0, "human_review_required": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
