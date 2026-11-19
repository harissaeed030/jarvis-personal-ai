# OpenJarvis integration and secure deployment

## Architecture

The production browser app and its existing Cloudflare Worker remain the public entry point. When configured, the Worker forwards authenticated chat requests to the official OpenJarvis OpenAI-compatible API at `/v1/chat/completions`. The Worker adds its existing conversation context and saved JARVIS memories, keeps the OpenJarvis API key server-side, and falls back to Cloudflare Workers AI if the OpenJarvis service is unavailable.

This is an optional bridge, not a bundled or embedded copy of Stanford's Python framework. The full OpenJarvis runtime must be installed and operated as a separate Python service. The upstream project is maintained at https://github.com/open-jarvis/OpenJarvis and its documentation is at https://open-jarvis.github.io/OpenJarvis/.

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

The latest 20 saved items are added to the assistant's system context as user-provided data, not instructions. Conversation history remains separate. The memory API is currently an authenticated API surface; a dedicated visual memory/settings panel is still future UI work.

## Verification boundaries

GitHub Actions can validate Worker syntax, embedded browser scripts, and public production health/security/PWA checks. It cannot prove a private OpenJarvis deployment is reachable until the service URL and API key have been configured in Cloudflare, nor can it perform a real user login without the user's password. Do not report full OpenJarvis integration as active until a real authenticated chat returns from the OpenJarvis provider and its fallback path has been exercised.
