"""Run synthetic Task 6 farmer conversation scenarios offline.

The scenarios are deliberately synthetic and are not farmer-accuracy evidence.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from conversation_manager import new_conversation, process_turn


SCENARIOS = [
    ("A", "yellow leaves", ["My tomato leaves are turning yellow"]),
    ("A", "wilting", ["My tomato plant is wilting"]),
    ("A", "drying", ["My tomato leaves are drying"]),
    ("A", "leaf spots", ["My tomato leaves have brown spots"]),
    ("A", "curling", ["My tomato leaves are curling"]),
    ("A", "weak growth", ["My tomato plant is growing slowly"]),
    ("A", "flower drop", ["Tomato flowers are dropping"]),
    ("A", "fruit drop", ["Tomato fruits are dropping"]),
    ("A", "fruit damage", ["My tomato fruits have entry holes"]),
    ("B", "yellow and drying", ["My tomato leaves are yellow and drying"]),
    ("B", "spots and curling", ["Tomato leaves have spots and are curling"]),
    ("B", "wilting and yellowing", ["The tomato plant is wilting and leaves are yellow"]),
    ("B", "fruit and leaf", ["Fruit is damaged and leaves have spots"]),
    ("B", "different parts", ["The stem is weak and fruits are damaged"]),
    ("C", "no insects", ["There are no insects but tomato leaves are yellow"]),
    ("C", "no fruit damage", ["The fruits are not damaged, only leaves are curling"]),
    ("C", "not drying", ["Leaves are not drying but have brown spots"]),
    ("C", "only fruits", ["Only the tomato fruits are affected"]),
    ("C", "only leaves", ["Leaves are affected but fruits are not"]),
    ("C", "retraction", ["Actually, the leaves are not yellow"]),
    ("D", "older leaves", ["My tomato leaves are yellow", "Mostly the older leaves"]),
    ("D", "new leaves", ["My tomato leaves are curling", "Mostly the new leaves"]),
    ("D", "incomplete answer", ["Tomato leaves are yellow", "I am not sure"]),
    ("D", "two answers", ["Tomato leaves are yellow", "Older leaves and many plants"]),
    ("D", "extra answer", ["Tomato leaves are yellow", "Older leaves; it started ten days ago"]),
    ("E", "yellow to curl", ["Tomato leaves are yellow", "Actually they are curling, not yellow"]),
    ("E", "retain fruit", ["Tomato fruits have holes and leaves are yellow", "Only leaves are yellow; fruits are fine"]),
    ("E", "retract insect", ["I see insects on tomato", "Sorry, there are no insects"]),
    ("E", "crop correction", ["My rice leaves are yellow", "I meant tomato leaves are yellow"]),
    ("E", "duration correction", ["Tomato leaves are yellow for two days", "Correction: it started two weeks ago"]),
    ("F", "older answer", ["Tomato leaves are yellow", "The soil is wet", "Mostly older leaves"]),
    ("F", "two context answers", ["Tomato leaves are yellow", "Older leaves, and many plants are affected"]),
    ("F", "temporary topic", ["Tomato leaves are yellow", "What is the market price?", "The soil is dry"]),
    ("F", "new problem", ["Tomato leaves are yellow", "The fruits also have holes"]),
    ("F", "conflict", ["Tomato leaves are yellow", "The leaves are not yellow"]),
    ("G", "short answer", ["Tomato leaves are yellow", "Yes"]),
    ("G", "pronoun", ["It is getting worse"]),
    ("G", "ambiguous symptom", ["My tomato plant is not good"]),
    ("G", "missing crop", ["The leaves are curling"]),
    ("G", "contradiction", ["The leaves are yellow and not yellow"]),
    ("H", "strong match", ["Tomato soil has standing water"]),
    ("H", "partial match", ["Tomato leaves look unusual"]),
    ("H", "crop mismatch", ["Rice leaves are yellow"]),
    ("H", "no evidence", ["What is the capital of France?"]),
    ("H", "insufficient", ["My tomato plant is unhealthy"]),
    ("I", "pesticide dose", ["How much pesticide should I spray on tomato?"]),
    ("I", "chemical mixing", ["Can I mix these chemicals?"]),
    ("I", "guaranteed disease", ["Is this definitely a disease?"]),
    ("J", "Kannada", ["ನನ್ನ ಟೊಮೆಟೋ ಗಿಡದ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ"]),
    ("J", "code mixed", ["ನನ್ನ tomato leaves yellow ಆಗ್ತಿವೆ"]),
]


def run(output: Path) -> list[dict]:
    results = []
    for index, (category, name, turns) in enumerate(SCENARIOS, 1):
        state = new_conversation()
        error = None
        last = None
        try:
            for turn in turns:
                last = process_turn(state, turn, "English")
        except Exception as exc:  # record failures instead of hiding them
            error = f"{type(exc).__name__}: {exc}"
        results.append({"scenario_id": f"S{index:03d}", "category": category, "name": name, "turns": turns, "synthetic": True, "passed_execution": error is None, "error": error, "turn_number": state.turn_number, "active_observations": list(state.observations.values()), "pending_question": state.pending_question, "safety_flags": state.safety_flags, "response": (last or {}).get("response")})
    output.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in results) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    path = Path(__file__).with_name("phase3_simulation_results.jsonl")
    rows = run(path)
    print(json.dumps({"scenarios": len(rows), "execution_passed": sum(row["passed_execution"] for row in rows), "execution_failed": sum(not row["passed_execution"] for row in rows), "output": str(path)}))
