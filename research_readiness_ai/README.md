# ResearchReadiness AI

**ResearchReadiness AI** is an AI-assisted research paper assessment system that evaluates how ready a research paper is for submission or review.

The system accepts a **research paper** (`PDF`, `DOCX`, or `TXT`) and an optional **dataset** (`CSV`). It analyzes the paper, dataset, literature references, and methodology, then produces a **Research Readiness Score (RRS) from 0–100**.

The result includes:

* Overall Research Readiness Score
* Breakdown across major research-quality dimensions
* SHAP-based explainability showing which factors influenced the score
* Targeted recommendations for improving weak areas

The project is designed as a working end-to-end prototype where the user uploads research materials and receives an automated readiness assessment.

---

## How It Works

The system follows this pipeline:

**Research Paper + Optional Dataset**
↓
**Paper Analysis**
↓
**Dataset Analysis**
↓
**Literature Analysis**
↓
**Methodology Evaluation**
↓
**Feature Fusion**
↓
**XGBoost Prediction**
↓
**SHAP Explainability**
↓
**Targeted Recommendations**
↓
**Research Readiness Score**

### Main Components

| Component                  | Purpose                                                                                                                                   |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `dataset_analyzer.py`      | Analyzes dataset quality such as completeness, uniqueness, class balance, validity, consistency, size, feature richness, and outliers     |
| `paper_analyzer.py`        | Extracts and analyzes the research paper structure, sections, citations, methodology, experiments, writing quality, visuals, and abstract |
| `literature_analyzer.py`   | Analyzes the references section, including reference count, recency, author coverage, and related-work depth                              |
| `methodology_checker.py`   | Checks for baselines, evaluation metrics, statistical rigor, and reproducibility signals                                                  |
| `feature_fusion.py`        | Combines the extracted metrics into a feature vector for the prediction model                                                             |
| `model.py`                 | Loads and uses the XGBoost model to generate the Research Readiness Score                                                                 |
| `shap_explainer.py`        | Explains which features contributed positively or negatively to the predicted score                                                       |
| `recommendation_engine.py` | Generates targeted recommendations based on weak areas                                                                                    |
| `main.py`                  | FastAPI backend that connects all components into the `/assess` endpoint                                                                  |
| `frontend/index.html`      | Web interface for uploading files and viewing the assessment results                                                                      |

---

## Features

### 1. Research Paper Analysis

The system analyzes uploaded research papers and checks factors such as:

* Section completeness
* Abstract quality
* Citation density
* Novelty signaling
* Methodology presence
* Experimental evidence
* Writing quality
* Visual support

Supported formats:

* PDF
* DOCX
* TXT

### 2. Dataset Quality Analysis

For an uploaded CSV dataset, the system evaluates factors including:

* Completeness
* Uniqueness
* Class balance
* Data validity
* Consistency
* Dataset size
* Feature richness
* Outlier control

The dataset is optional. The system can assess a paper without a dataset when the research does not require one.

### 3. Literature Intelligence

The system analyzes the references included in the paper and considers:

* Number of references
* Reference recency
* Author coverage
* Related-work depth

### 4. Methodology Evaluation

The system checks whether the paper contains important research methodology signals, including:

* Baseline comparisons
* Named evaluation metrics
* Statistical rigor
* Reproducibility information

### 5. Research Readiness Score

The extracted information is combined and passed to an XGBoost model to generate a score between:

**0–100**

A higher score indicates that more of the evaluated research-readiness criteria are satisfied.

### 6. Explainability

The system uses **SHAP** to explain the prediction.

This helps identify which factors had the greatest positive or negative contribution to the final score.

### 7. Targeted Recommendations

Instead of only providing a score, the system identifies weak areas and provides specific recommendations for improvement.

---

## Project Structure

```text
research_readiness_ai/
│
├── app/
│   ├── main.py
│   ├── dataset_analyzer.py
│   ├── paper_analyzer.py
│   ├── literature_analyzer.py
│   ├── methodology_checker.py
│   ├── feature_fusion.py
│   ├── model.py
│   ├── shap_explainer.py
│   └── recommendation_engine.py
│
├── frontend/
│   └── index.html
│
├── sample_data/
│   ├── sample_paper.txt
│   └── sample_dataset.csv
│
├── models/
│   └── rrs_xgboost.joblib
│
├── train_model.py
├── requirements.txt
└── README.md
```

---

# Setup

## 1. Clone or Download the Project

Download the project and open a terminal inside the project directory.

```bash
cd research_readiness_ai
```

---

## 2. Create a Virtual Environment

Creating a virtual environment is recommended.

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Mac/Linux

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 4. Train the Model

Before running the application, train the XGBoost model:

```bash
python train_model.py
```

This creates the model file:

```text
models/rrs_xgboost.joblib
```

---

## 5. Start the API Server

Run the FastAPI application using Uvicorn:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The server will start at:

```text
http://localhost:8000/
```

Open this address in your browser to use the application.

---

## 6. Test the Application

Sample files are included in the `sample_data/` directory.

You can test the system using:

```bash
curl -X POST http://localhost:8000/assess ^
  -F "paper=@sample_data/sample_paper.txt" ^
  -F "dataset=@sample_data/sample_dataset.csv"
```

For Mac/Linux:

```bash
curl -X POST http://localhost:8000/assess \
  -F "paper=@sample_data/sample_paper.txt" \
  -F "dataset=@sample_data/sample_dataset.csv"
```

You can also use the web interface instead of `curl`.

---

# API

## `POST /assess`

Evaluates a research paper and optionally its dataset.

### Input

**Required:**

```text
paper
```

Supported formats:

```text
.pdf
.docx
.txt
```

**Optional:**

```text
dataset
```

Supported format:

```text
.csv
```

### Example Response

```json
{
  "research_readiness_score": 75.9,
  "dimension_breakdown": {
    "dataset_quality": {},
    "paper_structure": {},
    "literature_intelligence": {},
    "methodology": {}
  },
  "explainability": "Base Value: 50.17\n\nTop Positive Contributors:\n- pp_novelty_signaling impacted the score positively.",
  "recommendations": [
    {
      "feature": "example_feature",
      "score": 15.0,
      "recommendation": "Improve this area by adding..."
    }
  ]
}
```

---

# Technology Stack

* **Python**
* **FastAPI**
* **Uvicorn**
* **XGBoost**
* **SHAP**
* **Pandas**
* **Scikit-learn**
* **PDF/DOCX text extraction**
* **HTML/CSS/JavaScript**

---

# Running the Project

For normal use, the complete process is:

```bash
# Create environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train model
python train_model.py

# Start application
python -m uvicorn app.main:app --reload --port 8000
```

Then open:

```text
http://localhost:8000/
```

Upload a research paper and, if applicable, its dataset to receive the assessment.

---

## Important Note

The current prediction model is intended as a **working prototype**. The model can operate end-to-end, but its predictive reliability depends on the quality and amount of training data used to train it.

For a production-level system, the model should eventually be trained and validated using real research papers, datasets, and reviewer-provided readiness labels.
