"""
data/pipelines/ingestion.py — Reusable ETL functions for RentSignal

Functions:
    extract_apify_record(rec)   → dict from one Apify JSON record
    extract_sections(rec)       → dict with thermalChar + yearConstructed fallback
    year_to_building_era(year)  → canonical era string (matches model encoder)
    clean_bezirk(raw, source)   → cleaned bezirk string (23 old Berlin Bezirke)
    decode_html(text)           → decode HTML entities (ß, ö, ä, ü)
    apply_quality_filters(df)   → filtered DataFrame
    assign_unit_ids(df, start)  → DataFrame with unit_id column
    build_listings_table(df)    → listings panel table
    build_units_table(df)       → units master table

Usage:
    from data.pipelines.ingestion import ingest_apify
    units, listings = ingest_apify('data/raw/scraping/dataset_...json')
"""

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUILDING_ERA_BINS = [
    (1918, "pre_1918"),
    (1949, "1919_1949"),
    (1964, "1950_1964"),
    (1972, "1965_1972"),
    (1990, "1973_1990"),
    (2002, "1991_2002"),
    (2014, "2003_2014"),
    (9999, "2015_plus"),
]

ENERGY_SECTION_TITLES = {
    "Bausubstanz & Energieausweis",
    "Building details & energy certificate",
}

THERMAL_LABELS = {
    "energieverbrauchskennwert", "endenergiebedarf", "endenergieverbrauch",
    "energy consumption", "primary energy demand",
}

YEAR_LABELS = {"baujahr", "year of construction"}

BINARY_COLS = ["balcony", "hasKitchen", "lift", "cellar", "garden", "newlyConst"]

NUMERIC_COLS = [
    "baseRent", "totalRent", "serviceCharge", "heatingCosts",
    "livingSpace", "noRooms", "floor", "numberOfFloors", "thermalChar",
]

CATEGORICAL_COLS = ["condition", "interiorQual", "typeOfFlat", "heatingType"]

