"""Export the FastAPI OpenAPI spec to openapi.json (committed, per the plan).

Run from apps/api:  python scripts/export_openapi.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
spec = app.openapi()
for path in (os.path.join(ROOT, "openapi.json"), os.path.join(ROOT, "apps", "api", "openapi.json")):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2)
    print(f"Wrote {path} ({len(spec['paths'])} paths)")
