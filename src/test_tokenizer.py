import pandas as pd
from transformers import AutoTokenizer

# Load our training data
df = pd.read_csv("data/distilbert/train.csv")

# Take one complaint
text = df.iloc[0]["complaint_text"]

print("Original complaint:")
print(text)

# Load the DistilBERT tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Tokenize the complaint
encoded = tokenizer(
    text,
    padding="max_length",
    truncation=True,
    max_length=128
)

print("\nTokens:")
print(tokenizer.convert_ids_to_tokens(encoded["input_ids"]))

print("\nToken IDs:")
print(encoded["input_ids"])

print("\nAttention mask:")
print(encoded["attention_mask"])