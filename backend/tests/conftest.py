# # backend/tests/conftest.py
# import json
# import pathlib
# import pytest
# from src.infrastructure.integrations.tecdoc.client import AsyncTecDocClient
# import sys
# from pathlib import Path

# PROJECT_ROOT = Path(__file__).resolve().parents[2]
# if str(PROJECT_ROOT) not in sys.path:
#     sys.path.insert(0, str(PROJECT_ROOT) + "/backend")

# FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "tecdoc"

# class DummyTecDocClient(AsyncTecDocClient):
#     def __init__(self):
#         # Don’t force env settings for tests
#         pass
#     def set_response(self, path: str, payload: dict):
#         if not hasattr(self, "_data"):
#             self._data = {}
#         self._data[path] = payload
#     async def __aenter__(self):
#         return self
#     async def __aexit__(self, *args):
#         return False
#     async def get(self, path: str, params=None):
#         return getattr(self, "_data", {}).get(path, {})

# @pytest.fixture
# def load_json():
#     def _load(name: str) -> dict:
#         return json.loads((FIXTURES / name).read_text())
#     return _load

# @pytest.fixture
# def dummy_client():
#     return DummyTecDocClient()
