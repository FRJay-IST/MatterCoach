# MatterCoach MCP server

Read-only MCP service for the existing Socratic MatterCoach tutor. Three tools: `list_problems`, `get_problem`, `check_answer`.

**Setup is incomplete:** the original twelve exercise statements must be placed in `mcp-server/data/statements.txt` before deployment. Do not invent or replace the original statements. The verified instructor solutions must NOT be committed to this public repository. The `check_answer` tool only prepares a structured answer for the tutor; it does not automatically verify correctness.

Deploy `mcp-server/` as a Python web service (start command: `python app.py`) or using Docker. Public MCP endpoint: `https://YOUR-SERVICE/mcp`. Confirm MCP initialize and tools/list before configuring a plugin. Do not claim the plugin is deployed or approved until tested.

The existing GitHub Pages site is unaffected.
