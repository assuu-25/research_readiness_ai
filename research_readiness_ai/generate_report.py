import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

def create_report():
    doc = docx.Document()
    
    # Title
    title = doc.add_heading('Research Readiness AI - Project Details', 0)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    # Introduction
    doc.add_heading('1. Introduction', level=1)
    doc.add_paragraph(
        "Research Readiness AI is an end-to-end machine learning pipeline designed to automatically evaluate "
        "draft research papers and accompanying datasets. The system generates a 'Research Readiness Score (RRS)' "
        "ranging from 0 to 100, broken down across four distinct dimensions. The tool not only provides a final score "
        "but also offers high explainability through SHAP values and actionable recommendations to improve the paper."
    )
    
    # Models and Tools Used
    doc.add_heading('2. Models and Tools Used', level=1)
    doc.add_paragraph("The project heavily relies on standard data science, machine learning, and web backend tools:")
    
    ul = doc.add_paragraph(style='List Bullet')
    ul.add_run("XGBoost (Extreme Gradient Boosting): ").bold = True
    ul.add_run("Used as the core predictive model to map the 24 extracted features into a 0-100 score.")
    
    ul = doc.add_paragraph(style='List Bullet')
    ul.add_run("SHAP (SHapley Additive exPlanations): ").bold = True
    ul.add_run("Used to provide transparent and explainable AI capabilities. It explains the output of the XGBoost model.")
    
    ul = doc.add_paragraph(style='List Bullet')
    ul.add_run("FastAPI & Uvicorn: ").bold = True
    ul.add_run("Used to construct and serve the RESTful API that handles file uploads and returns the assessment JSON.")
    
    ul = doc.add_paragraph(style='List Bullet')
    ul.add_run("Data Processing & Text Analytics: ").bold = True
    ul.add_run("Pandas, NumPy, Scikit-Learn for data manipulation. pdfplumber for extracting text from PDFs. textstat for writing quality analysis.")
    
    ul = doc.add_paragraph(style='List Bullet')
    ul.add_run("Frontend UI: ").bold = True
    ul.add_run("A minimal HTML/JS browser interface to interact with the API.")
    
    # XGBoost and SHAP in Detail
    doc.add_heading('3. Why XGBoost and SHAP?', level=1)
    doc.add_heading('XGBoost (Extreme Gradient Boosting)', level=2)
    doc.add_paragraph(
        "Reason for Use: XGBoost was selected as the regressor for this project because the data structure consists of "
        "tabular, numerical features (a 24-dimensional feature vector). XGBoost is highly optimized, handles non-linear "
        "relationships exceptionally well without requiring extensive feature scaling, and provides robust performance out of the box. "
        "It maps the multi-modal metrics (from paper, dataset, methodology, and literature) into a unified continuous score (0-100) efficiently."
    )
    
    doc.add_heading('SHAP (SHapley Additive exPlanations)', level=2)
    doc.add_paragraph(
        "Reason for Use: While XGBoost is a powerful model, it is often viewed as a 'black box'. In an academic or editorial context, "
        "simply telling an author their paper scored a '75' is not helpful. SHAP is used to decompose the final prediction into the "
        "sum of contributions from each of the 24 features. \n\n"
        "By computing SHAP values (via shap.TreeExplainer), the system can pinpoint exactly which metrics pushed the score up "
        "(e.g., strong methodology presence) and which metrics dragged the score down (e.g., lack of dataset baseline comparison). "
        "This guarantees local interpretability—explaining the specific 'WHY' for each individual paper evaluated."
    )
    
    # Methodology
    doc.add_heading('4. Detailed Methodology', level=1)
    doc.add_paragraph(
        "The project methodology is broken down into a multi-modal feature extraction phase, followed by feature fusion, "
        "scoring, and recommendation generation."
    )
    
    # Sub-sections for Methodology
    doc.add_heading('A. Feature Extraction (4 Dimensions)', level=2)
    p = doc.add_paragraph()
    p.add_run("1. Dataset Quality (8 dims): ").bold = True
    p.add_run("Analyzes an uploaded CSV file. Metrics include completeness (missing values), uniqueness, class balance, validity, consistency, size adequacy, feature richness, and outlier control.")
    
    p = doc.add_paragraph()
    p.add_run("2. Paper Structure (8 dims): ").bold = True
    p.add_run("Extracts raw text from PDF/DOCX/TXT files. It evaluates section completeness, citation density, novelty signaling (keyword-based), methodology/experiment presence, writing quality, visual support, and abstract quality.")
    
    p = doc.add_paragraph()
    p.add_run("3. Literature Intelligence (4 dims): ").bold = True
    p.add_run("Parses the References section to score reference count, recency of citations, author coverage breadth, and related-work depth via regex-based parsing.")
    
    p = doc.add_paragraph()
    p.add_run("4. Methodology Evaluation (4 dims): ").bold = True
    p.add_run("Scans the text for baseline comparisons, named evaluation metrics, statistical rigor language, and reproducibility signals.")
    
    doc.add_heading('B. Multi-Modal Feature Fusion', level=2)
    doc.add_paragraph(
        "All 24 extracted metrics (each scored typically from 0-100) are flattened into a single, strictly ordered "
        "feature vector. Maintaining this exact order is crucial because it allows the SHAP explainer to map the numerical "
        "importances back to human-readable dimension names."
    )
    
    doc.add_heading('C. Synthetic Dataset & XGBoost Training', level=2)
    doc.add_paragraph(
        "Because a massive dataset of 10,000+ labeled draft/published papers does not publicly exist, the project utilizes a "
        "synthetic but realistic data generation approach. It samples plausible metric values using skewed Beta distributions. "
        "The target 'readiness label' is generated using a reviewer-informed weighted formula (placing higher importance on "
        "methodology and structure) combined with random noise. The XGBoost Regressor is trained on this synthetic dataset "
        "to simulate a real-world evaluation model."
    )
    
    doc.add_heading('D. Rule-Based Recommendation Engine', level=2)
    doc.add_paragraph(
        "Separate from the ML prediction, a recommendation engine looks at the individual 24 features. If any feature falls "
        "below a pre-defined threshold, it triggers a specific, actionable recommendation (e.g., 'Increase baseline comparisons' "
        "or 'Address class imbalance in the dataset')."
    )
    
    # Work Procedure
    doc.add_heading('5. Work Procedure (End-to-End Pipeline)', level=1)
    doc.add_paragraph(
        "The workflow of the system from the user's perspective to the final output is defined as follows:"
    )
    
    steps = [
        ("Step 1: Input", "The user uploads a draft paper (in PDF, DOCX, or TXT format) and optionally an accompanying dataset (CSV file) via the minimal frontend UI."),
        ("Step 2: Parsing & Extraction", "The FastAPI backend receives the files. The paper is parsed into raw text. The CSV dataset is loaded into a Pandas DataFrame."),
        ("Step 3: Multi-Dimensional Analysis", "The system runs the four analyzers (Dataset, Paper, Literature, Methodology) independently. If no dataset is provided, neutral placeholder scores are used to maintain vector structure."),
        ("Step 4: Fusion", "The feature_fusion.py module aggregates the output into a 24-dimensional feature vector."),
        ("Step 5: Prediction", "The pre-trained XGBoost model consumes the vector and outputs the final Research Readiness Score (0-100)."),
        ("Step 6: Explainability", "The shap_explainer.py module takes the same vector and the XGBoost model to calculate the exact positive and negative SHAP contributions of the features."),
        ("Step 7: Recommendations", "The recommendation engine generates targeted advice based on weak metrics."),
        ("Step 8: Output", "A comprehensive JSON payload is returned to the frontend, displaying the score, visual SHAP charts, dimension breakdowns, and actionable fixes to the user.")
    ]
    
    for title, desc in steps:
        p = doc.add_paragraph(style='List Number')
        p.add_run(f"{title}: ").bold = True
        p.add_run(desc)
        
    # Extending the project
    doc.add_heading('6. Future Extensions', level=1)
    doc.add_paragraph(
        "The system's architecture is highly modular. Future improvements include swapping the synthetic data loader for real labeled data, "
        "integrating semantic embeddings (e.g., Semantic Scholar API) for robust novelty detection, and utilizing citation graph APIs "
        "(like GROBID or OpenAlex) for advanced literature intelligence."
    )
    
    doc.save('e:/Downloads/ALL_Final_Project/ml_project/research_readiness_ai/Research_Readiness_AI_Details.docx')

if __name__ == '__main__':
    create_report()
