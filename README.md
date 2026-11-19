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

## Source-backed research

- Turn on the `Research: ON` control before sending a question to retrieve relevant Wikipedia article extracts.
- JARVIS receives those excerpts as reference context and returns article URLs alongside its answer. The source list is displayed below the answer.
- This is a limited Wikipedia-backed research feature, not general web search. It uses the public MediaWiki API and does not require a separate API key. It may not find recent news, niche websites, or information outside Wikipedia. Verify important claims against the linked source pages.

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

- `worker.js`: source of truth for the deployed self-contained UI and API; the HTML/CSS/browser JavaScript are currently embedded in this Worker file.
- `index.html`, `styles.css`, `app.js`: earlier standalone frontend scaffold files; they are not currently served by the Worker route.
- `wrangler.toml`: Worker and Workers AI binding configuration.
- `manifest.webmanifest`: installable web-app metadata.
- `.github/workflows/validate.yml`: JavaScript syntax checks.

## Planned next work

PDF/document uploads, general web search beyond Wikipedia, and full Stanford OpenJarvis backend integration remain future work. Voice input/output and the in-app sign-in/logout experience are implemented in the live Worker interface. The GitHub workflow now also performs a live health and UI smoke test; if the public endpoint is unreachable from the runner, that check will fail visibly.


## Version 12 update
- Research results now render as clickable source links.
- Source links are restricted in the UI to HTTPS URLs on `en.wikipedia.org`.
- Session authentication, D1 conversation memory, and Workers AI bindings are preserved in deployment.


## Version 13 security hardening
- Private session, chat, history, and logout responses send `Cache-Control: no-store, private`.
- GitHub Actions checks Worker and browser JavaScript syntax, live health/bindings, core UI markers, and private API cache headers.
- The automated runner's session context can be authenticated, so CI does not treat that environment as a reliable anonymous-login test; real sign-in/chat should also be checked in a fresh private browser session.


## Version 14 document attachments
- Chat accepts `.txt` and `.md` file attachments from the browser.
- Attachment limit: 100 KB per file; combined prompt limit: 40,000 characters.
- Document text is included as untrusted reference material, not executable instructions.
- PDF, DOCX, and other binary formats are not supported by this lightweight Worker upload path.

- CI live smoke tests validate that private API endpoints send `Cache-Control: no-store`; they do not claim a full authenticated browser login/chat test.


## Version 15 — session and deployment verification
- The browser waits for the server's session check before showing the signed-in state or requesting saved chat history.
- GitHub Actions verifies Worker and browser JavaScript syntax, live health and required bindings, core interface markers, and that invalid session cookies are rejected by the session, history, and chat APIs with HTTP 401.
- The same private API checks verify `Cache-Control: no-store` to prevent private responses from being cached.
- Latest verified workflow run: [Run #51](https://github.com/harissaeed030/jarvis-personal-ai/actions/runs/44440110678) — successful.
- Latest Cloudflare deployment: Worker version 15, deployed at 100% traffic. Required AI, D1, and password-secret bindings are attached.
- These automated checks do not submit a real password or prove a complete authenticated AI conversation in a browser. That final user-session test remains a separate check.

## Version 16 session security
- Session cookies now contain an HMAC-signed issuance timestamp and expire server-side after 7 days; replaying an expired cookie no longer authenticates.
- Session signatures use a versioned HMAC payload and are compared without an early-exit character comparison.
- Deployments preserve the existing `JARVIS_PASSWORD` secret, Workers AI binding, and D1 database binding.
- All existing browser sessions are invalidated by the session format change; sign in again with the already-configured password. Never send that password in chat.


## Version 17 — Android installable PWA
- The live Worker now serves a real web app manifest, a JARVIS SVG app icon, and a service worker instead of returning the home page for those asset paths.
- The service worker caches only the public app shell (home page, manifest, icon) for offline launch fallback. It explicitly bypasses all `/api/` requests so private chat, login, and history are never cached.
- The home page registers the service worker and exposes standalone install metadata. On Android Chrome, use the browser menu and choose **Install app** or **Add to Home screen** when offered.
- GitHub Actions now checks the live manifest, icon, service worker, install hooks, and API-cache bypass marker.
