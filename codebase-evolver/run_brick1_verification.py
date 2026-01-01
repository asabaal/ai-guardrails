#!/usr/bin/env python3
"""
Minimal local runner for Brick 1 verification UI

This script provides a simple HTTP API for the verification UI to call
the start_daemon function interactively.
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_agent.oracle.pyright_daemon import start_daemon


class Brick1Handler(BaseHTTPRequestHandler):
    """HTTP request handler for start_daemon brick verification."""

    def log_message(self, format, *args):
        """Suppress default logging to keep output clean."""

    def do_POST(self):
        """Handle POST requests to start_daemon API endpoint."""
        if self.path == '/api/brick/start_daemon':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)

                # Parse JSON
                data = json.loads(post_data.decode('utf-8'))
                repo_path = data.get('repo_path')
                port = data.get('port')

                # Validate inputs
                if not repo_path or not port:
                    self._send_json_response({
                        'success': False,
                        'error': 'Missing required fields: repo_path and port'
                    })
                    return

                # Call start_daemon function
                result = start_daemon(repo_path, port)

                # Format response (convert process to dict)
                response_data = {
                    'success': True,
                    'result': {
                        'pid': result.pid,
                        'port': result.port,
                        'process_info': f"Popen(pid={result.pid})"
                    }
                }

                # Cleanup: Stop the daemon after 5 seconds for verification
                import time
                time.sleep(5)
                result.process.kill()
                result.process.wait()

                self._send_json_response(response_data)

            except ValueError as e:
                self._send_json_response({
                    'success': False,
                    'error': f'Validation error: {str(e)}'
                })
            except RuntimeError as e:
                self._send_json_response({
                    'success': False,
                    'error': f'Runtime error: {str(e)}'
                })
            except Exception as e:
                self._send_json_response({
                    'success': False,
                    'error': f'Unexpected error: {str(e)}'
                })
        else:
            self._send_error(404, 'Not Found')

    def do_GET(self):
        """Serve the HTML verification UI."""
        if self.path == '/' or self.path == '/index.html':
            # Read and serve the HTML file
            ui_path = os.path.join(
                os.path.dirname(__file__),
                'verification_ui',
                'brick1_start_daemon.html'
            )
            try:
                with open(ui_path, 'r') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self._send_error(404, 'HTML file not found')
        else:
            self._send_error(404, 'Not Found')

    def _send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error(self, code, message):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': False,
            'error': message
        }).encode('utf-8'))


def main():
    """Start the local verification UI server."""
    port = 8765

    print(f"Starting Brick 1 verification UI server on port {port}...")
    print(f"Open http://localhost:{port}/ in your browser to verify start_daemon()")
    print("Press Ctrl+C to stop the server.")

    try:
        server = HTTPServer(('localhost', port), Brick1Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
