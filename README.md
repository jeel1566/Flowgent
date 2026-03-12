# Flowgent — AI-Powered n8n Workflow Automation

**A Chrome extension + FastAPI backend that lets you build, edit, debug, and execute production-grade n8n workflows using natural language.**

![Flowgent Icon](extension/assets/icon128.png)

---

## ✨ Features

### 🤖 AI Chat Assistant (Production-Grade)
The agent follows a **5-phase protocol** for every workflow request — it doesn't just generate JSON, it thinks, researches, and builds real automations:

| Phase | What It Does |
|-------|-------------|
| 🧠 **Think** | Analyzes the business goal, trigger, steps, and services involved |
| 📖 **Research Templates** | Searches n8n community templates for real working examples |
| 🔍 **Research Nodes & Docs** | Reads official node documentation for every node it uses |
| 💬 **Ask & Recommend** | Presents the workflow plan and asks clarifying questions |
| 🔨 **Build** | Constructs a validated, production-ready workflow |

**What you can say:**
- `"Create a workflow that syncs new Shopify orders to Google Sheets"`
- `"Build a Slack bot that replies to messages using an LLM"`
- `"Add an If node to workflow #123 to handle errors"`
- `"Fix the broken connection in workflow #456"`
- `"Rename workflow #789 to 'Daily Reports'"`

### 🌐 Web Search
- Agent can search the web to find API docs, webhook formats, and integration patterns
- Powered by DuckDuckGo (no API key required)

### ℹ️ Information Hand
- Hover over any n8n node for instant documentation
- Shows: description, common use cases, best practices, example configurations
- Auto-positions tooltip, caches results, works with custom nodes

### 📊 Dashboard
- View all your n8n workflows with status, node count, and timestamps
- Execution history (last 10 runs with status and timing)
- Execute workflows with custom input data
- Quick workflow actions without leaving Chrome

---

## 🏗️ Architecture

```
Flowgent/
├── backend/                  # FastAPI + Google Agent Development Kit
│   ├── agent/
│   │   ├── flowgent_agent.py # Agent tools (11 tools) + ADK runner
│   │   └── config.py         # Multi-LLM config + system prompt
│   ├── api/                  # REST API routes
│   ├── n8n_mcp/              # n8n MCP + direct HTTP client
│   └── models/               # Pydantic schemas
└── extension/                # Chrome Extension (Manifest V3)
    ├── sidepanel/            # Chat + Dashboard UI
    ├── content/              # Information Hand tooltips
    └── lib/                  # Shared utilities
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Chrome browser**
- **n8n instance** (local or cloud)
- An LLM API key (see [LLM Options](#-llm-options) below)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Copy and configure the environment file:
```bash
cp .env.example .env
```

Edit `.env` with your chosen LLM and n8n settings (see next section), then start:
```bash
python main.py
# Or with uvicorn:
uvicorn main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`.

### 2. Chrome Extension Setup

1. Go to `chrome://extensions/` and enable **Developer mode**
2. Click **Load unpacked** and select the `extension/` folder
3. Click the Flowgent icon → **Settings tab**
4. Enter your backend URL (`http://localhost:8000`) and your n8n instance URL + API key
5. Click **Save Settings** and **Test Connection**
6. Navigate to your n8n instance and open the side panel ✅

---

## 🤖 LLM Options

Flowgent supports multiple LLM providers. Set `LLM_MODEL` in `backend/.env`:

| Provider | `LLM_MODEL` value | Key variable |
|----------|-------------------|--------------|
| **OpenRouter** (default) | `openrouter/deepseek/deepseek-chat` | `OPENROUTER_API_KEY` |
| **Google Gemini** | `gemini-2.0-flash` | `GOOGLE_GENAI_API_KEY` |
| **Azure AI** | `azure/<your-deployment>` | `AZURE_AI_API_KEY` + `AZURE_API_BASE` |
| Any OpenRouter model | `openrouter/<provider>/<model>` | `OPENROUTER_API_KEY` |

**Get free API keys:**
- OpenRouter (free tier): https://openrouter.ai/keys
- Google Gemini: https://aistudio.google.com/apikey

**Example `.env` (OpenRouter — default):**
```env
LLM_MODEL=openrouter/deepseek/deepseek-chat
OPENROUTER_API_KEY=sk-or-...

N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
```

**Example `.env` (Google Gemini):**
```env
LLM_MODEL=gemini-2.0-flash
GOOGLE_GENAI_API_KEY=AIza...

N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
```

