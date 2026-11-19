# JARVIS — Personal AI Assistant

A mobile-first personal AI web app, kept completely separate from NEXUS ISP Management.

## Live deployment

- App: https://jarvis-personal-ai.harissaeed030.workers.dev
- Health endpoint: https://jarvis-personal-ai.harissaeed030.workers.dev/api/health
- Cloudflare Worker: `jarvis-personal-ai`

## Current foundation
- Responsive dark interface for Android and desktop.
- Roman Urdu, Urdu, and English assistant behavior.
- Cloudflare Workers AI binding; no Gemini key or other external API key is required.
- Model: `@cf/zai-org/glm-4.7-flash`.
- Health endpoint reports whether the AI binding is available.

## Usage and limits
Workers AI currently includes 10,000 free Neurons per day on the Workers Free plan. The allowance resets daily at 00:00 UTC. Requests stop when the free daily allowance or another account limit is reached; use is not unlimited. The selected model is available on the Workers Free plan according to Cloudflare's current model availability guidance. Check official pricing and model availability before relying on it for continuous use.

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
