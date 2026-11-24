"""Deterministic, evidence-preserving LU layer for the Phase 1 contract.

This module interprets observations only. It never diagnoses or generates advice.
The legacy agriculture_engine.parse_question interface remains unchanged.
"""
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from agriculture_engine import normalize_text

SAFETY_FLAGS = {
    "REQUESTS_PESTICIDE_DOSE": ("pesticide dosage", "pesticide dose", "how much pesticide", "ಔಷಧಿ ಎಷ್ಟು", "ಔಷಧಿ ಪ್ರಮಾಣ", "ಪೆಸ್ಟಿಸೈಡ್ ಎಷ್ಟು"),
    "REQUESTS_CHEMICAL_MIXING": ("mix chemical", "mix pesticide", "chemical mixture", "tank mix", "ರಾಸಾಯನಿಕ ಮಿಶ್ರಣ", "ಔಷಧಿ ಮಿಕ್ಸ್"),
    "REQUESTS_FERTILIZER_QUANTITY": ("how much fertilizer", "fertilizer dose", "fertilizer quantity", "ರಸಗೊಬ್ಬರ ಎಷ್ಟು", "ಗೊಬ್ಬರ ಪ್ರಮಾಣ"),
    "REQUESTS_GUARANTEED_DIAGNOSIS": ("guaranteed diagnosis", "confirm disease", "100% disease", "ರೋಗ ಖಚಿತವಾಗಿ"),
    "REQUESTS_UNSUPPORTED_TREATMENT": ("best medicine", "which medicine", "cure this", "ಯಾವ ಔಷಧಿ", "ಚಿಕಿತ್ಸೆ ಹೇಳಿ"),
}

CROP_ALIASES = {
    "tomato": ("tomato", "ಟೊಮೆಟೋ", "ಟೊಮಾಟೊ", "ಟಮೋಟೊ", "ಟೊಮೇಟೊ"),
    "rice": ("rice", "paddy", "paddy plant", "rice crop", "ಭತ್ತ", "ಭತ್ತದ ಬೆಳೆ"),
    "potato": ("potato", "potatoes", "ಆಲೂಗಡ್ಡೆ", "ಆಲೂಗಡ್ಡೆ ಬೆಳೆ"),
    "maize": ("maize", "corn", "ಮೆಕ್ಕೆಜೋಳ", "ಜೋಳದ ಬೆಳೆ"),
    "chilli": ("chilli", "chili", "chillies", "ಮೆಣಸಿನಕಾಯಿ", "ಮೆಣಸಿನ ಬೆಳೆ"),
}
OBSERVATION_RULES = (
    ("leaf_yellowing", ("ಹಳದಿ", "yellow", "yellowing", "paddy plants are getting yellow", "rice plants are yellow", "ಭತ್ತದ ಗಿಡ ಹಳದಿ"), ("ಎಲೆ", "leaf", "paddy", "rice", "ಭತ್ತ", "plant")),
    ("wilting", ("ಬಾಡ", "ಒಣಗ", "ಸೊರಗ", "wilting", "wilt", "drying", "drying out"), ("ಗಿಡ", "plant", "leaf", "leaves")),
    ("brown_spots", ("ಕಂದು ಕಲೆ", "brown spot", "brown spots"), ("ಎಲೆ", "leaf")),
    ("leaf_spots", ("ಎಲೆ ಕಲೆ", "leaf spots", "leaves spots", "spots"), ("ಎಲೆ", "leaf")),
    ("serpentine_leaf_trails", ("ಹಾವಿನಂತೆ ಗೆರೆ", "ಸರ್ಪದಂತೆ ಗೆರೆ", "winding trails", "serpentine", "leaf miner"), ("ಎಲೆ", "leaf")),
    ("leaf_curling", ("ಮುರುಕ", "curling", "leaf curl"), ("ಎಲೆ", "leaf")),
    ("whitefly_observation", ("ಬಿಳಿ ಕೀಟ", "ಬಿಳಿ ಹುಳು", "whitefly", "tiny white insects"), ("ಎಲೆ", "leaf")),
    ("fruit_entry_holes", ("ಹಣ್ಣುಗಳಲ್ಲಿ ರಂಧ್ರ", "fruit entry holes", "entry holes"), ("ಹಣ್ಣು", "fruit", "ಕಾಯಿ")),
    ("fruit_damage", ("ಹಣ್ಣು ಹಾನಿ", "fruit damage", "damaged fruit"), ("ಹಣ್ಣು", "fruit", "ಕಾಯಿ")),
    ("insects", ("ಕೀಟ", "ಹುಳು", "insect", "insects", "pest"), ("ಗಿಡ", "ಎಲೆ", "ಹಣ್ಣು", "plant", "leaf", "fruit")),
    ("waterlogging", ("ನೀರು ನಿಂತ", "ಒದ್ದೆ ಮಣ್ಣು", "waterlogging", "standing water", "wet soil", "soil is wet"), ("ಮಣ್ಣು", "soil")),
    ("water_stress", ("ಮಣ್ಣು ಒಣ", "ಒಣ ಮಣ್ಣು", "dry soil", "soil is dry"), ("ಮಣ್ಣು", "soil")),
)