---

## 📚 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check and connection status |
| `POST` | `/api/chat` | Chat with the AI agent |
| `GET` | `/api/workflows` | List all workflows |
| `POST` | `/api/workflows` | Create a new workflow |
| `GET` | `/api/workflows/{id}` | Get workflow details |
| `PUT` | `/api/workflows/{id}` | Update an existing workflow |
| `POST` | `/api/execute` | Execute a workflow |
| `GET` | `/api/node-info/{type}` | Get node documentation |
| `GET` | `/api/executions` | Get execution history |

### Example: Chat Request
```json
POST /api/chat
{
  "message": "Create a workflow that monitors GitHub issues and posts to Slack",
  "context": { "currentPage": "https://your-n8n-instance.com" }
}
```

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async Python web framework
- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) — agentic AI runtime
- [LiteLLM](https://litellm.ai/) — unified LLM interface (OpenRouter, Azure, etc.)
- [Google GenAI SDK](https://ai.google.dev/) — Gemini model support
- [duckduckgo-search](https://pypi.org/project/duckduckgo-search/) — web search for the agent
- [httpx](https://www.python-httpx.org/) — async HTTP client for n8n API calls
- [Pydantic v2](https://docs.pydantic.dev/) — request/response validation

**Frontend (Chrome Extension)**
- Manifest V3
- Vanilla JavaScript — no build step required
- Modern CSS — glassmorphism design, dark mode

**Integration**
- [n8n MCP Server](https://www.npmjs.com/package/@n8n/n8n-mcp) — official n8n Model Context Protocol server for node docs, templates, and workflow management
- Direct n8n REST API — fallback for workflow CRUD and execution

---

## 🧠 Agent Tools (11 total)

| Tool | Purpose |
|------|---------|
| `web_search` | Research APIs, webhook formats, integration patterns |
| `search_workflow_templates` | Find community templates by keyword |
| `get_workflow_template` | Fetch full template configuration |
| `search_nodes` | Find exact node type identifiers |
| `get_node_documentation` | Get node parameters, versions, and examples |
| `validate_workflow_json` | Validate workflow structure before deploying |
| `list_workflows` | List all workflows in connected n8n instance |
| `get_workflow` | Fetch a specific workflow by ID |
| `create_workflow` | Deploy a new workflow |
| `update_workflow` | Edit/fix an existing workflow |
| `execute_workflow` | Run a workflow with optional input data |

---

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List my workflows"}'

# Run backend tests
cd backend
python test_endpoints.py
```

---

## 🌐 Deployment

### Google Cloud Run

```bash
cd backend
gcloud run deploy flowgent-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LLM_MODEL=openrouter/deepseek/deepseek-chat,OPENROUTER_API_KEY=your-key
```

After deploying, update the backend URL in the Chrome extension settings to your Cloud Run URL.

---

## 💡 Tips

- **Be specific:** `"Create a workflow that sends a Slack message when a new row is added to Google Sheets"` works better than `"automate Slack"`
- **Reference workflows by ID:** `"Edit workflow #123 to add error handling"`
- **Information Hand:** Hover slowly on nodes — there's a 100ms delay to prevent flickering
- **Check the connection indicator:** The header shows backend and n8n connection status
- **Web search:** Ask the agent to look up APIs — e.g., `"Research the Stripe webhook format and build a workflow"`

---

## ❓ Troubleshooting

**Extension not loading?**
- Enable Developer mode in `chrome://extensions/`
- Check Chrome DevTools console for errors

**Backend connection failed?**
- Verify the backend is running: `curl http://localhost:8000/health`
- Confirm the URL in extension Settings matches your backend

**n8n connection failed?**
- Make sure your n8n instance URL and API key are set in Settings
- For local n8n: use `http://localhost:5678`
- For cloud n8n: use your full instance URL (e.g., `https://your-team.app.n8n.cloud`)

**AI not responding / API key error?**
- Check `backend/.env` has the correct key variable for your chosen LLM
- See [LLM Options](#-llm-options) for the correct variable names
- Restart the backend after editing `.env`

**Information Hand not showing?**
- Refresh the n8n page after loading the extension
- Check you're on an n8n workflow editor page
- Open DevTools and look for errors in the Console

---

## 📄 License

MIT License

---

## 👥 Team

Built for **Agentic+ Product Hackathon** by Team Flowgent

---

**Happy automating! 🚀**
