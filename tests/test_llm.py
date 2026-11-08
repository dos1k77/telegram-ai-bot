import io
import json
import os
import unittest
from unittest import mock

import llm


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class LLMTests(unittest.TestCase):
    def test_parses_reply(self):
        payload = {"candidates": [{"content": {"parts": [{"text": "Сәлем"}, {"text": "!"}]}}]}
        fake = FakeResponse(json.dumps(payload).encode())
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "x"}), \
             mock.patch("urllib.request.urlopen", return_value=fake):
            self.assertEqual(llm.ask("hi"), "Сәлем!")

    def test_missing_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(llm.LLMError):
                llm.ask("hi")

    def test_bad_response(self):
        fake = FakeResponse(json.dumps({"error": "x"}).encode())
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "x"}), \
             mock.patch("urllib.request.urlopen", return_value=fake):
            with self.assertRaises(llm.LLMError):
                llm.ask("hi")


if __name__ == "__main__":
    unittest.main()
