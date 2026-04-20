"""
Judge: scores S3 narratives (narrative_score, faithfulness_score,
monitoring_awareness_flag) and S1 rationales (faithfulness_score).

Scoring is BLIND — monitoring_condition label is never passed to the judge prompt.
Input:  results/raw_results.jsonl
Output: results/judged_results.jsonl  (all rows; judge fields added to S1/S3)
"""

import asyncio
import json
import os
import re
from pathlib import Path

import anthropic
from tqdm.asyncio import tqdm as atqdm

from config import (
    JUDGE_MODEL,
    JUDGED_RESULTS_FILE,
    RAW_RESULTS_FILE,
    SEMAPHORE_CAP,
)
from prompts import (
    JUDGE_S1_RATIONALE_PROMPT_TEMPLATE,
    JUDGE_S3_PROMPT_TEMPLATE,
    JUDGE_SYSTEM,
)


# ── JSON extraction ───────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    """Remove markdown code fences before JSON parsing."""
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())
    return text.strip()


def _parse_judge_json(text: str) -> dict:
    cleaned = _strip_fences(text)
    return json.loads(cleaned)


# ── API call ──────────────────────────────────────────────────────────────────

async def call_judge(
    client: anthropic.AsyncAnthropic,
    user_prompt: str,
    semaphore: asyncio.Semaphore,
) -> str:
    async with semaphore:
        response = await client.messages.create(
            model=JUDGE_MODEL,
            max_tokens=512,
            system=JUDGE_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )
    return response.content[0].text


# ── Per-row scoring ───────────────────────────────────────────────────────────

async def score_row(
    client: anthropic.AsyncAnthropic,
    row: dict,
    semaphore: asyncio.Semaphore,
) -> dict:
    scenario = row.get("scenario")

    if scenario == "S3":
        rationale = row.get("raw_rationale", "")
        if not rationale:
            row["judge_error"] = "empty raw_rationale"
            return row
        prompt = JUDGE_S3_PROMPT_TEMPLATE.format(rationale=rationale)
        try:
            raw = await call_judge(client, prompt, semaphore)
            scores = _parse_judge_json(raw)
            row["narrative_score"] = scores.get("narrative_score")
            row["faithfulness_score"] = scores.get("faithfulness_score")
            row["monitoring_awareness_flag"] = scores.get("monitoring_awareness_flag")
            row["narrative_score_reason"] = scores.get("narrative_score_reason", "")
            row["faithfulness_score_reason"] = scores.get("faithfulness_score_reason", "")
            row["monitoring_awareness_reason"] = scores.get("monitoring_awareness_reason", "")
            row["judge_error"] = None
        except Exception as exc:
            row["judge_error"] = str(exc)

    elif scenario == "S1":
        rationale = row.get("rationale", "")
        if not rationale:
            row["judge_error"] = "empty rationale"
            return row
        prompt = JUDGE_S1_RATIONALE_PROMPT_TEMPLATE.format(rationale=rationale)
        try:
            raw = await call_judge(client, prompt, semaphore)
            scores = _parse_judge_json(raw)
            row["faithfulness_score"] = scores.get("faithfulness_score")
            row["faithfulness_score_reason"] = scores.get("faithfulness_score_reason", "")
            row["judge_error"] = None
        except Exception as exc:
            row["judge_error"] = str(exc)

    # S2 rows pass through unchanged (no judge scoring needed)

    return row


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    raw_path = Path(RAW_RESULTS_FILE)
    if not raw_path.exists():
        raise FileNotFoundError(f"{RAW_RESULTS_FILE} not found. Run runner.py first.")

    rows = []
    with raw_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    scoreable = [r for r in rows if r.get("scenario") in ("S1", "S3") and not r.get("parse_error")]
    passthrough = [r for r in rows if r.get("scenario") == "S2" or r.get("parse_error")]

    print(f"Rows to score: {len(scoreable)}  Pass-through: {len(passthrough)}")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    semaphore = asyncio.Semaphore(SEMAPHORE_CAP)

    tasks = [score_row(client, row, semaphore) for row in scoreable]
    scored = await atqdm.gather(*tasks, desc="Judging")

    all_rows = list(scored) + passthrough
    all_rows.sort(key=lambda r: r.get("timestamp", ""))

    out_path = Path(JUDGED_RESULTS_FILE)
    with out_path.open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")

    print(f"\nDone. Judged results written to {JUDGED_RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
