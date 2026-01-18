import time
import json
import urllib.request
import urllib.error
import logging

TOOL_DEFINITION = {
    "name": "monitor_github_workflow",
    "description": "Monitors the latest GitHub Actions workflow run for a repository until it completes or times out.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "The owner of the GitHub repository"
            },
            "repo": {
                "type": "string",
                "description": "The name of the GitHub repository"
            },
            "timeout_minutes": {
                "type": "number",
                "description": "Timeout in minutes (default: 20)",
                "default": 20
            }
        },
        "required": ["owner", "repo"]
    }
}

def get_latest_run(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=1"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "MCP-Monitor-Server")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            runs = data.get("workflow_runs", [])
            return runs[0] if runs else None
    except urllib.error.URLError as e:
        logging.error(f"Error fetching runs: {e}")
        return None

def handler(arguments):
    owner = arguments.get("owner")
    repo = arguments.get("repo")
    timeout_minutes = arguments.get("timeout_minutes", 20)
    
    if not owner or not repo:
        raise ValueError("Missing 'owner' or 'repo' arguments")

    start_time = time.time()
    end_time = start_time + (float(timeout_minutes) * 60)
    
    logging.info(f"Starting monitor for {owner}/{repo} with timeout {timeout_minutes}m")
    
    last_status = ""
    
    while time.time() < end_time:
        run = get_latest_run(owner, repo)
        if not run:
            logging.warning("No runs found or error fetching data. Retrying in 30s...")
            time.sleep(30)
            continue

        status = run.get("status")
        conclusion = run.get("conclusion")
        run_id = run.get("id")
        html_url = run.get("html_url")

        current_display = f"Run ID: {run_id} | Status: {status}"
        if conclusion:
            current_display += f" | Conclusion: {conclusion}"
        
        if current_display != last_status:
            logging.info(current_display)
            last_status = current_display

        if status == "completed":
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "status": "completed",
                            "conclusion": conclusion,
                            "run_id": run_id,
                            "url": html_url
                        }, indent=2)
                    }
                ]
            }
        
        time.sleep(30)

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps({
                    "status": "timeout",
                    "message": f"Timeout reached after {timeout_minutes} minutes."
                }, indent=2)
            }
        ]
    }
