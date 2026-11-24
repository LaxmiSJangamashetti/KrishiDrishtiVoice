"""Deterministic conversation orchestration for farmer investigations.

This module coordinates the existing LU, safety, retrieval, and guidance layers.
It does not diagnose disease or generate agricultural facts.
"""
from dataclasses import asdict, dataclass, field
import re
from typing import Any
from uuid import uuid4

from agriculture_engine import build_guidance
from language_understanding import understand
from market_service import is_market_query


@dataclass
class ConversationState:
    session_id: str = field(default_factory=lambda: f"conv-{uuid4().hex[:12]}")
    turn_number: int = 0
    messages: list[dict[str, Any]] = field(default_factory=list)
    observations: dict[str, dict[str, Any]] = field(default_factory=dict)
    observation_history: list[dict[str, Any]] = field(default_factory=list)
    asked_questions: list[str] = field(default_factory=list)
    answered_questions: list[dict[str, Any]] = field(default_factory=list)
    pending_question: dict[str, Any] | None = None
    safety_flags: list[str] = field(default_factory=list)
    completed: bool = False
    profile_context: dict[str, Any] = field(default_factory=dict)


FOLLOW_UPS = (
    ("soil_condition", "Is the soil staying wet, or is it dry?", ("waterlogging", "water_stress", "leaf_yellowing", "wilting")),
    ("duration", "How long has this problem been happening?", ("leaf_yellowing", "wilting", "brown_spots", "leaf_curling", "fruit_damage")),
    ("spread", "Is the problem affecting one plant or many plants?", ("leaf_yellowing", "wilting", "brown_spots", "leaf_curling", "fruit_damage")),
    ("plant_part", "Which plant part is affected: leaves, stem, flowers, or fruit?", ("fruit_damage", "insects")),
    ("insects", "Are you seeing insects under the leaves or on the plant?", ("leaf_yellowing", "leaf_curling", "insects")),
)


def new_conversation() -> ConversationState:
    return ConversationState()


def _context_answer(text: str) -> dict[str, str]:
    normalized = text.casefold()
    answers: dict[str, str] = {}
    if re.search(r"older|old leaves|ಕೆಳಗಿನ ಎಲೆ|ಹಳೆಯ ಎಲೆ", normalized):
        answers["leaf_age"] = "older leaves"
    elif re.search(r"new leaves|ನতুন ಎಲೆ|ಮೇಲಿನ ಎಲೆ|ಹೊಸ ಎಲೆ", normalized):
        answers["leaf_age"] = "new leaves"
    if re.search(r"one plant|ಒಂದು ಗಿಡ", normalized):
        answers["spread"] = "one plant"
    elif re.search(r"many|all plants|ಹಲವು ಗಿಡ|ಎಲ್ಲಾ ಗಿಡ", normalized):
        answers["spread"] = "many plants"
    if re.search(r"wet|ಒದ್ದೆ|ನೀರು ನಿಂತ", normalized):
        answers["soil_condition"] = "wet"
    elif re.search(r"dry|ಒಣ ಮಣ್ಣು|ಒಣಗಿದ", normalized):
        answers["soil_condition"] = "dry"
    duration = re.search(r"(\d+)\s*(day|days|ದಿನ|ವಾರ|week|weeks)", normalized)
    if duration:
        answers["duration"] = duration.group(0)
    return answers


def _question_for(state: ConversationState, observations: list[dict[str, Any]]) -> dict[str, Any] | None:
    values = {o.get("normalized_value") for o in observations if o.get("polarity") == "present"}
    answered = {item.get("field") for item in state.answered_questions}
    for field_name, question, relevant_values in FOLLOW_UPS:
        if field_name in answered or field_name in state.asked_questions:
            continue
        if values.intersection(relevant_values):
            return {"id": f"q-{state.turn_number + 1:02d}-{field_name}", "field": field_name, "text": question, "reason": "This detail can distinguish the next safe investigation step."}
    return None


