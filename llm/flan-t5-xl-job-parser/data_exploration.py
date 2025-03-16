from datasets import load_dataset
import tiktoken
from transformers import T5Tokenizer
import json

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-xl")
# Example: Load the AG News dataset
dataset = load_dataset("vmal/jobs_dataset")

# Print dataset split details
print(dataset)

max_source=0
max_target=0
for example in dataset["train"]:
    # print(example)
    sn = len(tokenizer.tokenize(example['target_text']))
    tn = len(tokenizer.tokenize(example['source_text']))
    max_source = max(max_source, sn)
    max_target = max(max_target, tn)

print(f'Max source tokens: {max_source}')
print(f'Max target tokens: {max_target}')