def _id(message_id: str, n: int) -> str:
    return f"obs-{hashlib.sha1(message_id.encode('utf-8')).hexdigest()[:10]}-{n:02d}"

def _contains_alias(text: str, alias: str) -> bool:
    if re.fullmatch(r"[a-z0-9 ]+", alias):
        return re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", text) is not None
    return alias in text

def _evidence(message_id: str, phrase: str, origin: str = "current_message") -> list[dict[str, Any]]:
    return [{"message_id": message_id, "phrase": phrase, "origin": origin, "start": None, "end": None}]

def _polarity(text: str, phrase: str) -> str:
    phrase_start = text.find(phrase)
    if phrase_start < 0:
        return "uncertain"
    prefix = text[:phrase_start]
    boundary = max(
        prefix.rfind(","), prefix.rfind(";"), prefix.rfind(" ಆದರೆ "),
        prefix.rfind(" ಮತ್ತು "), prefix.rfind(" but "), prefix.rfind(" and ")
    )
    start = max(boundary + 1, phrase_start - 22)
    window = text[start:phrase_start + len(phrase) + 12]
    if re.search(r"(?:ಇಲ್ಲ|ಆಗಿಲ್ಲ|ಬಾಡುತ್ತಿಲ್ಲ|ಬಾಡಿಲ್ಲ|ಒಣಗುತ್ತಿಲ್ಲ|ಒಣಗಿಲ್ಲ|ಇಲ್ಲದೆ|not|no)\b", window): return "absent"
    if re.search(r"(?:maybe|ಬಹುಶಃ|ಅನಿಸುತ್ತದೆ|perhaps)", window): return "uncertain"
    return "present"

