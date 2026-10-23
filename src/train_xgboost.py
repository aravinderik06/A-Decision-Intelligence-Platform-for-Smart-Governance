import json
import joblib
import pandas as pd

from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = "data/xgboost/train.csv"
VALIDATION_PATH = "data/xgboost/validation.csv"
TEST_PATH = "data/xgboost/test.csv"

MODEL_PATH = "models/xgboost_severity_model.pkl"
PREPROCESSOR_PATH = "models/xgboost_preprocessor.pkl"
METRICS_PATH = "results/xgboost_test_metrics.json"


# ============================================================
# LOAD DATA
# ============================================================

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)
test_df = pd.read_csv(TEST_PATH)

TARGET = "severity_score"

FEATURES = [
    "problem_category",
    "complaint_count",
    "affected_population",
    "population",
    "infrastructure_condition",
    "historical_incidents",
    "problem_duration_days",
]


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_validation = validation_df[FEATURES]
y_validation = validation_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ============================================================
# FEATURE TYPES
# ============================================================

CATEGORICAL_FEATURES = [
    "problem_category",
    "infrastructure_condition",
]

NUMERICAL_FEATURES = [
    "complaint_count",
    "affected_population",
    "population",
    "historical_incidents",
    "problem_duration_days",
]


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            CATEGORICAL_FEATURES,
        ),
        (
            "numerical",
            "passthrough",
            NUMERICAL_FEATURES,
        ),
    ]
)


X_train_processed = preprocessor.fit_transform(X_train)
X_validation_processed = preprocessor.transform(X_validation)
X_test_processed = preprocessor.transform(X_test)


# ============================================================
# TRAIN XGBOOST
# ============================================================

print("\nStarting XGBoost training...")
print("-" * 50)

model = XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1,
)

model.fit(
    X_train_processed,
    y_train,
    eval_set=[
        (X_validation_processed, y_validation)
    ],
    verbose=False,
)

print("Training complete!")


# ============================================================
# VALIDATION
# ============================================================

validation_predictions = model.predict(
    X_validation_processed
)

validation_mae = mean_absolute_error(
    y_validation,
    validation_predictions
)

validation_rmse = mean_squared_error(
    y_validation,
    validation_predictions
) ** 0.5

validation_r2 = r2_score(
    y_validation,
    validation_predictions
)

print("\nVALIDATION RESULTS")
print("-" * 50)
print("MAE  :", round(validation_mae, 4))
print("RMSE :", round(validation_rmse, 4))
print("R2   :", round(validation_r2, 4))


# ============================================================
# FINAL TEST
# ============================================================

print("\nEvaluating final model on TEST data...")

test_predictions = model.predict(
    X_test_processed
)

test_mae = mean_absolute_error(
    y_test,
    test_predictions
)

test_rmse = mean_squared_error(
    y_test,
    test_predictions
) ** 0.5

test_r2 = r2_score(
    y_test,
    test_predictions
)


print("\nTEST RESULTS")
print("-" * 50)
print("MAE  :", round(test_mae, 4))
print("RMSE :", round(test_rmse, 4))
print("R2   :", round(test_r2, 4))


# ============================================================
# SAVE MODEL
# ============================================================

print("\nSaving XGBoost model...")

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    preprocessor,
    PREPROCESSOR_PATH
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics = {
    "model": "XGBoost",
    "target": "severity_score",
    "validation_mae": validation_mae,
    "validation_rmse": validation_rmse,
    "validation_r2": validation_r2,
    "test_mae": test_mae,
    "test_rmse": test_rmse,
    "test_r2": test_r2,
    "data_status": "synthetic_demo",
}

with open(METRICS_PATH, "w") as file:
    json.dump(
        metrics,
        file,
        indent=4
    )


print("\nModel saved to:")
print(MODEL_PATH)

print("\nPreprocessor saved to:")
print(PREPROCESSOR_PATH)

print("\nMetrics saved to:")
print(METRICS_PATH)

print("\nXGBoost Model 2 training complete!")