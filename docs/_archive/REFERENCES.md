# References — External Resources & Contacts

## Mapping / Geospatial
- **basemap.de** — https://basemap.de/ — German federal basemap service. Useful for creating maps, overlays, and spatial visualizations.

## Data Sourcing
- **Apify ImmoScout24 scrapers** — https://apify.com/store?q=immoscout24 — Multiple actors for scraping live Berlin rental listings with 50+ fields. Free tier: $5/month credits. Key actors:
  - `clearpath/immoscout24-api-pro` — 50+ fields, API-based, fast
  - `memo23/immobilienscout24-scraper` — $1.75/run, search + detail pages
  - Could provide current 2024-2025 asking rents to supplement Kaggle 2018-2019 training data

## Apartment Listing Bots / Potential Partners
- **Homeboy** — https://www.homeboy.immo/en — Bot-based apartment finding service for clients. Potential partnership/contact for data access or distribution.
- **Stekkies** — https://www.stekkies.com/de/ — Similar bot-based apartment search service. Potential partnership/contact.

## GitHub Repos Assessed (2026-03-14)
All rated LOW for direct use, but documented for reference:

- **flathunter** — https://github.com/flathunters/flathunter — Active Python bot for rental listing alerts. Scrapers for ImmoScout24, Immowelt, WG-Gesucht, Kleinanzeigen. **Notable:** PR #706 discovered ImmoScout mobile API (JSON endpoints) — worth studying if we ever need to scrape.
- **wohnung-scraper** — https://github.com/sibbl/wohnung-scraper — Node.js scraper with rich data schema (Kaltmiete/Warmmiete breakdown, construction year, floor, etc.). Last maintained 2023. No data included.
- **Berlin-Rental-Market-Clustering** — https://github.com/Amirabs7/Berlin-Rental-Market-Clustering — Zensus 2022 district-level rent averages + K-Means clustering. Too coarse for ML training.
- **Berlin-House-Prices-Prediction** — https://github.com/MoMkhani/Berlin-House-Prices-Prediction — Same Kaggle ImmoScout24 data, basic sklearn models (R²~0.82-0.91). Confirms baseline our approach should beat.
