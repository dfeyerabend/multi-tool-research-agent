import json

from agents.research_agent import research_agent_run
from agents.analysis_agent import analysis_agent_run

from config import client, MODEL, MAX_TOKENS, ROUTER_PROMPT, MAX_ITERATIONS_ROUTER

router_tools = [
    {
        "name": "call_research_agent",
        "description": (
            "Route a task to the Research Agent. Use when the user needs "
            "web search, information gathering, or fact-finding. "
            "The Research Agent has tools: web_search, summarize."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Clear description of the research task"
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "call_analysis_agent",
        "description": (
            "Route a task to the Analysis Agent. Use when text needs to be "
            "analyzed: word counts, sentiment, key facts, statistics. "
            "The Analysis Agent has tools: text_analysis, sentiment_analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Clear description of the analysis task"
                },
                "context": {
                    "type": "string",
                    "description": "Text or data that the agent should analyze"
                }
            },
            "required": ["task"]
        }
    }
]

tool_list = [t['name'] for t in router_tools]

def router_agent_run(router_task: str, router_context: str = "") -> str:

    if router_context:
        message_content = f"Task: {router_task}\n\nContext:\n{router_context}" # only include if context is not empty
    else:
        message_content = router_task

    messages = [{"role": "user", "content": message_content}]

    for iteration in range(MAX_ITERATIONS_ROUTER):

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=ROUTER_PROMPT,
            tools=router_tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            # Router is done, extract text and return it
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Router completed but no response found"

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":

                    agent_task = block.input.get("task", "")
                    agent_context = block.input.get("context", "")

                    # Call Subagent Banner
                    print(f"\n  {'─' * 46}")
                    print(f"  ⮕  ROUTER → {block.name.replace('call_', '').replace('_', ' ').upper()}")
                    print(f"     Task: {agent_task[:150]}")
                    print(f"  {'─' * 46}")

                    if block.name == "call_research_agent":
                        try:
                            result = research_agent_run(agent_task)
                        except Exception as e:
                            result = json.dumps({
                                "error": str(e),
                                "failed_agent": "research_agent",
                                "failed_task": agent_task,
                            })

                    elif block.name == "call_analysis_agent":
                        try:
                            result = analysis_agent_run(agent_task)
                        except Exception as e:
                            result = json.dumps({
                                "error": str(e),
                                "failed_agent": "analysis_agent",
                                "failed_task": agent_task,
                            })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})
            # Loop continues

    return "Router: Max iterations reached"











