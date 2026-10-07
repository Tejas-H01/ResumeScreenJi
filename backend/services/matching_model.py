from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from services.preprocessing import basic_clean_text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

MATCHING_CLEANED_PATH = PROCESSED_DIR / "matching_cleaned.csv"
MATCHING_VECTORIZER_PATH = MODELS_DIR / "matching_tfidf_vectorizer.pkl"
MATCHING_MODEL_PATH = MODELS_DIR / "matching_model.pkl"
MATCHING_METRICS_PATH = OUTPUTS_DIR / "matching_model_metrics.csv"
MATCHING_REPORT_PATH = OUTPUTS_DIR / "matching_model_report.csv"
ACTIVE_MATCHING_MODEL_PATH = MODELS_DIR / "active_matching_model.json"


@dataclass(frozen=True)
class MatchingTrainingResult:
    rows: int
    positive_rows: int
    negative_rows: int
    test_accuracy: float
    test_precision: float
    test_recall: float
    test_f1: float
    test_roc_auc: float
    cv_accuracy_mean: float
    cv_f1_mean: float
    cv_roc_auc_mean: float
    vectorizer_path: str
    model_path: str


def build_matching_vectorizer(max_features: int = 15_000) -> TfidfVectorizer:
    return TfidfVectorizer(
        preprocessor=basic_clean_text,
        analyzer="char_wb",
        lowercase=False,
        max_features=max_features,
        ngram_range=(3, 5),
        min_df=3,
        max_df=0.98,
        sublinear_tf=True,
    )


