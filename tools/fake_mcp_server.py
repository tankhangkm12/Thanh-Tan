# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=2.3,<3"]
# ///
"""A tiny MCP server with one tool that reads and one that writes, for trying `agentflow role grant`.

    uv run tools/fake_mcp_server.py        # speaks MCP on stdio

Its tools keep notes in memory only. The smoke test lists them over MCP and grants roles tools by their real names.
"""

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

SERVER_NAME = "fakesrv"
READ_TOOL = "get_note"
WRITE_TOOL = "write_note"
TOOL_NAMES = (READ_TOOL, WRITE_TOOL)
NOTES: dict[str, str] = {}


def build_server() -> MCPServer:
    server = MCPServer(SERVER_NAME, instructions="Notes kept in memory, for trying agentflow role grant.")

    def get_note(name: str) -> str:
        return NOTES.get(name, "")

    def write_note(name: str, text: str) -> str:
        NOTES[name] = text
        return "saved"

    server.tool(name=READ_TOOL, description="Read a note.", annotations=ToolAnnotations(readOnlyHint=True))(get_note)
    server.tool(name=WRITE_TOOL, description="Write a note.", annotations=ToolAnnotations(readOnlyHint=False))(write_note)
    return server


if __name__ == "__main__":
    build_server().run("stdio")
