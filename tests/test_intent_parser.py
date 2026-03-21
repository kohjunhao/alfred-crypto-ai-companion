import unittest

from alfred_app.intent_parser import determine_intent


class IntentParserTests(unittest.TestCase):
    def test_price_query_detects_bitcoin(self):
        parsed = determine_intent("What is the price of Bitcoin?")
        self.assertEqual(parsed.intent, "price")
        self.assertEqual(parsed.entity, "bitcoin")
        self.assertTrue(parsed.needs_live_data)

    def test_tvl_query_detects_protocol(self):
        parsed = determine_intent("Show me the TVL of Aave.")
        self.assertEqual(parsed.intent, "tvl")
        self.assertEqual(parsed.entity, "aave")
        self.assertTrue(parsed.needs_live_data)

    def test_alias_resolution_handles_btc(self):
        parsed = determine_intent("btc price")
        self.assertEqual(parsed.intent, "price")
        self.assertEqual(parsed.entity, "bitcoin")

    def test_general_chat_falls_back(self):
        parsed = determine_intent("Hello Alfred")
        self.assertEqual(parsed.intent, "general_chat")
        self.assertFalse(parsed.needs_live_data)


if __name__ == "__main__":
    unittest.main()

