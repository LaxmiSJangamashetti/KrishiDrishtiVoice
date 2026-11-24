import unittest

from conversation_manager import new_conversation, process_turn, state_as_dict


class ConversationManagerTests(unittest.TestCase):
    def test_creation_and_turn_persistence(self):
        state = new_conversation()
        result = process_turn(state, "My tomato leaves are turning yellow")
        self.assertEqual(state.turn_number, 1)
        self.assertTrue(result["response"]["reported_observations"])
        self.assertEqual(state_as_dict(state)["session_id"], state.session_id)

    def test_follow_up_answer_is_recorded_without_repeating_question(self):
        state = new_conversation()
        first = process_turn(state, "My tomato leaves are turning yellow")
        asked = first["response"]["follow_up_question"]
        self.assertIsNotNone(asked)
        process_turn(state, "Mostly the older leaves")
        self.assertTrue(any(item["field"] == "leaf_age" for item in state.answered_questions))
        self.assertNotEqual(state.pending_question and state.pending_question["field"], "leaf_age")

    def test_new_symptom_is_added(self):
        state = new_conversation()
        process_turn(state, "My tomato leaves are yellow")
        process_turn(state, "The leaves are also drying")
        values = {o["normalized_value"] for o in state.observations.values()}
        self.assertIn("leaf_yellowing", values)
        self.assertIn("wilting", values)

    def test_correction_supersedes_only_target(self):
        state = new_conversation()
        process_turn(state, "My tomato leaves are yellow")
        process_turn(state, "The leaves are not yellow but are curling")
        active = {o["normalized_value"]: o for o in state.observations.values()}
        self.assertEqual(active["leaf_yellowing"]["polarity"], "absent")
        self.assertEqual(active["leaf_curling"]["polarity"], "present")

    def test_safety_blocks_normal_guidance(self):
        result = process_turn(new_conversation(), "What pesticide dose should I use for tomato?")
        self.assertTrue(result["response"]["safety"])
        self.assertEqual(result["guidance"]["sources"], [])

    def test_empty_and_completed_state_are_safe(self):
        state = new_conversation()
        result = process_turn(state, "")
        self.assertIsNone(result.get("guidance"))
        state.completed = True
        result = process_turn(state, "another question")
        self.assertIn("complete", result["response"]["acknowledgement"])

    def test_new_conversation_is_isolated(self):
        first = new_conversation()
        process_turn(first, "My tomato leaves are yellow")
        second = new_conversation()
        self.assertNotEqual(first.session_id, second.session_id)
        self.assertEqual(second.turn_number, 0)
        self.assertEqual(second.observations, {})
        self.assertIsNone(second.pending_question)

    def test_profile_context_is_metadata_not_an_observation(self):
        state = new_conversation()
        result = process_turn(state, "My leaves are curling", profile_context={"registered_crops": ["Tomato"], "soil_type": "Loam"})
        self.assertEqual(result["response"]["profile_context"]["registered_crops"], ["Tomato"])
        self.assertFalse(any(o.get("kind") == "crop" for o in result["response"]["reported_observations"]))
        self.assertTrue(state.profile_context["requires_crop_confirmation"] is False)

    def test_multiple_profile_crops_require_confirmation(self):
        state = new_conversation()
        result = process_turn(state, "The leaves are curling", profile_context={"registered_crops": ["Tomato", "Rice"]})
        self.assertTrue(result["response"]["profile_context"]["requires_crop_confirmation"])

    def test_market_intent_routes_through_conversation_manager(self):
        result = process_turn(new_conversation(), "What is today's tomato market price in Karnataka?")
        self.assertEqual(result["response"]["intent"], "market_price")

    def test_environment_observations_are_context_only(self):
        result = process_turn(new_conversation(), "My tomato leaves are yellow", profile_context={"registered_crops": ["Tomato"], "environmental_observations": [{"source": "AgroMonitoring", "kind": "weather", "data": {"dt": 123}}]})
        self.assertEqual(result["response"]["profile_context"]["environmental_observations"][0]["source"], "AgroMonitoring")
        self.assertFalse(any(o.get("kind") == "weather" for o in result["response"]["reported_observations"]))


if __name__ == "__main__":
    unittest.main()