def safety_flags(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [flag for flag, phrases in SAFETY_FLAGS.items() if any(phrase in normalized for phrase in phrases)]

@dataclass
class LUContext:
    observations: dict[str, dict[str, Any]] = field(default_factory=dict)
    followups: dict[str, dict[str, Any]] = field(default_factory=dict)

def understand(text: str, *, message_id: str | None = None, context: LUContext | None = None, input_channel: str = "text", interaction_type: str = "initial_report") -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return _empty(text if isinstance(text, str) else "", message_id, input_channel, interaction_type, ["INSUFFICIENT_EVIDENCE"])
    message_id = message_id or f"msg-{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}"
    normalized = normalize_text(text)
    result = {"schema_version":"1.0.0","message_id":message_id,"original_text":text,"normalized_text":normalized,"language":{"primary":"kn-IN" if any("ಕ" <= c <= "ೞ" for c in text) else "en-IN","code_mixed":bool(any("ಕ" <= c <= "ೞ" for c in text) and re.search(r"[A-Za-z]", text)),"evidence":_evidence(message_id,text),"confidence":None},"intents":[],"observations":[],"conversation_delta":{"new_observation_ids":[],"updated_observation_ids":[],"superseded_observation_ids":[],"contradictions":[]},"ambiguities":[],"missing_information":[],"follow_up":{"required":False,"candidates":[]},"confidence":{"language_detection":None,"intent_extraction":None,"observation_extraction":None,"context_resolution":None},"abstention":{"required":False,"reason_codes":[],"safe_clarification":None},"lu_safety_flags":safety_flags(text)}
    observation_number = 0
    for crop, aliases in CROP_ALIASES.items():
        for alias in aliases:
            if _contains_alias(normalized, alias):
                observation_number += 1
                result["observations"].append(_observation(message_id,"crop",crop,text,"not_applicable",text[text.lower().find(alias.lower()):text.lower().find(alias.lower()) + len(alias)] if alias.lower() in text.lower() else alias, observation_number)); break
    for value, phrases, parts in OBSERVATION_RULES:
        phrase = next((p for p in phrases if p in normalized), None)
        if not phrase: continue
        polarity = _polarity(normalized, phrase)
        part = next((p for p in parts if p in normalized), None)
        observation_number += 1
        exact = _find_exact_phrase(text, phrase)
        result["observations"].append(_observation(message_id,"symptom",value,text,polarity,exact,observation_number,part))
    _remove_broad_overlaps(result)
    if result["observations"]:
        result["intents"].append({"value":"REPORT_CROP_PROBLEM","evidence":_evidence(message_id,text),"confidence":None})
    else:
        result["ambiguities"].append({"reason":"No supported observation phrase found","evidence":_evidence(message_id,text)})
        result["abstention"]={"required":True,"reason_codes":["INSUFFICIENT_EVIDENCE"],"safe_clarification":"Which crop and plant symptom are you observing?"}
    if not any(o["kind"] == "crop" for o in result["observations"]):
        result["missing_information"].append({"field":"crop","state":"not_mentioned"})
    if result["lu_safety_flags"]:
        result["abstention"]={"required":True,"reason_codes":["SAFETY_REVIEW_REQUIRED"],"safe_clarification":"I can help organize observations, but dosage, mixing, diagnosis, or treatment decisions need qualified agricultural advice."}
    if context:
        _merge_context(result, context)
    return result

def _find_exact_phrase(original: str, normalized_phrase: str) -> str:
    if normalized_phrase in original:
        return normalized_phrase
    folded = original.casefold()
    pos = folded.find(normalized_phrase.casefold())
    return original[pos:pos + len(normalized_phrase)] if pos >= 0 else normalized_phrase

def _remove_broad_overlaps(result: dict[str, Any]) -> None:
    observations = result["observations"]
    specific = {"whitefly_observation", "fruit_entry_holes", "serpentine_leaf_trails"}
    result["observations"] = [
        observation for observation in observations
        if not (
            observation.get("normalized_value") == "insects"
            and any(other.get("normalized_value") == "whitefly_observation" for other in observations)
        ) and not (
            observation.get("normalized_value") == "fruit_damage"
            and any(other.get("normalized_value") == "fruit_entry_holes" for other in observations)
        )
    ]

def _observation(message_id, kind, value, text, polarity, phrase, number, part=None):
    return {"observation_id":_id(message_id, number),"kind":kind,"farmer_mention":phrase,"normalized_value":value,"extraction_status":"extracted","polarity":polarity,"validity":"active","relationship":"new","references":[],"describes_observation_id":None,"evidence":_evidence(message_id,phrase),"confidence":None,"plant_part":part}

def _merge_context(result, context):
    for oid, old in context.observations.items():
        if not any(o.get("normalized_value") == old.get("normalized_value") for o in result["observations"]):
            result["observations"].append({**old,"relationship":"repeated","references":[oid]})
            result["conversation_delta"]["updated_observation_ids"].append(oid)

def _empty(text, message_id, channel, interaction, reasons):
    mid = message_id or "msg-empty"
    return {"schema_version":"1.0.0","message_id":mid,"original_text":text,"normalized_text":normalize_text(text),"language":{"primary":"unknown","code_mixed":False,"evidence":[],"confidence":None},"intents":[],"observations":[],"conversation_delta":{"new_observation_ids":[],"updated_observation_ids":[],"superseded_observation_ids":[],"contradictions":[]},"ambiguities":[],"missing_information":[],"follow_up":{"required":False,"candidates":[]},"confidence":{"language_detection":None,"intent_extraction":None,"observation_extraction":None,"context_resolution":None},"abstention":{"required":True,"reason_codes":reasons,"safe_clarification":None},"lu_safety_flags":[]}

def validate_lu(result: dict[str, Any]) -> tuple[bool, list[str]]:
    errors=[]
    if result.get("schema_version") != "1.0.0": errors.append("schema_version")
    if not isinstance(result.get("observations"), list): errors.append("observations")
    ids=set()
    for o in result.get("observations", []):
        if o.get("observation_id") in ids: errors.append("duplicate_observation_id")
        ids.add(o.get("observation_id"))
        if o.get("polarity") not in {"present","absent","uncertain","not_applicable"}: errors.append("polarity")
        if not o.get("evidence") and o.get("extraction_status") == "extracted": errors.append("missing_evidence")
    return not errors, errors
