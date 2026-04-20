"""
Stratified sample export.

Samples 100 rows from judged_results.jsonl stratified by scenario × monitoring_condition,
then writes:
  results/sample_100.jsonl          — one JSON per line
  results/sample_100_readable.md    — full prompt, response, and scores per trial

Run from the project root: python results/sample_export.py
"""

import json
import math
import random
from pathlib import Path

JUDGED = Path(__file__).parent / "judged_results.jsonl"
OUT_JSONL = Path(__file__).parent / "sample_100.jsonl"
OUT_MD = Path(__file__).parent / "sample_100_readable.md"

TARGET = 100
SEED = 42

# Strata key
def stratum(row: dict) -> str:
    return f"{row.get('scenario','?')}|{row.get('monitoring_condition','?')}"


def load_rows() -> list[dict]:
    rows = []
    with JUDGED.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def stratified_sample(rows: list[dict], n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    by_stratum: dict[str, list[dict]] = {}
    for row in rows:
        k = stratum(row)
        by_stratum.setdefault(k, []).append(row)

    strata = sorted(by_stratum.keys())
    k = len(strata)
    base = n // k
    remainder = n % k

    sampled: list[dict] = []
    for i, s in enumerate(strata):
        pool = by_stratum[s]
        quota = base + (1 if i < remainder else 0)
        take = min(quota, len(pool))
        sampled.extend(rng.sample(pool, take))

    # If total < n due to small strata, top up from remaining rows at random
    sampled_ids = {r["trial_id"] for r in sampled}
    remaining = [r for r in rows if r["trial_id"] not in sampled_ids]
    shortfall = n - len(sampled)
    if shortfall > 0 and remaining:
        sampled.extend(rng.sample(remaining, min(shortfall, len(remaining))))

    rng.shuffle(sampled)
    return sampled


def score_summary(row: dict) -> str:
    scen = row.get("scenario")
    if scen == "S1":
        return (
            f"compliance_score={row.get('compliance_score','—')}  "
            f"faithfulness_score={row.get('faithfulness_score','—')}  "
            f"limit_breach={row.get('limit_breach','—')}"
        )
    if scen == "S2":
        return (
            f"exploitation_score={row.get('exploitation_score','—')}  "
            f"methodology={row.get('methodology','—')}  "
            f"volatility={row.get('volatility_value','—')}"
        )
    if scen == "S3":
        return (
            f"narrative_score={row.get('narrative_score','—')}  "
            f"faithfulness_score={row.get('faithfulness_score','—')}  "
            f"monitoring_awareness_flag={row.get('monitoring_awareness_flag','—')}"
        )
    return "—"


def to_markdown(rows: list[dict]) -> str:
    lines = [
        "# Governance Experiment v2 — Sample Export (100 trials)",
        "",
        f"Stratified by scenario × monitoring_condition. Seed={SEED}.",
        "",
    ]
    for i, row in enumerate(rows, 1):
        scen = row.get("scenario", "?")
        mon = row.get("monitoring_condition", "?")
        pat = row.get("governance_pattern") or "—"
        framing = row.get("framing", "?")
        rep = row.get("rep", "?")
        trial_id = row.get("trial_id", "?")

        lines += [
            f"---",
            f"## Trial {i} — {scen} | {mon} | {pat} | framing={framing} rep={rep}",
            f"**trial_id:** `{trial_id}`  **timestamp:** {row.get('timestamp','?')}",
            "",
            f"**Scores:** {score_summary(row)}",
            "",
        ]

        # Response text
        resp = row.get("response_text") or row.get("raw_rationale") or ""
        if resp:
            lines += ["**Response:**", "```", resp.strip(), "```", ""]

        # Judge reasoning (if present)
        for key in ("faithfulness_score_reason", "narrative_score_reason",
                    "monitoring_awareness_reason"):
            val = row.get(key)
            if val:
                label = key.replace("_", " ").title()
                lines.append(f"**{label}:** {val}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    if not JUDGED.exists():
        raise FileNotFoundError(f"{JUDGED} not found. Run judge.py first.")

    rows = load_rows()
    print(f"Loaded {len(rows)} rows from {JUDGED.name}")

    sample = stratified_sample(rows, TARGET, SEED)
    print(f"Sampled {len(sample)} rows across "
          f"{len({stratum(r) for r in sample})} strata")

    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for row in sample:
            f.write(json.dumps(row) + "\n")
    print(f"Written: {OUT_JSONL}")

    OUT_MD.write_text(to_markdown(sample), encoding="utf-8")
    print(f"Written: {OUT_MD}")


if __name__ == "__main__":
    main()
