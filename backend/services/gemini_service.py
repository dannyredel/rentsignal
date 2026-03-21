"""Gemini image analysis service — extract apartment features from photos.

Sends up to 10 photos to Gemini 2.5 Flash and returns structured features
for the ML model (interior quality, kitchen/bathroom quality, floor type, etc.).
"""

import json
import os
import sys
from io import BytesIO

_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

# Lazy-load the Gemini client
_client = None
_MODEL_ID = "gemini-2.5-flash"


def _get_client():
    global _client
    if _client is None:
        if not _GEMINI_KEY:
            raise RuntimeError("GEMINI_API_KEY not set")
        from google import genai
        _client = genai.Client(api_key=_GEMINI_KEY)
    return _client


MULTI_PHOTO_PROMPT = """You are a Berlin real estate expert. You are seeing MULTIPLE photos from the SAME apartment listing.
Review ALL photos together. Score kitchen/bathroom from whichever photo shows them. Score building exterior from whichever photo shows the building from outside.

IMPORTANT: Do NOT default to 3. Score accurately:
- 1=very poor/rundown, 2=basic/dated, 3=average/maintained, 4=good/renovated, 5=luxury/designer
- If you see Dielen (wide boards) + high ceilings + stucco → style is "altbau"
- Plattenbau = prefab concrete blocks (common in East Berlin)

Return ONE JSON combining interior + exterior observations:
{"iq":3,"kq":0,"bq":0,"br":3,"rn":3,"ch":"normal","st":"modern","fl":"unknown","vw":"nv","sg":"empty","cw":"neutral","rr":false,"fu":false,"vk":false,"vb":false,"rm":"living_room","rs":1,"bc":3,"bs":"unknown","bf":0,"bg":false,"bgf":false}

Interior keys:
iq=interior 1-5. kq=kitchen 0-5 (0=not in any photo). bq=bathroom 0-5 (0=not in any photo).
br=brightness 1-5. rn=renovation 1-5.
ch: high|normal|low. st: altbau|modern|luxury|industrial|basic|neubau.
fl: dielen|parkett|laminate|tile|carpet|concrete|unknown.
vw: park|water|street|courtyard|skyline|nv. sg: empty|staged|lived_in|construction.
cw: warm|neutral|cool|dark. rr=any photo is 3D render. fu=furnished. vk=kitchen in any photo. vb=balcony in any photo.
rm=primary room in first photo: living_room|kitchen|bathroom|bedroom|floorplan|exterior|other.
rs=rooms shown (int, count distinct rooms across all photos).

Building exterior keys (from exterior photos if any):
bc=facade condition 0-5 (0=no exterior photo). bs: altbau|plattenbau|neubau|mixed|unknown.
bf=floors visible from outside (0=no exterior). bg=trees/garden around building. bgf=shops at ground floor.
Return ONLY JSON, one line."""

# Map short keys to model feature names
KEY_MAP = {
    "iq": "interior_quality", "kq": "kitchen_quality", "bq": "bathroom_quality",
    "br": "brightness", "rn": "renovation_level",
    "ch": "ceiling_height", "st": "style", "fl": "floor_type",
    "vw": "view_type", "sg": "staging", "cw": "color_warmth",
    "rr": "is_render", "fu": "is_furnished",
    "vk": "has_visible_kitchen", "vb": "has_visible_balcony",
    "rm": "room_type", "rs": "rooms_shown",
    "bc": "bldg_condition", "bs": "bldg_style",
    "bf": "bldg_floors", "bg": "bldg_green", "bgf": "bldg_commercial_gf",
}


def analyze_photos(images: list, max_retries: int = 3) -> dict:
    """Send photos to Gemini and return structured features.

    Args:
        images: list of PIL Image objects (max 10)
        max_retries: number of retry attempts on failure

    Returns:
        dict with model-ready feature names, or empty dict on failure
    """
    if not images:
        return {}

    client = _get_client()
    from google.genai import types

    images = images[:10]  # cap at 10

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=_MODEL_ID,
                contents=[MULTI_PHOTO_PROMPT] + images,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2000,
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            text = response.text.strip()
            raw = json.loads(text)

            # Map short keys to full names
            features = {}
            for short, full in KEY_MAP.items():
                if short in raw:
                    features[full] = raw[short]

            if "interior_quality" in features:
                return features

        except (json.JSONDecodeError, Exception) as e:
            print(f"Gemini attempt {attempt + 1} failed: {e}", file=sys.stderr)
            import time
            time.sleep(2)

    return {}
