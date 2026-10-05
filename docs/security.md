# Security and privacy

This is a localhost single-user demo with no authentication. Do not expose it publicly. Text is handled in memory; no database or file history is created. Reports are stored only when users download them. Browser memory and server process memory are not secure deletion guarantees.

Only the explicit LLM endpoint performs outbound model requests, to a fixed HTTPS OpenAI endpoint. API credentials stay in environment variables on the server. Error responses do not return keys or raw provider errors. The config endpoint exposes model/configured status, never credentials.

Uploads have byte, text, page and DOCX XML-size limits. Extraction is not sandboxed; production service deployment requires hardened file parsing, authentication, rate limits and isolation. HTML rendering escapes supplied and model text. No source URLs are fetched, preventing document links from becoming automatic outbound requests.

Consent is a per-request UI/API requirement, not a legal authorization determination. Program policy and data permissions must be verified by the student. The provider payload requests store=false; provider processing/retention obligations still apply.

Production roadmap: identity and per-user isolation, institution-approved storage/retention controls, document provenance, explicit provider policy configuration, monitored model quality, native accessible exports and independently verified citations.
