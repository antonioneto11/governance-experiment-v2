"""
Judge: scores S3 narratives (narrative_score, faithfulness_score,
monitoring_awareness_flag) and S1 rationales (faithfulness_score).

Scoring is BLIND — monitoring_condition label is never passed to the judge prompt.
Input:  results/raw_results.jsonl   (first run)
        results/judged_results.jsonl (resume/retry run — re-scores only failed rows)
Output: results/judged_results.jsonl

Re-runnable: on subsequent runs, rows that already have a clean score
(judge_error is None and the relevant score field is not null) are kept as-is;
only rows with judge_error or null scores are re-scored.
"""

import asyncio
import json
import os
import re
import time
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
from runner import parse_s1

# Judge concurrency is capped lower than runner to respect 50 req/min limit.
# At cap=5 with ~2 s latency each, throughput ≈ 150 req/min theoretical max,
# but retries with backoff keep effective rate well under the ceiling.
JUDGE_SEMAPHORE_CAP = min(SEMAPHORE_CAP, 5)

# Retry config for 429 / transient errors
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2.0   # seconds; doubled each attempt


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())
    return text.strip()


def _parse_judge_json(text: str) -> dict:
    return json.loads(_strip_fences(text))


def _needs_scoring(row: dict) -> bool:
    """True if the row requires (re-)scoring."""
    scenario = row.get("scenario")
    if row.get("parse_error"):
        return False
    if scenario == "S2":
        return False
    if row.get("judge_error"):
        return True
    if scenario == "S3":
        return row.get("narrative_score") is None or row.get("faithfulness_score") is None
    if scenario == "S1":
        return row.get("faithfulness_score") is None
    return False


# ── API call with retry ───────────────────────────────────────────────────────

async def call_judge(
    client: anthropic.AsyncAnthropic,
    user_prompt: str,
    semaphore: asyncio.Semaphore,
) -> str:
    delay = RETRY_BASE_DELAY
    last_exc: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                response = await client.messages.create(
                    model=JUDGE_MODEL,
                    max_tokens=512,
                    system=JUDGE_SYSTEM,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                await asyncio.sleep(1)  # 1 s per slot to stay under 50 req/min
            return response.content[0].text
        except anthropic.RateLimitError as exc:
            last_exc = exc
            await asyncio.sleep(delay)
            delay *= 2
        except anthropic.APIStatusError as exc:
            # Retry on 5xx; re-raise immediately on 4xx (except 429 above)
            if exc.status_code >= 500:
                last_exc = exc
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise

    raise RuntimeError(f"Judge call failed after {MAX_RETRIES} retries: {last_exc}") from last_exc


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
        # If the stored rationale is empty but response_text exists, the original
        # parse missed markdown bold formatting (**RATIONALE: ...**). Re-parse now.
        if not rationale and row.get("response_text"):
            reparsed = parse_s1(row["response_text"])
            rationale = reparsed.get("rationale", "")
            if rationale:
                row.update(reparsed)  # backfill fixed parse fields into the row
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

    return row


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    raw_path = Path(RAW_RESULTS_FILE)
    judged_path = Path(JUDGED_RESULTS_FILE)

    if not raw_path.exists():
        raise FileNotFoundError(f"{RAW_RESULTS_FILE} not found. Run runner.py first.")

    # raw_results is always the authoritative source of all trial rows.
    raw_rows: list[dict] = []
    with raw_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                raw_rows.append(json.loads(line))

    # judged_results is a cache: load already-clean scores keyed by trial_id.
    already_scored: dict[str, dict] = {}
    if judged_path.exists():
        with judged_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if not _needs_scoring(r):
                    already_scored[r["trial_id"]] = r

    # Merge: prefer cached score → pass-through (no scoring needed) → queue.
    to_score: list[dict] = []
    skip: list[dict] = []
    for row in raw_rows:
        cached = already_scored.get(row["trial_id"])
        if cached is not None:
            # Already has a clean score from a previous run.
            skip.append(cached)
        elif not _needs_scoring(row):
            # parse_error=True or S2 — pass through as-is from raw_results.
            skip.append(row)
        else:
            to_score.append(row)

    print(
        f"raw_results rows: {len(raw_rows)}  |  "
        f"Already scored (cached): {len(skip)}  |  "
        f"To score: {len(to_score)}"
    )
    if not to_score:
        print("Nothing to score — all rows already have clean results.")
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)
    semaphore = asyncio.Semaphore(JUDGE_SEMAPHORE_CAP)

    tasks = [score_row(client, row, semaphore) for row in to_score]
    scored = list(await atqdm.gather(*tasks, desc="Judging"))

    errors = [r for r in scored if r.get("judge_error")]
    print(f"\nScored: {len(scored) - len(errors)}  |  Errors remaining: {len(errors)}")
    if errors:
        print("  Re-run judge.py to retry failed rows.")

    all_rows = scored + skip
    all_rows.sort(key=lambda r: r.get("timestamp", ""))

    with judged_path.open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")

    print(f"Written: {JUDGED_RESULTS_FILE}  ({len(all_rows)} rows)")


if __name__ == "__main__":
    asyncio.run(main())
