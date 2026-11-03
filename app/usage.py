"""Usage totals per day (UTC) from cost logs."""

import json
from datetime import UTC, datetime
from pathlib import Path


def usage_by_day(path: str) -> dict[str, dict]:
    days: dict[str, dict] = {}

    p = Path(path)

    if not p.exists():
        return days

    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        day = datetime.fromtimestamp(
            record["ts"], tz=UTC
        ).date().isoformat()

        daily = days.setdefault(
            day,
            {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
            },
        )

        daily["calls"] += 1
        daily["input_tokens"] += record["input_tokens"]
        daily["output_tokens"] += record["output_tokens"]
        daily["cost_usd"] = round(
            daily["cost_usd"] + record["cost_usd"], 8
        )

    return days