# Apify obj_regio4 (Ortsteil) → old 23 Bezirke mapping
# Modern merged Bezirke split back into old ones via Ortsteil membership
ORTSTEIL_TO_BEZIRK = {
    # Mitte (modern) → Mitte, Tiergarten, Wedding
    "mitte": "Mitte", "tiergarten": "Tiergarten", "wedding": "Wedding",
    "moabit": "Tiergarten", "hansaviertel": "Tiergarten",
    "gesundbrunnen": "Wedding",
    # Friedrichshain-Kreuzberg → Friedrichshain, Kreuzberg
    "friedrichshain": "Friedrichshain", "kreuzberg": "Kreuzberg",
    # Pankow (modern) → Pankow, Prenzlauer Berg, Weißensee
    "pankow": "Pankow", "prenzlauer berg": "Berg",
    "prenzlauer_berg": "Berg",
    "weißensee": "Weißensee", "weissensee": "Weißensee",
    "niederschönhausen": "Pankow", "buch": "Pankow",
    "französisch buchholz": "Pankow", "blankenburg": "Weißensee",
    "heinersdorf": "Weißensee", "karow": "Weißensee",
    "rosenthal": "Pankow", "wilhelmsruh": "Pankow",
    "blankenfelde": "Pankow", "malchow": "Hohenschönhausen",
    "stadtrandsiedlung malchow": "Hohenschönhausen",
    # Charlottenburg-Wilmersdorf → Charlottenburg, Wilmersdorf
    "charlottenburg": "Charlottenburg", "wilmersdorf": "Wilmersdorf",
    "schmargendorf": "Wilmersdorf", "grunewald": "Wilmersdorf",
    "halensee": "Wilmersdorf", "westend": "Charlottenburg",
    "charlottenburg-nord": "Charlottenburg",
    # Spandau
    "spandau": "Spandau", "haselhorst": "Spandau", "siemensstadt": "Spandau",
    "staaken": "Spandau", "gatow": "Spandau", "kladow": "Spandau",
    "hakenfelde": "Spandau", "falkenhagener feld": "Spandau",
    "wilhelmstadt": "Spandau",
    # Steglitz-Zehlendorf → Steglitz, Zehlendorf
    "steglitz": "Steglitz", "zehlendorf": "Zehlendorf",
    "lichterfelde": "Steglitz", "lankwitz": "Steglitz",
    "dahlem": "Zehlendorf", "nikolassee": "Zehlendorf",
    "wannsee": "Zehlendorf",
    # Tempelhof-Schöneberg → Tempelhof, Schöneberg
    "tempelhof": "Tempelhof", "schöneberg": "Schöneberg",
    "schoeneberg": "Schöneberg",
    "mariendorf": "Tempelhof", "marienfelde": "Tempelhof",
    "lichtenrade": "Tempelhof", "friedenau": "Schöneberg",
    # Neukölln
    "neukölln": "Neukölln", "neukoelln": "Neukölln",
    "britz": "Neukölln", "buckow": "Neukölln", "rudow": "Neukölln",
    "gropiusstadt": "Neukölln",
    # Treptow-Köpenick → Treptow, Köpenick
    "treptow": "Treptow", "köpenick": "Köpenick", "koepenick": "Köpenick",
    "adlershof": "Treptow", "altglienicke": "Treptow",
    "baumschulenweg": "Treptow", "johannisthal": "Treptow",
    "niederschöneweide": "Treptow", "oberschöneweide": "Köpenick",
    "plänterwald": "Treptow", "bohnsdorf": "Treptow",
    "friedrichshagen": "Köpenick", "grünau": "Köpenick",
    "müggelheim": "Köpenick", "rahnsdorf": "Köpenick",
    "schmöckwitz": "Köpenick", "alt-treptow": "Treptow",
    # Marzahn-Hellersdorf → Marzahn, Hellersdorf
    "marzahn": "Marzahn", "hellersdorf": "Hellersdorf",
    "biesdorf": "Marzahn", "kaulsdorf": "Hellersdorf",
    "mahlsdorf": "Hellersdorf",
    # Lichtenberg (modern) → Lichtenberg, Hohenschönhausen
    "lichtenberg": "Lichtenberg",
    "hohenschönhausen": "Hohenschönhausen",
    "alt-hohenschönhausen": "Hohenschönhausen",
    "neu-hohenschönhausen": "Hohenschönhausen",
    "karlshorst": "Lichtenberg", "rummelsburg": "Lichtenberg",
    "friedrichsfelde": "Lichtenberg", "fennpfuhl": "Lichtenberg",
    "falkenberg": "Hohenschönhausen",
    # Reinickendorf
    "reinickendorf": "Reinickendorf", "tegel": "Reinickendorf",
    "heiligensee": "Reinickendorf", "frohnau": "Reinickendorf",
    "hermsdorf": "Reinickendorf", "waidmannslust": "Reinickendorf",
    "wittenau": "Reinickendorf", "märkisches viertel": "Reinickendorf",
    "lübars": "Reinickendorf", "konradshöhe": "Reinickendorf",
    "borsigwalde": "Reinickendorf",
}

