from __future__ import annotations
from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ...services.tecdoc_service import TecDocService


class TecDocToolInput(BaseModel):
    path: str = Field(..., description="Path-only endpoint (e.g. '/languages/list')")


class TecDocTool(BaseTool):
    name = "tecdoc_api"
    description = (
        "Call TecDoc API via service. Input is a path-only string as built by the endpoints module."
    )
    args_schema: Type[BaseModel] = TecDocToolInput

    def __init__(self, service: TecDocService | None = None, **kwargs):
        super().__init__(**kwargs)
        self.service = service or TecDocService()

    async def _arun(self, path: str):
        # Return raw JSON (tooling often fans out to model parsing later)
        return await self.service._fetch(path)

    def _run(self, *args, **kwargs):
        raise NotImplementedError("TecDocTool supports async only")