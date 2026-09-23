"""
main.py
--------
FastAPI application exposing the ResearchReadiness AI pipeline.

POST /assess
    multipart/form-data:
        paper: PDF/DOCX/TXT file (the draft manuscript)
        dataset: CSV file (the accompanying dataset) [optional]
    Returns: full RRS breakdown, SHAP explanation, and recommendations.

GET /health
    Simple liveness check.
"""

from __future__ import annotations
import os
import shutil
import tempfile
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.dataset_analyzer import analyze_dataset
from app.paper_analyzer import analyze_paper
from app.literature_analyzer import analyze_literature
from app.methodology_checker import check_methodology
from app.feature_fusion import fuse_features, FEATURE_NAMES
from app.model import predict_rrs
from app.shap_explainer import explain
from app.recommendation_engine import generate_recommendations

app = FastAPI(title="ResearchReadiness AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _neutral_dataset_report() -> dict:
    """Used when no dataset file is provided; keeps the feature vector well-formed."""
    return {
        "dimension": "dataset_quality",
        "aggregate_score": 50.0,
        "metrics": {
            "completeness": 50.0, "uniqueness": 50.0, "balance": 50.0, "validity": 50.0,
            "consistency": 50.0, "size_adequacy": 50.0, "feature_richness": 50.0,
            "outlier_control": 50.0,
        },
        "meta": {"note": "No dataset provided; neutral placeholder scores used."},
    }


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

@app.post("/assess")
async def assess(paper: UploadFile = File(...), dataset: UploadFile | None = File(None)):
    with tempfile.TemporaryDirectory() as tmpdir:
        paper_path = os.path.join(tmpdir, paper.filename)
        with open(paper_path, "wb") as f:
            shutil.copyfileobj(paper.file, f)

        try:
            paper_report = analyze_paper(paper_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse paper file: {e}")

        raw_text = paper_report.pop("_raw_text")

        if dataset is not None:
            dataset_path = os.path.join(tmpdir, dataset.filename)
            with open(dataset_path, "wb") as f:
                shutil.copyfileobj(dataset.file, f)
            try:
                df = pd.read_csv(dataset_path)
                dataset_report = analyze_dataset(df)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Could not parse dataset CSV: {e}")
        else:
            dataset_report = _neutral_dataset_report()

        literature_report = analyze_literature(raw_text)
        methodology_report = check_methodology(raw_text)

        feature_vector = fuse_features(dataset_report, paper_report,
                                        literature_report, methodology_report)
        feature_dict = dict(zip(FEATURE_NAMES, feature_vector))

        rrs = predict_rrs(feature_vector)
        shap_explanation = explain(feature_vector)
        recommendations = generate_recommendations(feature_dict)

        return JSONResponse({
            "research_readiness_score": round(rrs, 1),
            "dimension_breakdown": {
                "dataset_quality": dataset_report,
                "paper_structure": paper_report,
                "literature_intelligence": literature_report,
                "methodology_evaluation": methodology_report,
            },
            "explainability": shap_explanation,
            "recommendations": recommendations,
        })


# Keep the catch-all frontend mount after the API routes.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
