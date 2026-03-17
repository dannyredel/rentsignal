---
name: blog-content
description: Create SEO-optimized blog articles for blog.rentsignal.de using Quarto
---

# Blog Content Creation Skill

Use this skill when writing new blog articles for RentSignal. Every article must follow the SEO strategy in `docs/strategy/rentsignal-seo-strategy.md` and the tracking setup in `docs/strategy/rentsignal-seo-tracking-setup.md`.

## Pre-Writing Checklist

1. **Check the content calendar** in `docs/strategy/rentsignal-seo-strategy.md` §2 — identify the target article spec (keyword, title, word count, format, internal links, unique data point, CTA)
2. **Check existing articles** in `blog/posts/` — avoid duplicate topics, plan internal links to existing content
3. **Identify the target keyword** and verify it matches the priority in §1 of the SEO strategy

## Article Structure

Create the article at `blog/posts/{slug}/index.qmd` where `{slug}` is a short, keyword-rich URL slug.

### Required Frontmatter

```yaml
---
title: "Target keyword first — then compelling hook"
subtitle: "One-sentence value prop with specific numbers"
description: "150-160 chars. Include keyword + CTA. This becomes the meta description."
author: "Daniel Redel"
date: "YYYY-MM-DD"
categories: [Category1, Category2, Category3]
lang: de  # or en for English articles
# image: hero-image.png  # Add when available

keywords:
  - primary target keyword
  - secondary keyword variant
  - long-tail keyword 1
  - long-tail keyword 2
  - long-tail keyword 3

open-graph:
  title: "Keyword-optimized OG title | RentSignal"
  description: "Short, compelling OG description for social sharing."
---
```

### Required SEO Elements

| Element | Rule |
|---------|------|
| **Title tag** | Target keyword FIRST, brand last. Max 60 chars. |
| **Meta description** | 150-160 chars, include keyword + CTA |
| **H1** | One per page, matches title intent |
| **H2/H3** | Keyword variants in subheadings |
| **URL slug** | Short, keyword-rich: `/posts/mietpreisbremse-rechner-2026/` |
| **Language** | `lang: de` for German, `lang: en` for English |
| **Categories** | 3-5 relevant tags |
| **Keywords** | 5-7 in frontmatter for meta keywords |

### Content Formula

Every article follows this structure:

1. **TL;DR / Summary** — Lead with the outcome, key numbers, table if applicable
2. **The core content** — Explain the topic with real data from our analysis
3. **Mid-article CTA** — Link to relevant RentSignal tool with UTM params
4. **Detailed sections** — Deep dive with H2/H3 headings using keyword variants
5. **FAQ section** — 4-5 common questions (enables FAQ schema later)
6. **Bottom CTA** — Strong call to action with UTM link
7. **Cross-language summary** — German articles get English callout box, English articles get German callout box

### UTM Link Format

Every link to rentsignal.de MUST include UTM parameters:

```
https://rentsignal.de/path
  ?utm_source=blog
  &utm_medium=cta
  &utm_campaign={article-slug}
  &utm_content={position}
```

Positions: `hero`, `mid-article`, `bottom`, `signup`, `en-summary`, `de-summary`

### Internal Linking

- Every article links to **2-3 other blog articles** (check `blog/posts/` for existing)
- Every article links to **1-2 RentSignal tool pages** with UTM params
- Use descriptive anchor text with keywords, not "click here"

### Data Points

Every article must include at least **one unique data point** from our analysis:
- 10,275 Berlin apartments analyzed
- Kitchen CATE +€2.91/m², Balcony -€0.72/m²
- Dual-method convergence at 3%
- Restaurant density as #1 spatial predictor (SHAP=1.71)
- 84% of Berlin apartments trigger CO2 sharing
- Average rent exceeds legal max by €1.67/m²
- XGBoost R²=0.749 with 37 features
- Satellite + OSM spatial features unique to RentSignal

### Brand Voice (from PRODUCT.md §17)

- Precise, data-driven, never salesy
- Use "RentSignal" not "we" when referencing the product
- German: formal but accessible (no Sie/Du confusion — use "du" for blog)
- English: clear, no jargon, explain German legal terms on first use with italics
- Numbers: always specific (€2.91/m², not "around €3")

## Post-Writing Checklist

1. **Render locally:** `cd blog && quarto render` — verify no errors
2. **Check word count** meets the spec (1,500+ for guides, 1,800+ for data articles)
3. **Verify all links** work (UTM links, internal article links)
4. **Cross-language summary** present at bottom
5. **FAQ section** with 4-5 questions
6. **Push and verify** deployment at blog.rentsignal.de

## FAQ Schema (Add When Available)

For articles with FAQ sections, add JSON-LD FAQ schema as a Quarto include:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here"
      }
    }
  ]
}
</script>
```

Include per-article via frontmatter:
```yaml
format:
  html:
    include-after-body:
      - _includes/faq-{slug}.html
```

## Backlog Items (Not Yet Implemented)

- [ ] og:image — generate branded hero images per article
- [ ] FAQ schema JSON-LD per article
- [ ] Google Analytics tracking (waiting for Measurement ID)
- [ ] Hreflang tags for DE/EN article pairs
