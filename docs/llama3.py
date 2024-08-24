# filename: download_llama3.py
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download the model and tokenizer
model_name = "meta-llama/Meta-Llama-3.1-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Save the model and tokenizer
model.save_pretrained("./llama3_model")
tokenizer.save_pretrained("./llama3_tokenizer")  