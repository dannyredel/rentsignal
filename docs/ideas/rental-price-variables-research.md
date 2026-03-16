# Hard-to-Get Variables That Influence Rental Prices: A Literature Review

**Research Brief — March 2026**
**Compiled for: Daniel Redel**

---

## 1. Overview & Motivation

Standard hedonic rent models rely on structural attributes (size, rooms, age) and basic location variables (distance to CBD, transit stations). However, a growing body of literature demonstrates that **harder-to-obtain variables** — derived from remote sensing, computer vision, nighttime lights, social media, and environmental sensors — capture substantial unexplained variance in housing/rental prices. These variables proxy for neighborhood quality, environmental amenities, climate risk, and socioeconomic context that traditional data miss.

This brief maps the landscape of these "exotic" features across **seven categories**, with key papers, data sources, and practical notes on acquisition difficulty.

---

## 2. Taxonomy of Hard-to-Get Rental Price Variables

### 2.1 Satellite & Remote Sensing Imagery

**What it captures:** Neighborhood density, land use mix, vegetation coverage, building footprints, proximity to water, urban morphology — all at scale without surveys.

**Key features derived:**

- **NDVI (Normalized Difference Vegetation Index):** Measures greenness from multispectral satellite imagery. Consistently among the top predictors. In a Hong Kong study fusing multi-source images, NDVI ranked in the top 10 features with 45.3% SHAP importance (PMC, 2025 — multi-source image fusion study).
- **NDBI (Normalized Difference Built-up Index):** Captures building density from satellite bands. Ranked 44.8% SHAP importance in the same Hong Kong study.
- **NDWI (Normalized Difference Water Index):** Proximity/visibility of water bodies. 41.0% SHAP importance.
- **Multi-scale CNN features from satellite tiles:** Bency et al. (2017) showed that extracting deep CNN features from satellite imagery at multiple scales (fine to coarse neighborhoods) significantly improves house price prediction in London and other UK cities, particularly for rental properties where neighborhood amenities matter more than structural attributes.
- **Building age from aerial imagery:** A Dutch study achieved 93.48% accuracy in predicting building age (pre-1980 / 1980–2000 / post-2000) from aerial images using deep learning, outperforming street-view-based methods. Building age is a strong proxy for energy efficiency and construction quality.
- **Land use classification from satellite time series:** Temporal patterns in satellite imagery can identify land use transitions that affect property values.

**Data sources:**
- Sentinel-2 (free, 10m resolution, multispectral — ESA Copernicus)
- Landsat 8/9 (free, 30m — USGS)
- Google Earth Engine (processing platform)
- Commercial: Planet (3m daily), Maxar (30cm)

**Acquisition difficulty:** Medium. Free imagery is available but requires GIS/remote sensing skills for feature extraction. Pre-computed indices (NDVI, NDBI) are straightforward; CNN-based features require ML pipelines.

---

### 2.2 Street View Imagery (SVI) & Computer Vision

**What it captures:** Eye-level neighborhood quality — the "intangibles" that renters experience but traditional data miss: greenery visibility, building condition, street width, perceived safety, walkability.

**Key features derived:**

- **Green View Index (GVI):** Percentage of vegetation visible at street level. Studies confirm GVI is closer to human-perceived greenness than top-down NDVI and affects both commercial rents and residential prices. Yang et al. (2021) found significant effects on commercial building rents.
- **Sky View / Building View:** Proportion of sky vs. buildings visible from street level. "Building view" had 53.4% SHAP importance — the single highest image feature in the Hong Kong study.
- **Subjective perception scores:** Using deep learning on SVI to predict six perceptual qualities:
  - **Safety** (perceived crime risk)
  - **Walkability** (pedestrian friendliness)
  - **Greenness** (visual green exposure)
  - **Imageability** (memorability/distinctiveness)
  - **Enclosure** (sense of spatial containment)
  - **Complexity** (visual richness)
  
  A Shanghai study (2022) found that **subjectively-measured perceptions explain more housing price variation than objective pixel-ratio measures**, suggesting that human-perceived quality matters beyond what simple feature extraction captures.

- **Streetscape semantic segmentation features:** DeepLabv3+, SegFormer-B5, and SAM can segment SVI into building, sky, vegetation, road, sidewalk, car, etc. Pixel proportions become features. Sidewalk proportion, tree proportion, and image brightness (HSV_V) were positively correlated with perceived walkability in a Korean study.

**Key papers:**
- Law et al. (2018) — "Take a Look Around: Using Street View and Satellite Images to Estimate House Prices" — London, combined SVI + satellite + hedonic model
- Associations between Street-View Perceptions and Housing Prices (Remote Sensing, 2022) — Shanghai, subjective vs. objective measures
- PMC multi-source fusion study (2025) — Hong Kong, found remote sensing images contribute most to prediction accuracy among all image types

