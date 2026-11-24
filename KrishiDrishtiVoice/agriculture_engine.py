import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

KNOWLEDGE_PATH = Path(__file__).with_name("knowledge.json")
NORMALIZATION_ALIASES = {
    "ಟೊಮೇಟೊ": "ಟೊಮೆಟೋ",  # reviewed synthetic spelling/ASR-like variant; not a real STT claim
    "tomato plant": "tomato",
    "tomato ele": "tomato leaf",
    "ele haladi agtide": "leaf yellowing",
    "ಬಾಡ್ತಾ": "ಬಾಡುತ್ತ",
    "ಒಣಗ್ತಾ": "ಒಣಗುತ್ತ",
    "ಆಗ್ತಿದೆ": "ಆಗುತ್ತಿದೆ",
    "paddy plant": "rice plant",
    "paddy crop": "rice crop",
}
SAFETY_NOTICE = "This is symptom-based guidance, not a confirmed diagnosis. Do not apply pesticide or nutrient doses from this assistant."
SAFETY_PATTERNS = {
    "pesticide_dose": ("pesticide", "insecticide", "fungicide", "dose", "dosage", "spray how much", "ಔಷಧಿ ಎಷ್ಟು", "ಔಷಧಿ ಪ್ರಮಾಣ", "ಸಿಂಪಡಣೆ ಎಷ್ಟು"),
    "chemical_mixing": ("mix chemical", "mix pesticide", "chemical mixture", "tank mix", "ರಾಸಾಯನಿಕ ಮಿಶ್ರಣ"),
    "fertilizer_quantity": ("fertilizer quantity", "fertilizer dose", "how much fertilizer", "urea dose", "ರಸಗೊಬ್ಬರ ಎಷ್ಟು", "ಗೊಬ್ಬರ ಪ್ರಮಾಣ"),
    "guaranteed_diagnosis": ("guaranteed diagnosis", "guaranteed disease diagnosis", "confirm disease", "is it definitely", "100% disease"),
    "unsupported_treatment": ("cure this", "best medicine", "which medicine", "treatment for disease")
}
SYMPTOM_PATTERNS = (
    ("wet_soil_drying", ("drying even though the soil is wet", "drying while soil is wet")),
    ("waterlogging", ("standing water", "waterlogging", "water stagnation", "poor drainage", "wet soil", "soil is wet", "ನೀರು ನಿಂತಿದೆ", "ಒದ್ದೆ ಮಣ್ಣು")),
    ("water_stress", ("soil is dry", "dry soil", "irrigated yesterday", "irrigated my tomato", "last irrigation", "drying", "ಒಣ ಮಣ್ಣು")),
    ("leaf_yellowing", ("yellow", "yellowing", "ಹಳದಿ", "ಹಳದಿಯಾಗುತ್ತ")),
    ("wilting", ("wilting", "wilt", "ಒಣಗುತ್ತ", "ಬಾಡುತ್ತ")),
    ("brown_spots", ("brown spots", "brown spot", "leaf spots", "spots on leaves", "ಕಲೆಗಳ")),
    ("leaf_curling", ("curling", "curled", "leaf curl", "ಎಲೆಗಳು ಸುತ್ತ", "ಮುರುಕು")),
    ("whitefly_observation", ("tiny white insects", "small white insects", "leaf undersides", "insects under my tomato leaves", "ಬಿಳಿ ಕೀಟ")),
    ("insects", ("insects", "pests", "whitefly", "aphid", "thrips", "ಕೀಟ")),
    ("fruit_borer_observation", ("fruit borer", "entry hole", "entry holes", "frass", "ಹಣ್ಣು ಹಾನಿ")),
    ("leaf_miner_observation", ("leaf miner", "serpentine trails", "winding trails", "mines in leaves", "ಎಲೆಗಳಲ್ಲಿ ಗೆರೆ")),
    ("fruit_damage", ("fruit damaged", "fruits are damaged", "fruit is damaged", "damaged fruit", "fruit damage")),
)
SYMPTOM_RECORDS = {
    "leaf_yellowing": "tomato-leaf-yellowing-001", "wilting": "tomato-water-stress-001",
    "brown_spots": "tomato-leaf-yellowing-001", "leaf_curling": "tomato-leaf-yellowing-001",
    "waterlogging": "tomato-waterlogging-001", "water_stress": "tomato-water-stress-001",
    "whitefly_observation": "tomato-whitefly-001", "fruit_borer_observation": "tomato-fruit-borer-001",
    "leaf_miner_observation": "tomato-leaf-miner-001", "fruit_damage": "tomato-fruit-borer-001",
}

