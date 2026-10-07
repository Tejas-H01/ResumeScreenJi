from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RankingEvaluationRequest(BaseModel):
    relevance_by_query: list[list[float]] = Field(
        ...,
        description="Each inner list contains relevance labels ordered by predicted ranking.",
    )
    k: int | None = Field(default=None, ge=1)


class RankingEvaluationResponse(BaseModel):
    k: int | None
    query_count: int
    map: float
    ndcg: float


class RolePredictionRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    top_k: int = Field(default=5, ge=1, le=10)


class RolePredictionItem(BaseModel):
    role: str
    confidence: float


class RolePredictionResponse(BaseModel):
    predictions: list[RolePredictionItem]


class ResumeJobMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_text: str = Field(..., min_length=20)


class ResumeJobMatchResponse(BaseModel):
    match_label: int
    match_probability: float
    decision: str


class SkillGapRequest(BaseModel):
    resume_text: str = Field(..., min_length=10)
    job_text: str = Field(..., min_length=10)


class SkillGapResponse(BaseModel):
    resume_skills: list[str]
    job_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    skill_match_score: float


class CandidateScreeningRequest(BaseModel):
    skills: str = Field(..., min_length=2)
    experience_years: float = Field(default=0, ge=0)
    education: str = Field(default="")
    certifications: str = Field(default="")
    job_role: str = Field(..., min_length=2)
    projects_count: int = Field(default=0, ge=0)


class CandidateScreeningResponse(BaseModel):
    decision_label: int
    decision: str
    hire_probability: float
    ai_score: float
    extracted_skills: list[str]


class HybridRecommendationRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_text: str = Field(..., min_length=20)
    experience_years: float | None = Field(default=None, ge=0)
    education: str = Field(default="")
    certifications: str = Field(default="")
    projects_count: int = Field(default=0, ge=0)


class HybridRecommendationResponse(BaseModel):
    final_score: float
    fit_level: str
    role_predictions: list[RolePredictionItem]
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


class ParsedResumeResponse(BaseModel):
    filename: str
    extension: str
    character_count: int
    word_count: int
    text_preview: str


class UploadRecommendationResponse(HybridRecommendationResponse):
    filename: str
    parsed_character_count: int
    parsed_word_count: int
    parsed_text_preview: str


class RankingExportItem(BaseModel):
    filename: str = ""
    final_score: float = 0
    fit_level: str = ""
    match_probability: float = 0
    skill_match_score: float = 0
    screening_decision: str = ""
    hire_probability: float = 0
    ai_score: float = 0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommended_skills: list[str] = Field(default_factory=list)


class RankingExportRequest(BaseModel):
    rankings: list[RankingExportItem] = Field(..., min_length=1)


class RankingExportResponse(BaseModel):
    file_path: str
    filename: str
    rows_exported: int


class FeedbackRequest(BaseModel):
    filename: str
    feedback_type: Literal["good_match", "wrong_match", "hire", "reject", "correct_role", "wrong_role"]
    final_score: float = 0
    fit_level: str = ""
    match_probability: float = 0
    skill_match_score: float = 0
    screening_decision: str = ""
    hire_probability: float = 0
    ai_score: float = 0
    role_predictions: list[RolePredictionItem] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    resume_text: str = ""
    job_text: str = ""
    notes: str = ""


class FeedbackResponse(BaseModel):
    message: str
    file_path: str


class ModelVersionRequest(BaseModel):
    reason: str = "manual_snapshot"


class ModelStatusResponse(BaseModel):
    artifacts: list[dict]
    feedback: dict
    versions: list[dict]
    registry_path: str


class ModelVersionResponse(BaseModel):
    version_id: str
    created_at: str
    reason: str
    version_dir: str
    artifact_count: int
    feedback_rows: int
    copied_artifacts: list[str]


class RetrainResponse(BaseModel):
    message: str
    version: dict
    prepared_feedback: dict
    feedback: dict
    note: str
