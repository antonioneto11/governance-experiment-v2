"""
Re-runs specific S1v2 trials that returned markdown tables instead of
LABEL: value format, leaving rationale empty.

Reads/writes results/raw_results_s1v2.jsonl and results/judged_results_s1v2.jsonl only.
"""

import asyncio
import json
import os
from pathlib import Path

import anthropic

from config import AGENT_MODEL, SEMAPHORE_CAP
from runner import assemble_system_prompt, get_user_turn, parse_s1

RAW_FILE = "results/raw_results_s1v2.jsonl"
JUDGED_FILE = "results/judged_results_s1v2.jsonl"

TARGET_IDS = [
    "60a5db1b-2b9d-45a7-82b6-f950d3a8c889",
    "9d1c3b85-5b3e-4bab-8c49-ccdbb6581b2c",
    "0b1cf1b0-6cf1-4ee8-a75e-d5158f1813ce",
]

MAX_ATTEMPTS = 5


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


async def rerun_one(client: anthropic.AsyncAnthropic, raw_row: dict) -> dict:
    system_prompt = assemble_system_prompt(raw_row)
    user_turn = get_user_turn(raw_row)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = await client.messages.create(
            model=AGENT_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_turn}],
        )
        text = response.content[0].text
        parsed = parse_s1(text)

        if parsed.get("rationale"):
            print(f"  attempt {attempt}: OK ({len(parsed['rationale'])} chars)")
            raw_row.update(parsed)
            raw_row["response_text"] = text
            raw_row["parse_error"] = False
            return raw_row

        print(f"  attempt {attempt}: still empty — {repr(text[:100])}")

    print(f"  all {MAX_ATTEMPTS} attempts returned empty rationale; keeping last")
    raw_row.update(parsed)
    raw_row["response_text"] = text
    raw_row["parse_error"] = False
    return raw_row


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    raw_path = Path(RAW_FILE)
    judged_path = Path(JUDGED_FILE)

    raw_rows = load_jsonl(raw_path)
    raw_by_id = {r["trial_id"]: r for r in raw_rows}

    missing = [tid for tid in TARGET_IDS if tid not in raw_by_id]
    if missing:
        print(f"WARNING: not found in raw: {missing}")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    fixed_ids: set[str] = set()

    for tid in TARGET_IDS:
        if tid not in raw_by_id:
            continue
        raw_row = raw_by_id[tid]
        print(f"\n{tid[:8]}…  {raw_row['monitoring_condition']}  "
              f"{raw_row['governance_pattern']}  framing={raw_row['framing']}  rep={raw_row['rep']}")
        await rerun_one(client, raw_row)
        fixed_ids.add(tid)

    write_jsonl(raw_path, raw_rows)
    print(f"\nUpdated {RAW_FILE} ({len(fixed_ids)} rows refreshed)")

    if judged_path.exists():
        judged_rows = load_jsonl(judged_path)
        cleared = 0
        for row in judged_rows:
            if row["trial_id"] in fixed_ids:
                for key in ("judge_error", "faithfulness_score", "faithfulness_score_reason"):
                    row.pop(key, None)
                cleared += 1
        write_jsonl(judged_path, judged_rows)
        print(f"Cleared judge_error on {cleared} rows in {JUDGED_FILE}")

    print("\nRun python judge_s1v2.py to score the updated rows.")


if __name__ == "__main__":
    asyncio.run(main())
