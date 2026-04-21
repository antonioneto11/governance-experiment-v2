"""
Re-runs a specific set of trial_ids by calling the agent API again,
then updates raw_results.jsonl in-place (same trial_id, fresh response).
Clears judge_error in judged_results.jsonl so judge.py will re-score them.

Usage:
  python rerun_targeted.py <trial_id> [<trial_id> ...]
  python rerun_targeted.py --table-failures   # re-runs the 4 known table-format rows
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import anthropic

from config import AGENT_MODEL, JUDGED_RESULTS_FILE, RAW_RESULTS_FILE, SEMAPHORE_CAP
from runner import assemble_system_prompt, get_user_turn, parse_s1, parse_s2, parse_s3

# The 4 known table-format trial_ids
TABLE_FAILURE_IDS = [
    "eb137e2e-6ea2-45ed-91b2-0d0abbbf376f",
    "990eb90e-4fbf-42aa-863d-964170de661b",
    "55d89d3c-35e3-4d55-a03d-20de82a3ccf9",
    "f5910b04-353e-4de4-b6ee-cfb75ff569ec",
]

MAX_ATTEMPTS = 3  # retry each cell until rationale is non-empty


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


async def call_agent_once(
    client: anthropic.AsyncAnthropic,
    system_prompt: str,
    user_turn: str,
) -> str:
    response = await client.messages.create(
        model=AGENT_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_turn}],
    )
    return response.content[0].text


def parse_row(scenario: str, text: str) -> dict:
    if scenario == "S1":
        return parse_s1(text)
    if scenario == "S2":
        return parse_s2(text)
    return parse_s3(text)


def rationale_empty(scenario: str, parsed: dict) -> bool:
    if scenario == "S1":
        return not parsed.get("rationale", "")
    if scenario == "S3":
        return not parsed.get("raw_rationale", "")
    return False  # S2 has no rationale to check


async def rerun_trials(trial_ids: list[str]) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    raw_path = Path(RAW_RESULTS_FILE)
    judged_path = Path(JUDGED_RESULTS_FILE)

    raw_rows = load_jsonl(raw_path)
    raw_by_id = {r["trial_id"]: r for r in raw_rows}

    missing = [tid for tid in trial_ids if tid not in raw_by_id]
    if missing:
        print(f"WARNING: trial_ids not found in raw_results.jsonl: {missing}")
        trial_ids = [tid for tid in trial_ids if tid in raw_by_id]

    if not trial_ids:
        print("No valid trial_ids to process.")
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)

    for trial_id in trial_ids:
        original = raw_by_id[trial_id]
        scenario = original["scenario"]
        system_prompt = assemble_system_prompt(original)
        user_turn = get_user_turn(original)

        print(f"\n{trial_id[:8]}…  {scenario} | {original['monitoring_condition']} | "
              f"{original.get('governance_pattern','—')} | framing={original['framing']} rep={original['rep']}")

        parsed = {}
        response_text = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response_text = await call_agent_once(client, system_prompt, user_turn)
                parsed = parse_row(scenario, response_text)
                if not rationale_empty(scenario, parsed):
                    print(f"  attempt {attempt}: OK — rationale extracted")
                    break
                print(f"  attempt {attempt}: empty rationale again, retrying…")
            except Exception as exc:
                print(f"  attempt {attempt}: API error — {exc}")
                response_text = ""
                parsed = {"error": str(exc)}
        else:
            print(f"  all {MAX_ATTEMPTS} attempts returned empty rationale — keeping last response")

        # Update the row in-place, preserving trial_id and metadata
        original.update(parsed)
        original["response_text"] = response_text
        original["parse_error"] = bool(parsed.get("error"))

    # Write updated raw_results
    write_jsonl(raw_path, raw_rows)
    print(f"\nUpdated {RAW_RESULTS_FILE}")

    # Clear judge_error for these trial_ids in judged_results so judge.py re-scores them
    if judged_path.exists():
        judged_rows = load_jsonl(judged_path)
        cleared = 0
        for row in judged_rows:
            if row["trial_id"] in set(trial_ids) and row.get("judge_error"):
                row.pop("judge_error", None)
                row.pop("faithfulness_score", None)
                row.pop("faithfulness_score_reason", None)
                cleared += 1
        write_jsonl(judged_path, judged_rows)
        print(f"Cleared judge_error on {cleared} rows in {JUDGED_RESULTS_FILE}")

    print("\nDone. Run python judge.py to score the updated rows.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-run specific trials by trial_id.")
    parser.add_argument("trial_ids", nargs="*", help="trial_ids to re-run")
    parser.add_argument("--table-failures", action="store_true",
                        help="Re-run the 4 known table-format failures")
    args = parser.parse_args()

    ids = list(args.trial_ids)
    if args.table_failures:
        ids = TABLE_FAILURE_IDS

    if not ids:
        parser.print_help()
        sys.exit(1)

    asyncio.run(rerun_trials(ids))


if __name__ == "__main__":
    main()
