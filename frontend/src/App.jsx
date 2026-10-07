import { useEffect, useMemo, useRef, useState } from "react";
import appLogo from "./assets/logo.png";
import {
  checkHealth,
  recommendUploadedResume,
} from "./api.js";

const SAMPLE_JD =
  "Hiring a data scientist with Python, SQL, machine learning, NLP, model evaluation, API development, Docker, and AWS experience.";

const DEMO_RESUME_TEXT = `Alex Chen
Email: alex.chen@techmail.io | Phone: +1-555-019-2834 | San Francisco, CA
GitHub: github.com/alexchen-ml | LinkedIn: linkedin.com/in/alexchen-ml

PROFESSIONAL SUMMARY
Machine Learning Engineer with 4 years of experience building and deploying scalable NLP models and production ML microservices. Proficient in Python, FastAPI, Docker, Scikit-learn, and PyTorch with a strong background in model evaluation, REST APIs, and feature engineering.

TECHNICAL SKILLS
- Languages & Frameworks: Python, SQL, FastAPI, Scikit-learn, PyTorch, Pandas, NumPy
- Machine Learning & NLP: Supervised Learning, Text Classification, TF-IDF, Word Embeddings, Model Evaluation, Hyperparameter Tuning
- DevOps & Tools: Docker, Git, Linux, CI/CD pipelines, PostgreSQL

PROFESSIONAL EXPERIENCE
Machine Learning Engineer | DataCore Systems (2022 - Present)
- Designed and deployed real-time resume classification microservice using FastAPI and Docker, handling 50k+ requests daily.
- Built NLP text processing pipelines using TF-IDF and Linear classifiers, improving candidate categorization F1-score by 18%.
- Optimized scikit-learn and PyTorch model inference latency from 180ms to 42ms.

Associate ML Developer | Nexus Analytics (2020 - 2022)
- Built regression models to forecast candidate conversion rates with 89% accuracy using Random Forest and Scikit-learn.
- Developed automated data cleaning and feature engineering workflows in Python and Pandas.

EDUCATION
- Master of Science in Computer Science, Specialization in Machine Learning (2020)
- Bachelor of Technology in Computer Engineering (2018)

CERTIFICATIONS
- TensorFlow Developer Certificate
- DeepLearning.AI Machine Learning Specialization`;

const DEMO_JOB_TEXT = `We are hiring a Machine Learning Engineer to design and deploy intelligent candidate matching systems.

Key Requirements:
- 3+ years of professional experience with Python and core ML libraries (Scikit-learn, PyTorch).
- Proven hands-on experience building NLP pipelines, text preprocessing, and feature extraction.
- Experience building production inference REST APIs using FastAPI.
- Containerization experience with Docker.
- Cloud deployment experience with AWS and Kubernetes for scalable model serving.
- Strong foundation in model evaluation, cross-validation, and metrics tracking.`;


function classNames(...values) {
  return values.filter(Boolean).join(" ");
}

function formatPercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/* ==========================================================================
   CURATED SVG ICONS (Section 25 of DESIGN.md)
   ========================================================================== */
function SparkleIcon({ size = 16, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" stroke="#171717" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" />
    </svg>
  );
}

function BrainIcon({ size = 18, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04" />
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04" />
    </svg>
  );
}

function DocumentIcon({ size = 16, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  );
}

