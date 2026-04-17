"""
Vercel Serverless Function — Forged Wheels API
Handles /api/* routes on Vercel deployment.
"""

import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler

WHEELS_DIR = Path(__file__).parent.parent / "wheels"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path

        if path == "/api/health":
            fal_key = os.environ.get("FAL_KEY", "")
            self._json_response({
                "status": "ok",
                "version": "0.1.0",
                "ai_enabled": bool(fal_key),
                "fal_key_length": len(fal_key),
                "fal_key_has_colon": ":" in fal_key,
                "fal_key_preview": fal_key[:8] + "..." + fal_key[-4:] if len(fal_key) > 12 else "",
                "catalog_size": self._get_catalog_size(),
                "platform": "vercel"
            })

        elif path.startswith("/api/wheels"):
            self._handle_wheels(path)

        else:
            self._json_response({"error": "Not found"}, 404)

    def _handle_wheels(self, path):
        catalog_path = WHEELS_DIR / "catalog.json"
        if not catalog_path.exists():
            self._json_response({"error": "Catalog not found"}, 404)
            return

        with open(catalog_path) as f:
            wheels = json.load(f)

        # Parse query params
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(path)
        params = parse_qs(parsed.query)

        # /api/wheels/categories/list
        if "/categories/list" in path:
            categories = {}
            for w in wheels:
                cat = w.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
            self._json_response({"categories": categories})
            return

        # /api/wheels/{id}
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 3 and parts[2]:
            wheel_id = parts[2]
            for w in wheels:
                if w["id"] == wheel_id:
                    self._json_response(w)
                    return
            self._json_response({"error": f"Wheel {wheel_id} not found"}, 404)
            return

        # /api/wheels with filters
        category = params.get("category", [None])[0]
        pcd = params.get("pcd", [None])[0]
        size = params.get("size", [None])[0]

        if category:
            wheels = [w for w in wheels if w.get("category") == category]
        if pcd:
            wheels = [w for w in wheels if pcd in w.get("pcd", [])]
        if size:
            wheels = [w for w in wheels if size in w.get("sizes", [])]

        self._json_response({"total": len(wheels), "wheels": wheels})

    def _get_catalog_size(self):
        catalog_path = WHEELS_DIR / "catalog.json"
        if catalog_path.exists():
            with open(catalog_path) as f:
                return len(json.load(f))
        return 0

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
