from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.schemas import (
    CandidateScreeningRequest,
    CandidateScreeningResponse,
    FeedbackRequest,
    FeedbackResponse,
    HybridRecommendationRequest,
    HybridRecommendationResponse,
    ModelStatusResponse,
    ModelVersionRequest,
    ModelVersionResponse,
    ParsedResumeResponse,
    RankingExportRequest,
    RankingExportResponse,
    RankingEvaluationRequest,
    RankingEvaluationResponse,
    RetrainResponse,
    ResumeJobMatchRequest,
    ResumeJobMatchResponse,
    SkillGapRequest,
    SkillGapResponse,
    UploadRecommendationResponse,
    RolePredictionRequest,
    RolePredictionResponse,
)
from services.evaluation import ranking_report
from services.export_results import export_rankings
from services.feedback_store import save_feedback
from services.matching_model import predict_match_score
from services.model_registry import create_model_version, model_status
from services.model import predict_role
from services.parser import ResumeParsingError, extract_text_from_bytes
from services.recommender import recommend_as_dict
from services.retraining import retraining_plan
from services.screening_model import predict_screening
from services.skills import calculate_skill_gap

router = APIRouter(prefix="/api", tags=["resume-screening"])


@router.post("/evaluate-ranking", response_model=RankingEvaluationResponse)
def evaluate_ranking(payload: RankingEvaluationRequest) -> dict[str, float | int | None]:
    return ranking_report(payload.relevance_by_query, payload.k)


@router.post("/predict-role", response_model=RolePredictionResponse)
def predict_resume_role(payload: RolePredictionRequest) -> dict[str, list[dict[str, float | str]]]:
    return {"predictions": predict_role(payload.resume_text, payload.top_k)}


@router.post("/predict-match", response_model=ResumeJobMatchResponse)
def predict_resume_job_match(payload: ResumeJobMatchRequest) -> dict[str, float | int | str]:
    return predict_match_score(payload.resume_text, payload.job_text)


@router.post("/analyze-skills", response_model=SkillGapResponse)
def analyze_skill_gap(payload: SkillGapRequest) -> dict[str, float | list[str]]:
    return calculate_skill_gap(payload.resume_text, payload.job_text).__dict__


@router.post("/screen-candidate", response_model=CandidateScreeningResponse)
def screen_candidate(payload: CandidateScreeningRequest) -> dict[str, float | int | str | list[str]]:
    return predict_screening(
        skills=payload.skills,
        experience_years=payload.experience_years,
        education=payload.education,
        certifications=payload.certifications,
        job_role=payload.job_role,
        projects_count=payload.projects_count,
    )


@router.post("/recommend", response_model=HybridRecommendationResponse)
def recommend_candidate(payload: HybridRecommendationRequest) -> dict[str, object]:
    return recommend_as_dict(
        resume_text=payload.resume_text,
        job_text=payload.job_text,
        experience_years=payload.experience_years,
        education=payload.education,
        certifications=payload.certifications,
        projects_count=payload.projects_count,
    )


@router.post("/parse-resume", response_model=ParsedResumeResponse)
async def parse_resume(file: UploadFile = File(...)) -> dict[str, int | str]:
    try:
        parsed = extract_text_from_bytes(await file.read(), file.filename or "resume")
    except ResumeParsingError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "filename": parsed.filename,
        "extension": parsed.extension,
        "character_count": parsed.character_count,
        "word_count": parsed.word_count,
        "text_preview": parsed.text[:1000],
    }


@router.post("/recommend-upload", response_model=UploadRecommendationResponse)
async def recommend_uploaded_resume(
    file: UploadFile = File(...),
    job_text: str = Form(..., min_length=20),
    experience_years: float | None = Form(default=None, ge=0),
    education: str = Form(default=""),
    certifications: str = Form(default=""),
    projects_count: int = Form(default=0, ge=0),
) -> dict[str, object]:
    try:
        parsed = extract_text_from_bytes(await file.read(), file.filename or "resume")
    except ResumeParsingError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    recommendation = recommend_as_dict(
        resume_text=parsed.text,
        job_text=job_text,
        experience_years=experience_years,
        education=education,
        certifications=certifications,
        projects_count=projects_count,
    )
    return {
        **recommendation,
        "filename": parsed.filename,
        "parsed_character_count": parsed.character_count,
        "parsed_word_count": parsed.word_count,
        "parsed_text_preview": parsed.text[:1000],
    }


@router.post("/export-rankings", response_model=RankingExportResponse)
def export_ranking_results(payload: RankingExportRequest) -> dict[str, int | str]:
    try:
        return export_rankings([item.model_dump() for item in payload.rankings])
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest) -> dict[str, str]:
    return save_feedback(payload.model_dump())


@router.get("/model-status", response_model=ModelStatusResponse)
def get_model_status() -> dict[str, object]:
    return model_status()


@router.post("/create-model-version", response_model=ModelVersionResponse)
def create_version(payload: ModelVersionRequest) -> dict[str, object]:
    return create_model_version(reason=payload.reason)


@router.post("/retrain", response_model=RetrainResponse)
def retrain_models() -> dict[str, object]:
    return retraining_plan()
