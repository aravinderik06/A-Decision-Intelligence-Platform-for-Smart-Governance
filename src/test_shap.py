import joblib
import pandas as pd
import shap

# --------------------------------------------------
# Paths
# --------------------------------------------------

MODEL_PATH = "models/xgboost_severity_model.pkl"
PREPROCESSOR_PATH = "models/xgboost_preprocessor.pkl"

# --------------------------------------------------
# Load model and preprocessor
# --------------------------------------------------

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

print("XGBoost model loaded.")
print("Preprocessor loaded.")

# --------------------------------------------------
# Example governance problem
# --------------------------------------------------

complaint = pd.DataFrame([{
    "problem_category": "Drainage",
    "complaint_count": 47,
    "affected_population": 4200,
    "population": 8500,
    "infrastructure_condition": "Poor",
    "historical_incidents": 8,
    "problem_duration_days": 5
}])

print("\nInput:")
print(complaint)

# --------------------------------------------------
# Transform input
# --------------------------------------------------

X = preprocessor.transform(complaint)

# --------------------------------------------------
# Predict severity
# --------------------------------------------------

prediction = model.predict(X)[0]

print("\nPredicted Severity Score:")
print(round(float(prediction), 2))

# --------------------------------------------------
# SHAP explanation
# --------------------------------------------------

explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(X)

# Get feature names after one-hot encoding
feature_names = preprocessor.get_feature_names_out()

# Convert SHAP values to a readable Series
shap_importance = pd.Series(
    shap_values[0],
    index=feature_names
)

# Sort by absolute contribution
shap_importance = shap_importance.reindex(
    shap_importance.abs().sort_values(
        ascending=False
    ).index
)

print("\nSHAP Explanation")
print("-" * 50)

for feature, value in shap_importance.head(10).items():

    direction = "increased" if value > 0 else "decreased"

    print(
        f"{feature}: "
        f"{direction} severity by "
        f"{abs(value):.4f}"
    )

print("\nSHAP explanation complete!")