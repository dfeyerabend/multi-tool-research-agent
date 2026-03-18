"""
Research Agent — Specialized in web research and summarization.
Has its OWN tools and its OWN message list (context isolation).
"""

import json
from config import client, MODEL, MAX_TOKENS, MAX_ITERATIONS_SUBAGENTS, RESEARCH_PROMPT
from tools.research_tools import research_tools, run_research_tool

def research_agent_run(task: str) -> str:
    """
    Runs a research task.

    What happens here:
    - Receives a task string from the supervisor
    - Has its own tools (web_search, summarize)
    - Has its own messages list (it does NOT see anything from the supervisor)
    - Runs its own agent loop
    - Returns the result as a string

    Args:
        task: The research task as a string

    Returns:
        The research result as a string
    """

    # Banner
    print(f"\n    ┌── RESEARCH AGENT ──────────────────────┐")
    print(f"    │ Task: {task[:60]}")
    print(f"    └─────────────────────────────────────────┘")

    messages = [{"role": "user", "content": task}]

    for iteration in range(MAX_ITERATIONS_SUBAGENTS):
        print(f"  [Research Agent] Iteration {iteration + 1}")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=RESEARCH_PROMPT,
            tools=research_tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Research Agent finished task, but no response was found"

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"    Tool: {block.name}")

                    try:
                        result = run_research_tool(name=block.name, tool_input=block.input)
                    except Exception as e:
                        return json.dumps({
                            "error": str(e),
                            "failed_tool": block.name,
                        })
                    print(f"    Tool Result: {result[:300]}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

    return "Research Agent: Max iterations reached"