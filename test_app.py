"""Tests for the personal assistant web application."""

import json
import unittest
from io import BytesIO

from app import app, assistant_reply


def request(path, method="GET", body=b""):
    """Call the WSGI app and return its status, headers, and response bytes."""
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "CONTENT_LENGTH": str(len(body)),
        "PATH_INFO": path,
        "REQUEST_METHOD": method,
        "wsgi.input": BytesIO(body),
    }
    return captured, b"".join(app(environ, start_response))


class PersonalAssistantTests(unittest.TestCase):
    """Verify the chat page and API endpoint."""

    def test_home_page_contains_chat_interface(self):
        """The home page provides a history area, input, and send button."""
        captured, body = request("/")
        page = body.decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(captured["headers"]["Content-Type"], "text/html; charset=utf-8")
        self.assertIn("Personal AI Assistant", page)
        self.assertIn('id="history"', page)
        self.assertIn('id="message"', page)
        self.assertIn("Send</button>", page)

    def test_chat_endpoint_returns_assistant_reply(self):
        """A submitted message returns a JSON assistant response."""
        payload = json.dumps({"message": "Hello"}).encode("utf-8")
        captured, body = request("/chat", "POST", payload)

        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(captured["headers"]["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), {"reply": "Hello! How can I help you today?"})

    def test_assistant_reply_handles_empty_message(self):
        """The assistant offers guidance when it receives an empty message."""
        self.assertIn("Please enter a message", assistant_reply("  "))
