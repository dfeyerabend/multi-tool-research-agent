"""
Tools for the Research Agent.
Every Tool has a function and a schema.
"""

import json

# === TOOL SCHEMAS ===
research_tools = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information using DuckDuckGo. "
            "Returns titles, URLs, and text snippets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results (1-5). Default: 3"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "summarize",
        "description": (
            "Summarize a given text into key bullet points. "
            "Use after web_search to condense results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to summarize"
                },
                "max_points": {
                    "type": "integer",
                    "description": "Maximum number of bullet points. Default: 5"
                }
            },
            "required": ["text"]
        }
    }
]

# === TOOL EXECUTION ===
def run_research_tool(name: str, tool_input: dict) -> str:
    """
    Runs research tools
    """

    if name == "web_search":
        try:
            from ddgs import DDGS

            query = tool_input["query"]
            max_results = tool_input.get("max_results", 3)

            raw_results = DDGS().text(query, max_results=max_results)

            clean_results = []
            for r in raw_results:
                clean_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })

            return json.dumps({
                "query": query,
                "result_count": len(clean_results),
                "results": clean_results,
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"Web search tool failed: {str(e)}"})

    # Summarize logic
    elif name == "summarize":
        try:
            text = tool_input["text"]
            max_points = tool_input.get("max_points", 5)

            # Simple summary: extract sentences
            # In production you would call Claude again here
            # or use an NLP library
            sentences = text.replace("! ", ". ").replace("? ", ". ").split(". ")
            # Take the first N sentences as key points
            key_points = [s.strip() for s in sentences[:max_points] if s.strip()]

            return json.dumps({
                "original_length": len(text),
                "summary_points": key_points,
                "point_count": len(key_points)
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({"error": f"Summarize tool failed: {str(e)}"})

    else:
        return json.dumps({"error": f"Unknown research tool called: {name}"})



