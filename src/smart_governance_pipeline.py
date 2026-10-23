import joblib
import pandas as pd
import shap
import torch

from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.decision_engine import make_decision


# ============================================================
# PATHS
# ============================================================

DISTILBERT_PATH = "models/distilbert_model"

XGB_MODEL_PATH = "models/xgboost_severity_model.pkl"
XGB_PREPROCESSOR_PATH = "models/xgboost_preprocessor.pkl"


# ============================================================
# LOAD MODELS
# ============================================================

print("Loading AI models...")

tokenizer = AutoTokenizer.from_pretrained(
    DISTILBERT_PATH
)

distilbert_model = AutoModelForSequenceClassification.from_pretrained(
    DISTILBERT_PATH
)

distilbert_model.eval()

xgb_model = joblib.load(
    XGB_MODEL_PATH
)

xgb_preprocessor = joblib.load(
    XGB_PREPROCESSOR_PATH
)

print("All models loaded successfully.")


# ============================================================
# MODEL 1 — DISTILBERT
# ============================================================

def classify_problem(complaint_text):

    inputs = tokenizer(
        complaint_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = distilbert_model(
            **inputs
        )

    probabilities = torch.softmax(
        outputs.logits,
        dim=1
    )

    predicted_class = torch.argmax(
        probabilities,
        dim=1
    ).item()

    confidence = probabilities[
        0,
        predicted_class
    ].item()

    problem_category = (
        distilbert_model.config.id2label[
            predicted_class
        ]
    )

    return problem_category, confidence


# ============================================================
# MODEL 2 — XGBOOST
# ============================================================

def predict_severity(
    problem_category,
    complaint_count,
    affected_population,
    population,
    infrastructure_condition,
    historical_incidents,
    problem_duration_days
):

    input_data = pd.DataFrame([{
        "problem_category": problem_category,
        "complaint_count": complaint_count,
        "affected_population": affected_population,
        "population": population,
        "infrastructure_condition": infrastructure_condition,
        "historical_incidents": historical_incidents,
        "problem_duration_days": problem_duration_days
    }])

    X = xgb_preprocessor.transform(
        input_data
    )

    severity_score = xgb_model.predict(
        X
    )[0]

    return float(severity_score), X


# ============================================================
# SHAP EXPLANATION
# ============================================================

def explain_prediction(X):

    explainer = shap.TreeExplainer(
        xgb_model
    )

    shap_values = explainer.shap_values(
        X
    )

    feature_names = (
        xgb_preprocessor
        .get_feature_names_out()
    )

    shap_series = pd.Series(
        shap_values[0],
        index=feature_names
    )

    shap_series = shap_series.reindex(
        shap_series.abs()
        .sort_values(ascending=False)
        .index
    )

    explanations = []

    for feature, value in shap_series.head(5).items():

        direction = (
            "increased"
            if value > 0
            else "decreased"
        )

        explanations.append({
            "feature": feature,
            "impact": round(
                float(value),
                4
            ),
            "direction": direction
        })

    return explanations


# ============================================================
# COMPLETE PIPELINE
# ============================================================

def run_pipeline(
    complaint_text,
    complaint_count,
    affected_population,
    population,
    infrastructure_condition,
    historical_incidents,
    problem_duration_days
):

    # --------------------------------------------------------
    # 1. DistilBERT
    # --------------------------------------------------------

    problem_category, confidence = (
        classify_problem(
            complaint_text
        )
    )

    # --------------------------------------------------------
    # 2. XGBoost
    # --------------------------------------------------------

    severity_score, X = predict_severity(
        problem_category,
        complaint_count,
        affected_population,
        population,
        infrastructure_condition,
        historical_incidents,
        problem_duration_days
    )

    # --------------------------------------------------------
    # 3. SHAP
    # --------------------------------------------------------

    explanations = explain_prediction(
        X
    )

    # --------------------------------------------------------
    # 4. Decision Engine
    # --------------------------------------------------------

    decision = make_decision(
        problem_category=problem_category,
        severity_score=severity_score,
        complaint_count=complaint_count,
        affected_population=affected_population,
        infrastructure_condition=infrastructure_condition
    )

    # --------------------------------------------------------
    # 5. Final system output
    # --------------------------------------------------------

    result = {
        "complaint": complaint_text,

        "problem_category": problem_category,

        "classification_confidence": round(
            confidence,
            4
        ),

        "severity_score": round(
            severity_score,
            2
        ),

        "shap_explanation": explanations,

        "recommendation": decision[
            "recommendation"
        ],

        "priority": decision[
            "priority"
        ],

        "suggested_action": decision[
            "suggested_action"
        ],

        "reason": decision[
            "reason"
        ],

        "officer_decision_required": decision[
            "officer_decision_required"
        ]
    }

    return result


# ============================================================
# TEST THE COMPLETE PIPELINE
# ============================================================

if __name__ == "__main__":

    complaint = (
        "For the last 5 days, sewage water has been "
        "overflowing onto the road near the government "
        "school and entering nearby houses."
    )

    result = run_pipeline(

        complaint_text=complaint,

        complaint_count=47,

        affected_population=4200,

        population=8500,

        infrastructure_condition="Poor",

        historical_incidents=8,

        problem_duration_days=5
    )

    print("\n")
    print("=" * 60)
    print("SMART GOVERNANCE AI PIPELINE")
    print("=" * 60)

    print("\nCOMPLAINT:")
    print(result["complaint"])

    print("\nPROBLEM CATEGORY:")
    print(result["problem_category"])

    print(
        "\nCLASSIFICATION CONFIDENCE:",
        result["classification_confidence"]
    )

    print(
        "\nSEVERITY SCORE:",
        result["severity_score"]
    )

    print("\nSHAP EXPLANATION:")

    for explanation in result[
        "shap_explanation"
    ]:

        print(
            f"  {explanation['feature']} "
            f"→ {explanation['direction']} "
            f"severity by "
            f"{abs(explanation['impact'])}"
        )

    print("\nPRIORITY:")
    print(result["priority"])

    print("\nRECOMMENDATION:")
    print(result["recommendation"])

    print("\nSUGGESTED ACTION:")
    print(result["suggested_action"])

    print("\nREASON:")
    print(result["reason"])

    print(
        "\nOFFICER DECISION REQUIRED:",
        result["officer_decision_required"]
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)