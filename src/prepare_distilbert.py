import pandas as pd

# -----------------------------
# 1. Load datasets
# -----------------------------

train_df = pd.read_csv("data/distilbert/train.csv")
validation_df = pd.read_csv("data/distilbert/validation.csv")
test_df = pd.read_csv("data/distilbert/test.csv")


# -----------------------------
# 2. Define category mapping
# -----------------------------

label2id = {
    "Roads": 0,
    "Water Supply": 1,
    "Drainage": 2,
    "Waste Management": 3,
    "Healthcare": 4,
    "Education": 5,
    "Street Lighting": 6,
    "Other": 7
}

id2label = {
    0: "Roads",
    1: "Water Supply",
    2: "Drainage",
    3: "Waste Management",
    4: "Healthcare",
    5: "Education",
    6: "Street Lighting",
    7: "Other"
}


# -----------------------------
# 3. Convert categories to IDs
# -----------------------------

train_df["label"] = train_df["problem_category"].map(label2id)
validation_df["label"] = validation_df["problem_category"].map(label2id)
test_df["label"] = test_df["problem_category"].map(label2id)


# -----------------------------
# 4. Check the result
# -----------------------------

print("Label mapping:")
print(label2id)

print("\nFirst 5 training examples:")
print(train_df[["complaint_text", "problem_category", "label"]].head())

print("\nLabel counts:")
print(train_df["label"].value_counts().sort_index())

print("\nMissing labels:")
print("Train:", train_df["label"].isna().sum())
print("Validation:", validation_df["label"].isna().sum())
print("Test:", test_df["label"].isna().sum())