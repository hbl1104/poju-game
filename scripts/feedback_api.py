#!/usr/bin/env python3
"""
破局游戏反馈API服务器
接收前端反馈并保存到本地，同时尝试同步到飞书
"""

import json
import os
import sys
from datetime import datetime
from urllib import request, parse
from http.server import HTTPServer, BaseHTTPRequestHandler

FEEDBACK_FILE = os.path.expanduser("~/.hermes/scripts/poju_feedback.json")

# CORS headers
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
}


class FeedbackHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
    
    def do_POST(self):
        if self.path != '/api/feedback':
            self.send_response(404)
            self.end_headers()
            return
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            feedback = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            for key, value in CORS_HEADERS.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return
        
        # 保存到本地
        feedbacks = []
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            except:
                pass
        
        feedbacks.append(feedback)
        
        try:
            with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.send_response(500)
            for key, value in CORS_HEADERS.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
        
        # 返回成功
        self.send_response(200)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps({"success": True}).encode())
    
    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")


def run_server(port=8787):
    server = HTTPServer(('0.0.0.0', port), FeedbackHandler)
    print(f"Feedback API server running on port {port}")
    print(f"Endpoint: http://localhost:{port}/api/feedback")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    run_server(port)
