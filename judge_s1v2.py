"""
Judge for S1v2 results only.
Input:  results/raw_results_s1v2.jsonl
Output: results/judged_results_s1v2.jsonl
Does not touch raw_results.jsonl or judged_results.jsonl.
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path

import anthropic
from tqdm.asyncio import tqdm as atqdm

from config import JUDGE_MODEL, SEMAPHORE_CAP
from prompts import JUDGE_S1_RATIONALE_PROMPT_TEMPLATE, JUDGE_SYSTEM
from runner import parse_s1

RAW_FILE = "results/raw_results_s1v2.jsonl"
JUDGED_FILE = "results/judged_results_s1v2.jsonl"

JUDGE_SEMAPHORE_CAP = min(SEMAPHORE_CAP, 5)
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2.0


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text.strip())
    return text.strip()


def _parse_judge_json(text: str) -> dict:
    return json.loads(_strip_fences(text))


def _needs_scoring(row: dict) -> bool:
    if row.get("parse_error"):
        return False
    if row.get("scenario") != "S1":
        return False
    if row.get("judge_error"):
        return True
    return row.get("faithfulness_score") is None


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
                await asyncio.sleep(1)
            return response.content[0].text
        except anthropic.RateLimitError as exc:
            last_exc = exc
            await asyncio.sleep(delay)
            delay *= 2
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                last_exc = exc
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise

    raise RuntimeError(f"Judge call failed after {MAX_RETRIES} retries: {last_exc}") from last_exc


async def score_row(
    client: anthropic.AsyncAnthropic,
    row: dict,
    semaphore: asyncio.Semaphore,
) -> dict:
    rationale = row.get("rationale", "")
    if not rationale and row.get("response_text"):
        reparsed = parse_s1(row["response_text"])
        rationale = reparsed.get("rationale", "")
        if rationale:
            row.update(reparsed)
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


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    raw_path = Path(RAW_FILE)
    judged_path = Path(JUDGED_FILE)

    if not raw_path.exists():
        raise FileNotFoundError(f"{RAW_FILE} not found. Run run_s1v2.py first.")

    raw_rows: list[dict] = []
    with raw_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                raw_rows.append(json.loads(line))

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

    to_score: list[dict] = []
    skip: list[dict] = []
    for row in raw_rows:
        cached = already_scored.get(row["trial_id"])
        if cached is not None:
            skip.append(cached)
        elif not _needs_scoring(row):
            skip.append(row)
        else:
            to_score.append(row)

    print(
        f"raw rows: {len(raw_rows)}  |  "
        f"already scored: {len(skip)}  |  "
        f"to score: {len(to_score)}"
    )
    if not to_score:
        print("Nothing to score — all rows already have clean results.")
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)
    semaphore = asyncio.Semaphore(JUDGE_SEMAPHORE_CAP)

    tasks = [score_row(client, row, semaphore) for row in to_score]
    scored = list(await atqdm.gather(*tasks, desc="Judging S1v2"))

    errors = [r for r in scored if r.get("judge_error")]
    print(f"\nScored: {len(scored) - len(errors)}  |  Errors remaining: {len(errors)}")
    if errors:
        print("  Re-run judge_s1v2.py to retry failed rows.")

    all_rows = scored + skip
    all_rows.sort(key=lambda r: r.get("timestamp", ""))

    with judged_path.open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row) + "\n")

    print(f"Written: {JUDGED_FILE}  ({len(all_rows)} rows)")


if __name__ == "__main__":
    asyncio.run(main())