**Data sources:**
- Google Street View API (paid, ~$7/1000 panoramas)
- Mapillary (free/open, crowdsourced — coverage varies)
- Baidu Street View (China)
- KartaView (free/open)

**Acquisition difficulty:** Medium-High. API costs scale with coverage area. Semantic segmentation requires GPU compute. Subjective perception scoring requires training data from crowdsourced surveys (e.g., MIT Place Pulse).

---

### 2.3 Nighttime Light (NTL) Data

**What it captures:** Economic vitality, urbanization intensity, infrastructure quality, and energy access — all as proxy measures that correlate with neighborhood desirability and rent levels.

**Key findings:**

- A Scientific Reports paper (2020) demonstrated that **average nighttime light intensity (ANLI) from DMSP/OLS data** can forecast average housing prices in Chinese capital cities using quadratic polynomial regression, with predicted prices falling within interval estimates for most cities.
- NTL data has been validated as a proxy for GDP, electric power consumption, population density, and urbanization — all of which drive housing demand and rents.
- NTL is especially valuable in contexts where economic data is sparse or unreliable (developing countries, sub-national analysis).
- At fine-grained levels, a Swedish study found NTL correlates well with population and establishment density, though the relationship weakens for specific income measures.

**Specific use cases for rental prediction:**
- **Neighborhood economic vitality:** High NTL → commercial activity → higher rents
- **Infrastructure quality:** Consistent NTL → reliable electricity → premium
- **Temporal change detection:** NTL trends capture gentrification/decline faster than census data
- **Vacancy detection:** Low/declining NTL in residential areas may indicate vacancies

**Data sources:**
- VIIRS-DNB (500m resolution, daily since 2012 — free via NASA Black Marble / NOAA)
- DMSP-OLS (1km, 1992–2013 — historical baseline)
- Harmonized NTL dataset (Li et al., 2020) — consistent 1992–2021 time series, available in Google Earth Engine
- World Bank "Light Every Night" archive (250TB, analysis-ready on AWS)
- New: High-quality Daily NTL (HDNTL) dataset for 653 global cities (2025 preprint)

**Acquisition difficulty:** Low-Medium. Data is free and increasingly analysis-ready. Main challenge is spatial resolution (500m–1km) — too coarse for individual property valuation but useful for neighborhood-level features (e.g., average NTL within 500m buffer).

---

### 2.4 Air Quality, Noise, and Environmental Variables

**What it captures:** Environmental disamenities that renters pay to avoid — a well-established hedonic pricing literature dating back to Ridker & Henning (1967).

**Key features:**

- **PM2.5 / PM10 concentrations:** Hedonic studies consistently find negative price effects. A Hamilton, Canada study combined micro-scale PM2.5 dispersion modeling with accessibility measures, revealing a trade-off: properties near highways benefit from accessibility but suffer from air pollution.
- **NO₂ / SO₂ levels:** Spatial hedonic models for Seoul found significant willingness-to-pay for SO₂ reduction, with spatial econometric methods (GWR-SEM) capturing effects that OLS misses.
- **Traffic noise (dB levels):** Meta-analyses of hedonic noise studies find consistent negative effects of ~0.5–1% per additional dB for road traffic and ~0.5–2.5% per dB for aircraft noise. A Berlin study using ML methods found noise exposure was a significant predictor alongside structural variables.
- **Flood risk exposure:** Flood risk maps, FEMA flood zone designation, and First Street Foundation flood scores are increasingly capitalized into housing prices. A Nature Climate Change study (2023) found US residential properties in flood zones are overvalued by $121–$237 billion, with effects concentrated in areas without disclosure laws.
- **Temperature/heat exposure:** Emerging literature shows abnormal temperature exposure depresses house prices in areas with sea-level-rise risk, though rental effects are less clear.

**Data sources:**
- Air quality: OpenAQ (global), EEA Air Quality (Europe), EPA AQS (US), Copernicus Atmosphere Monitoring Service
- Noise: EU Environmental Noise Directive maps, OpenStreetMap road classifications as proxy
- Flood risk: First Street Foundation (US), EU Floods Directive maps, FEMA FIRMs
- Climate risk: FEMA National Risk Index, ClimateCheck, Risk Factor

**Acquisition difficulty:** Variable. Air quality station data is free but spatially sparse — interpolation or dispersion modeling needed for property-level estimates. Noise maps increasingly available in EU countries. Flood risk data improving rapidly. The real difficulty is at fine spatial resolution.

---

### 2.5 Points of Interest (POI) & Accessibility Variables

