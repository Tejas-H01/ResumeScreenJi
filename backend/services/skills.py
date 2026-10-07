from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from services.preprocessing import basic_clean_text


SKILL_SYNONYMS: dict[str, list[str]] = {
    "python": ["python", "py", "python3"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "ms sql", "sql server"],
    "java": ["java", "core java", "j2ee", "spring", "spring boot"],
    "javascript": ["javascript", "js", "ecmascript", "nodejs", "node.js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs", "react.js", "redux", "nextjs", "next.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "tailwind", "bootstrap", "sass", "scss"],
    "c": [" c ", "c language"],
    "cplusplus": ["c++", "cpp", "cplusplus"],
    "csharp": ["c#", "csharp", ".net", "dotnet", "asp.net"],
    "php": ["php", "laravel"],
    "ruby": ["ruby", "rails", "ruby on rails"],
    "go": ["golang", "go language"],
    "r": [" r ", "r programming", "rstudio"],
    "scala": ["scala", "spark scala"],
    "kotlin": ["kotlin"],
    "swift": ["swift", "ios"],
    "machine learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "deep learning": ["deep learning", "neural network", "neural networks", "ann", "cnn", "rnn"],
    "nlp": ["nlp", "natural language processing", "text mining", "text analytics"],
    "computer vision": ["computer vision", "opencv", "image processing"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "pytorch": ["pytorch", "torch"],
    "scikit learn": ["scikit learn", "scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib", "seaborn", "plotly", "data visualization"],
    "statistics": ["statistics", "statistical analysis", "hypothesis testing"],
    "data analysis": ["data analysis", "eda", "exploratory data analysis", "analytics"],
    "data science": ["data science", "data scientist"],
    "data engineering": ["data engineering", "etl", "data pipeline", "airflow"],
    "big data": ["big data", "hadoop", "hive", "spark", "pyspark"],
    "bert": ["bert", "transformers", "sentence transformers", "huggingface", "hugging face"],
    "llm": ["llm", "large language model", "generative ai", "gen ai", "prompt engineering"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "django": ["django"],
    "api development": ["api", "rest api", "restful", "graphql", "microservices"],
    "docker": ["docker", "container", "containers", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "redshift"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "git": ["git", "github", "gitlab", "bitbucket", "version control"],
    "ci cd": ["ci cd", "ci/cd", "jenkins", "github actions", "devops pipeline"],
    "linux": ["linux", "unix", "shell", "bash"],
    "networking": ["networking", "tcp/ip", "dns", "routing", "switching"],
    "cybersecurity": ["cybersecurity", "cyber security", "security", "information security"],
    "ethical hacking": ["ethical hacking", "penetration testing", "pentest", "vulnerability assessment"],
    "cloud security": ["cloud security", "iam", "identity access management"],
    "database": ["database", "dbms", "mongodb", "oracle", "nosql", "redis", "cassandra"],
    "excel": ["excel", "advanced excel", "spreadsheet"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "project management": ["project management", "agile", "scrum", "kanban", "jira"],
    "communication": ["communication", "written communication", "verbal communication"],
    "leadership": ["leadership", "team lead", "team management"],
    "problem solving": ["problem solving", "analytical thinking", "critical thinking"],
}


@dataclass(frozen=True)
class SkillGapResult:
    resume_skills: list[str]
    job_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    skill_match_score: float


def _skill_patterns() -> dict[str, list[re.Pattern[str]]]:
    patterns: dict[str, list[re.Pattern[str]]] = {}
    for canonical, synonyms in SKILL_SYNONYMS.items():
        patterns[canonical] = []
        for synonym in synonyms:
            normalized = basic_clean_text(synonym).strip()
            if not normalized:
                continue
            escaped = re.escape(normalized)
            patterns[canonical].append(re.compile(rf"(?<!\w){escaped}(?!\w)", flags=re.IGNORECASE))
    return patterns


SKILL_PATTERNS = _skill_patterns()


def extract_skills(text: object) -> list[str]:
    cleaned = f" {basic_clean_text(text)} "
    found = []
    for canonical, patterns in SKILL_PATTERNS.items():
        if any(pattern.search(cleaned) for pattern in patterns):
            found.append(canonical)
    return sorted(found)


def extract_skills_from_many(values: Iterable[object]) -> list[str]:
    found: set[str] = set()
    for value in values:
        found.update(extract_skills(value))
    return sorted(found)


def calculate_skill_gap(resume_text: object, job_text: object) -> SkillGapResult:
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))
    matched = resume_skills.intersection(job_skills)
    missing = job_skills.difference(resume_skills)
    extra = resume_skills.difference(job_skills)
    score = len(matched) / len(job_skills) if job_skills else 0.0
    return SkillGapResult(
        resume_skills=sorted(resume_skills),
        job_skills=sorted(job_skills),
        matched_skills=sorted(matched),
        missing_skills=sorted(missing),
        extra_skills=sorted(extra),
        skill_match_score=round(score, 4),
    )


def skills_to_text(skills: Iterable[str]) -> str:
    return ", ".join(sorted(set(skills)))
