# JARVIS — Personal AI Assistant

A mobile-first personal AI web app, kept completely separate from NEXUS ISP Management.

## Live deployment

- App: https://jarvis-personal-ai.harissaeed030.workers.dev
- Health endpoint: https://jarvis-personal-ai.harissaeed030.workers.dev/api/health
- Cloudflare Worker: `jarvis-personal-ai`

## Features in this foundation
- Responsive dark interface for Android and desktop.
- Roman Urdu, Urdu, and English prompt handling.
- Gemini 2.5 Flash API integration in a Cloudflare Worker.
- Provider key is read only from the `GEMINI_API_KEY` Worker secret; never put it in browser code.
- Health endpoint reports whether the key is configured.

## Enable live AI replies
The Worker is deployed, but AI replies remain disabled until a Gemini API key is added.

1. Open Cloudflare Dashboard → Workers & Pages → `jarvis-personal-ai`.
2. Open Settings → Variables and Secrets.
3. Add a secret named `GEMINI_API_KEY` with your Google AI Studio API key.
4. Save/deploy the new version.
5. Open the health endpoint and confirm `aiConfigured: true`.

Never commit or share the API key in GitHub or chat. Provider free-tier availability and limits may change.

## Deploy from a development machine
This project uses Wrangler because it has `wrangler.toml`:
`npx wrangler deploy`

## Repository layout
- `index.html`, `styles.css`, `app.js`: modular frontend source.
- `worker.js`: currently deployed self-contained Worker UI and API entry point.
- `wrangler.toml`: Worker deployment configuration.
- `manifest.webmanifest`: installable web-app metadata.

## Planned next work
Conversation history with private per-user storage, sign-in, PDF/document uploads, voice input/output, web research, and stronger abuse protection. These are not implemented yet.
