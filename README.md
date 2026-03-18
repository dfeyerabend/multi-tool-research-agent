# Multi-Agent Research System

A multi-agent system using the Supervisor-Worker pattern with the Anthropic Claude API. A Supervisor decomposes user requests into steps and delegates them through a Router Agent to specialized sub-agents, each running in full context isolation with their own tools and conversation history.

Built as part of the KI & Python Advanced module at Morphos GmbH.

---

## Architecture

```
                    ┌──────────────────────┐
                    │     SUPERVISOR        │
                    │  Task decomposition   │
                    │  Tool: call_router    │
                    └──────────┬────────────┘
                               │
                    ┌──────────▼────────────┐
                    │     ROUTER AGENT      │
                    │  Routing decisions     │
                    │  Tools: 2 (per agent) │
                    └──────────┬────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
     ┌────────────────┐                ┌────────────────┐
     │ RESEARCH AGENT │                │ ANALYSIS AGENT │
     │ web_search     │                │ text_analysis  │
     │ summarize      │                │ sentiment      │
     └────────────────┘                └────────────────┘
```

The Supervisor does not perform tasks directly. It breaks down the user's request, routes each step to the Router Agent, and assembles the final response from collected results.

The Router Agent is a custom addition that sits between the Supervisor and the sub-agents. The Supervisor only sees a single tool (`call_router_agent`) regardless of how many sub-agents exist. This keeps tool definition overhead constant as the system scales — adding a new agent means registering it in the Router, not modifying the Supervisor.

Each sub-agent runs its own agent loop with its own message list, system prompt, and tools. No agent sees another agent's context.

---

## Agents and Tools

| Agent | Tools | Role |
|---|---|---|
| **Supervisor** | `call_router_agent` | Decomposes tasks, sequences steps, presents results |
| **Router** | `call_research_agent`, `call_analysis_agent` | Routes each step to the appropriate specialist |
| **Research** | `web_search`, `summarize` | Web research via DuckDuckGo, result condensation |
| **Analysis** | `text_analysis`, `sentiment_analysis` | Word/sentence statistics, frequency analysis, sentiment scoring |

---

## Project Structure

```
multi_agent_system/
├── main.py                     # Supervisor + interactive mode
├── config.py                   # Shared settings, prompts, client
├── agents/
│   ├── __init__.py
│   ├── router_agent.py         # Routing layer
│   ├── research_agent.py       # Web research specialist
│   └── analysis_agent.py       # Text analysis specialist
├── tools/
│   ├── __init__.py
│   ├── research_tools.py       # web_search, summarize
│   └── analysis_tools.py       # text_analysis, sentiment_analysis
├── .env
├── .env.example
└── requirements.txt
```

---

## Setup

### Prerequisites
- Python 3.10+
- Anthropic API Key

### Installation

```bash
git clone https://github.com/yourusername/multi-agent-research-system.git
cd multi-agent-research-system

python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows

pip install -r requirements.txt
cp .env.example .env            # Add your API key
```

### Run

```bash
python main.py
```

---

## Example Queries

```
"Suche nach aktuellen Nachrichten über KI in Deutschland"
→ Supervisor → Router → Research Agent (web_search) → Result

"Analysiere den folgenden Text: Künstliche Intelligenz verändert die Arbeitswelt..."
→ Supervisor → Router → Analysis Agent (text_analysis + sentiment) → Result

"Recherchiere 'AI Agents' und analysiere die Ergebnisse"
→ Supervisor → Router → Research → Router → Analysis → Combined result
```

---

## Features

- **Router Agent** — Custom routing layer that decouples the Supervisor from sub-agent definitions
- **Context isolation** — Each agent maintains its own message history and tool set
- **Agent chaining** — Results from one agent are passed as context to the next
- **Conversation memory** — Supervisor retains history across queries within a session
- **Token tracking** — Per-iteration token usage logging
- **DuckDuckGo search** — Web search without additional API keys
- **German stopword filtering** — NLTK-based filtering for meaningful word frequency results

---

## Planned

- **Writer Agent** — Markdown report generation from combined research and analysis results
- **Advanced context management** — Lazy summarization with run IDs. Summarizes only on context window overflow and preserves compressed history for future reference.
- **Error handling with retry/fallback** — Graceful degradation when sub-agents fail
- **wandb integration** — Per-agent token cost monitoring

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Anthropic Claude SDK | LLM API + tool use |
| Claude Sonnet 4 | Agent reasoning |
| Python | Agent loops, orchestration |
| NLTK | German stopword filtering |
| ddgs | DuckDuckGo web search |

---

**Dennis Feyerabend** — Morphos GmbH, March 2026
