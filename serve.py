#!/usr/bin/env python3
"""Serve the notes viewer locally and rebuild the notes on every page refresh.

    python3 serve.py          # then open http://localhost:8000
    python3 serve.py 9000     # use another port

Edit any .md file in a notes/ folder, refresh the browser, and the change shows up.
"""
import http.server
import sys
import webbrowser
from functools import partial

from build_notes import ROOT, bundle


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/notes-data.js":
            body = bundle()[0].encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # always fetch fresh notes on refresh
        super().end_headers()

    def log_message(self, *args):
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT)))
    url = f"http://localhost:{port}"
    print(f"Notes viewer running at {url}  (Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
