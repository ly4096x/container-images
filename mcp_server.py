#!/usr/bin/env python3
import sys
import json
import logging
import os
import importlib.util

# Set up logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')

TOOLS = {}

def load_tools():
    tools_dir = os.path.join(os.path.dirname(__file__), "tools")
    if not os.path.exists(tools_dir):
        logging.warning("No 'tools' directory found.")
        return

    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            file_path = os.path.join(tools_dir, filename)
            module_name = filename[:-3]
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "TOOL_DEFINITION") and hasattr(module, "handler"):
                    tool_def = module.TOOL_DEFINITION
                    TOOLS[tool_def["name"]] = {
                        "definition": tool_def,
                        "handler": module.handler
                    }
                    logging.info(f"Loaded tool: {tool_def['name']}")
                else:
                    logging.warning(f"Skipping {filename}: Missing TOOL_DEFINITION or handler")
            except Exception as e:
                logging.error(f"Failed to load tool {filename}: {e}")

def handle_list_tools(request):
    return {
        "tools": [t["definition"] for t in TOOLS.values()]
    }

def handle_call_tool(request):
    params = request.get("params", {})
    name = params.get("name")
    arguments = params.get("arguments", {})

    if name in TOOLS:
        try:
            return TOOLS[name]["handler"](arguments)
        except Exception as e:
            raise ValueError(f"Error executing tool {name}: {str(e)}")
    else:
        raise ValueError(f"Unknown tool: {name}")

def main():
    load_tools()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            msg_id = request.get("id")

            response = {
                "jsonrpc": "2.0",
                "id": msg_id
            }

            try:
                if method == "tools/list":
                    response["result"] = handle_list_tools(request)
                elif method == "tools/call":
                    response["result"] = handle_call_tool(request)
                else:
                    continue
            except Exception as e:
                response["error"] = {
                    "code": -32603,
                    "message": str(e)
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            logging.error("Invalid JSON received")
            continue
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main()
