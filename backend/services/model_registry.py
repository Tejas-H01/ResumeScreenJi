from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FEEDBACK_PATH = PROJECT_ROOT / "data" / "feedback" / "feedback.csv"
VERSIONS_DIR = MODELS_DIR / "versions"
REGISTRY_PATH = MODELS_DIR / "model_registry.json"

ARTIFACT_PATHS = [
    MODELS_DIR / "role_classifier.pkl",
    MODELS_DIR / "label_encoder.pkl",
    MODELS_DIR / "matching_tfidf_vectorizer.pkl",
    MODELS_DIR / "matching_model.pkl",
    MODELS_DIR / "screening_decision_model.pkl",
    MODELS_DIR / "screening_score_model.pkl",
    MODELS_DIR / "active_model.json",
    MODELS_DIR / "active_matching_model.json",
    MODELS_DIR / "active_screening_model.json",
    OUTPUTS_DIR / "role_classifier_metrics.csv",
    OUTPUTS_DIR / "matching_model_metrics.csv",
    OUTPUTS_DIR / "screening_model_metrics.csv",
]


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _artifact_info(path: Path) -> dict[str, int | str | bool]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if path.exists() else "",
    }


def feedback_summary() -> dict[str, object]:
    if not FEEDBACK_PATH.exists():
        return {"path": str(FEEDBACK_PATH), "rows": 0, "counts": {}}

    frame = pd.read_csv(FEEDBACK_PATH)
    counts = frame["feedback_type"].value_counts(dropna=False).to_dict() if "feedback_type" in frame.columns else {}
    return {
        "path": str(FEEDBACK_PATH),
        "rows": len(frame),
        "counts": {str(key): int(value) for key, value in counts.items()},
    }


def list_versions() -> list[dict[str, object]]:
    registry = _read_json(REGISTRY_PATH, {"versions": []})
    return registry.get("versions", [])


def model_status() -> dict[str, object]:
    return {
        "artifacts": [_artifact_info(path) for path in ARTIFACT_PATHS],
        "feedback": feedback_summary(),
        "versions": list_versions(),
        "registry_path": str(REGISTRY_PATH),
    }


def create_model_version(reason: str = "manual_snapshot") -> dict[str, object]:
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    version_id = datetime.now().strftime("v%Y%m%d_%H%M%S_%f")
    version_dir = VERSIONS_DIR / version_id
    version_dir.mkdir(parents=True, exist_ok=False)

    copied = []
    for source in ARTIFACT_PATHS:
        if source.exists():
            target = version_dir / source.name
            shutil.copy2(source, target)
            copied.append(str(target))

    registry = _read_json(REGISTRY_PATH, {"versions": []})
    record = {
        "version_id": version_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "reason": reason,
        "version_dir": str(version_dir),
        "artifact_count": len(copied),
        "feedback_rows": feedback_summary()["rows"],
    }
    registry.setdefault("versions", []).append(record)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    return {**record, "copied_artifacts": copied}
