"""
Multi-Agent Research System — Supervisor
Der Supervisor routet User-Anfragen an spezialisierte Agents.
"""

import json
import anthropic
from config import client, MODEL, MAX_TOKENS, SUPERVISOR_PROMPT, MAX_ITERATIONS_SUPERVISOR

# === IMPORTS: Sub-Agents ===
# Only import the router agent, because the RA handles the specific subagents
from agents.router_agent import router_agent_run, tool_list

# === SUPERVISOR TOOLS ===
# Das sind KEINE echten Tools — das sind Routing-Entscheidungen.
# Jedes "Tool" ruft einen Sub-Agent auf.

supervisor_tools = [
    {
        "name": "call_router_agent",
        "description": (
            "Route a task to the router agent. Use when the user needs "
            "one of the capabilities of the specialist agents. "
            "These include: "
            "web search and information gathering, "
            "text analyses (word counts, sentiment, statistics), "
            "and report writing with markdown formatting."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Clear description of a single task step",
                },
                "context": {
                    "type": "string",
                    "description": "Results from previous steps, if this step depends on them.",
                }
            },
            "required": ["task"],
        }
    }
]

# Persists across agent runs for conversation memory
conversation_history = []

def supervisor_agent_run(user_query: str) -> str:
    """
    Main Supervisor Loop.
    Empfaengt eine User-Frage, routet an Sub-Agents, sammelt Ergebnisse.

    Was hier passiert:
    1. User-Frage geht an Claude mit den Routing-Tools
    2. Claude entscheidet welchen Agent er ruft (stop_reason == "tool_use")
    3. Wir fuehren den Sub-Agent aus und geben das Ergebnis zurueck
    4. Claude bekommt das Ergebnis und entscheidet: Nochmal routen oder antworten?
    5. Wenn stop_reason == "end_turn": Fertig, finale Antwort
    """

    print(f"\n{'='*60}")
    print(f"USER: {user_query}")
    print(f"{'='*60}")


    conversation_history.append({"role": "user", "content": user_query})

    # Statistics for tracking
    run_count = 0
    total_tokens = 0

    for iteration in range(MAX_ITERATIONS_SUPERVISOR): # Savety Limit

        print(f"\n--- Supervisor Iteration {iteration + 1} ---")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SUPERVISOR_PROMPT,
            tools=supervisor_tools,
            messages=conversation_history
        )

        # Token tracking
        tokens_current_run = response.usage.input_tokens + response.usage.output_tokens
        total_tokens += tokens_current_run
        print(f"Stop Reason: {response.stop_reason} | Tokens: {total_tokens}")

        # Logic for proceeding
        # Case 1: Claude is finished - return final answer and run statistics
        if response.stop_reason == "end_turn":
            # Add final message to history
            conversation_history.append({"role": "assistant", "content": response.content})

            # Extract text from response blocks
            final_message = None # Initiate empty

            for block in response.content:
                if hasattr(block, "text"):
                    final_message = f"\nAgent: {block.text}"
                    break                   # End if final message was found

            if not final_message:       # no text block was found at all
                final_message = "Run completed. But no Agent response found"

            print(f"\n[Total: {run_count} Runs, {total_tokens} Tokens]")
            return final_message

        elif response.stop_reason == "tool_use":
            # Add Assistant Message to history
            conversation_history.append({"role": "assistant", "content": response.content})

            tool_results = []                                   # collect results from all parallel tool calls
            for block in response.content:
                if block.type == "tool_use":
                    # Flag to call Router Agent
                    print(f"\n{'─' * 50}")
                    print(f"⮕  SUPERVISOR → ROUTER AGENT")
                    print(f"   Task: {json.dumps(block.input, ensure_ascii=False)[:200]}")
                    print(f"{'─' * 50}")

                    # Extract task and optional context from the tool call
                    task = block.input.get("task", "")          # get the task description the Supervisor wrote
                    context = block.input.get("context", "")    # results from earlier steps, if any

                    try:
                        # Call the router agent and get the result string
                        result = router_agent_run(task, context)    # Pass task and context (optional) to router agent
                    except Exception as e:
                        print(f"  Router Agent FAILED: {str(e)}")
                        result = json.dumps({
                            "error": str(e),
                            "failed_task": task,
                            "hint": "Consider rephrasing the task or trying a different approach"
                        })

                    print(f"  Router Result: {result[:200]}...")

                    # Package as tool_result so Claude knows what the tool returned
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # must match the tool_use block id
                        "content": result
                    })

            # Feed all tool results back into the conversation
            conversation_history.append({"role": "user", "content": tool_results})
            run_count += 1

        else:
            return "Max iterations reached. Ending run."




# === INTERACTIVE MODE ===
if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-AGENT RESEARCH SYSTEM")
    print(f"Including router agent with {len(tool_list)} Tools")
    print("Enter 'quit' to exit")
    print("=" * 60)

    while True:
        query = input("\nYour question: ")
        if query.lower() in ["quit", "exit", "q"]:
            print("System terminated.")
            break
        if query.strip() == "":
            continue

        answer = supervisor_agent_run(query)
        print(f"\n{'='*60}")
        print(f"FINAL ANSWER:\n{answer}")
        print(f"{'='*60}")
