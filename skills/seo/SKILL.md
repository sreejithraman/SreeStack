---
name: seo
description: Diagnose and improve website SEO. Use for crawling or indexing problems, search appearance, search-focused page content, structured data, or verifying deployed SEO fixes.
---

# SEO

Own organic search discoverability for public websites. For audits or plans,
return evidence and prioritized changes. For authorized implementation, make
and verify the requested changes. Keep deployment, account changes, and search
submissions within the user's authorized scope.

Use [ui-design](../ui-design/SKILL.md) for visual and accessibility work,
[react-best-practices](../react-best-practices/SKILL.md) for measured React/Next
performance, and [app-store-connect](../app-store-connect/SKILL.md) for App Store
optimization. Broad marketing, paid ads, backlink outreach, and mass content
generation are separate work.

## Scope the request

Match the investigation to the job. A local metadata change needs its owning
template and relevant regression checks; a site audit needs representative URL
families and states. For a new site, establish the intended discovery and
indexing behavior without inventing an existing failure.

Identify the production or intended canonical origin, affected pages, audience,
search engine, and requested outcome. Inspect the framework/CMS, hosting
configuration, and available Search Console or analytics evidence. Before
changing indexing controls, distinguish pages intended for search from staging,
private, duplicate, and other intentionally excluded URLs.

For an existing-site diagnosis, sample affected templates and relevant working,
failing, redirect, duplicate, or excluded states where available. Record URLs,
observation time, response evidence, and coverage. A sample supports conclusions
about the observed scope, not a whole-site pass.

Finish with the intended search behavior, affected templates, available access,
and evidence gaps identified. Continue repository and public-response checks
when account access is unavailable.

## Diagnose

For a reported problem, locate the failing stage: discovery, crawling,
rendering, indexing, search appearance, or traffic/conversion. For traffic
changes, compare the same URLs, queries, countries, devices, and date windows
where data permits. Distinguish indexing failures from changes in demand,
rankings, or click-through.

Consult official search-engine and framework documentation relevant to the
selected checks and the project's versions. Open only the sections needed to
resolve uncertainty or verify current behavior. Google-specific guidance does
not establish another engine's behavior. Choose the checks that address the
requested outcome:

- **Discovery and indexing.** Check internal links, sitemaps, actual status
  codes, robots.txt, hosting/CDN access, robots meta tags, and `X-Robots-Tag`.
  Preserve intentional exclusions. Google must crawl a page to see `noindex`;
  robots.txt blocking alone does not ensure removal from search.
  [Technical requirements](https://developers.google.com/search/docs/essentials/technical),
  [indexing controls](https://developers.google.com/search/docs/crawling-indexing/block-indexing).
- **JavaScript rendering.** Compare response HTML with rendered content, links,
  metadata, and resource failures. Google renders JavaScript; choose server
  rendering or prerendering for an observed need, accounting for other target
  crawlers. [JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics).
- **Duplicate URLs and redirects.** Trace hops and final destinations; compare
  canonicals, sitemap entries, and internal links. Align signals with the intended
  equivalent URL. A declared canonical is a preference, not proof of Google's
  selection. [Canonicalization](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
- **Metadata and content.** Map search intent to useful pages. Use descriptive
  titles, relevant descriptions, clear headings, and crawlable internal links.
  Preserve factual claims and authorship; add substantive information rather
  than keyword repetition or arbitrary length targets.
  [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide).
- **Structured data.** Select a currently supported feature appropriate to the
  page and visible content. Validate required properties and eligibility, not
  just JSON syntax; a passing test does not guarantee a rich result.
  [Structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies).
- **Page experience.** Measure the affected workload before changing it and
  compare the same conditions afterward. Use field and lab evidence for their
  respective purposes; a performance score is not proof of indexing or ranking.
  [Page experience](https://developers.google.com/search/docs/appearance/page-experience).
- **Google AI Overviews and AI Mode.** Apply existing SEO and snippet eligibility.
  Google requires no special AI files or schema for these features. Check other
  providers' current requirements separately.
  [AI features](https://developers.google.com/search/docs/appearance/ai-features).

Finish with each finding tied to an observed URL/template, its likely cause,
impact, proposed change, and acceptance check. Label hypotheses and prioritize
access/indexing blockers before appearance refinements. Avoid turning an audit
into an unconditional checklist of edits.

## Apply supported changes

Fix the owning template, route, CMS setting, header rule, or hosting layer.
Keep public URL and redirect changes consistent with existing links and search
traffic. Use the project's metadata and sitemap facilities instead of a second
competing implementation. Check the affected variants, including locale or
pagination behavior when relevant.

Apply changes supported by the intended search behavior or diagnosis. Check
current feature support before adding markup; Google's [documentation updates](https://developers.google.com/search/updates)
record retirements as well as new features. Use tests for meaningful routing,
metadata generation, or indexing-control regressions; a build alone does not
establish search discoverability.

## Verify the deployed result

After changes reach the target deployment, crawl the affected URL families.
Check new pages against the intended behavior and existing pages against the
baseline. Use the project's crawler or available HTTP and rendering tools;
set a bounded URL set and crawl rate suited to the site. Verify:

- Actual GET responses, redirect hops and final URLs, status codes, and indexing
  headers through the public hosting/CDN path.
- Relevant robots.txt and sitemap responses; intended indexable URLs and
  preserved exclusions.
- Response HTML and rendered content where JavaScript matters: important text,
  crawlable links, titles/descriptions, canonicals, and applicable structured data.
- Discovery paths and template variants affected by the fix, including links
  that were previously broken or orphaned.

Use Search Console's [URL Inspection](https://support.google.com/webmasters/answer/9012289)
when access exists. Distinguish its live fetch test from Google's stored indexed
version and selected canonical. A local browser render or a spoofed Googlebot
user agent does not prove Google's indexing behavior.

For an audit, report observed deployed behavior without making changes. For
fixes not yet deployed, report code/local checks separately and name the pending
deployment and live checks; do not claim deployed verification. Unavailable
production or account access leaves an explicit evidence gap, not an inferred pass.

## Handoff

Return the prioritized findings or implemented changes with affected URLs,
checks and results, crawl scope, remaining gaps, and any follow-up observation.
Separate technical eligibility, observed indexing, and measured search outcomes.
Indexing, rich results, rankings, and traffic gains are not guaranteed; report
later outcomes only from actual observations.
