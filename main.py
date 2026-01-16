"""
mem0-mcp: MCP server for mem0 memory operations

This server provides tools for AI agents to perform CRUD operations
on mem0 memories, organized by project_id in metadata.
"""

import os
from typing import Optional

from fastmcp import FastMCP
from mem0 import MemoryClient


# ============================================================================
# CONFIGURATION
# ============================================================================

HTTP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
# Railway uses PORT env var, fallback to MCP_PORT or 9000 for local dev
HTTP_PORT = int(os.getenv("PORT", os.getenv("MCP_PORT", "9000")))


# Initialize FastMCP server
mcp = FastMCP(
    name="mem0-mcp",
    instructions="""
    You are a memory management assistant that helps store and retrieve memories using mem0.
    
    Memories are organized by project_id - use this to categorize memories by project or purpose.
    When no project_id is specified, the default project from configuration will be used.
    
    Available operations:
    - add_memory: Store new information
    - search_memory: Find relevant memories using natural language
    - get_memory: Retrieve a specific memory by ID
    - update_memory: Modify existing memory content
    - delete_memory: Remove a memory
    - list_memories: List all memories for a project
    """,
    host=HTTP_HOST,
    port=HTTP_PORT,
)


# Initialize mem0 client
# Will use MEM0_API_KEY from environment
def get_mem0_client() -> MemoryClient:
    """Get mem0 client instance."""
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        raise ValueError("MEM0_API_KEY environment variable is required")
    return MemoryClient(api_key=api_key)


def get_default_project() -> Optional[str]:
    """Get default project ID from environment."""
    return os.environ.get("DEFAULT_PROJECT_ID")


def build_filters(project_id: Optional[str] = None) -> dict:
    """Build filters dict for mem0 queries."""
    effective_project = project_id or get_default_project()
    if effective_project:
        # mem0 API expects metadata as a nested dict
        return {"AND": [{"metadata": {"project_id": effective_project}}]}
    return {}


# ============================================================================
# TOOLS
# ============================================================================


@mcp.tool
def add_memory(
    content: str, project_id: Optional[str] = None, metadata: Optional[dict] = None
) -> dict:
    """
    Store a new memory in mem0.

    Args:
        content: The information to remember. Can be facts, preferences,
                 context, or any text you want to store.
        project_id: Optional project identifier to organize memories.
                   Falls back to DEFAULT_PROJECT_ID if not specified.
        metadata: Optional additional metadata to attach to the memory.
                 Example: {"category": "preferences", "priority": "high"}

    Returns:
        The created memory details including its ID.

    Example:
        add_memory("User prefers dark mode in all applications", project_id="my-app")
    """
    client = get_mem0_client()

    # Build metadata with project_id
    effective_project = project_id or get_default_project()
    memory_metadata = metadata.copy() if metadata else {}
    if effective_project:
        memory_metadata["project_id"] = effective_project

    # Add memory using messages format
    messages = [{"role": "user", "content": content}]

    # Get user_id from environment or use default
    user_id = os.environ.get("MEM0_USER_ID", "default_user")

    result = client.add(
        messages=messages,
        user_id=user_id,
        metadata=memory_metadata if memory_metadata else None,
    )

    return {
        "status": "success",
        "message": "Memory added successfully",
        "result": result,
    }


@mcp.tool
def search_memory(
    query: str, project_id: Optional[str] = None, limit: int = 10
) -> dict:
    """
    Search memories using natural language.

    Args:
        query: Natural language search query. Be descriptive for better results.
               Example: "What are the user's color preferences?"
        project_id: Optional project to search within.
                   Falls back to DEFAULT_PROJECT_ID if not specified.
        limit: Maximum number of results to return (default: 10).

    Returns:
        List of matching memories with relevance scores.

    Example:
        search_memory("coding preferences", project_id="dev-setup")
    """
    client = get_mem0_client()
    user_id = os.environ.get("MEM0_USER_ID", "default_user")

    # Build filters - user_id is required for search
    effective_project = project_id or get_default_project()
    if effective_project:
        filters = {
            "AND": [
                {"user_id": user_id},
                {"metadata": {"project_id": effective_project}},
            ]
        }
    else:
        filters = {"user_id": user_id}

    results = client.search(query=query, filters=filters, limit=limit)

    return {
        "status": "success",
        "query": query,
        "project_id": project_id or get_default_project() or "all",
        "results": results,
    }


@mcp.tool
def get_memory(memory_id: str) -> dict:
    """
    Retrieve a specific memory by its ID.

    Args:
        memory_id: The unique identifier of the memory to retrieve.

    Returns:
        The memory details including content, metadata, and timestamps.

    Example:
        get_memory("mem_abc123xyz")
    """
    client = get_mem0_client()

    result = client.get(memory_id=memory_id)

    return {"status": "success", "memory": result}


@mcp.tool
def update_memory(memory_id: str, content: str) -> dict:
    """
    Update the content of an existing memory.

    Args:
        memory_id: The unique identifier of the memory to update.
        content: The new content to replace the existing memory.

    Returns:
        Confirmation of the update.

    Example:
        update_memory("mem_abc123xyz", "Updated preference: User now prefers light mode")
    """
    client = get_mem0_client()

    result = client.update(memory_id=memory_id, data=content)

    return {
        "status": "success",
        "message": "Memory updated successfully",
        "result": result,
    }


@mcp.tool
def delete_memory(memory_id: str) -> dict:
    """
    Delete a specific memory.

    Args:
        memory_id: The unique identifier of the memory to delete.

    Returns:
        Confirmation of the deletion.

    Example:
        delete_memory("mem_abc123xyz")
    """
    client = get_mem0_client()

    client.delete(memory_id=memory_id)

    return {"status": "success", "message": f"Memory {memory_id} deleted successfully"}


@mcp.tool
def list_memories(project_id: Optional[str] = None, limit: int = 50) -> dict:
    """
    List all memories, optionally filtered by project.

    Args:
        project_id: Optional project to filter by.
                   Falls back to DEFAULT_PROJECT_ID if not specified.
                   Pass "all" to list memories from all projects.
        limit: Maximum number of memories to return (default: 50).

    Returns:
        List of memories with their details.

    Example:
        list_memories(project_id="my-project", limit=20)
    """
    client = get_mem0_client()
    user_id = os.environ.get("MEM0_USER_ID", "default_user")

    # Build filters - user_id is required, project_id is optional
    if project_id == "all":
        # Only filter by user_id
        filters = {"user_id": user_id}
    else:
        effective_project = project_id or get_default_project()
        if effective_project:
            filters = {
                "AND": [
                    {"user_id": user_id},
                    {"metadata": {"project_id": effective_project}},
                ]
            }
        else:
            filters = {"user_id": user_id}

    results = client.get_all(filters=filters, limit=limit)

    return {
        "status": "success",
        "project_id": project_id or get_default_project() or "all",
        "memories": results,
    }


# ============================================================================
# ENTRYPOINT
# ============================================================================


def main():
    """Run the MCP server."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                     mem0-mcp Server                          ║
╠══════════════════════════════════════════════════════════════╣
║  Host: {HTTP_HOST:<54}║
║  Port: {HTTP_PORT:<54}║
╚══════════════════════════════════════════════════════════════╝
    """)

    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
