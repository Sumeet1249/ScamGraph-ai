"""Script Detection Module for ScamGraph AI (Prompt 17 / Phase 5C).

Deterministic Unicode character range analyzer detecting:
- DEVANAGARI (\u0900-\u097F)
- BENGALI (\u0980-\u09FF)
- LATIN (\u0041-\u007A, \u00C0-\u024F)
- MIXED (e.g., Devanagari + Latin in single message)
- OTHER / UNKNOWN

Key Principle: SCRIPT IS NOT LANGUAGE.
A Latin message may be Hinglish or Roman Bengali.
A Devanagari message may be Hindi, Marathi, or Sanskrit.
"""

from typing import Dict, List, Tuple
import unicodedata
from packages.schemas.multilingual import ScriptType


def detect_scripts(text: str) -> Tuple[List[ScriptType], Dict[str, float]]:
    """
    Analyzes text and returns list of scripts present along with character ratio breakdown.
    Punctuation, digits, whitespace, and emojis are ignored for script classification.
    """
    if not text or not text.strip():
        return [ScriptType.UNKNOWN], {"UNKNOWN": 1.0}

    devanagari_count = 0
    bengali_count = 0
    latin_count = 0
    other_indic_count = 0
    other_count = 0
    total_alphabetic = 0

    for char in text:
        # Check if character is a letter or mark
        category = unicodedata.category(char)
        if not (category.startswith("L") or category.startswith("M")):
            continue

        code = ord(char)
        total_alphabetic += 1

        if 0x0900 <= code <= 0x097F:
            devanagari_count += 1
        elif 0x0980 <= code <= 0x09FF:
            bengali_count += 1
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A) or (0x00C0 <= code <= 0x024F):
            latin_count += 1
        elif (0x0A00 <= code <= 0x0DFF):  # Gurmukhi, Gujarati, Oriya, Tamil, Telugu, Kannada, Malayalam
            other_indic_count += 1
        else:
            other_count += 1

    if total_alphabetic == 0:
        return [ScriptType.UNKNOWN], {"UNKNOWN": 1.0}

    dev_ratio = devanagari_count / total_alphabetic
    ben_ratio = bengali_count / total_alphabetic
    lat_ratio = latin_count / total_alphabetic
    other_indic_ratio = other_indic_count / total_alphabetic
    other_ratio = other_count / total_alphabetic

    ratios = {
        "DEVANAGARI": round(dev_ratio, 4),
        "BENGALI": round(ben_ratio, 4),
        "LATIN": round(lat_ratio, 4),
        "OTHER_INDIC": round(other_indic_ratio, 4),
        "OTHER": round(other_ratio, 4),
    }

    scripts: List[ScriptType] = []

    # Significant threshold (>= 10% of alphabetic characters)
    if dev_ratio >= 0.10:
        scripts.append(ScriptType.DEVANAGARI)
    if ben_ratio >= 0.10:
        scripts.append(ScriptType.BENGALI)
    if lat_ratio >= 0.10:
        scripts.append(ScriptType.LATIN)
    if (other_indic_ratio >= 0.10 or other_ratio >= 0.10) and not scripts:
        scripts.append(ScriptType.OTHER)

    if not scripts:
        # Fall back to dominant script even if below threshold
        max_script = max(ratios, key=ratios.get)
        if max_script == "DEVANAGARI":
            scripts.append(ScriptType.DEVANAGARI)
        elif max_script == "BENGALI":
            scripts.append(ScriptType.BENGALI)
        elif max_script == "LATIN":
            scripts.append(ScriptType.LATIN)
        else:
            scripts.append(ScriptType.UNKNOWN)

    # If both Latin and an Indic script are substantially present, classify as MIXED
    if len(scripts) > 1:
        scripts.insert(0, ScriptType.MIXED)

    return scripts, ratios