INTENT_PATTERNS = {
        "cultivation": ("grow", "cultivat", "plant", "manage my", "ಬೆಳೆಸ", "ಬೆಳೆಸುವುದು", "ಬೆಳೆಸಲು", "ಬೆಳೆಯುವುದು", "ಬೆಳೆಯಲು", "ಕೃಷಿ", "ಸಾಗುವಳಿ"),
    "propagation": ("more plants", "seed", "sow", "nursery", "propagat", "ಸಸಿ", "ಬೀಜ", "ನರ್ಸರಿ", "ಹೆಚ್ಚು ಗಿಡ"),
    "productivity": ("yield", "productive", "increase production", "more harvest", "ಉತ್ಪಾದನೆ", "ಇಳುವರಿ", "ಹೆಚ್ಚು ಬೆಳೆ"),
    "irrigation": ("water", "irrigat", "when should i water", "ನೀರು", "ನೀರಾವರಿ"),
    "soil": ("soil preparation", "soil", "ಮಣ್ಣು", "ಭೂಮಿ ತಯಾರಿ"),
        "harvest": ("harvest", "harvesting", "pick", "ಹಾರ್ವೆಸ್ಟ್", "ಕೊಯ್ಲು", "ಕೊಯ್ಲು ಮಾಡುವುದು"),
        "maintenance": ("maintain", "maintenance", "weed", "ನಿರ್ವಹಣೆ", "ಕಳೆ"),
        "seed_selection": ("seed", "seedling", "planting material", "ವಿಧ", "ಬೀಜ", "ಸಸಿ"),
    "market_price": ("market price", "price", "mandi", "wholesale price", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ"),
    "weather": ("weather", "rain", "forecast", "ಹವಾಮಾನ", "ಮಳೆ"),
}


def classify_intent(question: str, symptom: str | None = None) -> str:
    text = normalize_text(question)
    if symptom:
        return "symptom_investigation"
    priority = ("market_price", "weather", "irrigation", "harvest", "productivity", "soil", "seed_selection", "maintenance", "cultivation", "propagation")
    for intent in priority:
        phrases = INTENT_PATTERNS[intent]
        if any(phrase in text for phrase in phrases):
            return intent
    return "general_crop_information" if identify_crop(text) else "unknown"
KANNADA_SYMPTOM_RECORDS = {
    "leaf_yellowing": "tomato-leaf-yellowing-001", "wilting": "tomato-water-stress-001",
    "brown_spots": "tomato-leaf-yellowing-001", "leaf_curling": "tomato-leaf-yellowing-001",
    "fruit_damage": "tomato-fruit-borer-001",
}


@dataclass(frozen=True)
class Match:
    record: dict
    score: int
    reasons: tuple[str, ...] = ()


def load_knowledge() -> dict:
    with KNOWLEDGE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text).casefold().strip()
    normalized = re.sub(r"[!?।]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    for variant, canonical in NORMALIZATION_ALIASES.items():
        normalized = re.sub(rf"(?<!\w){re.escape(variant)}(?!\w)", canonical, normalized)
    return normalized


def _negates_symptom(text: str, symptom: str) -> bool:
    """Conservative guard only; full polarity extraction remains future work."""
    guards = {
        "leaf_yellowing": (r"ಹಳದಿ\s*(?:ಆಗಿಲ್ಲ|ಇಲ್ಲ)", r"not\s+yellow", r"yellow\s+not"),
        "wilting": (r"ಬಾಡುತ್ತಿಲ್ಲ", r"ಒಣಗುತ್ತಿಲ್ಲ", r"not\s+wilting"),
        "insects": (r"ಕೀಟ\s*ಇಲ್ಲ", r"ಹುಳು\s*ಇಲ್ಲ", r"no\s+insects"),
        "brown_spots": (r"ಕಂದು\s*ಕಲೆ\s*ಇಲ್ಲ", r"no\s+brown\s+spots"),
        "water_stress": (r"ಮಣ್ಣು\s*ಒಣಗಿಲ್ಲ", r"soil\s+is\s+not\s+dry"),
    }
    return any(re.search(pattern, text) for pattern in guards.get(symptom, ()))


def _parse_kannada_symptom(text: str) -> str | None:
    """Match conservative Kannada observation phrases, including common inflections."""
    kannada_patterns = (
        ("waterlogging", (r"ನೀರು\s*(?:ನಿಂತ|ನಿಲ್ಲ)", r"ಮಣ್ಣು\s*(?:ತುಂಬಾ\s*)?ಒದ್ದೆ", r"ಒದ್ದೆಯಾಗ")),
        ("water_stress", (r"ನೀರು\s*ಸಾಲದೆ", r"ನೀರು\s*ಇಲ್ಲದೆ", r"ಮಣ್ಣು\s*ಒಣ")),
        ("whitefly_observation", (r"ಎಲೆಗಳ?\s*ಕೆಳಗೆ.*(?:ಚಿಕ್ಕ\s*)?ಬಿಳಿ\s*(?:ಕೀಟ|ಹುಳು)", r"ಬಿಳಿ\s*(?:ಕೀಟ|ಹುಳು)")),
        ("fruit_borer_observation", (r"ಹಣ್ಣುಗಳ?\s*(?:ನಲ್ಲಿ|ಒಳಗೆ).*ರಂಧ್ರ", r"ಹಣ್ಣುಗಳ?\s*(?:ನಲ್ಲಿ|ಒಳಗೆ).*ಕುಳಿ", r"ಹಣ್ಣಿನೊಳಗೆ.*ಕುಳಿ", r"ಹಣ್ಣುಗಳಲ್ಲಿ.*ರಂಧ್ರ")),
        ("leaf_miner_observation", (r"ಎಲೆಗಳ?\s*ಒಳಗೆ.*ಗೆರೆ", r"ಹಾವಿನಂತೆ.*ಗೆರೆ", r"ಸರ್ಪದಂತೆ.*ಗೆರೆ")),
        ("brown_spots", (r"ಕಂದು\s*ಕಲೆ", r"ಎಲೆಗಳ?.*ಕಲೆ")),
        ("leaf_curling", (r"ಎಲೆಗಳ?.*(?:ಮುರುಕು|ಸುತ್ತ|ಕುಗ್ಗ)", r"ಮುರುಕಾಗ")),
        ("leaf_yellowing", (r"ಹಳದಿ\s*(?:ಬಣ್ಣ|ಆಗ|ಇದೆ|ಇರುತ್ತ|ಯಾಗ)", r"ಹಳದಿಯಾಗ")),
        ("fruit_damage", (r"ಹಣ್ಣು.*ಹಾನಿ",)),
        ("wilting", (r"ಬಾಡುತ್ತ", r"ಒಣಗುತ್ತ")),
    )
    for symptom, patterns in kannada_patterns:
        if any(re.search(pattern, text) for pattern in patterns):
            return symptom
    return None


def parse_question(question: str) -> dict:
    """Identify only observable entities; this function never assigns a disease."""
    text = normalize_text(question)
    crop = "tomato" if any((re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", text) if token.isascii() else token in text) for token in ("tomato", "ಟೊಮೆಟೋ", "ಟೊಮಾಟೊ", "ಟಮೋಟೊ")) else None
    if any((re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", text) if token.isascii() else token in text) for token in ("rice", "paddy", "ಭತ್ತ", "ಭತ್ತದ ಬೆಳೆ")):
        crop = "rice"
    if any((re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", text) if token.isascii() else token in text) for token in ("potato", "potatoes", "ಆಲೂಗಡ್ಡೆ")):
        crop = "potato"
    if any((re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", text) if token.isascii() else token in text) for token in ("maize", "corn", "ಮೆಕ್ಕೆಜೋಳ", "ಜೋಳದ ಬೆಳೆ")):
        crop = "maize"
    if any((re.search(rf"(?<![a-z0-9]){token}(?![a-z0-9])", text) if token.isascii() else token in text) for token in ("chilli", "chili", "chillies", "ಮೆಣಸಿನಕಾಯಿ", "ಮೆಣಸಿನ ಗಿಡ", "ಮೆಣಸಿನ ಗಿಡಗಳನ್ನು")):
        crop = "chilli"
    symptom = _parse_kannada_symptom(text)
    if symptom is None:
        symptom = next((name for name, phrases in SYMPTOM_PATTERNS if any(phrase in text for phrase in phrases)), None)
    if symptom and _negates_symptom(text, symptom):
        symptom = None
    return {"crop": crop, "symptom": symptom, "normalized_text": text}


def validate_safety(question: str) -> str | None:
    text = normalize_text(question)
    for category, phrases in SAFETY_PATTERNS.items():
        if any(phrase in text for phrase in phrases):
            return category
    return None


def identify_crop(question: str, knowledge: dict | None = None) -> str | None:
    parsed = parse_question(question)
    if parsed["crop"]:
        return parsed["crop"]
    text = parsed["normalized_text"]
    for crop in (knowledge or load_knowledge()).get("crops", []):
        if normalize_text(crop) in text:
            return crop
    return None


def search(question: str, limit: int = 5, lu_result: dict | None = None) -> list[Match]:
    text = normalize_text(question)
    knowledge = load_knowledge()
    crop = identify_crop(text, knowledge)
    parsed_symptom = parse_question(text)["symptom"]
    intent = classify_intent(text, parsed_symptom)
    structured_values = set()
    absent_values = set()
    if lu_result:
        for observation in lu_result.get("observations", []):
            if observation.get("polarity") in {"absent", "uncertain"}:
                if observation.get("polarity") == "absent":
                    absent_values.add(normalize_text(str(observation.get("normalized_value", ""))))
                continue
            structured_values.add(normalize_text(str(observation.get("normalized_value", ""))))
            structured_values.add(normalize_text(str(observation.get("farmer_mention", ""))))
        crop_observation = next((o for o in lu_result.get("observations", []) if o.get("kind") == "crop" and o.get("polarity") == "not_applicable"), None)
        if crop_observation:
            crop = crop_observation.get("normalized_value")
    matches = []
    for record in knowledge.get("entries", []):
        if crop and record.get("crop") and record.get("crop") != crop:
            continue
        if not parsed_symptom and intent in {"market_price", "weather"}:
            continue
        if not parsed_symptom and intent not in {"symptom_investigation", "pest_investigation", "disease_investigation"}:
            if record.get("category") in {"symptom", "disease_reference", "disease_observation", "pest_reference", "pest_observation", "environmental_stress"}:
                continue
        record_identity = normalize_text(f"{record.get('id', '')} {record.get('topic', '')}").replace("_", " ").replace("-", " ")
        if any(value.replace("_", " ").replace("-", " ") in record_identity for value in absent_values):
            continue
        score = 10 if crop and record.get("crop") == crop else 0
        reasons = ["crop_match"] if score else []
        keyword_hits = []
        for keyword in record.get("keywords", []):
            token = normalize_text(keyword)
            if token and (token in text or any(token in value or value in token for value in structured_values)):
                score += 2 if len(token) > 3 else 1
                keyword_hits.append(keyword)
        if keyword_hits:
            reasons.append("keyword_match:" + ",".join(keyword_hits[:5]))
        if score:
            preferred_id = SYMPTOM_RECORDS.get(parsed_symptom)
            if any("ಕ" <= character <= "ೞ" for character in text):
                preferred_id = KANNADA_SYMPTOM_RECORDS.get(parsed_symptom, preferred_id)
            if preferred_id == record.get("id"):
                score += 8
                reasons.append("symptom_record_match")
            if record.get("intent") == intent:
                score += 8
                reasons.append("intent_match")
            matches.append(Match(record, score, tuple(reasons)))
    return sorted(matches, key=lambda match: (-match.score, match.record["id"]))[:limit]


def _questions(matches: list[Match]) -> list[str]:
    seen, result = set(), []
    for match in matches:
        for question in match.record.get("follow_up_questions", []):
            if question not in seen:
                seen.add(question)
                result.append(question)
    return result[:6]


def build_guidance(question: str, language: str = "English", lu_result: dict | None = None) -> dict:
    safety_category = validate_safety(question)
    if lu_result and lu_result.get("lu_safety_flags") and not safety_category:
        safety_category = "language_understanding_safety_review"
    if safety_category:
        return {"understanding": "I cannot provide that unsafe or unsupported recommendation.", "possible_explanations": [], "follow_up_questions": ["What crop, symptom, crop age, and recent weather or irrigation conditions are you observing?"], "safe_actions": ["Do not mix chemicals or apply a dose based only on this assistant.", "Consult a qualified local agricultural officer for a current, crop-specific recommendation."], "referral": "A qualified agricultural expert should assess the crop before any chemical or fertilizer decision.", "sources": [], "uncertainty": SAFETY_NOTICE, "language": language, "crop": identify_crop(question), "safety_category": safety_category}
    parsed = parse_question(question)
    intent = classify_intent(question, parsed["symptom"])
    knowledge = load_knowledge()
    if parsed["symptom"] is None and intent in {"unknown", "general_crop_information"} and any("ಕ" <= character <= "ೞ" for character in parsed["normalized_text"]):
        return {"understanding": "ನಿಮ್ಮ ಟೊಮೆಟೋ ಗಿಡದ ಸಮಸ್ಯೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಇನ್ನಷ್ಟು ಮಾಹಿತಿ ಬೇಕಾಗಿದೆ.", "possible_explanations": [], "follow_up_questions": ["ಯಾವ ಭಾಗದಲ್ಲಿ ಸಮಸ್ಯೆ ಕಾಣಿಸುತ್ತಿದೆ?", "ಮಣ್ಣು ಒದ್ದೆಯೇ ಅಥವಾ ಒಣಗಿದೆಯೇ?", "ಎಲೆಗಳಲ್ಲಿ ಕಲೆ, ಕೀಟ ಅಥವಾ ಮುರುಕು ಕಾಣಿಸುತ್ತಿದೆಯೇ?", "ಎಷ್ಟು ಗಿಡಗಳಿಗೆ ಈ ಸಮಸ್ಯೆ ಇದೆ?"], "safe_actions": ["ಲಕ್ಷಣಗಳನ್ನು ಗಮನಿಸಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾದ ಫೋಟೋಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.", "ಖಚಿತ ಕಾರಣ ತಿಳಿಯುವವರೆಗೆ ಔಷಧಿ ಅಥವಾ ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣವನ್ನು ಬಳಸಬೇಡಿ."], "referral": "ಸಮಸ್ಯೆ ಹೆಚ್ಚಾದರೆ ಸ್ಥಳೀಯ ಕೃಷಿ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ.", "sources": [], "uncertainty": SAFETY_NOTICE, "language": language, "crop": identify_crop(question), "safety_category": None}
    matches = search(question, lu_result=lu_result)
    crop = identify_crop(question)
    if not matches:
        if not crop:
            return {"understanding": "I could not match this question to the current curated agricultural knowledge base.", "possible_explanations": [], "follow_up_questions": ["Which crop, market, or location should I use?" if intent in {"market_price", "weather"} else "Which crop and symptom are you observing?"], "safe_actions": ["Please provide the crop and location so the relevant service or source can be selected."], "referral": "Please consult a qualified local agricultural officer for crop-specific guidance when the question concerns plant health.", "sources": [], "uncertainty": SAFETY_NOTICE, "language": language, "crop": None, "intent": intent}
        missing = [] if crop else ["Which crop are you observing?"]
        if intent in {"market_price", "weather"}:
            return {"understanding": f"I recognized {crop} and a {intent.replace('_', ' ')} question. This should be handled by the corresponding live service, not disease retrieval.", "possible_explanations": [], "follow_up_questions": ["Which state and market should I use?" if intent == "market_price" else "Which farm location should I use?"], "safe_actions": [], "referral": "", "sources": [], "uncertainty": "No live service result is available in this response.", "language": language, "crop": crop, "intent": intent, "safety_category": None}
        return {"understanding": f"I recognized {crop} and a {intent.replace('_', ' ')} question, but the curated knowledge base has no verified record for this topic yet.", "possible_explanations": [], "follow_up_questions": ["Do you want guidance on planting, nursery/propagation, irrigation, soil preparation, or improving yield?"], "safe_actions": ["Please share the variety, growth stage, location, and current practice so a suitable verified source can be selected."], "referral": "Please consult a qualified local agricultural extension officer for crop-specific cultivation guidance.", "sources": [], "uncertainty": "No verified cultivation record matched; this is not a diagnosis.", "language": language, "crop": crop, "intent": intent, "safety_category": None}
        return {"understanding": f"I recognized {crop or 'the crop'} and the reported observation, but no verified guidance record matched yet.", "possible_explanations": [], "follow_up_questions": missing + ["Which plant part is affected, and how long has this been happening?"], "safe_actions": ["Record the affected plant part, crop age, recent weather, irrigation and spread before changing treatment."], "referral": "Please consult a qualified local agricultural officer for crop-specific guidance.", "sources": [], "uncertainty": SAFETY_NOTICE, "language": language, "crop": crop}
    cultivation_intents = {"cultivation", "propagation", "productivity", "irrigation", "soil", "general_crop_information", "harvest", "maintenance", "seed_selection"}
    if intent in cultivation_intents:
        guidance_items = [m.record for m in matches[:3] if m.record.get("intent") == intent]
        if intent == "cultivation" and crop:
            order = {"cultivation": 0, "seed_selection": 1, "soil": 2, "planting": 3, "irrigation": 4, "maintenance": 5, "productivity": 6, "harvest": 7}
            guidance_items = sorted(
                [r for r in knowledge.get("entries", []) if r.get("crop") == crop and r.get("category") == "cultivation_guidance"],
                key=lambda r: order.get(r.get("intent"), 99),
            )
        if guidance_items:
            steps = []
            sources = []
            for record in guidance_items:
                for step in record.get("practical_steps", []):
                    if step not in steps:
                        steps.append(step)
                source = record.get("source", {})
                if source and source not in sources:
                    sources.append(source)
            follow_up = next((q for record in guidance_items for q in record.get("follow_up_questions", [])), "Which variety, crop stage and local soil conditions apply to your field?")
            intro = next((record.get("description_en") for record in guidance_items if record.get("description_en")), f"Here is source-backed {intent.replace('_', ' ')} guidance for {crop}.")
            return {"understanding": intro, "possible_explanations": [], "follow_up_questions": [follow_up], "safe_actions": steps[:8], "referral": "", "sources": sources, "uncertainty": "General guidance; verify variety, season, soil test and local conditions before making input decisions.", "language": language, "crop": crop, "intent": intent, "safety_category": None}
    explanations, safe_actions, sources = [], [], []
    for match in matches[:3]:
        record = match.record
        for value in record.get("possible_causes", []):
            if value not in explanations: explanations.append(value)
        for value in record.get("safe_initial_actions", []):
            if value not in safe_actions: safe_actions.append(value)
        source = record.get("source", {})
        if source and source not in sources: sources.append(source)
    return {"understanding": f"Your question appears related to {crop} crop information in the curated knowledge base. The observed symptom is not a confirmed diagnosis.", "possible_explanations": explanations[:6], "follow_up_questions": _questions(matches), "safe_actions": safe_actions[:5], "referral": "Seek a qualified local agricultural expert if symptoms are spreading, plants are wilting rapidly, or the cause remains unclear.", "sources": sources, "uncertainty": SAFETY_NOTICE, "language": language, "crop": crop, "intent": intent, "safety_category": None}


def get_answer(question: str, language: str = "English") -> str:
    guidance = build_guidance(question, language)
    lines = [f"**Understanding**\n{guidance['understanding']}\n"]
    if guidance["possible_explanations"]:
        lines.append("**Possible explanations (not a diagnosis)**\n" + "\n".join(f"- {item}" for item in guidance["possible_explanations"]))
    if guidance["follow_up_questions"]:
        lines.append("**Clarification questions**\n" + "\n".join(f"- {item}" for item in guidance["follow_up_questions"]))
    if guidance["safe_actions"]:
        action_lines = (
            "\n".join(f"{index}. {item}" for index, item in enumerate(guidance["safe_actions"], 1))
            if guidance.get("intent") in {"cultivation", "propagation", "productivity", "irrigation", "soil", "general_crop_information", "harvest", "maintenance", "seed_selection"}
            else "\n".join(f"- {item}" for item in guidance["safe_actions"])
        )
        lines.append("**Practical steps**\n" + action_lines if guidance.get("intent") in {"cultivation", "propagation", "productivity", "irrigation", "soil", "general_crop_information", "harvest", "maintenance", "seed_selection"} else "**Safe initial actions**\n" + action_lines)
    if guidance.get("referral"):
        lines.append(f"**When to seek help**\n{guidance['referral']}")
    if guidance.get("uncertainty"):
        lines.append(f"**Safety and uncertainty**\n{guidance['uncertainty']}")
    if guidance["sources"]:
        lines.append("**Sources**\n" + "\n".join(f"- {source['title']} — {source['organization']} ({source['url']})" for source in guidance["sources"]))
    return "\n".join(lines)
