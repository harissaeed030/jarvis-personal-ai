# OpenJarvis integration and secure deployment

## Architecture

The production browser app and its existing Cloudflare Worker remain the public entry point. When configured, the Worker forwards authenticated chat requests to the official OpenJarvis OpenAI-compatible API at `/v1/chat/completions`. The Worker adds its existing conversation context and saved JARVIS memories, keeps the OpenJarvis API key server-side, and falls back to Cloudflare Workers AI if the OpenJarvis service is unavailable.

This is an optional bridge, not a bundled or embedded copy of Stanford's Python framework. The full OpenJarvis runtime must be installed and operated as a separate Python service. The upstream project is maintained at https://github.com/open-jarvis/OpenJarvis and its documentation is at https://open-jarvis.github.io/OpenJarvis/.

## Card-free evaluation deployment (separate Python service)

This repository now includes an optional Dockerfile and Render Blueprint for the official Stanford runtime. The Docker build fetches the official upstream `open-jarvis/OpenJarvis` source at pinned commit `c3ed63f1d2a2c0c1f7dabbc69050e1968a11dc10`; it does not fork, patch, or write to that upstream repository. Pinning makes the container build reproducible.

- Blueprint: https://dashboard.render.com/blueprint/new?repo=https://github.com/harissaeed030/jarvis-personal-ai
- Select the **Free** web-service plan. Render's official documentation says free web services need no payment for the initial deploy, but they sleep after 15 minutes idle, take about a minute to wake, may restart, and have ephemeral filesystems. Free services cannot attach persistent disks. This is an evaluation/demo host, not permanent always-on production hosting.
- The Blueprint generates `OPENJARVIS_API_KEY` automatically. Add `GEMINI_API_KEY` as a secret from Google AI Studio; do not commit it. The container selects the official OpenJarvis cloud engine and `gemini-2.5-flash`, which Google's current pricing page lists with a free tier. Do not add a payment method or enable paid billing; quotas and model availability can change.
- Google states free-tier Gemini API content may be used to improve its products. Do not send confidential ISP/customer data through this free-tier provider.
- OpenJarvis's own local SQLite state is ephemeral on this host. JARVIS conversation history and owner-scoped saved memories remain in Cloudflare D1 and are not stored on Render.

After Render reports a successful deploy, copy its HTTPS service URL and generated `OPENJARVIS_API_KEY` into Cloudflare Worker settings as `OPENJARVIS_API_URL` and secret `OPENJARVIS_API_KEY`. Set `OPENJARVIS_MODEL=gemini-2.5-flash` (this model ID is present in the pinned OpenJarvis cloud-engine catalog). Then sign in to JARVIS and call the authenticated `GET /api/openjarvis/status` endpoint (or use the app's API) to verify `/health` and `/v1/models`. The production Worker still falls back to Workers AI if this sidecar sleeps or fails.

**Deployment boundary:** I can prepare and test the repository configuration, but cannot create a Render service or mint a Google AI Studio key from the connected GitHub/Cloudflare access. Those actions require the user's Render and Google accounts. Until the service URL and key exist, actual OpenJarvis chat is not live.

## Runtime requirements

The official installation guide currently lists Python 3.10–3.13, uv, Git, Rust (for the Python extension), Node.js 18+ for the browser UI, and at least one reachable inference engine. The built-in server requires the `server` extra. SQLite/FTS5 memory is available by default; optional vector memory backends add extra dependencies.

A low-memory Android handset is not a suitable always-on host for the complete framework and model runtime. Keep the Android phone as the PWA client and run OpenJarvis on a separate Linux host/container with persistent storage and a reachable inference engine. A free hosting tier is acceptable only if it supports the required Python/Rust build, persistent disk, outbound inference traffic, and an always-available service; do not assume a sleeping or ephemeral free tier meets those requirements.

## Start the official service

Follow the upstream installation guide and configure a working inference engine and an agent if tool execution is desired. The server command is:

```bash
uv sync --extra server
uv run jarvis serve --host 0.0.0.0 --port 8000 --agent orchestrator
```

Set `OPENJARVIS_API_KEY` in the service environment before exposing the server publicly. Configure the service's firewall/reverse proxy to accept traffic only from trusted callers where possible, use HTTPS, and do not expose an unauthenticated server to the public internet. Confirm the service's `/health` and `/v1/models` endpoints before connecting JARVIS.

## Connect the Cloudflare Worker

Set these as Cloudflare Worker secrets/variables (never in GitHub source or browser JavaScript):

- `OPENJARVIS_API_URL`: HTTPS origin/base URL of the OpenJarvis service, for example `https://jarvis-api.example.com`.
- `OPENJARVIS_API_KEY`: the same API key configured in the OpenJarvis server.
- `OPENJARVIS_MODEL`: a model ID returned by the OpenJarvis `/v1/models` endpoint.

The Worker calls `POST /v1/chat/completions` using bearer authentication. If this upstream request fails, the existing Workers AI binding is used as a fallback. The current chat session, D1 history, and browser interface are retained.

## Persistent JARVIS memory API

All endpoints below require the existing JARVIS session cookie and D1 binding:

- `GET /api/memory`: list up to 100 saved memory items.
- `POST /api/memory`: JSON body `{"content":"..." }`; saves one item (maximum 2,000 characters).
- `DELETE /api/memory?id=<id>`: delete one item.
- `DELETE /api/memory`: clear saved memories.

The latest 20 saved items are added to the assistant's system context as user-provided data, not instructions. Conversation history remains separate. The signed-in browser UI includes a Saved memory panel to add, list, delete individual items, or clear all memories. The panel uses the authenticated API and remains hidden while signed out.

## Verification boundaries

GitHub Actions can validate Worker syntax, embedded browser scripts, and public production health/security/PWA checks. It cannot prove a private OpenJarvis deployment is reachable until the service URL and API key have been configured in Cloudflare, nor can it perform a real user login without the user's password. Do not report full OpenJarvis integration as active until a real authenticated chat returns from the OpenJarvis provider and its fallback path has been exercised.


## JARVIS persistent memory and account isolation

The Worker stores conversation history and saved memories in the existing Cloudflare D1 database. On the first authenticated request, a migration creates a stable random owner ID in a singleton D1 account-scope row, assigns it to existing conversations, and copies legacy memories into `user_memories_scoped`. The owner ID is independent of the login password, so rotating `JARVIS_PASSWORD` does not orphan saved data.

The migration is non-destructive: it retains the original `user_memories` source table, copies with `INSERT OR IGNORE`, and records a migration marker. Concurrent first requests can safely repeat the copy. All active memory create/read/update/delete and assistant-context queries use the scoped table.

This is a single-owner password-login application, not a multi-user registration system. The account-scope row isolates this JARVIS account's records; multiple people sharing the same password are the same account. D1 remains the persistent source of truth even if the optional OpenJarvis sidecar restarts or sleeps.
