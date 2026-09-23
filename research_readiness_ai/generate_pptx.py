import collections 
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os

def add_slide(prs, layout, title, content_lines=None, code_block=None):
    slide = prs.slides.add_slide(layout)
    if slide.shapes.title:
        slide.shapes.title.text = title
    
    # Text content
    if content_lines:
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 1:
                tf = shape.text_frame
                tf.clear()
                for i, line in enumerate(content_lines):
                    p = tf.add_paragraph()
                    p.text = line
                    p.level = 0
                    p.font.size = Pt(16)
                break
                
    # Add code block if present
    if code_block:
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(9), Inches(3.5))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.add_paragraph()
        p.text = code_block
        p.font.name = 'Courier New'
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(0, 51, 102)

def generate_presentation():
    prs = Presentation()
    
    # Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "Research Readiness AI"
    subtitle.text = "Detailed Methodology & Code Explanation\n(Real Project Structure & Implementation)"

    # Overview Slide
    bullet_slide_layout = prs.slide_layouts[1]
    content = [
        "Objective: Evaluate draft research papers and datasets, yielding a 0-100 Readiness Score.",
        "4 Key Dimensions: Dataset Quality, Paper Structure, Literature, Methodology.",
        "The project maps 24 extracted metrics into a single fused feature vector.",
        "Outputs:",
        " - An XGBoost-predicted Research Readiness Score (RRS)",
        " - SHAP interpretability charts explaining the score",
        " - Targeted actionable recommendations based on weak metrics"
    ]
    add_slide(prs, bullet_slide_layout, "Project Overview", content)

    # Methodology 1: Feature Fusion (with code)
    content = [
        "All 24 metrics extracted from the 4 analyzers are flattened into a single, ordered list.",
        "Maintaining this strict order (the FEATURE_NAMES list) is critical.",
        "It guarantees that SHAP values can map numerical importances back to readable names.",
        "Below is the actual implementation of the feature fusion:"
    ]
    code = """# app/feature_fusion.py (Snippet)
def fuse_features(dataset_report, paper_report, literature_report, methodology_report):
    ds, pp = dataset_report["metrics"], paper_report["metrics"]
    lit, mv = literature_report["metrics"], methodology_report["metrics"]
    vector = [
        ds["completeness"], ds["uniqueness"], ds["balance"], ds["validity"], ...
        pp["section_completeness"], pp["citation_density"], ...
        lit["reference_count_score"], lit["recency_score"], ...
        mv["baseline_comparison"], mv["metric_selection"], ...
    ]
    return vector
    """
    add_slide(prs, bullet_slide_layout, "Methodology: Feature Fusion", content, code)

    # Methodology 2: XGBoost and Synthetic Data weighting (with code)
    content = [
        "Why XGBoost? It excels at mapping tabular, non-linear feature interactions to a single score.",
        "Since a real dataset of 10,000 labeled papers doesn't exist, the project uses a synthetic generator.",
        "It creates realistic data by applying a Reviewer-Informed Weighting Formula.",
        "Methodology and paper structure metrics are assigned the highest weights."
    ]
    code = """# train_model.py (Actual Weighting Implementation)
WEIGHTS = {
    "ds_completeness": 0.9, "ds_size_adequacy": 1.0, 
    "pp_section_completeness": 1.3, "pp_novelty_signaling": 1.4,
    "mv_baseline_comparison": 1.4, "mv_statistical_rigor": 1.3,
    # ... other 18 weights
}
# A Beta distribution generates metric scores. Then base score is:
weighted_sum = df[FEATURE_NAMES].values @ weight_vec
base_score = (weighted_sum / max_possible) * 100
label = np.clip(base_score + noise, 0, 100) # Final Readiness Score
    """
    add_slide(prs, bullet_slide_layout, "Methodology: XGBoost & Weightings", content, code)

    # XGBoost Training Code
    content = [
        "The XGBoost Regressor is trained to minimize the Mean Absolute Error (MAE).",
        "It uses 300 estimators and limits depth to 4 to prevent overfitting the synthetic data.",
        "The trained model is then serialized via joblib for the FastAPI backend."
    ]
    code = """# train_model.py (Actual Training Logic)
model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    reg_lambda=1.0,
    random_state=42,
    objective="reg:squarederror",
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
joblib.dump(model, "models/rrs_xgboost.joblib")
    """
    add_slide(prs, bullet_slide_layout, "Methodology: XGBoost Training", content, code)

    # SHAP Explainability (with code)
    content = [
        "Why SHAP? XGBoost is a 'black box'. SHAP makes it transparent.",
        "SHAP (SHapley Additive exPlanations) breaks down the final score prediction.",
        "It tells the user exactly how much each specific metric pushed the score up or down.",
        "The explainer calculates the impact for a single uploaded paper."
    ]
    code = """# app/shap_explainer.py (Actual SHAP Logic)
def explain(feature_vector, top_k=8):
    explainer = shap.TreeExplainer(model)
    X = pd.DataFrame([feature_vector], columns=FEATURE_NAMES)
    shap_values = explainer(X)
    
    contributions = list(zip(FEATURE_NAMES, feature_vector, shap_values.values[0]))
    contributions.sort(key=lambda t: abs(t[2]), reverse=True) # Sort by absolute impact
    
    top_positive = [c for c in contributions if c[2] > 0][:top_k]
    top_negative = [c for c in contributions if c[2] < 0][:top_k]
    return {"top_positive_contributors": top_positive, ...}
    """
    add_slide(prs, bullet_slide_layout, "Methodology: SHAP Explainer", content, code)

    # End-to-End Workflow / API
    content = [
        "1. Input: User POSTs files to `/assess` endpoint in FastAPI.",
        "2. Parse: Analyzers process PDF text & CSV data into 24 metrics.",
        "3. Fuse: feature_fusion.py flattens the 24 metrics into a vector.",
        "4. Predict: models/rrs_xgboost.joblib generates the 0-100 score.",
        "5. Explain: shap_explainer.py maps feature impacts.",
        "6. Recommend: rule-engine checks metrics against thresholds.",
        "7. Output: JSON response returned to the frontend."
    ]
    code = """# app/main.py (Endpoint architecture snippet)
@app.post("/assess")
async def assess(paper: UploadFile = File(...), dataset: UploadFile = File(None)):
    ...
    feature_vector = fuse_features(ds_report, pp_report, lit_report, mv_report)
    rrs = predict_rrs(feature_vector)
    shap_explanation = explain(feature_vector)
    recommendations = generate_recommendations(dict(zip(FEATURE_NAMES, feature_vector)))
    
    return {"score": rrs, "explainability": shap_explanation, ...}
    """
    add_slide(prs, bullet_slide_layout, "End-to-End Work Procedure", content, code)

    # Save the presentation
    out_path = 'e:/Downloads/ALL_Final_Project/ml_project/research_readiness_ai/Research_Readiness_AI_Presentation.pptx'
    prs.save(out_path)

if __name__ == '__main__':
    generate_presentation()
