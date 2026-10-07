from __future__ import annotations

from pathlib import Path

import pandas as pd

from services.model_registry import create_model_version, feedback_summary


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_PATH = PROJECT_ROOT / "data" / "feedback" / "feedback.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FEEDBACK_MATCHING_PATH = PROCESSED_DIR / "feedback_matching_cleaned.csv"
FEEDBACK_SCREENING_PATH = PROCESSED_DIR / "feedback_screening_cleaned.csv"


MATCH_LABELS = {"good_match": 1, "wrong_match": 0}
SCREENING_LABELS = {"hire": 1, "reject": 0}


def prepare_feedback_training_rows() -> dict[str, object]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if not FEEDBACK_PATH.exists():
        return {"matching_rows": 0, "screening_rows": 0, "message": "No feedback file found."}

    frame = pd.read_csv(FEEDBACK_PATH).fillna("")
    matching_rows = []
    screening_rows = []

    for _, row in frame.iterrows():
        feedback_type = str(row.get("feedback_type", ""))
        resume_text = str(row.get("resume_text", ""))
        job_text = str(row.get("job_text", ""))

        if feedback_type in MATCH_LABELS and resume_text and job_text:
            matching_rows.append(
                {
                    "resume_id": str(row.get("filename", "")),
                    "job_id": "feedback_job",
                    "resume_text": resume_text,
                    "job_text": job_text,
                    "match_label": MATCH_LABELS[feedback_type],
                    "raw_status": feedback_type,
                }
            )

        if feedback_type in SCREENING_LABELS:
            screening_rows.append(
                {
                    "resume_id": str(row.get("filename", "")),
                    "candidate_name": str(row.get("filename", "")),
                    "skills": str(row.get("matched_skills", "")),
                    "experience_years": 0,
                    "education": "",
                    "certifications": "",
                    "job_role": str(row.get("top_role", "")),
                    "decision": feedback_type,
                    "decision_label": SCREENING_LABELS[feedback_type],
                    "salary_expectation": "",
                    "projects_count": 0,
                    "ai_score": float(row.get("ai_score", 0) or 0),
                }
            )

    if matching_rows:
        pd.DataFrame(matching_rows).to_csv(FEEDBACK_MATCHING_PATH, index=False, encoding="utf-8")
    if screening_rows:
        pd.DataFrame(screening_rows).to_csv(FEEDBACK_SCREENING_PATH, index=False, encoding="utf-8")

    return {
        "matching_rows": len(matching_rows),
        "screening_rows": len(screening_rows),
        "matching_path": str(FEEDBACK_MATCHING_PATH) if matching_rows else "",
        "screening_path": str(FEEDBACK_SCREENING_PATH) if screening_rows else "",
    }


def retraining_plan() -> dict[str, object]:
    version = create_model_version(reason="pre_retraining_snapshot")
    prepared = prepare_feedback_training_rows()
    return {
        "message": "Created a model snapshot and prepared feedback rows for the next training cycle.",
        "version": version,
        "prepared_feedback": prepared,
        "feedback": feedback_summary(),
        "note": "Full model retraining should be run after enough validated feedback rows are collected.",
    }
