import pandas as pd
from sklearn.model_selection import train_test_split

DATA_PATH = "data/xgboost/severity.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)

print("Dataset loaded")
print("-" * 50)
print("Shape:", df.shape)

# Target
TARGET = "severity_score"

# Features available BEFORE prediction
FEATURES = [
    "problem_category",
    "complaint_count",
    "affected_population",
    "population",
    "infrastructure_condition",
    "historical_incidents",
    "problem_duration_days",
]

X = df[FEATURES].copy()
y = df[TARGET].copy()

print("\nFeatures:")
print(X.columns.tolist())

print("\nTarget:")
print(TARGET)

print("\nCategorical features:")
print([
    "problem_category",
    "infrastructure_condition"
])

print("\nNumeric features:")
print([
    "complaint_count",
    "affected_population",
    "population",
    "historical_incidents",
    "problem_duration_days"
])

# Check missing values
print("\nMissing values:")
print(X.isnull().sum())

print("\nTarget statistics:")
print(y.describe())

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42
)

X_validation, X_test, y_validation, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42
)

print("\nDataset split:")
print("-" * 50)
print("Training:", X_train.shape)
print("Validation:", X_validation.shape)
print("Test:", X_test.shape)

# Save splits
X_train.assign(severity_score=y_train).to_csv(
    "data/xgboost/train.csv",
    index=False
)

X_validation.assign(severity_score=y_validation).to_csv(
    "data/xgboost/validation.csv",
    index=False
)

X_test.assign(severity_score=y_test).to_csv(
    "data/xgboost/test.csv",
    index=False
)

print("\nSaved:")
print("data/xgboost/train.csv")
print("data/xgboost/validation.csv")
print("data/xgboost/test.csv")

print("\nXGBoost dataset preparation complete!")