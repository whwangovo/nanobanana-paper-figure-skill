# OpenAI Image Generation API Reference

## Endpoint

```http
POST {base_url}/v1/images/generations
Authorization: Bearer {api_key}
Content-Type: application/json
```

Default base URL: `https://api.openai.com`

## Generation Request

```json
{
  "model": "gpt-image-1.5",
  "prompt": "Create a publication-quality architecture diagram...",
  "n": 1,
  "size": "1024x1024",
  "quality": "high",
  "output_format": "png",
  "background": "opaque"
}
```

### Parameters

| Parameter | Required | Values | Default |
|---|---|---|---|
| `model` | yes | `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini` | — |
| `prompt` | yes | up to 32000 chars | — |
| `n` | no | 1 | 1 |
| `size` | no | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | `auto` |
| `quality` | no | `low`, `medium`, `high`, `auto` | `auto` |
| `output_format` | no | `png`, `jpeg`, `webp` | `png` |
| `output_compression` | no | 0–100 (jpeg/webp only) | — |
| `background` | no | `transparent`, `opaque` | `opaque` |
| `moderation` | no | `auto`, `low` | `auto` |

## Generation Response

```json
{
  "data": [
    {
      "b64_json": "<base64-encoded image bytes>",
      "revised_prompt": "..."
    }
  ]
}
```

## Edit Request (future)

```http
POST {base_url}/v1/images/edits
Content-Type: multipart/form-data
Authorization: Bearer {api_key}
```

Multipart fields: `model`, `prompt`, `image` (file), `size`, `quality`.

Not yet implemented in this skill's CLI. Use `--backend gemini` for editing workflows.

## Differences from Gemini

| Aspect | Gemini | OpenAI |
|---|---|---|
| Endpoint | `generateContent` (unified) | `/images/generations` + `/images/edits` (separate) |
| Auth | `X-goog-api-key` header | `Authorization: Bearer` header |
| Size | `imageConfig.imageSize` + `aspectRatio` | `size` (WxH string) |
| Response | `candidates[0].content.parts` (text + image) | `data[0].b64_json` (image only) |
| Text output | Yes (interleaved with images) | Only `revised_prompt` |
| Edit input | Same endpoint, inline base64 | Separate endpoint, multipart form |

## Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | API key (required) | — |
| `OPENAI_API_KEY_FILE` | Read key from file | — |
| `OPENAI_IMAGE_MODEL` | Model name | `gpt-image-1.5` |
| `OPENAI_BASE_URL` | Custom endpoint | `https://api.openai.com` |
