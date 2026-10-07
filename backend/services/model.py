from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

from services.feature_extraction import build_tfidf_vectorizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RESUMES_CLEANED_PATH = PROCESSED_DIR / "resumes_cleaned.csv"
ROLE_MODEL_PATH = MODELS_DIR / "role_classifier.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"
ROLE_METRICS_PATH = OUTPUTS_DIR / "role_classifier_metrics.csv"
ROLE_REPORT_PATH = OUTPUTS_DIR / "role_classifier_report.csv"
ACTIVE_MODEL_PATH = MODELS_DIR / "active_model.json"


@dataclass(frozen=True)
class TrainingResult:
    rows: int
    categories: int
    test_accuracy: float
    test_precision_macro: float
    test_recall_macro: float
    test_f1_macro: float
    cv_accuracy_mean: float
    cv_f1_macro_mean: float
    model_path: str
    label_encoder_path: str


def load_resume_training_data(path: Path = RESUMES_CLEANED_PATH) -> tuple[pd.Series, pd.Series]:
    frame = pd.read_csv(path)
    frame = frame.dropna(subset=["resume_text", "category"])
    frame = frame[(frame["resume_text"].astype(str).str.len() > 0) & (frame["category"].astype(str).str.len() > 0)]
    return frame["resume_text"].astype(str), frame["category"].astype(str)


def build_role_classifier() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", build_tfidf_vectorizer()),
            ("classifier", LinearSVC(class_weight="balanced", random_state=42)),
        ]
    )


def build_calibrated_role_classifier() -> Pipeline:
    base_classifier = LinearSVC(class_weight="balanced", random_state=42)
    return Pipeline(
        steps=[
            ("tfidf", build_tfidf_vectorizer()),
            ("classifier", CalibratedClassifierCV(base_classifier, cv=3)),
        ]
    )


def evaluate_with_cross_validation(model: Pipeline, texts: pd.Series, labels: pd.Series) -> dict[str, float]:
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_validate(
        model,
        texts,
        labels,
        cv=splitter,
        scoring={
            "accuracy": "accuracy",
            "f1_macro": "f1_macro",
            "precision_macro": "precision_macro",
            "recall_macro": "recall_macro",
        },
        n_jobs=-1,
        error_score="raise",
    )
    return {key: float(value.mean()) for key, value in scores.items() if key.startswith("test_")}


def train_role_classifier(
    data_path: Path = RESUMES_CLEANED_PATH,
    model_path: Path = ROLE_MODEL_PATH,
    label_encoder_path: Path = LABEL_ENCODER_PATH,
    metrics_path: Path = ROLE_METRICS_PATH,
    report_path: Path = ROLE_REPORT_PATH,
) -> TrainingResult:
    texts, categories = load_resume_training_data(data_path)

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(categories)

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        encoded_labels,
        test_size=0.2,
        random_state=42,
        stratify=encoded_labels,
    )

    cv_model = build_role_classifier()
    cv_scores = evaluate_with_cross_validation(cv_model, texts, encoded_labels)

    final_model = build_calibrated_role_classifier()
    final_model.fit(x_train, y_train)
    predictions = final_model.predict(x_test)

    target_names = [str(label) for label in label_encoder.classes_]
    report = classification_report(y_test, predictions, target_names=target_names, output_dict=True, zero_division=0)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, model_path)
    joblib.dump(label_encoder, label_encoder_path)

    result = TrainingResult(
        rows=len(texts),
        categories=len(label_encoder.classes_),
        test_accuracy=float(accuracy_score(y_test, predictions)),
        test_precision_macro=float(precision_score(y_test, predictions, average="macro", zero_division=0)),
        test_recall_macro=float(recall_score(y_test, predictions, average="macro", zero_division=0)),
        test_f1_macro=float(f1_score(y_test, predictions, average="macro", zero_division=0)),
        cv_accuracy_mean=cv_scores["test_accuracy"],
        cv_f1_macro_mean=cv_scores["test_f1_macro"],
        model_path=str(model_path),
        label_encoder_path=str(label_encoder_path),
    )

    pd.DataFrame([asdict(result)]).to_csv(metrics_path, index=False)
    pd.DataFrame(report).transpose().to_csv(report_path)

    ACTIVE_MODEL_PATH.write_text(
        json.dumps(
            {
                "role_classifier": str(model_path),
                "label_encoder": str(label_encoder_path),
                "metrics": str(metrics_path),
                "report": str(report_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return result


def load_role_classifier(
    model_path: Path = ROLE_MODEL_PATH,
    label_encoder_path: Path = LABEL_ENCODER_PATH,
) -> tuple[Pipeline, LabelEncoder]:
    return joblib.load(model_path), joblib.load(label_encoder_path)


def predict_role(text: str, top_k: int = 5) -> list[dict[str, float | str]]:
    model, label_encoder = load_role_classifier()
    probabilities = model.predict_proba([text])[0]
    ranked_indices = probabilities.argsort()[::-1][:top_k]
    return [
        {
            "role": str(label_encoder.inverse_transform([index])[0]),
            "confidence": float(probabilities[index]),
        }
        for index in ranked_indices
    ]


def main() -> None:
    result = train_role_classifier()
    for key, value in asdict(result).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
