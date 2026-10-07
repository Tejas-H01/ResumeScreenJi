from __future__ import annotations

from dataclasses import asdict, dataclass

from services.matching_model import predict_match_score
from services.model import predict_role
from services.preprocessing import basic_clean_text
from services.screening_model import predict_screening
from services.skills import calculate_skill_gap, skills_to_text


DEFAULT_WEIGHTS = {
    "match_probability": 0.35,
    "skill_match": 0.25,
    "screening_score": 0.25,
    "role_confidence": 0.15,
}


@dataclass(frozen=True)
class HybridRecommendation:
    final_score: float
    fit_level: str
    role_predictions: list[dict[str, float | str]]
    match_probability: float
    match_decision: str
    skill_match_score: float
    screening_decision: str
    hire_probability: float
    ai_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    recommended_skills: list[str]
    resume_skills: list[str]
    job_skills: list[str]
    score_breakdown: dict[str, float]


def fit_level_from_score(score: float) -> str:
    if score >= 85:
        return "Strong Fit"
    if score >= 70:
        return "Good Fit"
    if score >= 55:
        return "Moderate Fit"
    return "Weak Fit"


def normalize_role(role: str) -> str:
    return role.strip().lower().replace("-", " ")


def lexical_similarity(left: str, right: str) -> float:
    left_tokens = set(basic_clean_text(left).split())
    right_tokens = set(basic_clean_text(right).split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))


def fallback_role_predictions(skill_gap) -> list[dict[str, float | str]]:
    if {"machine learning", "deep learning", "nlp", "scikit learn"}.intersection(skill_gap.resume_skills):
        return [{"role": "Data Science", "confidence": 0.55}]
    if {"react", "javascript", "typescript", "html", "css"}.intersection(skill_gap.resume_skills):
        return [{"role": "Web Developer", "confidence": 0.55}]
    if {"aws", "docker", "kubernetes", "ci cd"}.intersection(skill_gap.resume_skills):
        return [{"role": "DevOps Engineer", "confidence": 0.55}]
    return [{"role": "General", "confidence": 0.35}]


def fallback_match_score(resume_text: str, job_text: str, skill_match_score: float) -> dict[str, float | int | str]:
    probability = round((lexical_similarity(resume_text, job_text) * 0.4) + (skill_match_score * 0.6), 4)
    prediction = int(probability >= 0.45)
    return {
        "match_label": prediction,
        "match_probability": probability,
        "decision": "match" if prediction else "review",
    }


def fallback_screening_score(skill_match_score: float, experience_years: float, projects_count: int) -> dict[str, object]:
    experience_component = min(max(experience_years, 0) / 5, 1) * 20
    project_component = min(max(projects_count, 0) / 4, 1) * 10
    ai_score = round((skill_match_score * 70) + experience_component + project_component, 2)
    hire_probability = round(min(max(ai_score / 100, 0), 1), 4)
    return {
        "decision_label": int(hire_probability >= 0.5),
        "decision": "Hire" if hire_probability >= 0.5 else "Review",
        "hire_probability": hire_probability,
        "ai_score": ai_score,
        "extracted_skills": [],
    }


def infer_experience_years(resume_text: str) -> float:
    text = resume_text.lower()
    import re

    matches = re.findall(r"(\d{1,2})\+?\s*(?:years|year|yrs|yr)", text)
    if not matches:
        return 0.0
    return float(max(int(value) for value in matches))


def recommend_from_resume_and_job(
    resume_text: str,
    job_text: str,
    experience_years: float | None = None,
    education: str = "",
    certifications: str = "",
    projects_count: int = 0,
    weights: dict[str, float] | None = None,
) -> HybridRecommendation:
    active_weights = weights or DEFAULT_WEIGHTS

    skill_gap = calculate_skill_gap(resume_text, job_text)

    inferred_experience = infer_experience_years(resume_text) if experience_years is None else experience_years

    try:
        role_predictions = predict_role(resume_text, top_k=5)
    except Exception:
        role_predictions = fallback_role_predictions(skill_gap)
    top_role = str(role_predictions[0]["role"]) if role_predictions else "unknown"
    role_confidence = float(role_predictions[0]["confidence"]) if role_predictions else 0.0

    try:
        match_result = predict_match_score(resume_text, job_text)
    except Exception:
        match_result = fallback_match_score(resume_text, job_text, skill_gap.skill_match_score)

    try:
        screening_result = predict_screening(
            skills=skills_to_text(skill_gap.resume_skills),
            experience_years=inferred_experience,
            education=education,
            certifications=certifications,
            job_role=normalize_role(top_role),
            projects_count=projects_count,
        )
    except Exception:
        screening_result = fallback_screening_score(skill_gap.skill_match_score, inferred_experience, projects_count)

    match_probability = float(match_result["match_probability"])
    skill_match_score = float(skill_gap.skill_match_score)
    screening_score = float(screening_result["ai_score"]) / 100.0

    score_breakdown = {
        "match_probability_component": round(match_probability * active_weights["match_probability"] * 100, 4),
        "skill_match_component": round(skill_match_score * active_weights["skill_match"] * 100, 4),
        "screening_score_component": round(screening_score * active_weights["screening_score"] * 100, 4),
        "role_confidence_component": round(role_confidence * active_weights["role_confidence"] * 100, 4),
    }
    final_score = round(sum(score_breakdown.values()), 2)

    return HybridRecommendation(
        final_score=final_score,
        fit_level=fit_level_from_score(final_score),
        role_predictions=role_predictions,
        match_probability=round(match_probability, 4),
        match_decision=str(match_result["decision"]),
        skill_match_score=skill_match_score,
        screening_decision=str(screening_result["decision"]),
        hire_probability=round(float(screening_result["hire_probability"]), 4),
        ai_score=round(float(screening_result["ai_score"]), 2),
        matched_skills=skill_gap.matched_skills,
        missing_skills=skill_gap.missing_skills,
        extra_skills=skill_gap.extra_skills,
        recommended_skills=skill_gap.missing_skills[:8],
        resume_skills=skill_gap.resume_skills,
        job_skills=skill_gap.job_skills,
        score_breakdown=score_breakdown,
    )


def recommend_as_dict(*args, **kwargs) -> dict[str, object]:
    return asdict(recommend_from_resume_and_job(*args, **kwargs))
