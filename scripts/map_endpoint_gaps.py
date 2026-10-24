"""
Deep analysis script to identify all disconnected or unshown backend endpoints, ML models, and datasets.
"""

import ast
import json
import os
import re
from pathlib import Path

# Load API router prefix mappings from services/api/app/api/v1/api.py
api_router_file = Path("services/api/app/api/v1/api.py").read_text(encoding="utf-8")
prefix_map = {}
# look for api_router.include_router(module.router, prefix="/prefix", tags=[...])
for line in api_router_file.splitlines():
    line = line.strip()
    if "include_router" in line:
        m = re.search(r'include_router\(([a-zA-Z0-9_\.]+)\.router(?:,\s*prefix="([^"]+)")?', line)
        if m:
            mod_name = m.group(1).split(".")[-1]
            pfx = m.group(2) or ""
            prefix_map[mod_name] = pfx

print("Router Prefixes:", prefix_map)

# Get all frontend fetch calls
frontend_calls = set()
for f in Path("apps/web").rglob("*.*"):
    if f.suffix in [".ts", ".tsx", ".js", ".jsx"]:
        if "node_modules" in str(f) or ".next" in str(f):
            continue
        try:
            txt = f.read_text(encoding="utf-8")
            found = re.findall(r'/api/v1/[a-zA-Z0-9_\-\/]+', txt)
            for item in found:
                item = item.split("?")[0].split("$")[0].rstrip("`'\"}")
                frontend_calls.add(item)
        except Exception:
            pass

# Also check frontend proxy route files
proxy_routes = set()
for f in Path("apps/web/app/api").rglob("route.ts"):
    rel = f.relative_to(Path("apps/web/app"))
    route_path = "/" + str(rel.parent).replace("\\", "/")
    proxy_routes.add(route_path)

print(f"Frontend proxy routes count: {len(proxy_routes)}")

# Read all backend endpoints and compute full route
backend_endpoints = []
endpoint_dir = Path("services/api/app/api/v1/endpoints")

for ep in endpoint_dir.glob("*.py"):
    if ep.name == "__init__.py":
        continue
    mod_name = ep.stem
    mod_pfx = prefix_map.get(mod_name, f"/{mod_name}")
    content = ep.read_text(encoding="utf-8")

    # Find function definitions and router decorators
    lines = content.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'@router\.(get|post|put|delete|patch)\(\s*["\']([^"\']*)["\']', line.strip())
        if m:
            method = m.group(1).upper()
            subpath = m.group(2)
            # Find function name
            func_name = "unknown"
            for j in range(i+1, min(i+10, len(lines))):
                fn_m = re.match(r'(?:async\s+)?def\s+([a-zA-Z0-9_]+)\(', lines[j].strip())
                if fn_m:
                    func_name = fn_m.group(1)
                    break
            
            full_path = f"/api/v1{mod_pfx}{subpath}".replace("//", "/")
            if full_path.endswith("/") and len(full_path) > 8:
                full_path = full_path[:-1]

            # Check if called by frontend
            called_directly = False
            for fc in frontend_calls:
                if full_path == fc or full_path.startswith(fc) or fc.startswith(full_path):
                    called_directly = True
                    break

            backend_endpoints.append({
                "module": mod_name,
                "file": f"services/api/app/api/v1/endpoints/{ep.name}",
                "method": method,
                "subpath": subpath,
                "full_path": full_path,
                "function": func_name,
                "connected_to_frontend": called_directly,
            })

print(f"Total backend endpoints parsed: {len(backend_endpoints)}")
unconnected = [e for e in backend_endpoints if not e["connected_to_frontend"]]
print(f"Unconnected backend endpoints: {len(unconnected)}")

# Group unconnected by module
unconnected_by_mod = {}
for e in unconnected:
    unconnected_by_mod.setdefault(e["module"], []).append(e)

for mod, eps in sorted(unconnected_by_mod.items()):
    print(f"\n[{mod.upper()}] ({len(eps)} endpoints not called by frontend):")
    for e in eps[:8]:
        print(f"  - {e['method']} {e['full_path']} (func: {e['function']})")
    if len(eps) > 8:
        print(f"  ... and {len(eps)-8} more")
