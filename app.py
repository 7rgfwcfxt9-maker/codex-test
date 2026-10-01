"""A simple, local personal-assistant web application."""

import json
from wsgiref.simple_server import make_server


def assistant_reply(message):
    """Generate a small local response without requiring an API key."""
    text = message.strip()
    if not text:
        return "Please enter a message and I will do my best to help."

    lowered = text.lower()
    if "hello" in lowered or "hi" in lowered:
        return "Hello! How can I help you today?"
    if "help" in lowered:
        return "I can help you think through tasks, make plans, and answer simple questions."
    if "thank" in lowered:
        return "You're welcome!"
    return f"I heard: {text}. What would you like to do next?"


def home_page():
    """Return the chat interface."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Personal AI Assistant</title>
  <style>
    body { background: #f4f7fb; color: #182230; font-family: system-ui, sans-serif; margin: 0; }
    main { display: flex; flex-direction: column; height: 100vh; margin: auto; max-width: 720px; }
    header { padding: 24px 20px 12px; }
    h1 { font-size: 1.5rem; margin: 0; }
    #history { display: flex; flex: 1; flex-direction: column; gap: 12px; overflow-y: auto; padding: 20px; }
    .message { border-radius: 16px; max-width: 75%; padding: 12px 16px; white-space: pre-wrap; }
    .assistant { align-self: flex-start; background: #ffffff; }
    .user { align-self: flex-end; background: #2563eb; color: #ffffff; }
    form { background: #ffffff; display: flex; gap: 8px; padding: 16px 20px; }
    input { border: 1px solid #cbd5e1; border-radius: 8px; flex: 1; font: inherit; padding: 10px; }
    button { background: #2563eb; border: 0; border-radius: 8px; color: #ffffff; font: inherit; padding: 10px 16px; }
  </style>
</head>
<body>
  <main>
    <header><h1>Personal AI Assistant</h1></header>
    <section id="history" aria-label="Message history">
      <div class="message assistant">Hello! I am your personal assistant. How can I help?</div>
    </section>
    <form id="chat-form">
      <input id="message" name="message" type="text" placeholder="Ask me anything..." autocomplete="off" required>
      <button type="submit">Send</button>
    </form>
  </main>
  <script>
    const form = document.querySelector('#chat-form');
    const input = document.querySelector('#message');
    const history = document.querySelector('#history');

    function addMessage(text, speaker) {
      const message = document.createElement('div');
      message.className = `message ${speaker}`;
      message.textContent = text;
      history.append(message);
      history.scrollTop = history.scrollHeight;
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      addMessage(text, 'user');
      input.value = '';
      input.focus();

      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await response.json();
      addMessage(data.reply, 'assistant');
    });
  </script>
</body>
</html>"""


def read_json(environ):
    """Read and decode a JSON request body."""
    try:
        length = int(environ.get("CONTENT_LENGTH", "0"))
    except ValueError:
        length = 0

    payload = environ["wsgi.input"].read(max(length, 0)).decode("utf-8")
    return json.loads(payload)


def respond(start_response, status, body, content_type):
    """Create a WSGI response with the supplied body and content type."""
    response = body.encode("utf-8")
    start_response(status, [("Content-Type", content_type), ("Content-Length", str(len(response)))])
    return [response]


def app(environ, start_response):
    """Serve the chat page and local assistant chat endpoint."""
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path == "/" and method == "GET":
        return respond(start_response, "200 OK", home_page(), "text/html; charset=utf-8")

    if path == "/chat" and method == "POST":
        try:
            message = read_json(environ).get("message", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            error = json.dumps({"error": "Send a JSON object with a message."})
            return respond(start_response, "400 Bad Request", error, "application/json; charset=utf-8")

        body = json.dumps({"reply": assistant_reply(str(message))})
        return respond(start_response, "200 OK", body, "application/json; charset=utf-8")

    return respond(start_response, "404 Not Found", "Not Found", "text/plain; charset=utf-8")


if __name__ == "__main__":
    with make_server("127.0.0.1", 5000, app) as server:
        print("Serving on http://127.0.0.1:5000")
        server.serve_forever()
