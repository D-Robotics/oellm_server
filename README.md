# OpenAI Protocol Compatible Inference Server (oellm/xlm)

This directory adds `openai_server.py`. On startup, it calls `xlm_init` to initialize the model, and provides OpenAI-compatible endpoints:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions` (supports `stream=true` via SSE)

# Prerequisites

- D-Robotics LLM S100 Development Kit
```shell
wget https://d-robotics-aitoolchain.oss-cn-beijing.aliyuncs.com/llm_s100/1.0.0/D-Robotics_LLM_S100_1.0.0_SDK.tar.gz
```

- D-Robotics LLM S100 User Manual
```shell
wget https://d-robotics-aitoolchain.oss-cn-beijing.aliyuncs.com/llm_s100/1.0.0/D-Robotics_LLM_S100_1.0.0_Doc.zip
```

- Run LLM models on RDK S100 / RDK S100P (refer to the user manual)

For more usage, see [D-Robotics LLM Toolchain](https://developer.d-robotics.cc/rdk_doc/rdk_s/Advanced_development/toolchain_development/LLM_Toolchain)

- Download this repository

```shell
cd D-Robotics_LLM_S100_1.0.0_SDK/oellm_runtime/example/oellm_run
git clone https://github.com/D-Robotics/oellm_server.git
```

# Server Startup

Recommended to run in the **on-board Linux** environment (you must be able to load `oellm_runtime/lib/libxlm.so` and its dependencies).

Example (pure text models such as Qwen2.5 / InternLM2 / DeepSeek):

```shell
# export LIBXLM_PATH=/path/to/oellm_runtime/lib/libxlm.so  # Optional; if not set, the script infers it automatically
export LD_LIBRARY_PATH=/path/to/oellm_runtime/lib:$LD_LIBRARY_PATH
lib=/home/root/llm/D-Robotics_LLM_{version}/oellm_runtime/lib 
export LD_LIBRARY_PATH=${lib}:${LD_LIBRARY_PATH}

python3 openai_server.py \
  --model-type 7 \
  --hbm-path /path/to/model.hbm \
  --tokenizer-dir /path/to/tokenizer_dir \
  --template-path /path/to/chat_template.txt \
  --bpu-core -1 \
  --host 0.0.0.0 \
  --port 8000 \
  --model-id oellm-local
```

Currently, only 1 environment variable is kept:

- `LIBXLM_PATH`: path to the `libxlm.so` file. You can also pass a directory (it will auto-append `libxlm.so`), or not set it at all (default points to `oellm_runtime/lib/libxlm.so`).

All other parameters are passed via command line arguments:

- `--model-type`: required, supports `0/1/4/7`
- `--hbm-path`: required for text models (`1/4/7`)
- `--tokenizer-dir`: required for text models (`1/4/7`)
- `--config-path`: required when `model-type=0` (INTERNVL)
- `--template-path`: optional
- `--bpu-core`: `-1/0/1/2/3`, default `-1`
- `--host`: default `0.0.0.0`
- `--port`: default `8000`
- `--model-id`: default `oellm-local`

### Deepseek

```shell
# Set hardware registers to switch the device to performance mode
sh set_performance_mode.sh

# Set environment variables
lib=/home/root/llm/D-Robotics_LLM_S100_1.0.0_SDK/oellm_runtime/lib 
export LD_LIBRARY_PATH=${lib}:${LD_LIBRARY_PATH}

python3 oellm_server/openai_server.py \
  --model-type 1 \
  --hbm-path ../../model/DeepSeek_R1_Distill_Qwen_1.5B_4096.hbm \
  --tokenizer-dir ../../config/DeepSeek_R1_Distill_Qwen_1.5B_config/ \
  --template-path ../../config/DeepSeek_R1_Distill_Qwen_1.5B_config/DeepSeek_R1_Distill_Qwen_1.5B.jinja \
  --bpu-core -1 \
  --host 0.0.0.0 \
  --port 8000 \
  --model-id oellm-local
```

### Qwen2.5

```shell
# Set hardware registers to switch the device to performance mode
sh set_performance_mode.sh

# Set environment variables
lib=/home/root/llm/D-Robotics_LLM_S100_1.0.0_SDK/oellm_runtime/lib 
export LD_LIBRARY_PATH=${lib}:${LD_LIBRARY_PATH}

python3 oellm_server/openai_server.py \
  --model-type 7 \
  --hbm-path ../../model/Qwen2.5_1.5B_Instruct_1024.hbm \
  --tokenizer-dir ../../config/Qwen2.5_1.5B_Instruct_config/ \
  --template-path ../../config/Qwen2.5_1.5B_Instruct_config/Qwen2.5_1.5B_Instruct.jinja \
  --bpu-core -1 \
  --host 0.0.0.0 \
  --port 8000 \
  --model-id oellm-local
```

### InternLM2

```shell
# Set hardware registers to switch the device to performance mode
sh set_performance_mode.sh

# Set environment variables
lib=/home/root/llm/D-Robotics_LLM_S100_1.0.0_SDK/oellm_runtime/lib 
export LD_LIBRARY_PATH=${lib}:${LD_LIBRARY_PATH}

python3 oellm_server/openai_server.py \
  --model-type 4 \
  --hbm-path ../../model/InternLM2_1.8B_1024.hbm \
  --tokenizer-dir ../../config/InternLM2_1.8B_config/ \
  --bpu-core -1 \
  --host 0.0.0.0 \
  --port 8000 \
  --model-id oellm-local
```

# Client Calls

### Non-streaming

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "oellm-local",
    "messages": [
      {"role":"system","content":"You are a helpful assistant"},
      {"role":"user","content":"Introduce yourself in one sentence"}
    ]
  }'
```

![nostream](docs/chat_without_stream.gif)

### Streaming (SSE)

```bash
curl -N http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "oellm-local",
    "stream": true,
    "messages": [
      {"role":"user","content":"Introduce yourself in one sentence"}
    ]
  }'
```

![stream](docs/chat_with_stream.gif)

# Notes and Limitations

- To ensure safety and stability, the current implementation adds a global lock for inference, meaning **only one inference request is processed at a time** (to avoid concurrency issues with underlying handles). If you need concurrency, it can be extended to a "multi-process / multi-handle pool".
- `messages` are concatenated into a text prompt (no strict model-template rendering). If you provide `TEMPLATE_PATH`, it will be passed to the underlying `chat_template` for processing.
- Currently, only text chat for `chat/completions` is implemented. To support multi-modal (INTERNVL), you need to send images in the request and go through `XLM_INPUT_MULTI_MODAL`; you can extend this file accordingly.