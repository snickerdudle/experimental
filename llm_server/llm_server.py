# Self-sufficient Flask-based web server for running the model
from flask import Flask, request, jsonify, render_template
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

app = Flask(__name__)

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"


model = "tiiuae/falcon-7b"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="cuda:0",
)


@app.route("/prompt", methods=["POST"])
def index():
    prompt = request.form["prompt"]
    sequences = pipeline(
        prompt,
        max_length=1024,
        do_sample=False,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )
    for seq in sequences:
        print(f"Result: {seq['generated_text']}")
    return jsonify({"output": sequences})


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
