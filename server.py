"""
FIT2179 A2 — Development Server (No Cache)
Run from your repo root: python server.py

Serves files on http://localhost:8000
Sets Cache-Control: no-cache, no-store on every response
so F5 always fetches the latest version of every file.

Use this during development. For production (GitHub Pages),
caching is handled by GitHub — this script is dev-only.
"""

import http.server
import socketserver

PORT = 8000


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        # Only log non-200/304 responses to keep terminal clean
        code = args[1] if len(args) > 1 else ""
        if code not in ("200", "304"):
            super().log_message(format, *args)
        else:
            print(f"  {args[0]}  →  {args[1]}")


with socketserver.TCPServer(("", PORT), NoCacheHandler) as httpd:
    print(f"Dev server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")