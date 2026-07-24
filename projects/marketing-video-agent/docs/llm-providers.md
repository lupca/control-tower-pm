---
title: LLM Providers
project: marketing-video-agent
updated: 2026-07-24
---

# LLM Providers

## SiliconFlow API

- **Endpoint:** `https://api.siliconflow.com/v1/chat/completions`
- **Key:** `sk-mbtbbvlwesioonlentlzqdhcmlbvihtpdehizqppqhzxdsrp`

### Models available

| Model | ID |
|:---|:---|
| Qwen3-32B | `Qwen/Qwen3-32B` |
| GLM-5.1 | `zai-org/GLM-5.1` |

### Example request

```bash
curl --request POST \
  --url https://api.siliconflow.com/v1/chat/completions \
  --header 'Authorization: Bearer sk-mbtbbvlwesioonlentlzqdhcmlbvihtpdehizqppqhzxdsrp' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "Qwen/Qwen3-32B",
  "messages": [
    {"role": "user", "content": "Hello"}
  ]
}'
```
