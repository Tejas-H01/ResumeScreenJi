from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from services.preprocessing import basic_clean_text
from services.skills import extract_skills_from_many, skills_to_text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

SCREENING_CLEANED_PATH = PROCESSED_DIR / "screening_cleaned.csv"
DECISION_MODEL_PATH = MODELS_DIR / "screening_decision_model.pkl"
SCORE_MODEL_PATH = MODELS_DIR / "screening_score_model.pkl"
SCREENING_METRICS_PATH = OUTPUTS_DIR / "screening_model_metrics.csv"
SCREENING_REPORT_PATH = OUTPUTS_DIR / "screening_decision_report.csv"
ACTIVE_SCREENING_MODEL_PATH = MODELS_DIR / "active_screening_model.json"

TEXT_COLUMNS = ["skills", "certifications"]
CATEGORICAL_COLUMNS = ["education", "job_role"]
NUMERIC_COLUMNS = ["experience_years", "projects_count"]


@dataclass(frozen=True)
class ScreeningTrainingResult:
    rows: int
    positive_rows: int
    negative_rows: int
    decision_accuracy: float
    decision_precision: float
    decision_recall: float
    decision_f1: float
    decision_roc_auc: float
    decision_cv_f1_mean: float
    score_mae: float
    score_rmse: float
    score_r2: float
    decision_model_path: str
    score_model_path: str


def load_screening_training_data(path: Path = SCREENING_CLEANED_PATH) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = frame.dropna(subset=["skills", "job_role", "decision_label", "ai_score"])
    frame["profile_text"] = frame.apply(build_profile_text, axis=1)
    return frame


def build_profile_text(row: pd.Series | dict[str, object]) -> str:
    values = [
        row.get("skills", ""),
        row.get("certifications", ""),
        row.get("education", ""),
        row.get("job_role", ""),
    ]
    extracted = extract_skills_from_many(values)
    return basic_clean_text(" ".join([str(value) for value in values] + [skills_to_text(extracted)]))


def build_feature_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            (
                "text",
                TfidfVectorizer(
                    preprocessor=basic_clean_text,
                    tokenizer=str.split,
                    token_pattern=None,
                    lowercase=False,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=5_000,
                ),
                "profile_text",
            ),
            ("category", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ("numeric", StandardScaler(), NUMERIC_COLUMNS),
        ]
    )


def build_decision_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("features", build_feature_preprocessor()),
            (
                "classifier",
                LogisticRegression(class_weight="balanced", max_iter=1000, solver="liblinear", random_state=42),
            ),
        ]
    )


def build_score_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("features", build_feature_preprocessor()),
            (
                "regressor",
                RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=1),
            ),
        ]
    )


def evaluate_decision_cv(features: pd.DataFrame, labels: pd.Series) -> float:
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_validate(
        build_decision_model(),
        features,
        labels,
        cv=splitter,
        scoring={"f1": "f1"},
        n_jobs=-1,
        error_score="raise",
    )
    return float(scores["test_f1"].mean())


def train_screening_models(
    data_path: Path = SCREENING_CLEANED_PATH,
    decision_model_path: Path = DECISION_MODEL_PATH,
    score_model_path: Path = SCORE_MODEL_PATH,
    metrics_path: Path = SCREENING_METRICS_PATH,
    report_path: Path = SCREENING_REPORT_PATH,
) -> ScreeningTrainingResult:
    frame = load_screening_training_data(data_path)
    feature_columns = ["profile_text", *CATEGORICAL_COLUMNS, *NUMERIC_COLUMNS]
    features = frame[feature_columns]
    decision_labels = frame["decision_label"].astype(int)
    scores = frame["ai_score"].astype(float)

    x_train, x_test, y_train_decision, y_test_decision, y_train_score, y_test_score = train_test_split(
        features,
        decision_labels,
        scores,
        test_size=0.2,
        random_state=42,
        stratify=decision_labels,
    )

    cv_f1 = evaluate_decision_cv(features, decision_labels)

    decision_model = build_decision_model()
    decision_model.fit(x_train, y_train_decision)
    decision_predictions = decision_model.predict(x_test)
    decision_probabilities = decision_model.predict_proba(x_test)[:, 1]

    score_model = build_score_model()
    score_model.fit(x_train, y_train_score)
    score_predictions = np.clip(score_model.predict(x_test), 0, 100)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(decision_model, decision_model_path)
    joblib.dump(score_model, score_model_path)

    result = ScreeningTrainingResult(
        rows=len(frame),
        positive_rows=int(decision_labels.sum()),
        negative_rows=int((decision_labels == 0).sum()),
        decision_accuracy=float(accuracy_score(y_test_decision, decision_predictions)),
        decision_precision=float(precision_score(y_test_decision, decision_predictions, zero_division=0)),
        decision_recall=float(recall_score(y_test_decision, decision_predictions, zero_division=0)),
        decision_f1=float(f1_score(y_test_decision, decision_predictions, zero_division=0)),
        decision_roc_auc=float(roc_auc_score(y_test_decision, decision_probabilities)),
        decision_cv_f1_mean=cv_f1,
        score_mae=float(mean_absolute_error(y_test_score, score_predictions)),
        score_rmse=float(np.sqrt(mean_squared_error(y_test_score, score_predictions))),
        score_r2=float(r2_score(y_test_score, score_predictions)),
        decision_model_path=str(decision_model_path),
        score_model_path=str(score_model_path),
    )

    pd.DataFrame([asdict(result)]).to_csv(metrics_path, index=False)
    pd.DataFrame(
        classification_report(y_test_decision, decision_predictions, output_dict=True, zero_division=0)
    ).transpose().to_csv(report_path)
    ACTIVE_SCREENING_MODEL_PATH.write_text(
        json.dumps(
            {
                "decision_model": str(decision_model_path),
                "score_model": str(score_model_path),
                "metrics": str(metrics_path),
                "report": str(report_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return result


def load_screening_models(
    decision_model_path: Path = DECISION_MODEL_PATH,
    score_model_path: Path = SCORE_MODEL_PATH,
) -> tuple[Pipeline, Pipeline]:
    return joblib.load(decision_model_path), joblib.load(score_model_path)


def predict_screening(
    skills: str,
    experience_years: float,
    education: str,
    certifications: str,
    job_role: str,
    projects_count: int = 0,
) -> dict[str, float | int | str | list[str]]:
    row = {
        "skills": skills,
        "experience_years": experience_years,
        "education": education,
        "certifications": certifications,
        "job_role": job_role,
        "projects_count": projects_count,
    }
    row["profile_text"] = build_profile_text(row)
    frame = pd.DataFrame([row])[["profile_text", *CATEGORICAL_COLUMNS, *NUMERIC_COLUMNS]]

    decision_model, score_model = load_screening_models()
    hire_probability = float(decision_model.predict_proba(frame)[0, 1])
    if hasattr(score_model.named_steps.get("regressor"), "n_jobs"):
        score_model.named_steps["regressor"].n_jobs = 1
    predicted_score = float(np.clip(score_model.predict(frame)[0], 0, 100))
    decision_label = int(hire_probability >= 0.5)
    return {
        "decision_label": decision_label,
        "decision": "Hire" if decision_label else "Reject",
        "hire_probability": hire_probability,
        "ai_score": predicted_score,
        "extracted_skills": extract_skills_from_many([skills, certifications]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train AI screening decision and score models.")
    return parser.parse_args()


def main() -> None:
    parse_args()
    result = train_screening_models()
    for key, value in asdict(result).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
