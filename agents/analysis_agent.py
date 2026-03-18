"""
Text analysis Agent — Specialized in word analysis and semantics.
Has its OWN tools and its OWN message list (context isolation).
"""

import json
from config import client, MODEL, MAX_TOKENS, MAX_ITERATIONS_SUBAGENTS, ANALYSIS_PROMPT
from tools.analysis_tools import analysis_tools, run_text_analysis_tool

def analysis_agent_run(task: str) -> str:
    """
    Runs a test analysis task.

    What happens here:
    - Receives a task string from the supervisor
    - Has its own tools (text_analysis, sentiment_analysis)
    - Has its own messages list (it does NOT see anything from the supervisor)
    - Runs its own agent loop
    - Returns the result as a string

    Args:
        task: The research task as a string

    Returns:
        The research result as a string
    """

    print(f"\n  [Text Analysis Agent] Task: {task}")
    messages = [{"role": "user", "content": task}]

    for iteration in range(MAX_ITERATIONS_SUBAGENTS):
        print(f"  [Text Analysis Agent] Iteration {iteration + 1}")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=ANALYSIS_PROMPT,
            tools=analysis_tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Text Analysis Agent finished task, but no response was found"

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"    Tool: {block.name}")

                    try:
                        result = run_text_analysis_tool(name=block.name, tool_input=block.input)
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

    return "Text Analysis Agent: Max iterations reached"