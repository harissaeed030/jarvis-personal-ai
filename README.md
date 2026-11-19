# JARVIS — Personal AI Assistant

A mobile-first personal AI web app, kept completely separate from NEXUS ISP Management.

> **OpenJarvis integration status:** This repository currently contains a lightweight browser assistant using Cloudflare Workers AI. It is not yet running the full Stanford OpenJarvis framework. Stanford OpenJarvis is a Python-based local-first framework (Python 3.11+, `uv`, and Ollama/model runtime); Cloudflare Workers cannot directly host that Python/Ollama runtime. A separate Linux host or supported container runtime is required for full framework integration.

## Live deployment

- App: https://jarvis-personal-ai.harissaeed030.workers.dev
- Health endpoint: https://jarvis-personal-ai.harissaeed030.workers.dev/api/health
- Cloudflare Worker: `jarvis-personal-ai`

## Current foundation

- Responsive dark interface for Android and desktop.
- Roman Urdu, Urdu, and English assistant behavior.
- Native Cloudflare Workers AI binding; no Gemini key is needed.
- Model: `@cf/meta/llama-4-scout-17b-16e-instruct`.
- Password-protected chat API is implemented with an HttpOnly, Secure, SameSite session cookie.
- The password is designed to live only in a Cloudflare Worker secret named `JARVIS_PASSWORD`, never in GitHub or browser code.
- **One-time setup still required:** add `JARVIS_PASSWORD` under Cloudflare Dashboard → Workers & Pages → `jarvis-personal-ai` → Settings → Variables and Secrets → Add → Secret. Use a strong password you choose, save, and redeploy if the dashboard requests it. Until this secret exists, the API intentionally rejects chat/login requests.
- Health endpoint reports whether AI and authentication secrets are configured.

## Usage and limits

Workers AI usage is subject to the account's current free allocation, model pricing, and plan limits. It is not unlimited. Check Cloudflare's official Workers AI pricing and model pages before relying on continuous use.

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

Persistent private conversation history, PDF/document uploads, voice input/output, web research, and full Stanford OpenJarvis backend integration. These are not implemented yet.
