
"""MatterCoach MCP service. Original statements are loaded from data/statements.txt."""

import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.responses import PlainTextResponse


DATA = Path(__file__).parent / "data"

mcp = FastMCP(
    "MatterCoach",
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8000")),
    stateless_http=True,
    json_response=True,
)


# ------------------------------------------------------------
# MCP tool annotations
# ------------------------------------------------------------

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    openWorldHint=False,
)


# ------------------------------------------------------------
# Load original problem statements
# ------------------------------------------------------------

def read_statements():
    path = DATA / "statements.txt"

    if not path.exists():
        return None

    text = path.read_text(encoding="utf-8")

    matches = list(
        re.finditer(
            r"(?m)^PROBLEM\s+(\d+)\s+[—–-]\s+(.+)$",
            text,
        )
    )

    problems = {}

    for i, match in enumerate(matches):
        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(text)
        )

        problems[int(match.group(1))] = {
            "title": match.group(2).strip(),
            "statement": text[match.start():end].strip(),
        }

    if set(problems) != set(range(1, 13)):
        raise RuntimeError(
            "Expected twelve numbered problem statements."
        )

    return problems


# ------------------------------------------------------------
# Tool 1: List all problems
# ------------------------------------------------------------

@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
def list_problems() -> dict:
    """List available exercises from Structure of Matter, Problem Sheet 1."""

    problems = read_statements()

    if problems is None:
        return {
            "status": "not_configured",
            "message": "Original statements not installed yet.",
        }

    return {
        "problems": [
            {"number": n, "title": p["title"]}
            for n, p in sorted(problems.items())
        ]
    }


# ------------------------------------------------------------
# Tool 2: Retrieve a complete problem statement
# ------------------------------------------------------------

@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
def get_problem(number: int) -> dict:
    """Return the complete original statement for a numbered exercise (1-12)."""

    problems = read_statements()

    if problems is None:
        return {
            "status": "not_configured",
            "message": "Original statements not installed yet.",
        }

    if number not in problems:
        return {
            "error": "Choose a problem from 1 to 12."
        }

    return {
        "number": number,
        **problems[number],
    }


# ------------------------------------------------------------
# Tool 3: Socratic answer assessment
# ------------------------------------------------------------

@mcp.tool(annotations=READ_ONLY_ANNOTATIONS)
def check_answer(
    number: int,
    student_answer: str,
    part: str = "",
) -> dict:
    """Prepare a student's answer for Socratic assessment, without publishing the answer key."""

    problems = read_statements()

    if problems is None:
        return {
            "status": "not_configured",
            "message": "Original statements not installed yet.",
        }

    if number not in problems:
        return {
            "error": "Choose a problem from 1 to 12."
        }

    return {
        "number": number,
        "part": part,
        "student_answer": student_answer,
        "problem": problems[number]["statement"],
        "instruction": (
            "Evaluate using the tutor's verified private reference. "
            "Ask one guiding question; do not reveal the complete solution."
        ),
        "automatically_verified": False,
    }


# ------------------------------------------------------------
# OpenAI domain verification
# ------------------------------------------------------------

@mcp.custom_route(
    "/.well-known/openai-apps-challenge",
    methods=["GET"],
)
async def openai_domain_challenge(request):
    return PlainTextResponse(
        "xDyVC1zJtObUQ3cPQvhu4r6cABVgPPocp8UNCUSfrOE"
    )


# ------------------------------------------------------------
# Start MCP server
# ------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
