import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path so 'backend' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT) + "/backend")
    print(f"Added {str(PROJECT_ROOT) + '/backend'} to sys.path")

import pytest
from src.core.agents.tools.tecdoc_typed_tool import TecDocTypedTool, TecEndpoint
from src.config.settings import get_settings

def _require_key():
    s = get_settings()
    if not getattr(s, 'rapidapi_key', None):
        pytest.skip("No TecDoc rapidapi_key configured; skipping live TecDoc tests.")

@pytest.mark.asyncio
async def test_tool_languages_happy_path():
    _require_key()
    tool = TecDocTypedTool()  # uses real service/client
    out = await tool._arun(endpoint=TecEndpoint.LANGUAGES_LIST)
    assert "root" in out and len(out["root"]) >= 1

@pytest.mark.asyncio
async def test_tool_article_number_details_dispatch():
    _require_key()
    tool = TecDocTypedTool()
    out = await tool._arun(
        endpoint=TecEndpoint.ARTICLE_NUMBER_DETAILS,
        lang_id=4, country_id=120, article_no="113-1306X"
    )
    # We don’t hardcode exact shape (provider changes happen), just assert core keys exist
    assert "articles" in out or "article" in out or "allSpecifications" in out
