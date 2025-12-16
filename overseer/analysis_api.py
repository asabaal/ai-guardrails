#!/usr/bin/env python3
"""
Simple API server for Overseer analysis engine
Provides endpoints for text analysis using the LLM segmenter
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from layer1_segmentation.text_segmenter import LLMTextSegmenter, Normalizer, Aggregator

class AnalysisAPI(BaseHTTPRequestHandler):
    """Simple HTTP API for text analysis"""
    
    def __init__(self, *args, **kwargs):
        self.segmenter = LLMTextSegmenter({
            'model_name': 'gpt-oss:20b',
            'max_retries': 2,
            'timeout': 60
        })
        self.normalizer = Normalizer()
        self.aggregator = Aggregator()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self._send_response(200, {'message': 'Overseer Analysis API', 'status': 'running'})
        elif parsed_path.path == '/health':
            self._send_response(200, {'status': 'healthy', 'timestamp': time.time()})
        else:
            self._send_response(404, {'error': 'Not found'})
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/analyze':
            self._handle_analyze()
        else:
            self._send_response(404, {'error': 'Not found'})
    
    def _handle_analyze(self):
        """Handle text analysis requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            if not text:
                self._send_response(400, {'error': 'Text is required'})
                return
            
            # Perform analysis
            segments = self.segmenter.segment(text)
            normalized_segments = self.normalizer.normalize(segments)
            
            # Create simple logic objects (basic implementation)
            logic_objects = self._create_logic_objects(normalized_segments)
            
            # Create evaluation (basic implementation)
            evaluation = self._create_evaluation(normalized_segments, logic_objects)
            
            result = {
                'segments': normalized_segments,
                'logic_objects': logic_objects,
                'evaluation': evaluation,
                'metadata': {
                    'model_used': 'gpt-oss:20b',
                    'timestamp': time.time(),
                    'segment_count': len(normalized_segments)
                }
            }
            
            self._send_response(200, result)
            
        except json.JSONDecodeError:
            self._send_response(400, {'error': 'Invalid JSON'})
        except Exception as e:
            self._send_response(500, {'error': str(e)})
    
    def _create_logic_objects(self, segments):
        """Create basic logic objects from segments"""
        logic_objects = []
        
        for i, segment in enumerate(segments):
            # Simple logic object creation
            obj = {
                'id': f'obj_{i+1}',
                'text': segment,
                'type': self._classify_statement_type(segment),
                'entities': self._extract_entities(segment),
                'confidence': 0.8  # Placeholder confidence
            }
            logic_objects.append(obj)
        
        return logic_objects
    
    def _classify_statement_type(self, segment):
        """Simple statement type classification"""
        segment_lower = segment.lower()
        
        if 'therefore' in segment_lower or 'thus' in segment_lower or 'hence' in segment_lower:
            return 'conclusion'
        elif 'if' in segment_lower and 'then' in segment_lower:
            return 'conditional'
        elif 'all' in segment_lower or 'every' in segment_lower:
            return 'generalization'
        else:
            return 'atomic_assertion'
    
    def _extract_entities(self, segment):
        """Simple entity extraction"""
        # Very basic entity extraction - just look for capitalized words
        import re
        words = re.findall(r'\b[A-Z][a-z]+\b', segment)
        return list(set(words))  # Remove duplicates
    
    def _create_evaluation(self, segments, logic_objects):
        """Create basic evaluation"""
        # Simple evaluation logic
        has_conclusion = any(obj['type'] == 'conclusion' for obj in logic_objects)
        has_premises = len([obj for obj in logic_objects if obj['type'] in ['atomic_assertion', 'generalization']]) > 0
        
        valid_reasoning = has_premises and has_conclusion
        
        # Simple severity assessment
        if not valid_reasoning:
            severity = 'major'
        elif len(segments) < 2:
            severity = 'minor'
        else:
            severity = 'none'
        
        return {
            'valid_reasoning': valid_reasoning,
            'severity': severity,
            'fallacies': [],
            'contradictions': [],
            'hidden_assumptions': []
        }
    
    def _send_response(self, status_code, data):
        """Send HTTP response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_server(port=8080):
    """Start the analysis API server"""
    server = HTTPServer(('localhost', port), AnalysisAPI)
    print(f"Overseer Analysis API running on http://localhost:{port}")
    print("Available endpoints:")
    print("  GET  /        - API status")
    print("  GET  /health  - Health check")
    print("  POST /analyze - Text analysis")
    print()
    print("Example usage:")
    print(f"  curl -X POST http://localhost:{port}/analyze -H 'Content-Type: application/json' -d '{{\"text\": \"Your text here\"}}'")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    start_server()