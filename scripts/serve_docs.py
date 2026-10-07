"""Serve the built bilingual documentation with its GitHub Pages URL prefix."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith("/testscript/"):
            path = path[len("/testscript") :]
        return super().translate_path(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not (ROOT / "site/index.html").exists():
        parser.error("Build documentation first: python scripts/build_docs.py")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT / "site")))
    print(f"TestScript documentation: http://127.0.0.1:{args.port}/testscript/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
