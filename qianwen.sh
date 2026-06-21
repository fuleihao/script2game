#!/usr/bin/env bash

export TMPDIR=/root/siton-data-guanchunxiangData/tmp
export HF_HOME=/root/siton-data-guanchunxiangData/.cache/huggingface
export TRANSFORMERS_CACHE=/root/siton-data-guanchunxiangData/.cache/huggingface


CUDA_VISIBLE_DEVICES=1 uvicorn qwen3_api_server:app \
  --host 0.0.0.0 \
  --port 8001