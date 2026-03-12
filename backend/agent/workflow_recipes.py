"""Pre-built workflow recipes for common automation patterns.

Each recipe is a complete workflow structure (nodes + connections) that the agent
can customize instead of building from scratch. This eliminates 3-4 LLM calls
per workflow by skipping template search, node search, and doc lookup.
"""

RECIPES = {
    "schedule_fetch_process": {
        "name": "Schedule + Fetch + Process",
        "description": "Fetches data from an API on a schedule, processes it with Code, outputs result.",
        "trigger": "schedule",
        "use_when": "User wants periodic data fetching from a public API with transformation",
        "nodes": [
            {
                "name": "Daily Schedule",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [250, 300],
                "parameters": {
                    "rule": {
                        "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
                    }
                }
            },
            {
                "name": "Fetch Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [450, 300],
                "parameters": {
                    "method": "GET",
                    "url": "={{REPLACE_URL}}",
                    "options": {}
                }
            },
            {
                "name": "Process Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [650, 300],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// REPLACE: Process the fetched data\nconst input = $input.first().json;\nreturn [{ json: { result: input } }];"
                }
            }
        ],
        "connections": {
            "Daily Schedule": {"main": [[{"node": "Fetch Data", "type": "main", "index": 0}]]},
            "Fetch Data": {"main": [[{"node": "Process Data", "type": "main", "index": 0}]]}
        }
    },

    "loop_per_item": {
        "name": "Loop: Fetch Details Per Item",
        "description": "Fetches a list, loops through each item to get details, aggregates results.",
        "trigger": "schedule_or_manual",
        "use_when": "User wants to fetch a list then get details for each item (e.g., top stories, user profiles)",
        "nodes": [
            {
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [250, 300],
                "parameters": {
                    "rule": {
                        "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
                    }
                }
            },
            {
                "name": "Fetch List",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [450, 300],
                "parameters": {
                    "method": "GET",
                    "url": "={{REPLACE_LIST_URL}}",
                    "options": {}
                }
            },
            {
                "name": "Extract Items",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [650, 300],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// IMPORTANT: Handle n8n's JSON array wrapping\nconst input = $input.first().json;\nconst arr = Array.isArray(input) ? input : Object.values(input);\nreturn arr.slice(0, 10).map(id => ({ json: { itemId: id } }));"
                }
            },
            {
                "name": "Fetch Item Details",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [850, 300],
                "parameters": {
                    "method": "GET",
                    "url": "={{REPLACE_DETAIL_URL}}",
                    "options": {}
                }
            },
            {
                "name": "Aggregate Results",
                "type": "n8n-nodes-base.aggregate",
                "typeVersion": 1,
                "position": [1050, 300],
                "parameters": {
                    "aggregate": "aggregateAllItemData",
                    "options": {}
                }
            },
            {
                "name": "Format Output",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1250, 300],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// REPLACE: Format the aggregated results\nconst items = $input.first().json;\nreturn [{ json: { results: items, count: Object.keys(items).length } }];"
                }
            }
        ],
        "connections": {
            "Schedule Trigger": {"main": [[{"node": "Fetch List", "type": "main", "index": 0}]]},
            "Fetch List": {"main": [[{"node": "Extract Items", "type": "main", "index": 0}]]},
            "Extract Items": {"main": [[{"node": "Fetch Item Details", "type": "main", "index": 0}]]},
            "Fetch Item Details": {"main": [[{"node": "Aggregate Results", "type": "main", "index": 0}]]},
            "Aggregate Results": {"main": [[{"node": "Format Output", "type": "main", "index": 0}]]}
        }
    },

    "webhook_process_respond": {
        "name": "Webhook + Process + Respond",
        "description": "Receives webhook input, processes data, responds with result.",
        "trigger": "webhook",
        "use_when": "User wants an API endpoint that processes input and returns a response",
        "nodes": [
            {
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [250, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "={{REPLACE_PATH}}",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "name": "Process Input",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [450, 300],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// Access webhook body via $json\nconst input = $json;\n// REPLACE: Process the input\nreturn [{ json: { result: input } }];"
                }
            },
            {
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [650, 300],
                "parameters": {
                    "respondWith": "json",
                    "options": {}
                }
            }
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Process Input", "type": "main", "index": 0}]]},
            "Process Input": {"main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]}
        }
    },

    "parallel_fetch_merge": {
        "name": "Parallel Fetch + Merge",
        "description": "Fetches data from multiple APIs in parallel, merges results, processes combined data.",
        "trigger": "any",
        "use_when": "User wants to call multiple APIs simultaneously and combine their results",
        "nodes": [
            {
                "name": "Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [250, 300],
                "parameters": {}
            },
            {
                "name": "Fetch Source A",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [450, 200],
                "parameters": {"method": "GET", "url": "={{REPLACE_URL_A}}", "options": {}}
            },
            {
                "name": "Fetch Source B",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [450, 400],
                "parameters": {"method": "GET", "url": "={{REPLACE_URL_B}}", "options": {}}
            },
            {
                "name": "Merge Results",
                "type": "n8n-nodes-base.merge",
                "typeVersion": 3,
                "position": [650, 300],
                "parameters": {"mode": "combine", "combineBy": "combineAll"}
            },
            {
                "name": "Process Combined",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [850, 300],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// REPLACE: Process the merged data\nconst combined = $input.all();\nreturn [{ json: { result: combined } }];"
                }
            }
        ],
        "connections": {
            "Trigger": {"main": [[
                {"node": "Fetch Source A", "type": "main", "index": 0},
                {"node": "Fetch Source B", "type": "main", "index": 0}
            ]]},
            "Fetch Source A": {"main": [[{"node": "Merge Results", "type": "main", "index": 0}]]},
            "Fetch Source B": {"main": [[{"node": "Merge Results", "type": "main", "index": 1}]]},
            "Merge Results": {"main": [[{"node": "Process Combined", "type": "main", "index": 0}]]}
        }
    },

    "conditional_branching": {
        "name": "Fetch + Conditional Branch",
        "description": "Fetches data, checks a condition, takes different paths based on result.",
        "trigger": "schedule",
        "use_when": "User wants different actions based on data conditions (alerts, filtering)",
        "nodes": [
            {
                "name": "Schedule",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [250, 300],
                "parameters": {
                    "rule": {
                        "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
                    }
                }
            },
            {
                "name": "Fetch Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [450, 300],
                "parameters": {"method": "GET", "url": "={{REPLACE_URL}}", "options": {}}
            },
            {
                "name": "Check Condition",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [650, 300],
                "parameters": {
                    "conditions": {
                        "options": {"caseSensitive": True, "leftValue": ""},
                        "conditions": [{"leftValue": "={{ $json.REPLACE_FIELD }}", "rightValue": "REPLACE_VALUE", "operator": {"type": "string", "operation": "equals"}}],
                        "combinator": "and"
                    }
                }
            },
            {
                "name": "Handle True",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [850, 200],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// REPLACE: Handle true condition\nreturn [{ json: { action: 'true_path', data: $json } }];"
                }
            },
            {
                "name": "Handle False",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [850, 400],
                "parameters": {
                    "language": "javaScript",
                    "jsCode": "// REPLACE: Handle false condition\nreturn [{ json: { action: 'false_path', data: $json } }];"
                }
            }
        ],
        "connections": {
            "Schedule": {"main": [[{"node": "Fetch Data", "type": "main", "index": 0}]]},
            "Fetch Data": {"main": [[{"node": "Check Condition", "type": "main", "index": 0}]]},
            "Check Condition": {"main": [
                [{"node": "Handle True", "type": "main", "index": 0}],
                [{"node": "Handle False", "type": "main", "index": 0}]
            ]}
        }
    }
}


def get_recipe(recipe_name: str) -> dict:
    """Get a workflow recipe by name."""
    return RECIPES.get(recipe_name)


def list_recipes() -> list:
    """List all available recipe names with descriptions."""
    return [
        {"name": k, "description": v["description"], "trigger": v["trigger"], "use_when": v["use_when"]}
        for k, v in RECIPES.items()
    ]
