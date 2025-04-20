from openai_agents import function_tool
import subprocess
import os

@function_tool
def write_file(filename: str, content: str) -> str:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Written {filename}"

@function_tool
def docker_compose_up() -> str:
    proc = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
    return proc.stdout + proc.stderr

@function_tool
def activate_plugin(plugin_slug: str) -> str:
    proc = subprocess.run(
        ["docker-compose", "exec", "-T", "wordpress", "wp", "plugin", "activate", plugin_slug],
        capture_output=True,
        text=True
    )
    return proc.stdout + proc.stderr

@function_tool
def list_plugins() -> str:
    proc = subprocess.run(
        ["docker-compose", "exec", "-T", "wordpress", "wp", "plugin", "list"],
        capture_output=True,
        text=True
    )
    return proc.stdout + proc.stderr