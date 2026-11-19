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
- **Authentication secret configured:** Cloudflare currently has the `JARVIS_PASSWORD` secret attached to the Worker. Never put its value in this repository, browser code, or chat.
- Authenticated chat history is stored in the D1 `conversations` table; `/api/history` reads it and `DELETE /api/history` clears it.
- Login attempts are rate-limited per hashed client IP using D1: after 10 attempts in a 15-minute window, sign-in is temporarily blocked. Records older than 24 hours are cleaned up during login checks.
- Health endpoint reports whether AI, database, and authentication are configured. The public health URL could not be independently fetched by the available web checker during the latest review, so perform a browser check before treating end-to-end runtime as verified.

## Voice controls

- The live Worker interface includes a microphone button using the browser SpeechRecognition API where supported. Dictation fills the message box; press Send to submit it.
- The speaker button toggles browser speech synthesis for assistant replies.
- Voice recognition and speech voices depend on Android browser support, installed language packs, and microphone permission. They are optional browser features, not server-side audio processing.
- Voice recognition currently requests `en-PK`; Urdu speech recognition availability varies by browser.

## Usage and limits

Workers AI usage is subject to the account's current free allocation, model pricing, and plan limits. It is not unlimited. Check Cloudflare's official Workers AI pricing and model pages before relying on continuous use.

## Deploy

This project uses Wrangler:
`npx wrangler deploy` (run from this repository after authenticating Wrangler). Keep the existing `JARVIS_PASSWORD` Worker secret configured; never replace it with a blank value.

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

PDF/document uploads, web research, and full Stanford OpenJarvis backend integration remain future work. Voice input/output and the in-app sign-in/logout experience are implemented in the live Worker interface. The GitHub workflow now also performs a live health and UI smoke test; if the public endpoint is unreachable from the runner, that check will fail visibly.
