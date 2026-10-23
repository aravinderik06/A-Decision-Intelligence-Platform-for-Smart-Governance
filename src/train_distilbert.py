import os
import json
import pandas as pd
import torch

from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

from transformers import AutoTokenizer, AutoModelForSequenceClassification

from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# ============================================================
# 1. SETTINGS
# ============================================================

MODEL_NAME = "distilbert-base-uncased"

MAX_LENGTH = 128
BATCH_SIZE = 8
EPOCHS = 2
LEARNING_RATE = 2e-5

TRAIN_PATH = "data/distilbert/train.csv"
VALIDATION_PATH = "data/distilbert/validation.csv"
TEST_PATH = "data/distilbert/test.csv"

MODEL_OUTPUT_DIR = "models/distilbert_model"
RESULTS_DIR = "results"


# ============================================================
# 2. LABEL MAPPING
# ============================================================

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


# ============================================================
# 3. LOAD DATA
# ============================================================

print("Loading datasets...")

train_df = pd.read_csv(TRAIN_PATH)
validation_df = pd.read_csv(VALIDATION_PATH)
test_df = pd.read_csv(TEST_PATH)

print("Train:", train_df.shape)
print("Validation:", validation_df.shape)
print("Test:", test_df.shape)


# Convert category names into numerical labels
train_df["label"] = train_df["problem_category"].map(label2id)
validation_df["label"] = validation_df["problem_category"].map(label2id)
test_df["label"] = test_df["problem_category"].map(label2id)


# Safety check
assert train_df["label"].notna().all()
assert validation_df["label"].notna().all()
assert test_df["label"].notna().all()


# ============================================================
# 4. LOAD DISTILBERT TOKENIZER
# ============================================================

print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


# ============================================================
# 5. CREATE PYTORCH DATASET
# ============================================================

class ComplaintDataset(Dataset):

    def __init__(self, dataframe):

        self.texts = dataframe["complaint_text"].tolist()
        self.labels = dataframe["label"].astype(int).tolist()

        self.encodings = tokenizer(
            self.texts,
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH
        )

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):

        item = {
            key: torch.tensor(value[index])
            for key, value in self.encodings.items()
        }

        item["labels"] = torch.tensor(
            self.labels[index],
            dtype=torch.long
        )

        return item


# Create datasets
train_dataset = ComplaintDataset(train_df)
validation_dataset = ComplaintDataset(validation_df)
test_dataset = ComplaintDataset(test_df)


# ============================================================
# 6. CREATE DATALOADERS
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# ============================================================
# 7. SELECT DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("\nTraining device:", device)


# ============================================================
# 8. LOAD DISTILBERT MODEL
# ============================================================

print("\nLoading DistilBERT model...")

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=8,
    id2label=id2label,
    label2id=label2id
)

model.to(device)


# ============================================================
# 9. OPTIMIZER
# ============================================================

optimizer = AdamW(
    model.parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# 10. EVALUATION FUNCTION
# ============================================================

def evaluate(model, dataloader):

    model.eval()

    all_predictions = []
    all_labels = []

    total_loss = 0

    with torch.no_grad():

        for batch in dataloader:

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            total_loss += outputs.loss.item()

            predictions = torch.argmax(
                outputs.logits,
                dim=1
            )

            all_predictions.extend(
                predictions.cpu().tolist()
            )

            all_labels.extend(
                labels.cpu().tolist()
            )

    accuracy = accuracy_score(
        all_labels,
        all_predictions
    )

    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels,
        all_predictions,
        average="weighted",
        zero_division=0
    )

    average_loss = total_loss / len(dataloader)

    return {
        "loss": average_loss,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ============================================================
# 11. TRAINING
# ============================================================

print("\nStarting training...")
print("----------------------------------------")

for epoch in range(EPOCHS):

    model.train()

    total_training_loss = 0

    for batch_number, batch in enumerate(train_loader):

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss

        loss.backward()

        optimizer.step()

        total_training_loss += loss.item()

        if (batch_number + 1) % 50 == 0:

            print(
                f"Epoch {epoch + 1}/{EPOCHS} | "
                f"Batch {batch_number + 1}/{len(train_loader)} | "
                f"Loss: {loss.item():.4f}"
            )

    average_training_loss = (
        total_training_loss / len(train_loader)
    )

    validation_metrics = evaluate(
        model,
        validation_loader
    )

    print("\nEpoch completed:")
    print("Training Loss:", round(average_training_loss, 4))
    print("Validation Loss:", round(validation_metrics["loss"], 4))
    print("Validation Accuracy:", round(validation_metrics["accuracy"], 4))
    print("Validation F1:", round(validation_metrics["f1"], 4))
    print("----------------------------------------")


# ============================================================
# 12. FINAL TEST EVALUATION
# ============================================================

print("\nEvaluating final model on TEST data...")

test_metrics = evaluate(
    model,
    test_loader
)

print("\nTEST RESULTS")
print("----------------------------------------")
print("Accuracy :", round(test_metrics["accuracy"], 4))
print("Precision:", round(test_metrics["precision"], 4))
print("Recall   :", round(test_metrics["recall"], 4))
print("F1 Score :", round(test_metrics["f1"], 4))


# ============================================================
# 13. SAVE MODEL
# ============================================================

os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

print("\nSaving model...")

model.save_pretrained(MODEL_OUTPUT_DIR)
tokenizer.save_pretrained(MODEL_OUTPUT_DIR)


# Save label mapping
with open(
    os.path.join(MODEL_OUTPUT_DIR, "label_mapping.json"),
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        {
            "label2id": label2id,
            "id2label": id2label
        },
        file,
        indent=4
    )


# Save test metrics
with open(
    os.path.join(RESULTS_DIR, "distilbert_test_metrics.json"),
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        test_metrics,
        file,
        indent=4
    )


print("\nModel saved to:")
print(MODEL_OUTPUT_DIR)

print("\nTraining complete!")