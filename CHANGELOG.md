# Changelog

All notable changes to `oellm_server` will be documented in this file.

## [1.0.0] - 2026-03-20

### Initialization
- Introduced `openai_server.py` as an OpenAI-compatible inference server that supports:
  - `GET /health`
  - `GET /v1/models`
  - `POST /v1/chat/completions` with `stream=true` (SSE)
- Documented startup prerequisites and runtime parameters (including `LIBXLM_PATH`, `--model-type`, `--hbm-path`, `--tokenizer-dir`, optional `--template-path`, and `--host/--port/model-id`).
- Added model-specific run examples (e.g., DeepSeek, Qwen2.5, InternLM2) and client call examples for both non-streaming and streaming requests.
- Captured current limitations: a global inference lock (one request at a time), simple message-to-prompt concatenation (template handling via `chat_template` when provided), and text-only `chat/completions` (multi-modal support noted for future extension).

