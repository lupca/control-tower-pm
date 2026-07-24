---
title: LLM Providers
project: marketing-video-agent
updated: 2026-07-24
---

# LLM Providers

## SiliconFlow API

- **Endpoint:** `https://api.siliconflow.com/v1/chat/completions`
- **Key:** set via env var `LLM_API_KEY` (see `.env` in target repo)

### Models available

| Model | ID |
|:---|:---|
| Qwen3-32B | `Qwen/Qwen3-32B` |
| GLM-5.1 | `zai-org/GLM-5.1` |

### Example request

```bash
curl --request POST \
  --url https://api.siliconflow.com/v1/chat/completions \
  --header 'Authorization: Bearer $LLM_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "Qwen/Qwen3-32B",
  "messages": [
    {"role": "user", "content": "Hello"}
  ]
}'
```
