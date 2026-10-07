from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer

from services.preprocessing import preprocess_text


def build_tfidf_vectorizer(
    max_features: int = 25_000,
    ngram_range: tuple[int, int] = (1, 2),
    min_df: int = 2,
    max_df: float = 0.95,
) -> TfidfVectorizer:
    return TfidfVectorizer(
        preprocessor=preprocess_text,
        tokenizer=str.split,
        token_pattern=None,
        lowercase=False,
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        sublinear_tf=True,
    )
