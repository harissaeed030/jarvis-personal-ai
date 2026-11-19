# JARVIS — Personal AI Assistant

A mobile-first personal AI web app, built as a separate project from NEXUS ISP Management.

## Current foundation
- Responsive chat interface for Android and desktop browsers.
- Roman Urdu, Urdu, and English assistant behavior.
- Cloudflare Worker API with Gemini provider integration.
- API key is read only from the `GEMINI_API_KEY` Worker secret; never put it in browser code.
- Health endpoint: `/api/health`.

## Cloudflare deployment
1. Install Wrangler and authenticate: `npx wrangler login`.
2. Add the provider key as a secret: `npx wrangler secret put GEMINI_API_KEY`.
3. Deploy: `npx wrangler deploy`. Cloudflare will provide a Worker URL.
4. Open that URL in your mobile browser.

## Important
- A Gemini API key and an eligible provider account are required for live AI responses. Free-tier availability and limits are controlled by Google and may change.
- Do not commit API keys, passwords, or tokens.
- This repository is independent. Do not merge its files into NEXUS.

## Up next
Conversation persistence, sign-in, document upload, voice input/output, and optional web research require additional implementation and security review.
