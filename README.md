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

General web search beyond Wikipedia remains future work. PDF and DOCX text extraction, voice input/output, and the in-app sign-in/logout experience are implemented in the Worker interface. Full Stanford OpenJarvis runtime integration still requires deployment of the separate Python service and its provider credentials. The GitHub workflow performs live health, UI, and private-route smoke checks.


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


## Version 19 — cross-origin request protection
- State-changing `/api/` requests reject a mismatched `Origin` header and browser `Sec-Fetch-Site: cross-site` requests with HTTP 403.
- The rejection response is private and non-cacheable.
- GitHub Actions verifies the live cross-origin login rejection, PWA assets, required Worker bindings, invalid-session rejection, and private response cache headers.
- Worker version 19 is deployed to 100% traffic with the existing AI, D1, and `JARVIS_PASSWORD` secret bindings preserved.
- Latest cross-origin validation run: https://github.com/harissaeed030/jarvis-personal-ai/actions/runs/44441286689

## Version 20 — premium mobile interface
- The self-contained Worker UI has been upgraded with a refined responsive layout, improved spacing and typography, premium dark visual styling, and mobile-focused composer controls.
- The deployment uses the existing Cloudflare Workers AI binding, D1 database, and `JARVIS_PASSWORD` secret; no credentials were added to the repository.
- GitHub Actions validation run #65 completed successfully for commit `f49b57d8e7cc89330cbd8aa5ab7a776503f8b522`.
- Cloudflare Worker version 20 is assigned 100% of production traffic. Its version metadata confirms the AI, D1, and password-secret bindings are present.
- The automated workflow and deployment metadata do not replace a real user-side browser sign-in and AI conversation test.

## Document attachments
- TXT and Markdown: up to 100 KB.
- PDF: up to 5 MB and 20 pages; selectable text is extracted in the browser. Scanned/image-only PDFs are not OCR-processed.
- DOCX: up to 2 MB; plain text is extracted in the browser. Embedded images and complex layout are not preserved.
- PDF.js and Mammoth are loaded from cdnjs only when a matching file is attached, so document extraction needs an internet connection. File contents are treated as untrusted reference text and are not executed.
- Extracted text is capped before sending to the AI to keep mobile memory and request sizes manageable.

## Version 21 — PDF and DOCX reading
- Production Worker v21 adds browser-side extraction for selectable-text PDFs (maximum 5 MB / 20 pages) and DOCX files (maximum 2 MB), alongside TXT/Markdown.
- PDF.js and Mammoth are loaded only when needed from cdnjs; document parsing therefore requires an internet connection. Scanned PDFs are not OCR-supported, and DOCX images/layout are not retained.
- Extracted text is capped at 28,000 characters before being sent to the AI. File content is handled as untrusted reference text.
- GitHub Actions now validates the embedded browser scripts as well as Worker/app syntax and live endpoint security checks.
- Cloudflare Worker version 21 is deployed to 100% traffic with the existing AI, D1, and password-secret bindings preserved.


## Phase 2 — optional OpenJarvis bridge and saved memory
- Added an authenticated D1-backed saved-memory API (`GET/POST/DELETE /api/memory`) with a 100-item cap and 2,000-character per-item limit. The latest 20 saved items are supplied as context to the assistant; conversation history remains separate.
- Added an optional secure OpenJarvis upstream bridge using the official OpenAI-compatible `/v1/chat/completions` API. The API key remains a Worker secret; upstream failures fall back to the existing Workers AI model.
- Cloudflare Worker version 25 is deployed to 100% production traffic with the existing AI, D1, and `JARVIS_PASSWORD` bindings preserved. The bridge remains dormant until `OPENJARVIS_API_URL`, `OPENJARVIS_API_KEY`, and `OPENJARVIS_MODEL` are configured in Cloudflare; the separate Python service is not yet hosted.
- Setup and architecture: [docs/OPENJARVIS-INTEGRATION.md](docs/OPENJARVIS-INTEGRATION.md).
- The visual Saved memory panel is deployed: signed-in users can add, list, delete, and clear saved memories. GitHub Actions checks the live panel markers, unauthenticated memory-route rejection, and cross-origin write blocking. Authenticated memory CRUD with the private user password and the full Stanford OpenJarvis runtime hosting/real upstream chat remain pending.

- Browser voice settings now let the user select English (Pakistan), Urdu, or English (US) for speech recognition; spoken replies use the selected locale, with Urdu-script detection as a fallback. Actual voice availability still depends on the Android browser and installed speech services.


## Phase 3 — owner-scoped memory and OpenJarvis runtime preparation
- Conversation history, recent context retrieval, and saved-memory CRUD are now scoped to an HMAC-derived owner identifier based on the existing password secret. Existing rows are preserved and assigned to the current owner by a one-time D1 migration.
- Memory now supports create, list, edit, individual delete, and clear. The UI includes an Edit action. This remains a single-owner password-login application; it is not a multi-user account system.
- Authenticated `GET /api/openjarvis/status` checks the configured upstream `/health` and `/v1/models` endpoints without exposing the API key.
- `Dockerfile` and `render.yaml` prepare an optional no-card Render evaluation deployment of the official Stanford OpenJarvis Python runtime. Render free services sleep and have ephemeral filesystems, so this is not always-on production hosting. The Python service is not considered live until the Render service URL and API credentials are configured and a real chat is verified.
- Phase 3 regression tests cover owner isolation, migration preservation, memory CRUD, and persistence semantics. They do not replace authenticated production API testing.


## Phase 3 production deployment
- Cloudflare Worker version **28** is deployed to 100% production traffic. The deployed Worker source is commit `1c776aa4d808eb915490515d2f622f4b68b1bd8b`.
- Preserved production bindings: Workers AI (`AI`), D1 (`DB`, existing database), and `JARVIS_PASSWORD`.
- Saved memories and conversations now use an owner scope; memory supports create/read/update/delete. The first authenticated use runs the D1 owner-scope migration.
- Android browser voice controls now show clearer microphone permission, speech recognition, and speech-output fallback errors. Actual microphone/audio behavior still requires testing on the user's physical Android phone.
- The optional official Stanford OpenJarvis Python sidecar builds successfully in GitHub Actions. The external Python host and Gemini API secret are not configured yet; Workers AI remains the live fallback.


## Phase 3 memory migration deployment
- Cloudflare Worker version **29** is deployed to 100% production traffic from commit `1eefb046a9a234091f0562a942cb4d8dc31bdc93`.
- The production Worker v29 currently has the legacy dashboard variable `OPENJARVIS_MODEL=gemini-2.5-flash-lite`. This branch aligns `wrangler.toml` with the pinned sidecar and Render Blueprint by setting `OPENJARVIS_MODEL=gemini-2.5-flash`; the production value changes only after a reviewed Worker deployment. The OpenJarvis bridge remains inactive until its HTTPS service URL and API key are configured.
- The first authenticated request creates a stable account-scope ID in D1 and performs the non-destructive, atomic legacy-memory copy. The production database is not migrated by unauthenticated health checks.
- The optional official OpenJarvis Python service remains unconfigured until its host URL and API key are configured in Cloudflare. Workers AI remains the active fallback.
