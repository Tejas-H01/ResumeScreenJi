from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ScrapedDocument:
    source_url: str
    title: str
    text: str


def scrape_text_page(url: str, timeout: int = 20) -> ScrapedDocument:
    """Fetch a public page and return readable text for dataset enrichment.

    Use this only for sources whose terms allow collection. Store source URLs
    so the dataset remains auditable.
    """
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "resume-screening-ml/0.1"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else "Untitled"
    text = " ".join(soup.get_text(" ", strip=True).split())
    return ScrapedDocument(source_url=url, title=title, text=text)


def collect_public_text_dataset(urls: Iterable[str], output_path: str | Path) -> pd.DataFrame:
    rows = []
    for url in urls:
        document = scrape_text_page(url)
        rows.append({"source_url": document.source_url, "title": document.title, "text": document.text})

    frame = pd.DataFrame(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame


def load_labeled_resume_dataset(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required_columns = {"resume_text", "category"}
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    return frame.dropna(subset=["resume_text", "category"]).reset_index(drop=True)