def _merge_observations(state: ConversationState, incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active = dict(state.observations)
    for observation in incoming:
        value = observation.get("normalized_value")
        if observation.get("kind") == "crop":
            active[observation["observation_id"]] = observation
            continue
        if observation.get("polarity") == "absent":
            for old_id, old in list(active.items()):
                if old.get("normalized_value") == value and old.get("polarity") == "present":
                    old = {**old, "validity": "superseded", "relationship": "corrected_by", "references": [observation["observation_id"]]}
                    state.observation_history.append(old)
                    active.pop(old_id, None)
            active[observation["observation_id"]] = observation
        elif observation.get("polarity") == "present":
            active[observation["observation_id"]] = observation
    state.observations = active
    return list(active.values())


def process_turn(state: ConversationState, text: str, language: str = "English", profile_context: dict[str, Any] | None = None) -> dict[str, Any]:
    if state.completed:
        return {"state": state, "response": _response("This conversation is complete. Start a new conversation to investigate another issue.", state, None, None)}
    cleaned = text.strip() if isinstance(text, str) else ""
    if not cleaned:
        return {"state": state, "response": _response("Please describe what you are observing on the crop.", state, None, None)}
    state.turn_number += 1
    if profile_context is not None:
        state.profile_context = {
            "registered_crops": list(profile_context.get("registered_crops", [])),
            "preferred_language": profile_context.get("preferred_language"),
            "soil_type": profile_context.get("soil_type"),
            "irrigation_type": profile_context.get("irrigation_type"),
            "environmental_observations": list(profile_context.get("environmental_observations", [])),
            "requires_crop_confirmation": len(profile_context.get("registered_crops", [])) != 1,
        }
    state.messages.append({"role": "farmer", "text": cleaned, "turn": state.turn_number})
    answers = _context_answer(cleaned)
    for field_name, answer in answers.items():
        state.answered_questions.append({"field": field_name, "answer": answer, "turn": state.turn_number})
    if state.pending_question:
        pending_field = state.pending_question.get("field")
        if pending_field in answers:
            state.pending_question = None
        elif re.search(r"don't know|do not know| ಗೊತ್ತಿಲ್ಲ|ತಿಳಿದಿಲ್ಲ", cleaned.casefold()):
            state.answered_questions.append({"field": pending_field, "answer": "unknown", "turn": state.turn_number})
            state.pending_question = None
    lu = understand(cleaned, message_id=f"{state.session_id}-m{state.turn_number}")
    if is_market_query(cleaned):
        state.profile_context["last_intent"] = "market_price"
    state.safety_flags = sorted(set(state.safety_flags).union(lu.get("lu_safety_flags", [])))
    active = _merge_observations(state, lu.get("observations", []))
    current_lu = {**lu, "observations": active, "lu_safety_flags": state.safety_flags}
    question = None if state.pending_question else _question_for(state, active)
    if question:
        state.pending_question = question
        state.asked_questions.append(question["field"])
    guidance = build_guidance(cleaned, language, lu_result=current_lu)
    response = _response(None, state, guidance, question)
    state.messages.append({"role": "assistant", "text": response["acknowledgement"], "turn": state.turn_number})
    return {"state": state, "response": response, "lu": current_lu, "guidance": guidance}


def _response(message: str | None, state: ConversationState, guidance: dict[str, Any] | None, question: dict[str, Any] | None) -> dict[str, Any]:
    if message:
        return {"acknowledgement": message, "reported_observations": [], "understood_observations": [], "possible_explanations": [], "follow_up_question": None, "guidance": None, "safety": state.safety_flags, "uncertainty": "Information is insufficient for agricultural guidance."}
    observations = list(state.observations.values())
    if guidance and guidance.get("safety_category"):
        acknowledgement = "I cannot provide that unsafe recommendation."
    elif question:
        acknowledgement = "I have recorded what you reported. I need one more detail before narrowing the agricultural information."
    else:
        acknowledgement = "I have recorded your observations."
    return {"acknowledgement": acknowledgement, "reported_observations": observations, "understood_observations": observations, "possible_explanations": (guidance or {}).get("possible_explanations", []), "follow_up_question": question, "guidance": guidance, "safety": state.safety_flags, "uncertainty": (guidance or {}).get("uncertainty", "More information may be needed; this is not a diagnosis."), "profile_context": state.profile_context, "intent": state.profile_context.get("last_intent")}


def state_as_dict(state: ConversationState) -> dict[str, Any]:
    return asdict(state)
