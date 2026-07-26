from app.services.mcp import MCPClient


async def query_code_graph(repo_root: str, query: str) -> dict:
    async with MCPClient("code-review-graph") as client:
        return await client.call("semantic_search_nodes_tool", {
            "repo_root": repo_root,
            "query": query
        })
