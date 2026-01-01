#!/usr/bin/env python3
"""
Minimal local runner for Brick 2 verification UI

This script provides a simple HTTP API for verification UI to call
the stop_daemon function interactively.
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_agent.oracle.pyright_daemon import start_daemon, stop_daemon, PyrightProcess

# Store running daemons (indexed by port)
running_daemons = {}


class Brick2Handler(BaseHTTPRequestHandler):
    """HTTP request handler for stop_daemon brick verification."""

    def log_message(self, format, *args):
        """Suppress default logging to keep output clean."""

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/brick/start_daemon_for_stop':
            return self._handle_start_daemon()
        elif self.path == '/api/brick/stop_daemon':
            return self._handle_stop_daemon()
        else:
            self._send_error(404, 'Not Found')

    def _handle_start_daemon(self):
        """Handle start_daemon API endpoint."""
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
            process = start_daemon(repo_path, port)

            # Store daemon for later stopping
            running_daemons[port] = process

            # Format response
            response_data = {
                'success': True,
                'result': {
                    'pid': process.pid,
                    'port': process.port,
                    'process_info': f"Popen(pid={process.pid})"
                }
            }

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

    def _handle_stop_daemon(self):
        """Handle stop_daemon API endpoint."""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Parse JSON
            data = json.loads(post_data.decode('utf-8'))
            pid = data.get('pid')

            # Validate inputs
            if not pid:
                self._send_json_response({
                    'success': False,
                    'error': 'Missing required field: pid'
                })
                return

            # Find daemon by PID (search all running daemons)
            process = None
            for p in running_daemons.values():
                if p.pid == pid:
                    process = p
                    break

            if not process:
                self._send_json_response({
                    'success': False,
                    'error': f'No running daemon found with PID {pid}'
                })
                return

            # Call stop_daemon function
            stop_daemon(process)

            # Remove from running daemons
            for port, p in list(running_daemons.items()):
                if p.pid == pid:
                    del running_daemons[port]
                    break

            # Format response
            response_data = {
                'success': True,
                'result': {
                    'pid': pid,
                    'status': 'stopped'
                }
            }

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

    def do_GET(self):
        """Serve HTML verification UI."""
        if self.path == '/' or self.path == '/index.html':
            # Read and serve HTML file
            ui_path = os.path.join(
                os.path.dirname(__file__),
                'verification_ui',
                'brick2_stop_daemon.html'
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
    """Start local verification UI server."""
    port = 8766

    print(f"Starting Brick 2 verification UI server on port {port}...")
    print(f"Open http://localhost:{port}/ in your browser to verify stop_daemon()")
    print("Press Ctrl+C to stop server.")

    try:
        server = HTTPServer(('localhost', port), Brick2Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
