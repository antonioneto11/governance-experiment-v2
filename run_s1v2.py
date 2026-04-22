"""
S1-only batch run appending to results/raw_results_s1v2.jsonl.

Uses the updated S1_USER_TURNS (add +$1.6M → post-trade $5.2M / 10.4% NAV).
Does not touch raw_results.jsonl.

Trial count: 4 monitoring × 4 patterns × 3 framings × REPS_PER_CELL = 1,440
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from tqdm.asyncio import tqdm as atqdm

from config import (
    AGENT_MODEL,
    FRAMINGS,
    GOVERNANCE_PATTERNS,
    MONITORING_CONDITIONS,
    REPS_PER_CELL,
    RESULTS_DIR,
    SEMAPHORE_CAP,
)
from runner import assemble_system_prompt, get_user_turn, parse_s1

OUTPUT_FILE = "results/raw_results_s1v2.jsonl"


def build_s1_trials() -> list[dict]:
    trials = []
    for mon in MONITORING_CONDITIONS:
        for pat in GOVERNANCE_PATTERNS:
            for framing in FRAMINGS:
                for rep in range(REPS_PER_CELL):
                    trials.append({
                        "scenario": "S1",
                        "monitoring_condition": mon,
                        "governance_pattern": pat,
                        "framing": framing,
                        "rep": rep,
                    })
    return trials


async def call_agent(
    client: anthropic.AsyncAnthropic,
    system_prompt: str,
    user_turn: str,
    semaphore: asyncio.Semaphore,
) -> str:
    async with semaphore:
        response = await client.messages.create(
            model=AGENT_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_turn}],
        )
    return response.content[0].text


async def run_trial(
    client: anthropic.AsyncAnthropic,
    trial: dict,
    semaphore: asyncio.Semaphore,
    write_lock: asyncio.Lock,
    out_path: Path,
) -> None:
    trial_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    system_prompt = assemble_system_prompt(trial)
    user_turn = get_user_turn(trial)

    parse_error = False
    parsed = {}

    try:
        response_text = await call_agent(client, system_prompt, user_turn, semaphore)
        parsed = parse_s1(response_text)
        parsed["response_text"] = response_text
    except Exception as exc:
        parse_error = True
        parsed = {"error": str(exc)}

    row = {
        "trial_id": trial_id,
        "scenario": trial["scenario"],
        "monitoring_condition": trial["monitoring_condition"],
        "governance_pattern": trial["governance_pattern"],
        "framing": trial["framing"],
        "rep": trial["rep"],
        "timestamp": timestamp,
        "parse_error": parse_error,
        **parsed,
    }

    async with write_lock:
        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")


async def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set.")

    Path(RESULTS_DIR).mkdir(exist_ok=True)
    out_path = Path(OUTPUT_FILE)

    trials = build_s1_trials()
    print(f"S1v2 trials: {len(trials)}  (REPS_PER_CELL={REPS_PER_CELL})")
    print(f"Output: {OUTPUT_FILE}")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    semaphore = asyncio.Semaphore(SEMAPHORE_CAP)
    write_lock = asyncio.Lock()

    tasks = [
        run_trial(client, trial, semaphore, write_lock, out_path)
        for trial in trials
    ]

    await atqdm.gather(*tasks, desc="Running S1v2 trials")
    print(f"\nDone. Results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
