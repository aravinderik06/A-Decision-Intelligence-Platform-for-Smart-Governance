import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "models/distilbert_model"

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

complaints = [
    "The road near the school has several large potholes and vehicles are finding it difficult to pass.",
    "Sewage water has been overflowing onto the street for the past week.",
    "There has been no water supply in our area for three days.",
    "Garbage has not been collected for several days and waste is piling up.",
    "The street lights are not working and the road becomes completely dark at night."
]

for complaint in complaints:

    inputs = tokenizer(
        complaint,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)
    predicted_class = torch.argmax(probabilities, dim=1).item()
    confidence = probabilities[0][predicted_class].item()

    predicted_label = model.config.id2label[predicted_class]

    print("\n" + "-" * 60)
    print("Complaint:")
    print(complaint)
    print("Predicted Problem:", predicted_label)
    print("Confidence:", round(confidence, 4))