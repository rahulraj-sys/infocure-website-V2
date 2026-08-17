import { Link, useLocation } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { ChevronRight } from "lucide-react";
import { SITE } from "@/data/site";

const BASE_LABELS = {
  services: "Services",
  products: "Products",
  solutions: "Solutions",
  industries: "Industries",
  insights: "Insights",
  "case-studies": "Case Studies",
  about: "About",
  contact: "Contact",
  privacy: "Privacy Policy",
  terms: "Terms of Use",
  disclaimer: "Disclaimer",
  resources: "Resources",
  "team-augmentation": "Team Augmentation",
};

const OVERRIDES = {
  "sap-consulting": "SAP Consulting",
  "oracle-consulting": "Oracle Consulting",
  "salesforce-consulting": "Salesforce Consulting",
  "build-cloud": "Build & Cloud",
  "digital-transformation": "Digital Transformation",
  hrms: "HRMS",
  crm: "CRM",
  dms: "Dealer Management (DMS)",
  oms: "Order Management (OMS)",
  ppc: "Production Planning (PPC)",
  erp: "Custom ERP",
  exim: "EXIM Trade Management",
  "e-invoicing": "e-Invoicing",
};

// Intermediate segments that resolve to a real index page (thus linkable + schema-safe).
const REAL_INDEX = new Set(["/industries", "/insights", "/case-studies"]);

// Never show breadcrumbs on these.
const HIDDEN_PREFIXES = ["/adminia"];

function labelFor(seg) {
  if (OVERRIDES[seg]) return OVERRIDES[seg];
  if (BASE_LABELS[seg]) return BASE_LABELS[seg];
  return seg
    .split("-")
    .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w))
    .join(" ");
}

export default function Breadcrumbs() {
  const { pathname } = useLocation();

  if (pathname === "/" || HIDDEN_PREFIXES.some((p) => pathname.startsWith(p))) return null;

  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return null;

  const crumbs = [{ name: "Home", href: "/", link: true }];
  let acc = "";
  segments.forEach((seg, i) => {
    acc += `/${seg}`;
    const isLast = i === segments.length - 1;
    crumbs.push({
      name: labelFor(seg),
      href: acc,
      // last crumb = current page (not a link); intermediates link only if a real index page exists
      link: !isLast && REAL_INDEX.has(acc),
    });
  });

  // BreadcrumbList schema — only include crumbs that resolve to a real URL (Home, real indexes, current page).
  const schemaCrumbs = crumbs.filter((c, i) => i === 0 || c.link || i === crumbs.length - 1);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: schemaCrumbs.map((c, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: c.name,
      item: `${SITE.domain}${c.href === "/" ? "" : c.href}`,
    })),
  };

  return (
    <nav
      aria-label="Breadcrumb"
      data-testid="breadcrumbs"
      className="pointer-events-none absolute inset-x-0 top-[84px] z-40"
    >
      <Helmet>
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      </Helmet>
      <div className="mx-auto max-w-[1440px] px-5 sm:px-8">
        <ol className="pointer-events-auto inline-flex max-w-full flex-wrap items-center gap-x-1.5 gap-y-1 rounded-full bg-black/75 px-3.5 py-1.5 text-[12px] font-medium tracking-[0.01em] ring-1 ring-white/15 backdrop-blur-md">
          {crumbs.map((c, i) => {
            const isLast = i === crumbs.length - 1;
            return (
              <li key={c.href} className="inline-flex items-center gap-x-1.5">
                {i > 0 && <ChevronRight className="h-3 w-3 shrink-0 text-white/45" aria-hidden="true" />}
                {isLast ? (
                  <span className="text-white" aria-current="page" data-testid="breadcrumb-current">
                    {c.name}
                  </span>
                ) : c.link ? (
                  <Link
                    to={c.href}
                    className="text-white/85 transition-colors duration-200 hover:text-white"
                    data-testid={`breadcrumb-link-${c.href.replace(/\//g, "-")}`}
                  >
                    {c.name}
                  </Link>
                ) : (
                  <span className="text-white/70">{c.name}</span>
                )}
              </li>
            );
          })}
        </ol>
      </div>
    </nav>
  );
}
