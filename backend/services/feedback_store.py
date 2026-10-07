from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_DIR = PROJECT_ROOT / "data" / "feedback"
FEEDBACK_PATH = FEEDBACK_DIR / "feedback.csv"

FEEDBACK_HEADERS = [
    "timestamp",
    "filename",
    "feedback_type",
    "final_score",
    "fit_level",
    "match_probability",
    "skill_match_score",
    "screening_decision",
    "hire_probability",
    "ai_score",
    "top_role",
    "matched_skills",
    "missing_skills",
    "resume_text",
    "job_text",
    "notes",
]


def _join_skills(value: list[str] | None) -> str:
    return "; ".join(value or [])


def save_feedback(payload: dict) -> dict[str, str]:
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = FEEDBACK_PATH.exists()
    role_predictions = payload.get("role_predictions") or []
    top_role = role_predictions[0].get("role", "") if role_predictions else ""

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "filename": payload.get("filename", ""),
        "feedback_type": payload.get("feedback_type", ""),
        "final_score": payload.get("final_score", ""),
        "fit_level": payload.get("fit_level", ""),
        "match_probability": payload.get("match_probability", ""),
        "skill_match_score": payload.get("skill_match_score", ""),
        "screening_decision": payload.get("screening_decision", ""),
        "hire_probability": payload.get("hire_probability", ""),
        "ai_score": payload.get("ai_score", ""),
        "top_role": top_role,
        "matched_skills": _join_skills(payload.get("matched_skills")),
        "missing_skills": _join_skills(payload.get("missing_skills")),
        "resume_text": payload.get("resume_text", ""),
        "job_text": payload.get("job_text", ""),
        "notes": payload.get("notes", ""),
    }

    with FEEDBACK_PATH.open("a", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FEEDBACK_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    return {"message": "Feedback saved", "file_path": str(FEEDBACK_PATH)}