# Fallback: modern bezirk name → pick one of the old ones
MODERN_BEZIRK_FALLBACK = {
    "mitte": "Mitte",
    "friedrichshain-kreuzberg": "Kreuzberg",
    "friedrichshain_kreuzberg": "Kreuzberg",
    "pankow": "Pankow",
    "charlottenburg-wilmersdorf": "Charlottenburg",
    "charlottenburg_wilmersdorf": "Charlottenburg",
    "spandau": "Spandau",
    "steglitz-zehlendorf": "Steglitz",
    "steglitz_zehlendorf": "Steglitz",
    "tempelhof-schöneberg": "Tempelhof",
    "tempelhof_schöneberg": "Tempelhof",
    "tempelhof-schoeneberg": "Tempelhof",
    "tempelhof_schoeneberg": "Tempelhof",
    "neukölln": "Neukölln",
    "neukoelln": "Neukölln",
    "treptow-köpenick": "Treptow",
    "treptow_köpenick": "Treptow",
    "treptow-koepenick": "Treptow",
    "treptow_koepenick": "Treptow",
    "marzahn-hellersdorf": "Marzahn",
    "marzahn_hellersdorf": "Marzahn",
    "lichtenberg": "Lichtenberg",
    "reinickendorf": "Reinickendorf",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def decode_html(text: str) -> str:
    """Decode HTML entities: &szlig; → ß, &ouml; → ö, etc."""
    if not text:
        return text
    return html.unescape(text).replace("_", " ")


def year_to_building_era(year) -> str:
    """Map construction year to canonical building era string.

    Matches the OrdinalEncoder categories used in the XGBoost model.
    """
    if pd.isna(year):
        return "unknown"
    y = int(year)
    for upper_bound, era_label in BUILDING_ERA_BINS:
        if y <= upper_bound:
            return era_label
    return "2015_plus"


def clean_bezirk(ortsteil: str, regio3: str = "", source: str = "apify") -> str:
    """Map Ortsteil/regio to one of the 23 old Berlin Bezirke.

    Strategy:
    1. Try exact Ortsteil → old Bezirk lookup
    2. Fall back to modern Bezirk name → default old Bezirk
    3. Last resort: return cleaned regio3
    """
    if not ortsteil and not regio3:
        return "unknown"

    # Normalize
    ot = decode_html(str(ortsteil)).lower().strip()
    ot = re.sub(r"_?(bezirk|ortsteil)$", "", ot).strip()
    ot = ot.replace("_", " ").strip()

    # Try Ortsteil lookup: try both space and hyphen variants
    if ot in ORTSTEIL_TO_BEZIRK:
        return ORTSTEIL_TO_BEZIRK[ot]
    ot_hyphen = ot.replace(" ", "-")
    if ot_hyphen in ORTSTEIL_TO_BEZIRK:
        return ORTSTEIL_TO_BEZIRK[ot_hyphen]

    # Try modern bezirk fallback from regio3
    r3 = decode_html(str(regio3)).lower().strip()
    r3 = re.sub(r"_?bezirk$", "", r3).strip().replace("_", "-")
    if r3 in MODERN_BEZIRK_FALLBACK:
        return MODERN_BEZIRK_FALLBACK[r3]

    # Last resort: capitalize ortsteil
    return ortsteil.strip().title() if ortsteil else "unknown"


# ---------------------------------------------------------------------------
# Apify extraction
# ---------------------------------------------------------------------------

def extract_apify_record(rec: dict) -> dict:
    """Extract one flat record from an Apify ImmoScout24 JSON object."""
    atp = rec.get("adTargetingParameters", {})
    addr = rec.get("basicInfo", {}).get("address", {})

    return {
        "scout_id":        str(atp.get("obj_scoutId", "")),
        "scraped_at":      rec.get("scrapedAt", ""),
        "url":             rec.get("url", ""),
        # Rent
        "baseRent":        atp.get("obj_baseRent"),
        "totalRent":       atp.get("obj_totalRent"),
        "serviceCharge":   atp.get("obj_serviceCharge"),
        "heatingCosts":    atp.get("obj_heatingCosts"),
        # Physical
        "livingSpace":     atp.get("obj_livingSpace"),
        "noRooms":         atp.get("obj_noRooms"),
        "yearConstructed": atp.get("obj_yearConstructed"),
        "floor":           atp.get("obj_floor"),
        "numberOfFloors":  atp.get("obj_numberOfFloors"),
        # Binary amenities
        "balcony":         atp.get("obj_balcony"),
        "hasKitchen":      atp.get("obj_hasKitchen"),
        "lift":            atp.get("obj_lift"),
        "cellar":          atp.get("obj_cellar"),
        "garden":          atp.get("obj_garden"),
        "newlyConst":      atp.get("obj_newlyConst"),
        # Categorical
        "condition":       atp.get("obj_condition"),
        "interiorQual":    atp.get("obj_interiorQual"),
        "typeOfFlat":      atp.get("obj_typeOfFlat"),
        "heatingType":     atp.get("obj_firingTypes") or atp.get("obj_heatingType"),
        # Location
        "plz":             str(atp.get("obj_zipCode", "")),
        "regio3":          atp.get("obj_regio3", ""),
        "regio4":          atp.get("obj_regio4", ""),
        "street":          atp.get("obj_street", ""),
        "street_plain":    atp.get("obj_streetPlain", ""),
        "house_number":    atp.get("obj_houseNumber", ""),
        # Coordinates from basicInfo.address
        "lat":             addr.get("lat"),
        "lon":             addr.get("lon"),
        # Meta
        "immotype":        atp.get("obj_immotype", ""),
    }


def extract_sections(rec: dict) -> dict:
    """Extract thermalChar and yearConstructed from listing sections.

    Fallback source when adTargetingParameters is missing these fields.
    """
    thermal, year_fb = None, None
    for s in rec.get("sections", []):
        if not isinstance(s, dict) or s.get("title") not in ENERGY_SECTION_TITLES:
            continue
        for attr in s.get("attributes", []):
            label = str(attr.get("label", "")).lower().strip().rstrip(":")
            text = str(attr.get("text", "")).strip()
            if not text or text.lower() in ("no information", "keine angabe", ""):
                continue
            if label in THERMAL_LABELS:
                m = re.search(r"[\d.,]+", text)
                if m:
                    try:
                        thermal = float(m.group().replace(",", "."))
                    except ValueError:
                        pass
            if label in YEAR_LABELS:
                m = re.search(r"\d{4}", text)
                if m:
                    try:
                        year_fb = float(m.group())
                    except ValueError:
                        pass
    return {"thermalChar_section": thermal, "yearConstructed_section": year_fb}


# ---------------------------------------------------------------------------
# Type conversions & cleaning
# ---------------------------------------------------------------------------

def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Apply type conversions: numeric, boolean, categorical."""
    df = df.copy()

    # Numeric
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Boolean (y/n → True/False)
    for col in BINARY_COLS:
        if col in df.columns:
            df[col] = df[col].map({"y": True, "n": False, "j": True, True: True, False: False})
            df[col] = df[col].fillna(False).astype(bool)

    # Categorical: fill missing with 'unknown'
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = (
                df[col].fillna("unknown")
                .astype(str).str.lower().str.strip()
                .replace({"no_information": "unknown", "keine angabe": "unknown", "": "unknown"})
            )

    return df


def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived columns: rent_sqm, sqm_per_room, building_era, bezirk."""
    df = df.copy()

    # Merge section fallbacks into main columns
    if "yearConstructed_section" in df.columns:
        df["yearConstructed"] = df["yearConstructed"].fillna(df["yearConstructed_section"])
        df.drop(columns=["yearConstructed_section"], inplace=True)
    if "thermalChar_section" in df.columns:
        if "thermalChar" not in df.columns:
            df["thermalChar"] = df["thermalChar_section"]
        else:
            df["thermalChar"] = df["thermalChar"].fillna(df["thermalChar_section"])
        df.drop(columns=["thermalChar_section"], inplace=True)

    # Derived numeric (guard against division by zero)
    df["rent_sqm"] = df["baseRent"] / df["livingSpace"].replace(0, np.nan)
    df["sqm_per_room"] = df["livingSpace"] / df["noRooms"].clip(lower=0.5)

    # Building era (canonical)
    df["building_era"] = df["yearConstructed"].apply(year_to_building_era)

    # Bezirk (map Ortsteil → old 23 Bezirke)
    df["bezirk"] = df.apply(
        lambda r: clean_bezirk(r.get("regio4", ""), r.get("regio3", "")),
        axis=1,
    )

    # Neighborhood (clean from regio4)
    if "regio4" in df.columns:
        df["neighborhood"] = df["regio4"].apply(
            lambda x: decode_html(str(x)).replace("_", " ").strip() if x else "unknown"
        )

    # Clean street names (HTML decode)
    if "street" in df.columns:
        df["street"] = df["street"].apply(
            lambda x: decode_html(str(x)) if x and str(x) != "no_information" else None
        )
    if "street_plain" in df.columns:
        df["street_plain"] = df["street_plain"].apply(
            lambda x: decode_html(str(x)).replace("_", " ") if x and str(x) != "no_information" else None
        )
    if "house_number" in df.columns:
        df["house_number"] = df["house_number"].apply(
            lambda x: str(x) if x and str(x) != "no_information" else None
        )

    return df


# ---------------------------------------------------------------------------
# Quality filters
# ---------------------------------------------------------------------------

def apply_quality_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Remove invalid / outlier records. Returns filtered DataFrame + drop report."""
    n0 = len(df)
    mask = pd.Series(True, index=df.index)

    # Must have core fields
    mask &= df["baseRent"].notna() & df["livingSpace"].notna() & df["noRooms"].notna()
    # Valid PLZ (Berlin: 10xxx–14xxx)
    mask &= df["plz"].str.match(r"^1[0-4]\d{3}$", na=False)
    # Rental listings only
    if "immotype" in df.columns:
        mask &= df["immotype"].isin({"wohnung_miete", ""})
    # Rent bounds
    mask &= (df["rent_sqm"] >= 3) & (df["rent_sqm"] <= 60)
    # Size bounds
    mask &= (df["livingSpace"] >= 8) & (df["livingSpace"] <= 500)
    # Room bounds
    mask &= (df["noRooms"] >= 0.5) & (df["noRooms"] <= 20)

    df_out = df[mask].copy()

    # Ensure numeric types before clipping (Arrow string types can sneak in)
    for col in ["floor", "yearConstructed", "numberOfFloors", "thermalChar"]:
        if col in df_out.columns:
            df_out[col] = pd.to_numeric(df_out[col], errors="coerce")

    # Clip (don't drop) for secondary fields
    df_out["floor"] = df_out["floor"].clip(lower=0, upper=40)
    year_mask = df_out["yearConstructed"].notna()
    df_out.loc[year_mask, "yearConstructed"] = (
        df_out.loc[year_mask, "yearConstructed"].clip(1800, 2027)
    )

    dropped = n0 - len(df_out)
    print(f"Quality filter: {n0} → {len(df_out)} ({dropped} dropped, {100*dropped/n0:.1f}%)")
    return df_out


# ---------------------------------------------------------------------------
# Unit ID assignment & deduplication
# ---------------------------------------------------------------------------

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate listings within the same source.

    Dedup key: scout_id (ImmoScout24 listing ID).
    Keeps the first occurrence.
    """
    n0 = len(df)
    df = df.drop_duplicates(subset=["scout_id"], keep="first")
    dupes = n0 - len(df)
    if dupes:
        print(f"Deduplication: removed {dupes} duplicate scout_ids")
    return df


def assign_unit_ids(df: pd.DataFrame, start_from: int = 1) -> pd.DataFrame:
    """Assign RS-XXXXXX unit IDs."""
    df = df.copy()
    df["unit_id"] = [f"RS-{i:06d}" for i in range(start_from, start_from + len(df))]
    return df


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------

UNITS_COLS = [
    "unit_id", "scout_id", "source",
    "plz", "bezirk", "neighborhood",
    "street", "street_plain", "house_number",
    "lat", "lon",
    "livingSpace", "noRooms", "yearConstructed",
    "floor", "numberOfFloors", "thermalChar",
    "balcony", "hasKitchen", "lift", "cellar", "garden", "newlyConst",
    "condition", "interiorQual", "typeOfFlat", "heatingType",
    "building_era", "sqm_per_room",
]

LISTINGS_COLS = [
    "listing_id", "unit_id", "observed_date", "source",
    "baseRent", "totalRent", "serviceCharge",
    "rent_sqm",
]


def build_units_table(df: pd.DataFrame) -> pd.DataFrame:
    """Extract the units (master) table from the processed DataFrame."""
    cols = [c for c in UNITS_COLS if c in df.columns]
    return df[cols].copy()


def build_listings_table(df: pd.DataFrame) -> pd.DataFrame:
    """Extract the listings (panel) table from the processed DataFrame."""
    cols = [c for c in LISTINGS_COLS if c in df.columns]
    return df[cols].copy()


# ---------------------------------------------------------------------------
# Address recovery: cross-match with historical data
# ---------------------------------------------------------------------------

def cross_match_addresses(
    units_missing: pd.DataFrame,
    historical_df: pd.DataFrame,
    street_col: str = "street",
    house_col: str = "houseNumber",
    plz_col: str = "plz",
    sqm_col: str = "livingSpace",
    rooms_col: str = "noRooms",
) -> pd.DataFrame:
    """Cross-match units missing coordinates against historical data with addresses.

    Matches on (plz, livingSpace rounded to nearest m², noRooms).
    When multiple historical matches exist, picks the closest by exact sqm.

    This should be run on every new data intake — each previous scrape/source
    becomes a potential address donor for units that hide their address.

    Args:
        units_missing: Units without coordinates (must have plz, livingSpace, noRooms)
        historical_df: Historical data WITH addresses (street, house number, plz, sqm, rooms)
        street_col: Column name for street in historical_df
        house_col: Column name for house number in historical_df
        plz_col: Column name for PLZ in both DataFrames
        sqm_col: Column name for living space in both DataFrames
        rooms_col: Column name for number of rooms in both DataFrames

    Returns:
        DataFrame with columns: [apify_idx, street, house_number, plz, sqm_diff, source]
    """
    hist = historical_df.copy()

    # Filter to rows with valid addresses
    has_addr = (
        hist[street_col].notna()
        & (hist[street_col].astype(str) != "no_information")
        & (hist[street_col].astype(str) != "")
    )
    hist = hist[has_addr].copy()

    if len(hist) == 0:
        print("  No historical records with addresses found.")
        return pd.DataFrame()

    # Decode HTML in street names
    hist["_street_clean"] = hist[street_col].apply(
        lambda x: html.unescape(str(x)) if pd.notna(x) else None
    )
    hist["_house_clean"] = hist[house_col].astype(str)
    hist[sqm_col] = pd.to_numeric(hist[sqm_col], errors="coerce")
    hist[rooms_col] = pd.to_numeric(hist[rooms_col], errors="coerce")
    hist["_sqm_rounded"] = hist[sqm_col].round(0)
    hist[plz_col] = hist[plz_col].astype(str).str.strip()

    # Group historical data for fast lookup
    grouped = hist.groupby([plz_col, "_sqm_rounded", rooms_col])

    # Prepare missing units
    missing = units_missing.copy()
    missing["_sqm_rounded"] = missing[sqm_col].round(0)

    matches = []
    for idx, row in missing.iterrows():
        key = (str(row[plz_col]).strip(), row["_sqm_rounded"], row[rooms_col])
        if key in grouped.groups:
            candidates = hist.loc[grouped.groups[key]]
            diffs = (candidates[sqm_col] - row[sqm_col]).abs()
            best_idx = diffs.idxmin()
            best = candidates.loc[best_idx]
            matches.append({
                "idx": idx,
                "street": best["_street_clean"],
                "house_number": best["_house_clean"],
                "plz": str(row[plz_col]),
                "sqm_diff": abs(row[sqm_col] - best[sqm_col]),
            })

    result = pd.DataFrame(matches)
    print(f"  Cross-match: {len(result)} addresses recovered from {len(hist)} historical records")
    return result


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def ingest_apify(
    filepath: str,
    source_tag: str = "apify_2026_03",
    start_unit_id: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Full ingestion pipeline for an Apify ImmoScout24 JSON scrape.

    Returns:
        (units_df, listings_df) — the two relational tables
    """
    filepath = Path(filepath)
    print(f"Loading {filepath.name}...")

    with open(filepath, encoding="utf-8") as f:
        raw = json.load(f)
    print(f"  Raw records: {len(raw):,}")

    # Extract
    df = pd.DataFrame([extract_apify_record(r) for r in raw])
    sec = pd.DataFrame([extract_sections(r) for r in raw])
    df = pd.concat([df, sec], axis=1)

    # Convert types
    df = convert_types(df)

    # Derive features
    df = derive_features(df)

    # Quality filters
    df = apply_quality_filters(df)

    # Deduplicate
    df = deduplicate(df)

    # Assign IDs
    df["source"] = source_tag
    df = assign_unit_ids(df, start_from=start_unit_id)

    # Observed date
    df["observed_date"] = pd.to_datetime(df["scraped_at"], errors="coerce").dt.date

    # Listing IDs
    df["listing_id"] = [f"AP-{i:06d}" for i in range(1, len(df) + 1)]

    # Build tables
    units = build_units_table(df)
    listings = build_listings_table(df)

    print(f"\n  Units:    {len(units):,} rows, {len(units.columns)} columns")
    print(f"  Listings: {len(listings):,} rows, {len(listings.columns)} columns")

    return units, listings
