# Clarity · Research Integrity Review Assistant

A student pre-submission review workspace: corpus-bounded source overlap, heuristic revision checks, and optional LLM-assisted research feedback.

**Local portfolio release v1.0. Not a plagiarism detector, AI-authorship detector, or institutional assessment engine.**

## Run on a Mac

Extract the project, open Terminal, type `cd ` with a trailing space, drag the extracted folder into Terminal, and press Return. Then run one line at a time:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8002
```

Open **http://127.0.0.1:8002**. Keep Terminal open. Ctrl+C stops it. Ports 8000 and 8001 remain available for the earlier portfolio projects.

A convenience script is also included: `bash start-mac.command`. It creates the environment, installs dependencies and starts the server. Python 3.11+ is required.

Docker alternative: `docker compose up --build`. Docker image build was not verified in the creation environment.

## Try it without an API key

1. Select **Load synthetic example**.
2. Inspect the paper and supplied source.
3. Select **Run local review**.
4. Review matched passages and writing/citation flags.
5. Download the report JSON and Markdown revision checklist, or Print → Save as PDF.
6. Edit the paper and rerun. Changing inputs invalidates the prior report.

Upload TXT, MD, PDF or DOCX; inspect extracted text for missing content. Files are processed in server memory and are not saved by the app. Scanned PDFs require external OCR. Individual uploads are limited to 5 MB and extracted text to 60,000 characters. Review one chapter at a time. Up to eight sources and 150,000 combined characters are supported.

## Optional actual LLM integration

An OpenAI Responses API adapter is implemented. There is no simulated LLM output substituted for a real model. Select a model available to your API account; no model is assumed or bundled.

Set **OPENAI_API_KEY** and **OPENAI_MODEL** in the server environment before starting. The `.env.example` documents the variables; this application does not automatically load a `.env` file. Keep keys out of GitHub. Your ChatGPT conversation does not configure credentials for this standalone application.

The UI displays configuration status and requires explicit permission/consent before a request. The entire supplied paper, sources and research context are sent to OpenAI. API charges may apply. Do not send restricted content without authorization. `store=false` is requested; this is not a guarantee of zero provider retention. Consult applicable provider and university requirements.

Model feedback is schema-validated. A finding is accepted only when its quoted passage appears exactly in the paper. Accepted suggestions remain unverified: exact quotation does not establish correct reasoning or citation support. Invalid provider responses fail visibly; local results remain available.

Integration reference: https://developers.openai.com/api/docs/guides/text

## What the percentage means

Text is normalized into word tokens. Eligible paper tokens participating in an exact eight-word sequence found in supplied sources form a union. Percentage = matched eligible tokens / total eligible paper tokens × 100. Overlapping sequences and duplicate sources do not double-count the numerator.

Recognized double-quoted spans and trailing References/Bibliography/Works Cited sections can be excluded. Patterns are intentionally simple and are not comprehensive citation parsing. No supplied corpus produces N/A, not a claim of 0% plagiarism. Exact matching misses paraphrases, translations and sources outside the corpus. General terminology may legitimately overlap.

Matched passages include paper offsets and source names. Source character offsets identify a witness eight-word sequence; merged paper matches may extend beyond that witness. Paper and source hashes document the review inputs.

## Scope boundaries

Local flags identify long paragraphs, absolute claims and certain research claims without recognized citation patterns. These are transparent heuristics and may be wrong. Bibliographic existence and cited-claim support are **not independently verified** in this release. The optional LLM can suggest questions using supplied excerpts, but it does not browse or certify references.

No originality grade, AI-written percentage, misconduct determination or institutional approval is produced. The AI disclosure draft must be edited to describe actual assistance and verification. Student policy requirements remain authoritative.

## Validation

```bash
python3 -m pytest -q
node --check frontend/app.js
```

Thirteen tests cover overlap unions, exclusions, no-corpus semantics, flags, offsets, file extraction, limits, consent, configuration, response validation and safe provider failures. DOM smoke checks exercised a sample review, rendered findings, stale-report invalidation and HTML escaping. No live API call or full visual browser/PDF review was performed.

For DOM checks, start the server on port 8002, then `npm install` and `npm run test:ui` (Node 22+).

See [review methodology](docs/methodology.md) and [security and limitations](docs/security.md). MIT licensed; independent portfolio project with synthetic demonstration text.
