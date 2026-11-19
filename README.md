# JARVIS — Personal AI Assistant

A mobile-first personal AI web app, kept completely separate from NEXUS ISP Management.

> **OpenJarvis integration status:** This repository currently contains a lightweight browser assistant using Cloudflare Workers AI. It is not yet running the full Stanford OpenJarvis framework. Stanford OpenJarvis is a Python-based local-first framework (Python 3.11+, `uv`, and Ollama/model runtime); Cloudflare Workers cannot directly host that Python/Ollama runtime. A separate Linux host or supported container runtime is required for full framework integration. The current web assistant is a working lightweight alternative while that integration is evaluated.

## Live deployment

- App: https://jarvis-personal-ai.harissaeed030.workers.dev
- Health endpoint: https://jarvis-personal-ai.harissaeed030.workers.dev/api/health
- Cloudflare Worker: `jarvis-personal-ai`

## Current foundation
- Responsive dark interface for Android and desktop.
- Roman Urdu, Urdu, and English assistant behavior.
- Native Cloudflare Workers AI binding; no Gemini key or external provider API key is required.
- Model: `@cf/meta/llama-4-scout-17b-16e-instruct`.
- The model was successfully tested through the connected Cloudflare account.
- Health endpoint reports whether the AI binding is available.

## Usage and limits
Cloudflare Workers AI currently includes 10,000 free Neurons per day on the Workers Free plan. The allowance resets daily at 00:00 UTC. When the daily allowance or another account limit is reached, further inference requests fail until capacity resets; usage is not unlimited. Model availability and pricing can change. Check Cloudflare's official Workers AI pricing and model pages before relying on continuous use.

## Deploy
This project uses Wrangler:
`npx wrangler deploy`

The AI binding is configured in `wrangler.toml`:
```toml
[ai]
binding = "AI"
```

## Repository layout
- `index.html`, `styles.css`, `app.js`: modular frontend source.
- `worker.js`: deployed self-contained Worker UI and API.
- `wrangler.toml`: Worker and Workers AI binding configuration.
- `manifest.webmanifest`: installable web-app metadata.
- `.github/workflows/validate.yml`: JavaScript syntax checks.

## Planned next work
Conversation history with private per-user storage, sign-in, PDF/document uploads, voice input/output, web research, and stronger abuse protection. These are not implemented yet.
