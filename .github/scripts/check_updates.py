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
        print(f"Error fetching release for {owner}/{repo}: {e}")
        return None

def get_latest_commit(owner, repo, branch="master"):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data["sha"]
    except Exception as e:
        print(f"Error fetching commit for {owner}/{repo}: {e}")
        return None

def update_dockerfile(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Dockerfile not found at {file_path}")
        sys.exit(1)

    updates = []

    # Check Caddy Version
    # Matches ARG CADDY_VERSION=...
    match = re.search(r"ARG CADDY_VERSION=(.*)", content)
    if match:
        current_caddy = match.group(1).strip()
        latest_caddy_tag = get_latest_release("caddyserver", "caddy")
        if latest_caddy_tag:
            # Strip 'v' prefix for Docker image comparison
            latest_caddy_clean = latest_caddy_tag.lstrip("v")
            if latest_caddy_clean != current_caddy:
                print(f"Update Caddy: {current_caddy} -> {latest_caddy_clean}")
                content = re.sub(r"ARG CADDY_VERSION=.*
", f"ARG CADDY_VERSION={latest_caddy_clean}", content)
                updates.append(f"Caddy: {latest_caddy_clean}")

    # Check Cache Handler Version
    match = re.search(r"ARG CACHE_HANDLER_VERSION=(.*)", content)
    if match:
        current_cache = match.group(1).strip()
        latest_cache = get_latest_release("caddyserver", "cache-handler")
        if latest_cache and latest_cache != current_cache:
            print(f"Update Cache Handler: {current_cache} -> {latest_cache}")
            content = re.sub(r"ARG CACHE_HANDLER_VERSION=.*
", f"ARG CACHE_HANDLER_VERSION={latest_cache}", content)
            updates.append(f"Cache Handler: {latest_cache}")

    # Check WebDAV Version (Commit SHA)
    match = re.search(r"ARG WEBDAV_VERSION=(.*)", content)
    if match:
        current_webdav = match.group(1).strip()
        latest_webdav = get_latest_commit("mholt", "caddy-webdav")
        if latest_webdav and latest_webdav != current_webdav:
            print(f"Update WebDAV: {current_webdav} -> {latest_webdav}")
            content = re.sub(r"ARG WEBDAV_VERSION=.*
", f"ARG WEBDAV_VERSION={latest_webdav}", content)
            updates.append(f"WebDAV: {latest_webdav[:7]}")

    if updates:
        with open(file_path, "w") as f:
            f.write(content)
        
        # Write summary to environment file for GHA
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"updates={', '.join(updates)}\n")
                f.write(f"updated=true\n")
    else:
        print("No updates found.")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("updated=false\n")

if __name__ == "__main__":
    update_dockerfile("Dockerfile")