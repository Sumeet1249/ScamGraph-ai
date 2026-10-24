"""Services root package.

Provides import aliases for hyphenated service packages:
- services.graph_engine -> services.graph-engine
- services.pattern_engine -> services.pattern-engine
"""

import importlib.util
from pathlib import Path
import sys

_services_dir = Path(__file__).resolve().parent

for _alias, _folder in [
    ("services.graph_engine", "graph-engine"),
    ("services.pattern_engine", "pattern-engine"),
]:
    if _alias not in sys.modules:
        _init_path = _services_dir / _folder / "__init__.py"
        if _init_path.exists():
            try:
                _spec = importlib.util.spec_from_file_location(
                    _alias,
                    _init_path,
                    submodule_search_locations=[str(_services_dir / _folder)],
                )
                if _spec and _spec.loader:
                    _mod = importlib.util.module_from_spec(_spec)
                    sys.modules[_alias] = _mod
                    _spec.loader.exec_module(_mod)
            except Exception as _e:
                import logging
                logging.getLogger(__name__).warning("Failed to register alias %s: %s", _alias, _e)
