from __future__ import annotations

from math import log2
from typing import Iterable, Sequence


def _limit(values: Sequence[float], k: int | None = None) -> list[float]:
    if k is None:
        return list(values)
    return list(values[: max(k, 0)])


def average_precision(relevance: Sequence[float], k: int | None = None) -> float:
    """Compute Average Precision for one ranked result list.

    relevance should be ordered by the model ranking. Values greater than zero
    are treated as relevant for MAP.
    """
    ranked = _limit(relevance, k)
    hits = 0
    precision_sum = 0.0

    for index, score in enumerate(ranked, start=1):
        if score > 0:
            hits += 1
            precision_sum += hits / index

    total_relevant = sum(1 for score in ranked if score > 0)
    if total_relevant == 0:
        return 0.0
    return precision_sum / total_relevant


def mean_average_precision(rankings: Iterable[Sequence[float]], k: int | None = None) -> float:
    scores = [average_precision(relevance, k) for relevance in rankings]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def dcg_at_k(relevance: Sequence[float], k: int | None = None) -> float:
    ranked = _limit(relevance, k)
    return sum(((2**score - 1) / log2(index + 2)) for index, score in enumerate(ranked))


def ndcg_at_k(relevance: Sequence[float], k: int | None = None) -> float:
    ranked = _limit(relevance, k)
    ideal = sorted(ranked, reverse=True)
    ideal_dcg = dcg_at_k(ideal, k)
    if ideal_dcg == 0:
        return 0.0
    return dcg_at_k(ranked, k) / ideal_dcg


def mean_ndcg(rankings: Iterable[Sequence[float]], k: int | None = None) -> float:
    scores = [ndcg_at_k(relevance, k) for relevance in rankings]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def ranking_report(rankings: Iterable[Sequence[float]], k: int | None = None) -> dict[str, float | int | None]:
    ranking_list = [list(row) for row in rankings]
    return {
        "k": k,
        "query_count": len(ranking_list),
        "map": mean_average_precision(ranking_list, k),
        "ndcg": mean_ndcg(ranking_list, k),
    }