def load_matching_training_data(
    path: Path = MATCHING_CLEANED_PATH,
    max_rows: int | None = None,
    sample_per_class: int | None = None,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    frame = pd.read_csv(path, usecols=["resume_text", "job_text", "match_label"], nrows=max_rows)
    frame = frame.dropna(subset=["resume_text", "job_text", "match_label"])
    frame = frame[(frame["resume_text"].astype(str).str.len() > 0) & (frame["job_text"].astype(str).str.len() > 0)]

    if sample_per_class is not None:
        sampled_groups = []
        for _, group in frame.groupby("match_label"):
            sampled_groups.append(group.sample(n=min(sample_per_class, len(group)), random_state=42))
        frame = pd.concat(sampled_groups, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

    return frame["resume_text"].astype(str), frame["job_text"].astype(str), frame["match_label"].astype(int)


def fit_pair_vectorizer(vectorizer: TfidfVectorizer, resume_texts: pd.Series, job_texts: pd.Series) -> TfidfVectorizer:
    combined = pd.concat([resume_texts, job_texts], ignore_index=True)
    vectorizer.fit(combined)
    return vectorizer


def _length_features(resume_texts: pd.Series | list[str], job_texts: pd.Series | list[str]) -> csr_matrix:
    resume_lengths = np.array([max(len(str(text).split()), 1) for text in resume_texts], dtype=float)
    job_lengths = np.array([max(len(str(text).split()), 1) for text in job_texts], dtype=float)
    length_ratio = np.minimum(resume_lengths, job_lengths) / np.maximum(resume_lengths, job_lengths)
    return csr_matrix(np.column_stack([np.log1p(resume_lengths), np.log1p(job_lengths), length_ratio]))


def build_pair_features(
    vectorizer: TfidfVectorizer,
    resume_texts: pd.Series | list[str],
    job_texts: pd.Series | list[str],
):
    resume_matrix = vectorizer.transform(resume_texts)
    job_matrix = vectorizer.transform(job_texts)

    cosine_similarity = resume_matrix.multiply(job_matrix).sum(axis=1)
    cosine_feature = csr_matrix(np.asarray(cosine_similarity))
    abs_difference = abs(resume_matrix - job_matrix)
    elementwise_product = resume_matrix.multiply(job_matrix)
    length_features = _length_features(resume_texts, job_texts)

    return hstack([cosine_feature, length_features, abs_difference, elementwise_product], format="csr")


def build_matching_classifier() -> LogisticRegression:
    return LogisticRegression(
        class_weight="balanced",
        solver="liblinear",
        max_iter=500,
        random_state=42,
    )


def evaluate_matching_cv(features, labels: pd.Series) -> dict[str, float]:
    splitter = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    classifier = build_matching_classifier()
    scores = cross_validate(
        classifier,
        features,
        labels,
        cv=splitter,
        scoring={"accuracy": "accuracy", "f1": "f1", "roc_auc": "roc_auc"},
        n_jobs=-1,
        error_score="raise",
    )
    return {key: float(value.mean()) for key, value in scores.items() if key.startswith("test_")}


def train_matching_model(
    data_path: Path = MATCHING_CLEANED_PATH,
    vectorizer_path: Path = MATCHING_VECTORIZER_PATH,
    model_path: Path = MATCHING_MODEL_PATH,
    metrics_path: Path = MATCHING_METRICS_PATH,
    report_path: Path = MATCHING_REPORT_PATH,
    max_rows: int | None = None,
    sample_per_class: int | None = None,
) -> MatchingTrainingResult:
    resume_texts, job_texts, labels = load_matching_training_data(
        data_path,
        max_rows=max_rows,
        sample_per_class=sample_per_class,
    )

    vectorizer = fit_pair_vectorizer(build_matching_vectorizer(), resume_texts, job_texts)
    features = build_pair_features(vectorizer, resume_texts, job_texts)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    cv_scores = evaluate_matching_cv(x_train, y_train)

    classifier = build_matching_classifier()
    classifier.fit(x_train, y_train)
    predictions = classifier.predict(x_test)
    probabilities = classifier.predict_proba(x_test)[:, 1]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(classifier, model_path)

    result = MatchingTrainingResult(
        rows=len(labels),
        positive_rows=int(labels.sum()),
        negative_rows=int((labels == 0).sum()),
        test_accuracy=float(accuracy_score(y_test, predictions)),
        test_precision=float(precision_score(y_test, predictions, zero_division=0)),
        test_recall=float(recall_score(y_test, predictions, zero_division=0)),
        test_f1=float(f1_score(y_test, predictions, zero_division=0)),
        test_roc_auc=float(roc_auc_score(y_test, probabilities)),
        cv_accuracy_mean=cv_scores["test_accuracy"],
        cv_f1_mean=cv_scores["test_f1"],
        cv_roc_auc_mean=cv_scores["test_roc_auc"],
        vectorizer_path=str(vectorizer_path),
        model_path=str(model_path),
    )

    pd.DataFrame([asdict(result)]).to_csv(metrics_path, index=False)
    pd.DataFrame(classification_report(y_test, predictions, output_dict=True, zero_division=0)).transpose().to_csv(
        report_path
    )
    ACTIVE_MATCHING_MODEL_PATH.write_text(
        json.dumps(
            {
                "matching_vectorizer": str(vectorizer_path),
                "matching_model": str(model_path),
                "metrics": str(metrics_path),
                "report": str(report_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return result


def load_matching_model(
    vectorizer_path: Path = MATCHING_VECTORIZER_PATH,
    model_path: Path = MATCHING_MODEL_PATH,
) -> tuple[TfidfVectorizer, LogisticRegression]:
    return joblib.load(vectorizer_path), joblib.load(model_path)


def predict_match_score(resume_text: str, job_text: str) -> dict[str, float | int | str]:
    vectorizer, classifier = load_matching_model()
    features = build_pair_features(vectorizer, [resume_text], [job_text])
    probability = float(classifier.predict_proba(features)[0, 1])
    prediction = int(probability >= 0.5)
    return {
        "match_label": prediction,
        "match_probability": probability,
        "decision": "match" if prediction == 1 else "reject",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the resume-job matching model.")
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional row cap for faster experiments. Omit to train on the full cleaned matching dataset.",
    )
    parser.add_argument(
        "--sample-per-class",
        type=int,
        default=None,
        help="Optional balanced sample size per class after loading rows.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = train_matching_model(max_rows=args.max_rows, sample_per_class=args.sample_per_class)
    for key, value in asdict(result).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
