import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from planner_executor_loop import run_planner_executor_loop


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/', '/index.html', '/app.js'):
            file_path = Path('.') / ('index.html' if parsed.path in ('/', '/index.html') else 'app.js')
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html' if parsed.path in ('/', '/index.html') else 'application/javascript')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, 'Not found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/run-workflow':
            self.send_error(404, 'Not found')
            return

        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length)
        data = json.loads(raw.decode('utf-8')) if raw else {}

        try:
            result = asyncio.run(run_planner_executor_loop(data.get('scenario')))
            payload = json.dumps({
                "output": result["output"],
                "intermediate_steps": result["intermediate_steps"],
                "trace": result["trace"],
                "confidence": result["confidence"],
                "roi": result["roi"],
                "citations": result["citations"],
                "privacy": result["privacy"],
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except Exception as exc:
            payload = json.dumps({"error": str(exc)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 3000), Handler)
    print('BizBrain Advisor app is running at http://127.0.0.1:3000/')
    server.serve_forever()
