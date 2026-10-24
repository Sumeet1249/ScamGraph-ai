"""
Audit script: Maps all backend endpoints, ML models, and datasets against the frontend.
"""

import ast
import os
import re
from pathlib import Path

ROOT = Path(".")

# 1. Inspect all endpoints in services/api/app/api/v1/endpoints
endpoint_files = list(Path("services/api/app/api/v1/endpoints").glob("*.py"))
endpoint_routes = []

for ep in endpoint_files:
    if ep.name == "__init__.py":
        continue
    content = ep.read_text(encoding="utf-8")
    # find router decorators like @router.get(...), @router.post(...)
    matches = re.findall(r'@router\.(get|post|put|delete|patch)\(\s*["\']([^"\']*)["\']', content)
    for method, path in matches:
        endpoint_routes.append({
            "file": str(ep),
            "module": ep.stem,
            "method": method.upper(),
            "path": path,
        })

print(f"Total backend endpoint routes discovered: {len(endpoint_routes)}")

# 2. Inspect all frontend API calls in apps/web
frontend_calls = set()
for f in Path("apps/web").rglob("*.*"):
    if f.suffix in [".ts", ".tsx", ".js", ".jsx"]:
        if "node_modules" in str(f) or ".next" in str(f):
            continue
        try:
            txt = f.read_text(encoding="utf-8")
            # find fetch calls or axios or api endpoints
            found = re.findall(r'/api/v1/[a-zA-Z0-9_\-\/]+', txt)
            for item in found:
                # clean up trailing quotes or braces
                item = item.split("?")[0].split("$")[0].rstrip("`'\"}")
                frontend_calls.add(item)
        except Exception:
            pass

print(f"Total unique frontend API paths called: {len(frontend_calls)}")
print("Frontend paths called:", sorted(list(frontend_calls)))

# 3. Inspect ML models in ml/
ml_files = list(Path("ml").rglob("*.py"))
print(f"Total ML files in ml/: {len(ml_files)}")

# 4. Inspect services/
service_dirs = [d.name for d in Path("services").iterdir() if d.is_dir() and not d.name.startswith("__")]
print("Service directories:", service_dirs)

# 5. Inspect datasets in data/
data_dirs = [d.name for d in Path("data").iterdir() if d.is_dir() and not d.name.startswith("__")]
print("Data directories:", data_dirs)