**What it captures:** Functional neighborhood quality — what's nearby and how accessible it is. Goes beyond simple distance-to-CBD.

**Key features (beyond standard transit distance):**

- **POI density by category within buffers:** Count of restaurants, cafés, schools, hospitals, banks, entertainment, shopping within 500m/1km. A Shanghai study found walking accessibility to major activity locations (MAL), metro stations (MTA), and social/economic services (SES) were the top 3 important non-image features.
- **Quantity-based vs. distance-based POI variables:** A Chinese study (Land, 2021) found that **quantity-based** neighborhood variables (how many restaurants within 1km) outperform **distance-based** variables (distance to nearest restaurant) in rental price models, as they better capture agglomeration effects.
- **Transit-Oriented Development (TOD) characteristics:** A five-megacity Chinese study found that TOD properties command significantly higher rents, with metro station density, neighborhood walkability, and the synergy between transit and land use all contributing.
- **School quality zones:** Often the single largest locational premium, but requires linking property locations to school catchment areas and performance data — non-trivial to automate.
- **Social infrastructure density:** Libraries, community centers, healthcare facilities. Hard to get at uniform quality globally.

**Data sources:**
- OpenStreetMap (free, global — variable completeness)
- Google Places API / Overpass API
- Foursquare Places (commercial)
- Yelp API (reviews + locations)
- National education databases for school quality

**Acquisition difficulty:** Low-Medium for basic POI counts. High for quality-weighted measures (e.g., restaurant ratings × density) and for school catchment linkage.

---

### 2.6 Social Media, Mobile Phone & Big Data Sources

**What it captures:** Revealed preferences, actual neighborhood usage patterns, population dynamics, and "buzz" — things surveys and censuses can't measure at high temporal frequency.

**Key features:**

- **Social media check-in density:** A Shenzhen study used Sina Weibo check-in data to construct POI hotspot maps and found that check-in density for catering, shopping, and entertainment significantly explain housing price variation via GWR models.
- **Mobile phone mobility patterns:** Cell tower data and GPS traces reveal actual commuting patterns, daytime vs. nighttime population, and neighborhood attractiveness. Korean cities' mobile phone data studies show these patterns differentiate urban structure and land use types.
- **Foot traffic / footfall data:** Commercial mobility data (SafeGraph, Placer.ai, Tamoco) provides visit counts to specific locations — can proxy for commercial vitality and neighborhood desirability.
- **Online listing text features / sentiment:** NLP on rental listing descriptions can extract quality signals (e.g., "renovated," "quiet neighborhood," "rooftop") that aren't in structured data.
- **Review sentiment by location:** Aggregated Yelp/Google Reviews sentiment within a buffer captures perceived neighborhood quality.

**Data sources:**
- Twitter/X API (limited free access, geo-tagged tweets declining)
- Foursquare check-in data (academic partnerships)
- SafeGraph / Dewey (US mobility data)
- Telco data (requires partnerships, privacy-sensitive)
- Google Popular Times (embedded in Places API)

**Acquisition difficulty:** High. Most valuable sources are commercial, privacy-restricted, or require institutional partnerships. Social media geo-tagging is declining. Mobile phone data requires telco agreements. But the signal can be very strong.

---

### 2.7 Socioeconomic & Demographic Spatial Data

**What it captures:** Neighborhood composition, income levels, education, demographic trends — the demand side of the rental equation.

**Key features:**

- **Population projections by age group:** A Japanese study (PETRA, 2025) found that integrating age-specific population projections into ML models significantly improved rent prediction accuracy beyond using current demographics alone, capturing future local demand shifts.
- **Income distribution at fine spatial resolution:** Census tract / Postleitzahl-level median income strongly predicts rent but is only available at coarse temporal resolution.
- **Share of young single-person households:** An Istanbul study found a 1pp increase in young singles' share leads to ~4.2% higher one-bedroom rents — a demand-side pressure variable.
- **Education levels / university proximity:** Both supply (student renters) and quality signal (educated neighborhoods).
- **Gentrification indices:** Composite measures from census change data — challenging to construct but highly predictive of rent trajectories.
- **Energy Performance Certificates (EPCs):** In the EU/UK, EPC ratings (A-G) are increasingly capitalized into rents, especially after MEES 2018 policy in the UK. Studies show F/G-rated properties face rent discounts, while A/B-rated command premiums.

**Data sources:**
- Census / Mikrozensus (Germany: Zensus 2022, Destatis)
- Eurostat NUTS-3 / LAU level data
- OpenEPC databases (UK)
- EU Building Stock Observatory
- National land registry / Grundbuchamt data

**Acquisition difficulty:** Low for census-based variables (but temporally sparse — updated every 5-10 years). Medium for EPC data (available in UK/Netherlands, harder elsewhere). High for fine-grained income data outside census years.

