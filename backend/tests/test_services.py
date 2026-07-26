import pytest
from app.services.mcp import MCPClient
from app.services.graph_client import query_code_graph


@pytest.mark.asyncio
async def test_mcp_client():
    async with MCPClient("code-review-graph") as client:
        res = await client.call("search", {"query": "test"})
        assert res["status"] == "success"
        assert res["tool"] == "search"


@pytest.mark.asyncio
async def test_query_code_graph():
    res = await query_code_graph("/tmp", "find tasks")
    assert res["status"] == "success"
