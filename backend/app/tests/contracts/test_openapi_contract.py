import json
from pathlib import Path

from app.main import app


def test_openapi_paths_snapshot() -> None:
    snapshot_path = Path(__file__).with_name("openapi_snapshot.json")
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))

    schema = app.openapi()
    paths = schema.get("paths", {})

    for route, methods in snapshot["required_paths"].items():
        assert route in paths, f"Missing path in OpenAPI: {route}"
        for method in methods:
            assert method in paths[route], f"Missing method {method} for path {route}"
