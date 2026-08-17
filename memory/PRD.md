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
- B10 Team Augmentation hero: DONE (2026-06). Re-treated user's TA.png into dark-navy Infocure theme (cyan glow, preserved hand proportions, left negative space) -> /media/ta-hero.jpg, wired in flagship.js (removed generic method-bg video). Verified visually.
- A4 numbers scrub (case studies + dashboard 87%): DONE (2026-06). Rewrote data/case-studies.js outcomes/titles/summaries to qualitative (no % / revenue / count claims); replaced decorative "87%" gauge with a non-numeric status dot ("OPTIMISED"). Scan confirms CLEAN.
- Upload cleanup on delete: DONE (2026-06). delete_insight now removes associated PDF/image from object storage (is_deleted + best-effort delete_object). Verified file 200 before delete -> 404 after.
- DT hero video (B9): DONE (2026-06). User confirmed the NeoSoft clip is licensed to them; swapped in the licensed Digital-Transformation-Web.mp4 as /media/dt-hero.mp4 (1280x720, 1.75MB — lighter than prior 3.5MB in-house), regenerated matching poster /media/dt-hero-poster.jpg via ffmpeg. Autoplay/muted/loop, dark gradient overlay, poster prevents layout shift. Verified rendering + served 200.

## 2026-06 — Final visual refinement round
- Mobile DT video: LazyVideo now serves lighter /media/dt-hero-mobile.mp4 on <=768px (matchMedia); desktop keeps dt-hero.mp4. `videoMobile` threaded via FlagshipPage.
- Global unsupported-numbers scrub (items 8/11): Home.jsx testimonial "INR 4,000 Cr revenue" -> removed; "Eleven years" -> "Over a decade"; "INR 200 Cr–5,000 Cr" positioning -> "Growing and mid-market enterprises across India, the GCC and international markets". No 100+/98%/N+ claims exist anywhere (already clean). 85% etc remain only on Team Augmentation.
- Sitemap: removed duplicate /services/team-augmentation entry (0 dup locs, 52 urls, no blog).
- SAP hero image bug: was SAP&ORACLE combo -> replaced (then superseded below).
- Products menu: "Custom ERM" -> "Custom ERP".
- FOUR service-page hero visuals (SAP/Oracle/Salesforce/Build&Cloud): generated 4 distinct dark-navy tech visuals -> /media/hero-sap.jpg, hero-oracle.jpg, hero-salesforce.jpg, hero-buildcloud.jpg. Removed the shared generic method-bg video from these 4; each uses new `vivid-right` Hero treatment (bright right-weighted visual + left dark scrim for headline). DT `vivid` treatment unchanged. Verified all 4 render distinct + readable.
- Hero.jsx: added `videoMobile`, `vivid-right` treatment (left-concentrated scrim), image-vivid support.

## Known remaining (reported, not changed)
- Breadcrumbs: BreadcrumbList schema builders exist in data, but visible breadcrumb trail may not be rendered on all inner pages (item 19) — needs go-ahead as it is additive UI.
- Case-study result metrics were rewritten qualitatively in a prior round; confirm if real approved numbers preferred.

## 2026-06 — Final hero visual update (user-supplied assets)
- SAP Consulting hero -> uploaded /media/hero-sap-v2.webp (charcoal + red, baked-in SAP branding). Static, no video.
- Build & Cloud hero -> uploaded /media/hero-buildcloud-v2.jpeg (dark digital infrastructure, red accents). Static, no video.
- Oracle & Salesforce heroes UNCHANGED (hero-oracle.jpg / hero-salesforce.jpg).
- Homepage + Digital Transformation videos preserved. Verified by testing_agent iteration_6.json (100% pass, no issues).
- Held (need explicit go-ahead; current spec was 'visual hero only'): visible breadcrumbs (item 19), About/Leadership/Careers spacing polish. Salesforce baked-in-text cleanup NOT done because the hero spec said keep Salesforce as-is.
