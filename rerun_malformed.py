"""
Fixes S1 rows where the agent responded with a markdown table instead of
LABEL: value fields, leaving rationale empty and judge_error set.

Detection: judge_error in ('empty rationale', 'empty raw_rationale')
           AND response_text is present in raw_results.jsonl
           (distinguishes from runner-API-failure rows which have no response_text)

For each such row: calls the agent again (up to MAX_ATTEMPTS), keeping the
same trial_id and metadata. Updates raw_results.jsonl in-place and clears
judge_error in judged_results.jsonl so judge.py picks them up.
"""

import asyncio
import json
import os
from pathlib import Path

import anthropic

from config import AGENT_MODEL, JUDGED_RESULTS_FILE, RAW_RESULTS_FILE
from runner import assemble_system_prompt, get_user_turn, parse_s1

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


def find_malformed(raw_by_id: dict, judged_rows: list[dict]) -> list[dict]:
    return [
        r for r in judged_rows
        if r.get("judge_error") in ("empty rationale", "empty raw_rationale")
        and raw_by_id.get(r["trial_id"], {}).get("response_text")
    ]


async def rerun_one(
    client: anthropic.AsyncAnthropic,
    raw_row: dict,
) -> dict:
    """Call the agent up to MAX_ATTEMPTS times until rationale is non-empty."""
    system_prompt = assemble_system_prompt(raw_row)
    user_turn = get_user_turn(raw_row)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response_text = await client.messages.create(
            model=AGENT_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_turn}],
        )
        text = response_text.content[0].text
        parsed = parse_s1(text)

        if parsed.get("rationale"):
            print(f"    attempt {attempt}: OK — rationale extracted ({len(parsed['rationale'])} chars)")
            raw_row.update(parsed)
            raw_row["response_text"] = text
            raw_row["parse_error"] = False
            return raw_row

        print(f"    attempt {attempt}: still empty — response[:100]: {repr(text[:100])}")

    print(f"    all {MAX_ATTEMPTS} attempts returned empty rationale; keeping last response")
    raw_row.update(parsed)
    raw_row["response_text"] = text
    raw_row["parse_error"] = False
    return raw_row


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    raw_path = Path(RAW_RESULTS_FILE)
    judged_path = Path(JUDGED_RESULTS_FILE)

    raw_rows = load_jsonl(raw_path)
    raw_by_id = {r["trial_id"]: r for r in raw_rows}
    judged_rows = load_jsonl(judged_path)

    targets = find_malformed(raw_by_id, judged_rows)
    if not targets:
        print("No malformed rows found — nothing to do.")
        return

    print(f"Found {len(targets)} malformed rows to re-run:\n")
    for r in targets:
        print(f"  {r['trial_id']}  {r['scenario']}  "
              f"{r['monitoring_condition']}  {r.get('governance_pattern', '—')}  "
              f"framing={r['framing']}  rep={r['rep']}")
    print()

    client = anthropic.AsyncAnthropic(api_key=api_key)
    fixed_ids: set[str] = set()

    for r in targets:
        tid = r["trial_id"]
        raw_row = raw_by_id[tid]
        print(f"{tid[:8]}…  {r['monitoring_condition']}  {r.get('governance_pattern', '—')}  "
              f"framing={r['framing']}  rep={r['rep']}")
        await rerun_one(client, raw_row)
        fixed_ids.add(tid)

    # Write updated raw_results
    write_jsonl(raw_path, raw_rows)
    print(f"\nUpdated {RAW_RESULTS_FILE} ({len(fixed_ids)} rows refreshed)")

    # Clear judge_error for fixed rows so judge.py re-scores them
    cleared = 0
    for row in judged_rows:
        if row["trial_id"] in fixed_ids:
            for key in ("judge_error", "faithfulness_score", "faithfulness_score_reason"):
                row.pop(key, None)
            cleared += 1

    write_jsonl(judged_path, judged_rows)
    print(f"Cleared judge_error on {cleared} rows in {JUDGED_RESULTS_FILE}")
    print("\nRun python judge.py to score the updated rows.")


if __name__ == "__main__":
    asyncio.run(main())
