"""Print per-case and overall usage from the local prompt-free journal."""

import argparse
import json
from pathlib import Path

from backend.observability.aggregate import aggregate_by_case, aggregate_overall


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("data/telemetry.jsonl"))
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.path.read_text().splitlines() if line.strip()] if args.path.exists() else []
    cases = aggregate_by_case(rows)
    print(json.dumps({"by_case": cases, "overall": aggregate_overall(cases)}, indent=2))


if __name__ == "__main__":
    main()
