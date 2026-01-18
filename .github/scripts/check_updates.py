import urllib.request
import json
import re
import os
import sys

def get_latest_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data["tag_name"]
    except Exception as e:
        print(f"Error fetching release for {owner}/{repo}: {e}", file=sys.stderr)
        return None

def get_latest_commit(owner, repo, branch="master"):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data["sha"]
    except Exception as e:
        print(f"Error fetching commit for {owner}/{repo}: {e}", file=sys.stderr)
        return None

def update_dockerfile(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Dockerfile not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    updates = []

    # Check Caddy Version
    match = re.search(r"ARG CADDY_VERSION=(.*)", content)
    if match:
        current_caddy = match.group(1).strip()
        latest_caddy_tag = get_latest_release("caddyserver", "caddy")
        if latest_caddy_tag:
            latest_caddy_clean = latest_caddy_tag.lstrip("v")
            if latest_caddy_clean != current_caddy:
                print(f"Update Caddy: {current_caddy} -> {latest_caddy_clean}")
                content = re.sub(r"ARG CADDY_VERSION=.*",