function CheckIcon({ size = 13, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function CrossIcon({ size = 13, className = "" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function SunIcon({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  );
}

function MoonIcon({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

function HighlightedText({ text, skills }) {
  const terms = (skills || []).filter(Boolean).sort((a, b) => b.length - a.length);
  if (!text || terms.length === 0) return <p>{text || "No preview available."}</p>;

  const pattern = new RegExp(`(${terms.map(escapeRegExp).join("|")})`, "gi");
  const parts = text.split(pattern);

  return (
    <p>
      {parts.map((part, index) => {
        const isMatch = terms.some((skill) => skill.toLowerCase() === part.toLowerCase());
        return isMatch ? (
          <mark key={`${part}-${index}`}>{part}</mark>
        ) : (
          <span key={`${part}-${index}`}>{part}</span>
        );
      })}
    </p>
  );
}

function PieChart({ score }) {
  const match = Math.max(0, Math.min(100, Number(score) || 0));
  const gap = 100 - match;
  const background = `conic-gradient(var(--accent-green) 0 ${match}%, var(--accent-pink) ${match}% 100%)`;

  return (
    <div className="pie-wrap" aria-label={`Match ${match.toFixed(0)} percent, gap ${gap.toFixed(0)} percent`}>
      <div className="pie" style={{ background }}>
        <span>{match.toFixed(0)}%</span>
      </div>
      <div className="chart-legend">
        <span><i className="legend-dot match" /> Match</span>
        <span><i className="legend-dot gap" /> Gap</span>
      </div>
    </div>
  );
}

function SkillBars({ matched = [], missing = [], extra = [] }) {
  const values = [
    { label: "Matched", value: matched.length, tone: "good" },
    { label: "Missing", value: missing.length, tone: "warn" },
    { label: "Additional", value: extra.length, tone: "neutral" },
  ];
  const max = Math.max(...values.map((item) => item.value), 1);

  return (
    <div className="bars">
      {values.map((item) => (
        <div className="bar-row" key={item.label}>
          <span>{item.label}</span>
          <div className="bar-track">
            <div className={classNames("bar-fill", item.tone)} style={{ width: `${(item.value / max) * 100}%` }} />
          </div>
          <strong>{item.value}</strong>
        </div>
      ))}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

// ==========================================================================
// FEATURE 1 — ML PIPELINE & MODEL EXPLANATION PANEL (Section 24)
// ==========================================================================
function ModelExplanationPanel({ onClose }) {
  return (
    <section className="explanation-panel" aria-label="Machine Learning Pipeline Architecture">
      <div className="explanation-header">
        <div>
          <p className="eyebrow">Academic AIML Architecture</p>
          <h2>How the AI/ML Screening Pipeline Works</h2>
          <p>
            Deterministic, explainable candidate ranking powered by classical supervised machine learning and NLP.
          </p>
        </div>
        <button className="close-panel-btn" type="button" onClick={onClose}>
          ✕ Close Panel
        </button>
      </div>

      <div className="pipeline-flow-container">
        <span className="pipeline-flow-title">End-to-End Processing Flow</span>
        <div className="pipeline-cards-flow">
          <div className="flow-step-card">
            <span className="flow-step-num">Step 1</span>
            <span className="flow-step-name">Input Documents</span>
            <p className="flow-step-desc">Resume (PDF, DOCX, TXT) parsed via parser engine + Job Description text.</p>
            <span className="flow-step-algo">pdfminer / python-docx</span>
          </div>

          <div className="flow-step-card">
            <span className="flow-step-num">Step 2</span>
            <span className="flow-step-name">NLP Preprocessing</span>
            <p className="flow-step-desc">Regex cleaning, case normalization, tech token preservation, NLTK stopwords & WordNet lemmatization.</p>
            <span className="flow-step-algo">NLTK Preprocessing</span>
          </div>

          <div className="flow-step-card">
            <span className="flow-step-num">Step 3</span>
            <span className="flow-step-name">Feature Extraction</span>
            <p className="flow-step-desc">Char n-gram (3-5) and word TF-IDF vectorization with sublinear scaling.</p>
            <span className="flow-step-algo">TF-IDF Vectorizer</span>
          </div>

          <div className="models-cluster-card">
            <span className="flow-step-num">Step 4 — Core Supervised ML Layer</span>
            <span className="flow-step-name">4 Trained Machine Learning Models</span>
            <div className="models-cluster-grid">
              <div className="model-mini-item">
                <strong>1. Role Classifier</strong>
                <span>LinearSVC (Calibrated)</span>
              </div>
              <div className="model-mini-item">
                <strong>2. Resume-Job Matcher</strong>
                <span>TF-IDF + Logistic Regression</span>
              </div>
              <div className="model-mini-item">
                <strong>3. Screening Decision</strong>
                <span>Logistic Regression (ColumnTransformer)</span>
              </div>
              <div className="model-mini-item">
                <strong>4. Score Regressor</strong>
                <span>Random Forest Regressor</span>
              </div>
            </div>
          </div>

          <div className="flow-step-card">
            <span className="flow-step-num">Step 5</span>
            <span className="flow-step-name">Skill Gap Engine</span>
            <p className="flow-step-desc">Lexical & canonical matching against tech taxonomy. Identifies matched vs missing skills.</p>
            <span className="flow-step-algo">Taxonomy Matcher</span>
          </div>

          <div className="flow-step-card">
            <span className="flow-step-num">Step 6</span>
            <span className="flow-step-name">Hybrid Scoring</span>
            <p className="flow-step-desc">Weighted mathematical fusion of match probability, skill match, AI score, and role confidence.</p>
            <span className="flow-step-algo">Linear Fusion Formula</span>
          </div>

          <div className="flow-step-card">
            <span className="flow-step-num">Step 7</span>
            <span className="flow-step-name">Recommendation</span>
            <p className="flow-step-desc">Final fit classification into Strong, Good, Moderate, or Weak fit with recruiter action triggers.</p>
            <span className="flow-step-algo">Fit Classification</span>
          </div>
        </div>
      </div>

      <div className="explanation-details-grid">
        <div className="info-card">
          <h4>Hybrid Candidate Score Formulation</h4>
          <div className="weights-list">
            <div className="weight-row">
              <span className="weight-badge">35%</span>
              <span><strong>Resume–Job Match</strong> (Semantic compatibility between resume and JD)</span>
              <span>0.35 × Match Prob</span>
            </div>
            <div className="weight-row">
              <span className="weight-badge">25%</span>
              <span><strong>Skill Match Score</strong> (Ratio of required job skills satisfied by candidate)</span>
              <span>0.25 × Skill Match</span>
            </div>
            <div className="weight-row">
              <span className="weight-badge">25%</span>
              <span><strong>Screening Score</strong> (AI prediction combining experience, education & skills)</span>
              <span>0.25 × AI Score</span>
            </div>
            <div className="weight-row">
              <span className="weight-badge">15%</span>
              <span><strong>Role Confidence</strong> (Classifier certainty in candidate's primary domain)</span>
              <span>0.15 × Role Conf</span>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h4>Fit Classification Thresholds</h4>
          <div className="fit-categories-list">
            <div className="fit-category-row">
              <span><strong>85 – 100</strong> Score Range</span>
              <span className="fit-pill-demo fit-strong">Strong Fit</span>
              <span>Top-tier match, minimal skill gaps</span>
            </div>
            <div className="fit-category-row">
              <span><strong>70 – 84</strong> Score Range</span>
              <span className="fit-pill-demo fit-good">Good Fit</span>
              <span>Core requirements met, minor gaps</span>
            </div>
            <div className="fit-category-row">
              <span><strong>55 – 69</strong> Score Range</span>
              <span className="fit-pill-demo fit-moderate">Moderate Fit</span>
              <span>Partial match, requires review</span>
            </div>
            <div className="fit-category-row">
              <span><strong>0 – 54</strong> Score Range</span>
              <span className="fit-pill-demo fit-weak">Weak Fit</span>
              <span>Low alignment, substantial gaps</span>
            </div>
          </div>
        </div>
      </div>

      <p className="academic-note">
        <strong>Academic Design Note:</strong> This application strictly employs traditional supervised machine learning (Scikit-learn: LinearSVC, Logistic Regression, Random Forest, TF-IDF) and rule-based NLP extraction. It <strong>does NOT</strong> use Large Language Models (LLMs) or generative AI, ensuring 100% deterministic, auditable, explainable, and reproducible candidate rankings.
      </p>
    </section>
  );
}

// ==========================================================================
// FEATURE 2 — STRUCTURED RESULTS & DEMONSTRATION DISPLAY (Section 17-23)
// ==========================================================================
function ResultCard({ result, rank }) {
  const matchPercent = Math.round((result.skill_match_score || 0) * 100);
  const topRole = result.role_predictions?.[0]?.role || "General";
  const roleConfidence = Math.round((result.role_predictions?.[0]?.confidence || 0) * 100);
  const jobMatchPercent = Math.round((result.match_probability || 0) * 100);
  const hireProbability = Math.round((result.hire_probability || 0) * 100);

  const fitTone =
    result.fit_level === "Strong Fit"
      ? "fit-strong"
      : result.fit_level === "Good Fit"
      ? "fit-good"
      : result.fit_level === "Moderate Fit"
      ? "fit-moderate"
      : "fit-weak";

  return (
    <article className="result-card">
      <div className="result-head">
        <div>
          <span className="rank-badge">Candidate #{rank}</span>
          <h3>{result.filename}</h3>
          <div className="head-tags">
            <span className={classNames("fit-badge", fitTone)}>{result.fit_level}</span>
            <span className="head-subtext">
              Screening decision: <strong>{result.screening_decision}</strong>
            </span>
          </div>
        </div>
        <div className="hero-score-badge">
          <span className="score-val">{Number(result.final_score).toFixed(1)}</span>
          <span className="score-max">/ 100</span>
        </div>
      </div>

      {/* 4 Structured ML Prediction Cards (Section 19, 20, 21) */}
      <div className="structured-predictions">
        <div className="prediction-box">
          <div className="prediction-label">PREDICTED ROLE</div>
          <div className="prediction-main">{topRole}</div>
          <div className="prediction-sub">Confidence: <strong>{roleConfidence}%</strong></div>
          <div className="model-badge">LinearSVC (Calibrated)</div>
        </div>

        <div className="prediction-box">
          <div className="prediction-label">JOB MATCH</div>
          <div className="prediction-main">{jobMatchPercent}%</div>
          <div className="prediction-sub">Decision: <strong>{result.match_decision === "match" ? "Match" : "Review"}</strong></div>
          <div className="model-badge">TF-IDF + Logistic Reg</div>
        </div>

        <div className="prediction-box">
          <div className="prediction-label">SCREENING DECISION</div>
          <div className="prediction-main">{result.screening_decision}</div>
          <div className="prediction-sub">Hire Probability: <strong>{hireProbability}%</strong></div>
          <div className="model-badge">Logistic Reg + Random Forest</div>
        </div>

        <div className="prediction-box">
          <div className="prediction-label">FINAL FIT LEVEL</div>
          <div className={classNames("prediction-main", fitTone)}>{result.fit_level.toUpperCase()}</div>
          <div className="prediction-sub">AI Score: <strong>{Number(result.ai_score).toFixed(1)}</strong></div>
          <div className="model-badge">Hybrid Scoring Fusion</div>
        </div>
      </div>

      {/* Structured Skill Analysis (Section 22 of DESIGN.md) */}
      <div className="skills-structured-section">
        <div className="skill-group">
          <div className="skill-group-title">
            <CheckIcon className="icon-check" size={15} /> Matched Skills ({result.matched_skills?.length || 0})
          </div>
          <div className="skill-chips-wrap">
            {result.matched_skills && result.matched_skills.length > 0 ? (
              result.matched_skills.map((skill) => (
                <span className="chip match-chip" key={skill}>
                  ✓ {skill}
                </span>
              ))
            ) : (
              <span className="no-skill-text">No direct skills matched</span>
            )}
          </div>
        </div>

        <div className="skill-group">
          <div className="skill-group-title">
            <CrossIcon className="icon-cross" size={15} /> Missing Skills ({result.missing_skills?.length || 0})
          </div>
          <div className="skill-chips-wrap">
            {result.missing_skills && result.missing_skills.length > 0 ? (
              result.missing_skills.map((skill) => (
                <span className="chip gap-chip" key={skill}>
                  ! {skill}
                </span>
              ))
            ) : (
              <span className="no-skill-text">All required job skills present</span>
            )}
          </div>
        </div>
      </div>

      {/* Explainable Score Breakdown (Section 23 of DESIGN.md) */}
      {result.score_breakdown && (
        <div className="explainable-score-panel">
          <div className="explainable-head">
            <span>Score Composition & Explainability (Hybrid Formula)</span>
            <strong>Final Score: {Number(result.final_score).toFixed(1)} / 100 pts</strong>
          </div>
          <div className="breakdown-grid">
            <div className="breakdown-card">
              <span className="breakdown-weight">35% Weight</span>
              <span className="breakdown-title">Resume–Job Match</span>
              <strong className="breakdown-points">
                {Number(result.score_breakdown.match_probability_component || 0).toFixed(1)} / 35 pts
              </strong>
              <span className="breakdown-detail">({jobMatchPercent}% match prob)</span>
            </div>
            <div className="breakdown-card">
              <span className="breakdown-weight">25% Weight</span>
              <span className="breakdown-title">Skill Match</span>
              <strong className="breakdown-points">
                {Number(result.score_breakdown.skill_match_component || 0).toFixed(1)} / 25 pts
              </strong>
              <span className="breakdown-detail">({matchPercent}% skills matched)</span>
            </div>
            <div className="breakdown-card">
              <span className="breakdown-weight">25% Weight</span>
              <span className="breakdown-title">AI Screening</span>
              <strong className="breakdown-points">
                {Number(result.score_breakdown.screening_score_component || 0).toFixed(1)} / 25 pts
              </strong>
              <span className="breakdown-detail">(AI Score: {Number(result.ai_score).toFixed(1)})</span>
            </div>
            <div className="breakdown-card">
              <span className="breakdown-weight">15% Weight</span>
              <span className="breakdown-title">Role Confidence</span>
              <strong className="breakdown-points">
                {Number(result.score_breakdown.role_confidence_component || 0).toFixed(1)} / 15 pts
              </strong>
              <span className="breakdown-detail">({roleConfidence}% role conf)</span>
            </div>
          </div>
        </div>
      )}

      {/* Visual Charts & Distributions (Section 28 of DESIGN.md) */}
      <div className="result-grid">
        <div className="chart-panel">
          <PieChart score={matchPercent} />
        </div>
        <div className="chart-panel">
          <SkillBars matched={result.matched_skills} missing={result.missing_skills} extra={result.extra_skills} />
        </div>
        <div className="metrics-panel">
          <Metric label="Match prob" value={formatPercent(result.match_probability)} />
          <Metric label="Skill match" value={formatPercent(result.skill_match_score)} />
          <Metric label="Hire prob" value={formatPercent(result.hire_probability)} />
          <Metric label="AI score" value={Number(result.ai_score).toFixed(1)} />
        </div>
      </div>

      <details className="preview">
        <summary>Resume preview with matched skill highlights</summary>
        <HighlightedText text={result.parsed_text_preview} skills={result.matched_skills} />
      </details>

    </article>
  );
}

// ==========================================================================
// MAIN APPLICATION COMPONENT
// ==========================================================================
export default function App() {
  const fileInputRef = useRef(null);
  const [theme, setTheme] = useState("light");
  const [files, setFiles] = useState([]);
  const [jobText, setJobText] = useState(SAMPLE_JD);
  const [experienceYears, setExperienceYears] = useState("");
  const [education, setEducation] = useState("");
  const [certifications, setCertifications] = useState("");
  const [projectsCount, setProjectsCount] = useState(0);
  const [results, setResults] = useState([]);
  const [errors, setErrors] = useState([]);
  const [isScreening, setIsScreening] = useState(false);
  const [backendReady, setBackendReady] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [isDemoLoaded, setIsDemoLoaded] = useState(false);

  useEffect(() => {
    checkHealth().then(setBackendReady).catch(() => setBackendReady(false));
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  // FEATURE 3 — Quick Fill Demo Data Handler
  function handleQuickFillDemo() {
    const demoFile = new File([DEMO_RESUME_TEXT], "alex_chen_ml_resume.txt", { type: "text/plain" });
    setFiles([demoFile]);
    setJobText(DEMO_JOB_TEXT);
    setExperienceYears(4);
    setProjectsCount(5);
    setEducation("M.S. in Computer Science");
    setCertifications("DeepLearning.AI ML Specialization");
    setIsDemoLoaded(true);
    setErrors([]);

    if (fileInputRef.current) {
      try {
        const dt = new DataTransfer();
        dt.items.add(demoFile);
        fileInputRef.current.files = dt.files;
      } catch (e) {
        // Fallback for browsers with strict file input setter policies
      }
    }
  }

  const rankedResults = useMemo(() => {
    return [...results].sort((a, b) => Number(b.final_score) - Number(a.final_score));
  }, [results]);

  async function handleScreen() {
    setErrors([]);
    setResults([]);

    if (!files.length) {
      setErrors(["Upload at least one resume file or click 'Quick Fill Demo'."]);
      return;
    }
    if (jobText.trim().length < 20) {
      setErrors(["Paste a job description with at least 20 characters."]);
      return;
    }

    setIsScreening(true);
    const completed = [];
    const failed = [];

    for (const file of files) {
      try {
        const result = await recommendUploadedResume({
          file,
          jobText,
          experienceYears,
          education,
          certifications,
          projectsCount,
        });
        completed.push(result);
        setResults([...completed]);
      } catch (error) {
        failed.push(`${file.name}: ${error.message}`);
      }
    }

    setErrors(failed);
    setIsScreening(false);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-wrapper">
          <img src={appLogo} alt="ResumeScreenJi Logo" className="brand-logo-img" />
          <div className="brand-text-col">
            <p className="eyebrow">AI Resume Screening System</p>
            <h1>Screen your next great candidate.</h1>
          </div>
        </div>

        <div className="topbar-actions">
          <button
            className={classNames("tactical-btn", showExplanation && "active")}
            type="button"
            onClick={() => setShowExplanation(!showExplanation)}
          >
            <BrainIcon size={16} />
            {showExplanation ? "Close ML Pipeline" : "How the AI/ML Works"}
          </button>
          <button
            className="tactical-btn btn-theme"
            type="button"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            aria-label="Toggle dark/light theme"
          >
            {theme === "light" ? <MoonIcon size={16} /> : <SunIcon size={16} />}
          </button>
        </div>
      </header>

      {/* FEATURE 1: ML Pipeline Explanation Panel */}
      {showExplanation && (
        <ModelExplanationPanel onClose={() => setShowExplanation(false)} />
      )}

      <section className="workspace">
        <aside className="control-panel">
          <div className="status-line">
            <span className={classNames("status-dot", backendReady ? "ready" : backendReady === false ? "down" : "")} />
            {backendReady === null ? "Checking API..." : backendReady ? "API connected" : "API unavailable"}
          </div>

          {/* FEATURE 3: Quick Fill Demo Button (Section 15) */}
          <div className="quick-fill-container">
            <button
              className="quick-fill-btn"
              type="button"
              onClick={handleQuickFillDemo}
              title="Populate realistic ML engineer candidate and job description for live demo"
            >
              <SparkleIcon size={14} /> Quick Fill Demo
            </button>
            {isDemoLoaded && (
              <span className="demo-loaded-tag">Demo Candidate Loaded</span>
            )}
          </div>

          <div className="file-input-wrapper">
            <label className="field">
              <span>Resume document (.pdf, .docx, .txt)</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                multiple
                onChange={(event) => {
                  setFiles([...event.target.files]);
                  setIsDemoLoaded(false);
                }}
              />
            </label>

            {files.length > 0 && (
              <div className="selected-files-bar">
                <span className="selected-files-label">Ready:</span>
                {files.map((file, i) => (
                  <span className="file-chip" key={i}>
                    {file.name} ({Math.round((file.size / 1024) * 10) / 10 || 1} KB)
                  </span>
                ))}
              </div>
            )}
          </div>

          <label className="field">
            <span>Job description</span>
            <textarea value={jobText} onChange={(event) => setJobText(event.target.value)} rows={7} />
          </label>

          <div className="compact-fields">
            <label className="field">
              <span>Experience (years)</span>
              <input type="number" min="0" value={experienceYears} onChange={(event) => setExperienceYears(event.target.value)} />
            </label>
            <label className="field">
              <span>Projects count</span>
              <input type="number" min="0" value={projectsCount} onChange={(event) => setProjectsCount(event.target.value)} />
            </label>
          </div>

          <label className="field">
            <span>Education</span>
            <input value={education} onChange={(event) => setEducation(event.target.value)} placeholder="B.Tech, MBA, M.Sc" />
          </label>

          <label className="field">
            <span>Certifications</span>
            <input value={certifications} onChange={(event) => setCertifications(event.target.value)} placeholder="AWS, Google ML, Cisco" />
          </label>

          {/* Primary Screening CTA (Section 16) */}
          <button className="primary-action" type="button" onClick={handleScreen} disabled={isScreening}>
            {isScreening ? "Screening resumes..." : "Screen Candidate →"}
          </button>
        </aside>

        <section className="results-area">
          {errors.length > 0 && (
            <div className="error-box">
              {errors.map((error) => (
                <p key={error}>{error}</p>
              ))}
            </div>
          )}

          {rankedResults.length === 0 ? (
            <div className="empty-state">
              <img src={appLogo} alt="ResumeScreenJi Mascot" className="empty-state-logo" />
              <h2>No rankings evaluated yet</h2>
              <p>
                Click <strong>"Quick Fill Demo"</strong> to load a realistic candidate, or upload a resume and job description to see ranked machine learning results.
              </p>
            </div>
          ) : (
            <div className="result-list">
              {rankedResults.map((result, index) => (
                <ResultCard
                  key={`${result.filename}-${index}`}
                  result={result}
                  rank={index + 1}
                />
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