---

## 3. Feature Importance Rankings from Key Studies

| Study | Location | Top Non-Structural Features | Method |
|-------|----------|----------------------------|--------|
| PMC multi-source fusion (2025) | Hong Kong | Building view (53.4%), NDVI (45.3%), NDBI (44.8%), NDWI (41.0%), Sky view (26.9%) | Extra Trees + SHAP |
| PETRA/ACM (2025) | Japan | Land price, age-specific population projections, station distance | XGBoost + SHAP |
| Street-View Perceptions (2022) | Shanghai | Subjective safety, walkability, greenness scores | Hedonic + ML |
| Quantity-based FCNN-GWR (2021) | China | POI quantities within buffers (restaurants, transit, shopping) | FCNN + GWR |
| Bency et al. (2017) | London/UK | Multi-scale satellite CNN features + POI density | Random Forest |
| NTL housing prices (2020) | China | Average nighttime light intensity (quadratic relationship) | Polynomial regression |
| Hamilton accessibility (2019) | Canada | PM2.5 concentration, employment accessibility, congestion | Spatial hedonic |

---

## 4. Practical Recommendations for a Research Project

### Quick Wins (free data, moderate effort):
1. **NDVI from Sentinel-2** — compute within 500m buffer of each property
2. **NTL intensity from VIIRS** — neighborhood-level economic vitality proxy
3. **POI density from OpenStreetMap** — count by category within walking distance
4. **Flood risk zones** — available from EU/national agencies
5. **Air quality from monitoring stations** — interpolate to property locations

### Medium Effort, High Impact:
6. **Street View semantic segmentation** — GVI, sky view, building condition from Mapillary (free) or Google SVI
7. **EPC ratings** — available in several EU countries
8. **Population projection data** — national statistical offices

### High Effort, Frontier:
9. **Subjective perception scoring** (safety, walkability) from SVI + deep learning
10. **Mobile phone mobility patterns** — if academic data access available
11. **Social media check-in density** — declining availability but powerful
12. **Micro-scale noise/air pollution modeling** — requires dispersion models

### For a German/Berlin Context Specifically:
- **Mietspiegel data** as ground truth
- **Zensus 2022** for demographic features
- **Berlin Umweltatlas** for noise maps, air quality, green spaces
- **Berlin 3D city model** for building characteristics
- **DWD climate data** for temperature/precipitation
- **Mapillary** has strong coverage in German cities
- **Sentinel-2 NDVI** — excellent for Berlin's varied green structure
- **OpenStreetMap** — very complete in Germany

---

## 5. Key References

1. **Bency et al. (2017)** — "Beyond Spatial Auto-Regressive Models: Predicting Housing Prices with Satellite Imagery" — Multi-scale CNN features from satellite images
2. **PMC/Hong Kong (2025)** — "Real estate valuation with multi-source image fusion and enhanced ML pipeline" — Fuses exterior photos, SVI, and remote sensing
3. **Law et al. (2018)** — "Take a Look Around: Using Street View and Satellite Images to Estimate House Prices" — London, visual desirability extraction
4. **NTL Housing Prices (Scientific Reports, 2020)** — "Study on Average Housing Prices using Night-time Light Remote Sensing and Official Statistics Data"
5. **Contat et al. (2024)** — "When Climate Meets Real Estate: A Survey of the Literature" — Comprehensive review of climate risk × housing
6. **Kousky et al. (2021, PNAS)** — "The effect of information about climate risk on property values" — Flood risk underpricing
7. **Shanghai Perceptions (Remote Sensing, 2022)** — "Associations between Street-View Perceptions and Housing Prices: Subjective vs. Objective Measures"
8. **FCNN-GWR (Land, 2021)** — "Exploring a Pricing Model for Urban Rental Houses from a Geographical Perspective" — Quantity-based POI variables
9. **PETRA/ACM (2025)** — "Rent Price Prediction Using ML with Public Land Price, Geospatial, and Demographic Projection Data"
10. **Spatial Hedonic Seoul (2003)** — "Measuring the benefits of air quality improvement: a spatial hedonic approach"
11. **Hamilton Accessibility (2019)** — "Accessibility, air pollution, and congestion: Capturing spatial trade-offs from agglomeration"
12. **Lisbon Multi-Modal (2025)** — "Predicting housing price, housing density, and green area coverage from combined satellite and street view imagery using deep learning"

---

*This brief is intended as a starting point for a deeper research agenda. Cross-references with Daniel's paper library and BeeSignal methodological framework may surface additional connections, particularly around causal inference methods (DiD, synthetic control) applied to policy interventions affecting rental markets.*
