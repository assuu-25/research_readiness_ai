# ResearchReadiness AI

A working implementation of the pipeline in your slide deck: upload a draft
paper (+ optional dataset) and get a **Research Readiness Score (0-100)**
broken down across 4 dimensions, with SHAP explainability and targeted
recommendations.

## What each piece is and what it's for

| File | Maps to deck slide | What it does |
|---|---|---|
| `app/dataset_analyzer.py` | Dataset Quality (8 dims) | Reads a CSV and scores completeness, uniqueness, class balance, validity, consistency, size adequacy, feature richness, outlier control |
| `app/paper_analyzer.py` | Paper Structure (8 dims) | Extracts text from PDF/DOCX/TXT, scores section completeness, citation density, novelty signaling, methodology/experiment presence, writing quality, visual support, abstract quality |
| `app/literature_analyzer.py` | Literature Intelligence | Parses the References section, scores reference count, recency, author coverage breadth, related-work depth |
| `app/methodology_checker.py` | Methodology Evaluation | Scans for baseline comparisons, named metrics, statistical rigor language, reproducibility signals |
| `app/feature_fusion.py` | "Multi-Modal Feature Fusion" | Flattens all 24 metrics into one ordered vector for the model |
| `train_model.py` / `app/model.py` | "XGBoost Predictor" | Trains/loads an XGBoost regressor that maps the 24-feature vector to a 0-100 RRS |
| `app/shap_explainer.py` | "SHAP Explainer" | Computes per-prediction SHAP values so you can see which specific metrics pushed the score up or down |
| `app/recommendation_engine.py` | "Recommendation Engine" | Rule-based: any feature below its threshold gets a specific, actionable fix — not generic advice |
| `app/main.py` | System Architecture (Input → ... → Predict & Recommend) | FastAPI app wiring all 7 modules into one `/assess` endpoint |
| `frontend/index.html` | (UI for the above) | Minimal browser UI: upload files, see score, breakdown, recommendations, SHAP chart |

## ⚠️ Important note on the ML model

Your deck claims training on "10,000+ draft and published papers" with
">90% accuracy." **No such public labeled dataset exists**, and I have not
fabricated one. What I built instead:

- `train_model.py` generates a **synthetic but realistic** training set,
  deriving readiness labels from a reviewer-informed weighted formula (methodology
  and paper structure weighted highest, matching typical review rubrics) plus noise.
- This makes the **entire pipeline fully functional today** — every module,
  the model, SHAP, and recommendations all run end-to-end on real uploaded
  files.
- To get a genuinely accurate predictor, you need real labeled data: pairs
  of (draft paper + dataset) → (accepted/rejected, or a readiness score from
  reviewers). This is exactly the "Collect Labeled Dataset" step already in
  your "Next Steps" slide. Once you have it, swap `generate_synthetic_dataset()`
  in `train_model.py` for a loader over your real data — nothing else in the
  pipeline needs to change, since the feature schema is already fixed in
  `feature_fusion.py`.

## Setup

```bash
cd research_readiness_ai
pip install -r requirements.txt

# 1. Train the model (creates models/rrs_xgboost.joblib)
python train_model.py

# 2. Start the API
python -m uvicorn app.main:app --reload --port 8000

# 3. Open frontend/index.html in a browser (just double-click it, or serve it)
```

## Try it via curl

```bash
curl -X POST http://localhost:8000/assess \
  -F "paper=@sample_data/sample_paper.txt" \
  -F "dataset=@sample_data/sample_dataset.csv"
```

Sample files are included in `sample_data/` so you can test immediately
without any of your own papers.

## API

### `POST /assess`
- `paper` (required): `.pdf`, `.docx`, or `.txt`
- `dataset` (optional): `.csv`

Returns:
```json
{
  "research_readiness_score": 75.9,
  "dimension_breakdown": { "dataset_quality": {...}, "paper_structure": {...}, ... },
  "explainability": { "top_positive_contributors": [...], "top_negative_contributors": [...] },
  "recommendations": [ { "feature": "...", "score": 15.0, "recommendation": "..." } ]
}
```

## Extending this

- **Novelty detection**: currently keyword-based (`pp_novelty_signaling`).
  A stronger version would embed the abstract and compare cosine similarity
  against a corpus of existing abstracts (e.g. via Semantic Scholar API).
- **Literature Intelligence**: currently regex-based reference parsing.
  For production, integrate a real citation parser (e.g. GROBID) and a
  citation-graph API (Semantic Scholar, OpenAlex) to check whether cited
  work is actually relevant, not just present.
- **Real accuracy numbers**: once you have real labeled data, re-run
  `train_model.py` and report the real validation MAE/R² instead of a
  marketing "90%" figure.
