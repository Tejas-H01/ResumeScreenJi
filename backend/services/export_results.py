from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

EXPORT_HEADERS = [
    "rank",
    "filename",
    "final_score",
    "fit_level",
    "match_probability",
    "skill_match_score",
    "screening_decision",
    "hire_probability",
    "ai_score",
    "matched_skills",
    "missing_skills",
    "recommended_skills",
]


def _join_skills(value: list[str] | None) -> str:
    return "; ".join(value or [])


def export_rankings(rows: list[dict]) -> dict[str, int | str]:
    if not rows:
        raise ValueError("No ranking rows were provided.")

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUTS_DIR / f"resume_rankings_{timestamp}.csv"

    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPORT_HEADERS)
        writer.writeheader()
        for index, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    "rank": index,
                    "filename": row.get("filename", ""),
                    "final_score": row.get("final_score", ""),
                    "fit_level": row.get("fit_level", ""),
                    "match_probability": row.get("match_probability", ""),
                    "skill_match_score": row.get("skill_match_score", ""),
                    "screening_decision": row.get("screening_decision", ""),
                    "hire_probability": row.get("hire_probability", ""),
                    "ai_score": row.get("ai_score", ""),
                    "matched_skills": _join_skills(row.get("matched_skills")),
                    "missing_skills": _join_skills(row.get("missing_skills")),
                    "recommended_skills": _join_skills(row.get("recommended_skills")),
                }
            )

    return {
        "file_path": str(output_path),
        "filename": output_path.name,
        "rows_exported": len(rows),
    }
