import time
from typing import List

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_PATH = "/root/siton-data-guanchunxiangData/renjiaju/phe3-finetune/models/Qwen3-8B"
SERVED_MODEL_NAME = "Qwen3-8B"

app = FastAPI()

print("[INFO] Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True
)

print("[INFO] Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
model.eval()

print("[INFO] Qwen3 API server is ready.")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = SERVED_MODEL_NAME
    messages: List[Message]
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 512
    stream: bool = False


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": SERVED_MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local"
            }
        ]
    }


@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )
    except TypeError:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    do_sample = req.temperature > 0

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature if do_sample else None,
            top_p=req.top_p if do_sample else None,
            do_sample=do_sample,
            repetition_penalty=1.05,
            eos_token_id=tokenizer.eos_token_id
        )

    new_ids = output_ids[0][inputs["input_ids"].shape[-1]:]
    text = tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    return {
        "id": "chatcmpl-local-{}".format(int(time.time())),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": SERVED_MODEL_NAME,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": text
                },
                "finish_reason": "stop"
            }
        ]
    }