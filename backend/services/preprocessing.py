from __future__ import annotations

import re
import string
from functools import lru_cache
from typing import Iterable

try:
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
except Exception:  # pragma: no cover - keeps imports resilient before NLTK data is installed.
    stopwords = None
    WordNetLemmatizer = None


URL_RE = re.compile(r"https?://\S+|www\.\S+")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4})")
NON_WORD_RE = re.compile(r"[^\w+#.\s]", flags=re.UNICODE)
WHITESPACE_RE = re.compile(r"\s+")

TECH_TOKEN_MAP = {
    "c++": "cplusplus",
    "c#": "csharp",
    ".net": "dotnet",
    "node.js": "nodejs",
    "react.js": "reactjs",
    "vue.js": "vuejs",
}

FALLBACK_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


@lru_cache(maxsize=1)
def get_stopwords() -> set[str]:
    if stopwords is None:
        return FALLBACK_STOPWORDS
    try:
        return set(stopwords.words("english"))
    except LookupError:
        return FALLBACK_STOPWORDS


@lru_cache(maxsize=1)
def get_lemmatizer() -> object | None:
    if WordNetLemmatizer is None:
        return None
    try:
        return WordNetLemmatizer()
    except Exception:
        return None


def normalize_tech_tokens(text: str) -> str:
    normalized = text
    for token, replacement in TECH_TOKEN_MAP.items():
        normalized = normalized.replace(token, replacement)
    return normalized


def basic_clean_text(text: object) -> str:
    if text is None:
        return ""
    value = str(text).lower()
    value = normalize_tech_tokens(value)
    value = URL_RE.sub(" ", value)
    value = EMAIL_RE.sub(" ", value)
    value = PHONE_RE.sub(" ", value)
    value = value.translate(str.maketrans("", "", string.punctuation.replace("+", "").replace("#", "")))
    value = NON_WORD_RE.sub(" ", value)
    value = WHITESPACE_RE.sub(" ", value).strip()
    return value


def tokenize(text: object, remove_stopwords: bool = True, lemmatize: bool = True) -> list[str]:
    cleaned = basic_clean_text(text)
    tokens = cleaned.split()
    if remove_stopwords:
        stopword_set = get_stopwords()
        tokens = [token for token in tokens if token not in stopword_set and len(token) > 1]

    lemmatizer = get_lemmatizer() if lemmatize else None
    if lemmatizer is not None:
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return tokens


def preprocess_text(text: object) -> str:
    return " ".join(tokenize(text))


def preprocess_many(texts: Iterable[object]) -> list[str]:
    return [preprocess_text(text) for text in texts]
