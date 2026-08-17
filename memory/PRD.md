# PRD — Infocure Website V2 (Final Refinement)

## Original problem statement
Refinement + production cleanup + two hero visual swaps of the existing approved Infocure enterprise site (React JS + FastAPI + MongoDB, CMS at `/adminia`). NOT a redesign. Implement ONLY the listed items; everything else that works stays untouched.

## Stack (confirmed on import)
- Frontend: React 19 (JavaScript, CRA + CRACO), Tailwind, framer-motion, lenis, react-helmet-async, radix/shadcn UI.
- Backend: FastAPI + Motor (MongoDB). Object storage via Emergent objstore. Email via Emergent (Resend).
- Admin auth: JWT single-email (PRESERVED per guardrail — not swapped to Google).
- CMS: `/adminia`. Insights collection with types: article, case-study, resource.

## Decisions
- PDF content: Option C — wire upload/download only (no AI-authored PDFs). 6 static resource PDFs already exist in /public/resources.
- DT hero video: original in-house generated (`/media/dt-hero.mp4` already present, wired in flagship.js).
- Admin auth kept as existing JWT (guardrail: "preserve admin auth").

## Status (as of import, 2026-06)
Imported the real site from `infocure-Website-V2-main.zip` (previous boilerplate replaced). Installed `lenis`, `react-helmet-async`, `reportlab`, `pypdf`. Configured backend `.env` (ADMIN_EMAIL/PASSWORD, JWT_SECRET, EMERGENT_LLM_KEY). Services healthy.

### Workstream A — Content & Governance
- A1 About consistency (Company/Leadership/Careers): DONE (verified prior).
- A2 Insights taxonomy = Article/Case Study/Resource, Blog removed from UI+CMS: DONE.
- A3 Blog→Article terminology: DONE (only SEO redirect /insights/blog -> /insights remains).
- A4 Numbers governance: Homepage numeric claims already scrubbed (hero shows non-numeric proof strip). Case-study outcome metrics (38%,95%,400 vehicles, etc.) and a decorative dashboard SVG "87%" REMAIN — flagged for user allowlist decision (legitimate case-study content, out of scope to auto-delete).
- A5 Approved numbers (300+/500+/85%) only on Team Augmentation: DONE (flagship.js).
- A6 Resources page: 6 cards + working Download PDF: DONE.
- A7 Resource CMS fields (Title, Short Desc, Category, Featured Image, PDF Upload, SEO Title, Meta Desc, Slug, Draft/Published): DONE.
- A8 Case Studies/Articles CMS fields: DONE.

### Workstream B — Hero Visual Swaps
- B9 DT hero cinematic video: DONE (`/media/dt-hero.mp4` + poster wired).
- B10 Team Augmentation hero with user's TA.png (re-treated dark-navy): PENDING — awaiting user's TA.png upload. Currently uses `/img-freedom-of-devices.webp`.

### Workstream C — QA & Report
- Full QA run (testing agent, iteration_4): all acceptance flows PASS (taxonomy, DT video, TA stats, 6 resource PDFs, CMS publish/delete, contact, legacy routes). Backend pytest 16/17.
- Post-QA hardening fixes applied & verified:
  - Protected `GET /api/contact` behind admin_guard (was leaking PII publicly) — now 401 unauth / 200 auth.
  - Constrained Insight `type` to Literal[article|case-study|resource] and `status` to Literal[draft|published] — `type=blog` now 422 (protects A2 "no Blog").
  - Added a delete-confirm dialog in `/adminia` content list (accidental data-loss safeguard).
- Reported (not fixed, out of scope): orphaned uploaded-file cleanup on insight delete (non-breaking storage housekeeping).

## Backlog / Next
- P0: Receive TA.png -> re-treat to dark-navy Infocure theme -> swap TA hero (B10).
- P1: User allowlist decision on case-study metrics + dashboard SVG "87%" (A4).
- P2: Optional — optimize hero video weights for faster load / less layout shift.
