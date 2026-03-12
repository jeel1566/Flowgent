import os
import json
import logging
from typing import Optional, Dict, Any, List

# Load environment variables FIRST, before any ADK imports
from dotenv import load_dotenv
load_dotenv()

# LiteLLM configuration
import litellm
litellm.set_verbose = False

# Set up API keys based on configured model
from agent.config import LLM_MODEL, USE_LITELLM, SYSTEM_INSTRUCTION, get_llm_api_key, get_agent_model, get_fallback_model, FALLBACK_LLM_MODEL

# Configure API keys before ADK loads
if USE_LITELLM:
    if "openrouter" in LLM_MODEL.lower():
        _api_key = os.getenv("OPENROUTER_API_KEY")
        if _api_key:
            os.environ["OPENROUTER_API_KEY"] = _api_key
    elif "azure" in LLM_MODEL.lower():
        _api_key = os.getenv("AZURE_AI_API_KEY") or os.getenv("AZURE_API_KEY")
        if _api_key:
            os.environ["AZURE_AI_API_KEY"] = _api_key
else:
    _api_key = os.getenv("GOOGLE_GENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if _api_key:
        os.environ["GOOGLE_GENAI_API_KEY"] = _api_key
        os.environ["GOOGLE_API_KEY"] = _api_key

# ADK imports
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent.context import get_n8n_credentials
from n8n_mcp.n8n_client import get_mcp_client
from n8n_mcp.direct_client import create_n8n_client

logger = logging.getLogger(__name__)

import re

def _strip_reasoning(text: str) -> str:
    """Strip Kimi-K2-Thinking's chain-of-thought reasoning from the response.
    
    Kimi-K2-Thinking models return their internal reasoning process as part of
    the text response. This function extracts only the final user-facing answer.
    
    The reasoning follows patterns like:
    - Starts with analytical text ("The user...", "Let me...", "I should...")
    - Ends with the actual response after a blank line or clear transition
    """
    if not text:
        return text
    
    # Pattern 1: If reasoning is clearly separated by double newlines,
    # the actual response is usually the last substantial block
    blocks = re.split(r'\n\n+', text.strip())
    
    if len(blocks) <= 1:
        return text
    
    # Identify reasoning blocks by common thinking patterns
    reasoning_patterns = [
        r'^(?:The user|I should|I need to|Let me|I\'ll|I see|I notice|Looking at|Given|Since|This is|They|My |I can|I must|I want|I\'m going|First,|However,|Based on|Now,|So |Okay)',
        r'^\d+\.\s+["✓✗]',  # Checklist-style reasoning
        r'^[-•]\s+',  # Bullet-point reasoning  
    ]
    
    # Find where reasoning ends and response begins
    response_start = 0
    for i, block in enumerate(blocks):
        block_stripped = block.strip()
        is_reasoning = False
        for pattern in reasoning_patterns:
            if re.match(pattern, block_stripped, re.IGNORECASE):
                is_reasoning = True
                break
        
        if not is_reasoning and i > 0:
            # This block doesn't look like reasoning — it's likely the start of the response
            response_start = i
            break
    
    if response_start > 0:
        response = '\n\n'.join(blocks[response_start:])
        # Only use filtered version if the response part is substantial
        if len(response.strip()) > 20:
            return response.strip()
    
    return text


# ============= Web Search Tool =============

async def web_search(query: str) -> Dict[str, Any]:
    """Search the web for information about APIs, services, automation patterns, and best practices.
    
    Use this to research:
    - API documentation and authentication methods
    - Webhook payload formats for specific services
    - Best practices for automation patterns
    - Service-specific integration details
    
    Args:
        query: Search query (e.g., "Stripe webhook events format", "GitHub API authentication")
    
    Returns:
        dict with search results containing title, body, and href for each result
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                })
        return {"status": "success", "results": results}
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return {"status": "error", "message": f"Search failed: {str(e)}. Continue without web search results."}


# ============= Core MCP Tools (Work without n8n API) =============

async def get_workflow_recipe(recipe_name: Optional[str] = None) -> Dict[str, Any]:
    """Get a pre-built workflow recipe to use as a starting point.
    
    If recipe_name is not provided, returns a list of available recipes and their descriptions.
    If recipe_name is provided, returns the complete workflow structure (nodes and connections)
    that you can customize instead of building from scratch.
    
    Args:
        recipe_name: The name of the recipe to get (e.g., 'schedule_fetch_process', 'loop_per_item')
        
    Returns:
        dict with recipe details or list of available recipes
    """
    from agent.workflow_recipes import get_recipe, list_recipes
    
    try:
        if not recipe_name:
            return {"status": "success", "available_recipes": list_recipes()}
            
        recipe = get_recipe(recipe_name)
        if not recipe:
            return {"status": "error", "message": f"Recipe '{recipe_name}' not found. Call without arguments to see available recipes."}
            
        return {"status": "success", "recipe": recipe}
    except Exception as e:
        return {"status": "error", "message": f"Failed to get recipe: {str(e)}"}


async def search_nodes(query: str) -> Dict[str, Any]:
    """Search for n8n nodes by name or description. Use this to find the correct node type identifier.
    
    Args:
        query: Search term (e.g., "slack", "http request", "google sheets", "webhook")
    
    Returns:
        dict with matching nodes including their type identifiers and descriptions
    """
    try:
        client = get_mcp_client()
        result = await client.search_nodes(query)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_node_documentation(node_type: str) -> Dict[str, Any]:
    """Get detailed documentation for a specific n8n node type. ALWAYS call this before using any node.
    
    Returns the node's required parameters, available options, correct typeVersion, and usage examples.
    
    Args:
        node_type: Full node type identifier (e.g., 'n8n-nodes-base.httpRequest', 'n8n-nodes-base.slack')
    
    Returns:
        dict with node documentation including parameters, typeVersion, and configuration options
    """
    try:
        client = get_mcp_client()
        result = await client.get_node(node_type, mode="docs", detail="full")
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def search_workflow_templates(query: str) -> Dict[str, Any]:
    """Search n8n community workflow templates by keyword. ALWAYS call this first when a user requests a workflow.
    
    Templates are real, working workflows built by the community. Study them to learn correct
    node configurations, connections patterns, and best practices before building your own.
    
    Args:
        query: Search keywords (e.g., "slack notification github", "shopify google sheets sync")
    
    Returns:
        dict with matching templates including their IDs, names, and descriptions
    """
    try:
        client = get_mcp_client()
        result = await client.search_templates(query, search_mode="keyword")
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_workflow_template(template_id: str) -> Dict[str, Any]:
    """Get the full configuration of a specific workflow template. Use after search_workflow_templates.
    
    Study the returned nodes, connections, and parameters to understand how the workflow is built.
    Use this as a foundation to create customized workflows.
    
    Args:
        template_id: The template ID from search_workflow_templates results
    
    Returns:
        dict with complete workflow including nodes, connections, and settings
    """
    try:
        client = get_mcp_client()
        result = await client.get_template(template_id, mode="full")
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def validate_workflow_json(workflow_json: str) -> Dict[str, Any]:
    """Validate a workflow JSON structure BEFORE creating it. Catches errors in node configs and connections.
    
    Args:
        workflow_json: JSON string with format {"nodes": [...], "connections": {...}}
    
    Returns:
        dict with validation results including errors, warnings, and suggestions
    """
    try:
        workflow = json.loads(workflow_json) if isinstance(workflow_json, str) else workflow_json
        client = get_mcp_client()
        result = await client.validate_workflow(workflow)
        return {"status": "success", "data": result}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============= n8n Management Tools (Require n8n API Config) =============

async def list_workflows() -> Dict[str, Any]:
    """List all workflows from connected n8n instance."""
    try:
        n8n_creds = get_n8n_credentials()
        if n8n_creds and n8n_creds.get("instance_url") and n8n_creds.get("api_key"):
            logger.info("Using direct n8n client for list_workflows (agent)")
            direct_client = create_n8n_client(n8n_creds["instance_url"], n8n_creds["api_key"])
            workflows = await direct_client.list_workflows()
            return {
                "status": "success",
                "count": len(workflows),
                "workflows": [{"id": w.get("id"), "name": w.get("name"), "active": w.get("active")} for w in workflows]
            }

        logger.info("Using MCP client for list_workflows (agent)")
        client = get_mcp_client()
        workflows = await client.list_workflows()
        return {
            "status": "success",
            "count": len(workflows),
            "workflows": [{"id": w.get("id"), "name": w.get("name"), "active": w.get("active")} for w in workflows]
        }
    except Exception as e:
        logger.error(f"list_workflows failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get a specific workflow by ID from connected n8n instance."""
    try:
        n8n_creds = get_n8n_credentials()
        if n8n_creds and n8n_creds.get("instance_url") and n8n_creds.get("api_key"):
            logger.info(f"Using direct n8n client for get_workflow {workflow_id} (agent)")
            direct_client = create_n8n_client(n8n_creds["instance_url"], n8n_creds["api_key"])
            workflow = await direct_client.get_workflow(workflow_id)
        else:
            logger.info(f"Using MCP client for get_workflow {workflow_id} (agent)")
            client = get_mcp_client()
            workflow = await client.get_workflow(workflow_id)

        if workflow:
            return {"status": "success", "workflow": workflow}
        return {"status": "error", "message": f"Workflow {workflow_id} not found"}
    except Exception as e:
        logger.error(f"get_workflow failed for {workflow_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def _auto_connect_nodes(nodes: List[Dict]) -> Dict[str, Any]:
    """Automatically connect nodes in a linear sequence (1->2->3)."""
    if not nodes or len(nodes) < 2:
        return {}

    connections = {}
    for i in range(len(nodes) - 1):
        source_node = nodes[i].get("name")
        target_node = nodes[i + 1].get("name")

        if source_node and target_node:
            connections[source_node] = {
                "main": [[{"node": target_node, "type": "main", "index": 0}]]
            }
    return connections


async def create_workflow(name: str, description: str, nodes_json: str) -> Dict[str, Any]:
    """Create a new n8n workflow. You MUST provide both nodes AND connections.
    
    Args:
        name: Descriptive workflow name (e.g., "GitHub Stars to Slack Notification")
        description: Brief description of what the workflow does
        nodes_json: JSON string containing BOTH nodes and connections. Format:
            {
              "nodes": [
                {
                  "id": "uuid-string",
                  "name": "Descriptive Node Name",
                  "type": "n8n-nodes-base.nodeType",
                  "typeVersion": 1.2,
                  "position": [250, 300],
                  "parameters": { ... populated from get_node_documentation ... }
                }
              ],
              "connections": {
                "Source Node Name": {
                  "main": [[{"node": "Target Node Name", "type": "main", "index": 0}]]
                }
              }
            }
    
    IMPORTANT:
    - ALWAYS include connections — do not rely on auto-connection
    - ALWAYS populate parameters from get_node_documentation — never use empty {}
    - Call validate_workflow_json first to catch errors before creating
    
    Returns:
        dict with status, workflow_id, and name
    """
    try:
        nodes_data = json.loads(nodes_json) if isinstance(nodes_json, str) else nodes_json

        if isinstance(nodes_data, list):
            nodes = nodes_data
            connections = {}
        else:
            nodes = nodes_data.get("nodes", [])
            connections = nodes_data.get("connections", {})

        if not isinstance(nodes, list):
            nodes = []

        # AUTO-CONNECT fallback: If we have nodes but no connections, connect them linearly
        # This is a safety net — the agent SHOULD provide explicit connections
        if nodes and not connections and len(nodes) > 1:
            logger.warning(f"No connections provided for workflow '{name}' — auto-connecting linearly (agent should provide connections)")
            connections = _auto_connect_nodes(nodes)

        n8n_creds = get_n8n_credentials()
        if n8n_creds and n8n_creds.get("instance_url") and n8n_creds.get("api_key"):
            logger.info(f"Using direct n8n client for create_workflow '{name}' (agent)")
            direct_client = create_n8n_client(n8n_creds["instance_url"], n8n_creds["api_key"])
            result = await direct_client.create_workflow(name, nodes, connections)
        else:
            logger.info(f"Using MCP client for create_workflow '{name}' (agent)")
            client = get_mcp_client()
            result = await client.create_workflow(name, nodes, connections)

        return {"status": "success", "workflow_id": result.get("id"), "name": name}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        logger.error(f"create_workflow failed for '{name}': {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def update_workflow(workflow_id: str, updates_json: str) -> Dict[str, Any]:
    """Update an existing n8n workflow. Provide the workflow ID and a JSON object with fields to update (name, nodes, connections, active)."""
    try:
        updates = json.loads(updates_json) if isinstance(updates_json, str) else updates_json

        n8n_creds = get_n8n_credentials()
        if n8n_creds and n8n_creds.get("instance_url") and n8n_creds.get("api_key"):
            logger.info(f"Using direct n8n client for update_workflow {workflow_id} (agent)")
            direct_client = create_n8n_client(n8n_creds["instance_url"], n8n_creds["api_key"])
            result = await direct_client.update_workflow(workflow_id, updates)
        else:
            logger.info(f"Using MCP client for update_workflow {workflow_id} (agent)")
            client = get_mcp_client()
            result = await client.update_workflow(workflow_id, updates)

        return {
            "status": "success",
            "workflow_id": result.get("id", workflow_id),
            "message": f"Workflow {workflow_id} updated successfully"
        }
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        logger.error(f"update_workflow failed for {workflow_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def execute_workflow(workflow_id: str, input_data: Optional[str] = None) -> Dict[str, Any]:
    """Execute a workflow with optional input data."""
    try:
        parsed_input = None
        if input_data:
            parsed_input = json.loads(input_data) if isinstance(input_data, str) else input_data

        n8n_creds = get_n8n_credentials()

        # Try direct n8n client first, but fall back to MCP if it fails
        if n8n_creds and n8n_creds.get("instance_url") and n8n_creds.get("api_key"):
            try:
                logger.info(f"Trying direct n8n client for execute_workflow {workflow_id}")
                direct_client = create_n8n_client(n8n_creds["instance_url"], n8n_creds["api_key"])
                result = await direct_client.execute_workflow(workflow_id, parsed_input)
                return {"status": "success", "execution_id": result.get("id"), "result": result}
            except Exception as direct_error:
                logger.warning(f"Direct n8n execute failed, falling back to MCP: {direct_error}")

        # Fall back to MCP for execution
        logger.info(f"Using MCP client for execute_workflow {workflow_id} (agent)")
        client = get_mcp_client()
        result = await client.execute_workflow(workflow_id, parsed_input)

        return {"status": "success", "execution_id": result.get("id"), "result": result}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid input JSON: {str(e)}"}
    except Exception as e:
        logger.error(f"execute_workflow failed for {workflow_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# ============= ADK Agent =============

APP_NAME = "flowgent"
USER_ID = "flowgent_user"

# Singletons
_session_service: Optional[InMemorySessionService] = None
_runner: Optional[Runner] = None
_agent: Optional[Agent] = None


def create_flowgent_agent() -> Agent:
    """Create the Flowgent agent with all MCP tools."""
    return Agent(
        name="flowgent",
        model=get_agent_model(),
        description="AI assistant for n8n workflow automation with MCP integration",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            # Research tools (use FIRST)
            get_workflow_recipe,
            web_search,
            search_workflow_templates,
            get_workflow_template,
            search_nodes,
            get_node_documentation,
            # Validation
            validate_workflow_json,
            # n8n management tools (need n8n API)
            list_workflows,
            get_workflow,
            create_workflow,
            update_workflow,
            execute_workflow,
        ]
    )


def get_session_service() -> InMemorySessionService:
    global _session_service
    if _session_service is None:
        _session_service = InMemorySessionService()
    return _session_service


def reset_agent():
    """Reset cached agent/runner/session to pick up new environment variables."""
    global _session_service, _runner, _agent
    _session_service = None
    _runner = None
    _agent = None


def _init_env():
    """Initialize environment for LLM provider."""
    # Validate key exists (will raise ValueError if missing)
    get_llm_api_key()


def get_agent() -> Agent:
    global _agent
    if _agent is None:
        _init_env()
        _agent = create_flowgent_agent()
    return _agent


def get_runner() -> Runner:
    global _runner
    if _runner is None:
        _init_env()
        _runner = Runner(
            agent=get_agent(),
            app_name=APP_NAME,
            session_service=get_session_service()
        )
    return _runner


async def ensure_session(session_id: str):
    """Ensure session exists - only create if it doesn't exist."""
    svc = get_session_service()
    session = await svc.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    if session is None:
        logger.info(f"Creating new session: {session_id}")
        await svc.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)


async def chat_with_agent(message: str, session_id: str = "default_session") -> str:
    """Send a message to the agent and get a response."""
    try:
        runner = get_runner()
        await ensure_session(session_id)

        user_content = types.Content(role="user", parts=[types.Part(text=message)])

        final_response = ""

        # Retry with exponential backoff for rate limit errors
        max_retries = 3
        retry_delays = [5, 15, 30]  # seconds between retries

        last_error = None
        for attempt in range(max_retries):
            try:
                final_response = ""
                async for event in runner.run_async(
                    user_id=USER_ID,
                    session_id=session_id,
                    new_message=user_content
                ):
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    final_response += part.text
                # Success — break out of retry loop
                last_error = None
                break
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                is_rate_limit = (
                    "ratelimit" in error_str or
                    "rate_limit" in error_str or
                    "too many requests" in error_str or
                    "request queue is full" in error_str or
                    "429" in error_str or
                    "503" in error_str
                )
                if is_rate_limit and attempt < max_retries - 1:
                    wait_time = retry_delays[attempt]
                    logger.warning(
                        f"Rate limit hit on attempt {attempt + 1}/{max_retries}. "
                        f"Retrying in {wait_time}s... Error: {e}"
                    )
                    import asyncio
                    await asyncio.sleep(wait_time)
                    continue
                # Not a rate limit error, or out of retries — stop retrying
                break

        if last_error is not None:
            e = last_error
            logger.error(f"Error during agent run: {e}", exc_info=True)

            error_msg = str(e).lower()

            # Rate limit / queue full error — give friendly message after all retries exhausted
            is_rate_limit = (
                "ratelimit" in error_msg or
                "rate_limit" in error_msg or
                "too many requests" in error_msg or
                "request queue is full" in error_msg or
                "429" in error_msg or
                ("503" in error_msg and "queue" in error_msg)
            )
            if is_rate_limit:
                # Try fallback model if configured
                fallback_model = get_fallback_model()
                if fallback_model:
                    logger.info(f"Primary model rate limited. Switching to fallback: {FALLBACK_LLM_MODEL}")
                    try:
                        # Create a temporary agent with the fallback model
                        fallback_agent = Agent(
                            name="flowgent_fallback",
                            model=fallback_model,
                            description="AI assistant for n8n workflow automation (fallback)",
                            instruction=SYSTEM_INSTRUCTION,
                            tools=[
                                web_search,
                                search_workflow_templates,
                                get_workflow_template,
                                search_nodes,
                                get_node_documentation,
                                validate_workflow_json,
                                list_workflows,
                                get_workflow,
                                create_workflow,
                                update_workflow,
                                execute_workflow,
                            ]
                        )
                        fallback_runner = Runner(
                            agent=fallback_agent,
                            app_name=APP_NAME,
                            session_service=get_session_service()
                        )
                        # Create a new session for fallback to avoid conflicts
                        fallback_session = f"{session_id}_fallback"
                        await ensure_session(fallback_session)
                        
                        final_response = ""
                        async for event in fallback_runner.run_async(
                            user_id=USER_ID,
                            session_id=fallback_session,
                            new_message=user_content
                        ):
                            if event.is_final_response():
                                if event.content and event.content.parts:
                                    for part in event.content.parts:
                                        if hasattr(part, 'text') and part.text:
                                            final_response += part.text
                        
                        if final_response:
                            return f"*(Handled by GPT-5.2 — Kimi K2.5 was busy)*\n\n{final_response}"
                    except Exception as fallback_error:
                        logger.error(f"Fallback model also failed: {fallback_error}", exc_info=True)
                        return (
                            "⏳ **Both Models Unavailable**\n\n"
                            f"Primary model (Kimi K2.5) hit rate limits, and fallback (GPT-5.2) also failed:\n"
                            f"`{str(fallback_error)[:200]}`\n\n"
                            "Please wait 1-2 minutes and try again."
                        )
                
                # No fallback configured
                return (
                    "⏳ **Model Rate Limit Reached**\n\n"
                    "Your Azure AI (Kimi K2.5) endpoint is currently overloaded — "
                    "the request queue is full. I retried 3 times but the model is still busy.\n\n"
                    "**What to do:**\n"
                    "1. Wait **30–60 seconds** and send your message again\n"
                    "2. For complex workflow requests, try breaking them into smaller steps\n"
                    "3. If this keeps happening, check your Azure AI quota in the Azure portal"
                )

            if "api_key" in error_msg or "missing key" in error_msg or "unauthorized" in error_msg:
                is_openrouter = USE_LITELLM and "openrouter" in LLM_MODEL.lower()
                is_azure = USE_LITELLM and "azure" in LLM_MODEL.lower()
                
                if is_openrouter:
                    return (
                        "⚠️ **API Key Not Configured**\n\n"
                        "The OpenRouter API key is not set. Please configure it:\n\n"
                        "1. Get your free API key from: https://openrouter.ai/keys\n"
                        "2. Add it to backend/.env: `OPENROUTER_API_KEY=your-key-here`\n"
                        "3. Restart the backend"
                    )
                elif is_azure:
                    return (
                        "⚠️ **Azure Configuration Missing**\n\n"
                        "Azure AI settings are not fully configured. Please check your `.env` file:\n\n"
                        "1. `AZURE_AI_API_KEY=your-api-key`\n"
                        "2. `AZURE_API_BASE=https://your-endpoint.services.ai.azure.com/models`\n"
                        "3. Restart the backend after adding the keys."
                    )
                else:
                    return (
                        "⚠️ **API Key Not Configured**\n\n"
                        "The Gemini API key is not set. Please configure it:\n\n"
                        "1. Get your API key from: https://aistudio.google.com/apikey\n"
                        "2. Add it to backend/.env: `GOOGLE_GENAI_API_KEY=your-key-here`\n"
                        "3. Restart the backend"
                    )

            return f"Error processing request: {str(e)}"

        # Strip reasoning/thinking text from Kimi-K2-Thinking models
        if final_response and "thinking" in LLM_MODEL.lower():
            final_response = _strip_reasoning(final_response)
        
        return final_response if final_response else "I processed your request but have no response."
    except ValueError as e:
        error_msg = str(e)
        if "OPENROUTER_API_KEY" in error_msg:
            return (
                "⚠️ **API Key Not Configured**\n\n"
                "The OpenRouter API key is not set. Please configure it in your backend .env file:\n\n"
                "1. Get your free API key from: https://openrouter.ai/keys\n"
                "2. Add it to backend/.env: `OPENROUTER_API_KEY=your-key-here`\n"
                "3. Restart the backend"
            )
        if "AZURE" in error_msg:
            return (
                "⚠️ **Azure Configuration Missing**\n\n"
                "The Azure API keys are not set. Please configure them in your backend .env file:\n\n"
                "1. `AZURE_AI_API_KEY=your-api-key`\n"
                "2. `AZURE_API_BASE=https://your-endpoint.services.ai.azure.com/models`\n"
                "3. Restart the backend"
            )
        if "GOOGLE_GENAI_API_KEY" in error_msg:
            return (
                "⚠️ **API Key Not Configured**\n\n"
                "The Gemini API key is not set. Please configure it in your backend .env file:\n\n"
                "1. Get your API key from: https://aistudio.google.com/apikey\n"
                "2. Add it to backend/.env: `GOOGLE_GENAI_API_KEY=your-key-here`\n"
                "3. Restart the backend"
            )
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat_with_agent: {e}", exc_info=True)
        return f"An unexpected error occurred: {str(e)}"
