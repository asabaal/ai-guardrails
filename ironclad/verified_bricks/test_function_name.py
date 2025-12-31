import pytest
import socket
import threading
import http.server
import time

from function_name import get_http_status

# Helper to find a free port

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

# Simple request handler that always returns 200 OK
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

# Request handler that delays before responding (to trigger timeout)
class DelayedHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        time.sleep(10)  # sleep longer than the 5s timeout
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Delayed OK")

# Context manager to run a server in a background thread
class ServerThread(threading.Thread):
    def __init__(self, handler_class, port):
        super().__init__()
        self.daemon = True
        self.port = port
        self.handler_class = handler_class
        self.server = http.server.HTTPServer(("", self.port), self.handler_class)

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

@pytest.fixture
def simple_server():
    port = find_free_port()
    server_thread = ServerThread(SimpleHandler, port)
    server_thread.start()
    time.sleep(0.1)  # give the server a moment to start
    yield f"http://localhost:{port}"
    server_thread.stop()

@pytest.fixture
def delayed_server():
    port = find_free_port()
    server_thread = ServerThread(DelayedHandler, port)
    server_thread.start()
    time.sleep(0.1)
    yield f"http://localhost:{port}"
    server_thread.stop()

def test_valid_url(simple_server):
    status = get_http_status(simple_server)
    assert status == 200

def test_invalid_url():
    # Use a port where no server is listening
    port = find_free_port()
    url = f"http://localhost:{port}"
    status = get_http_status(url)
    assert status is None

def test_empty_url():
    status = get_http_status("")
    assert status is None

def test_timeout(delayed_server):
    status = get_http_status(delayed_server)
    assert status is None
