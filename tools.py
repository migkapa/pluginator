from agents import function_tool
import subprocess
import os
from loguru import logger

# --- New Logging Tools ---
@function_tool
def log_start_writing_files() -> str:
    """Logs a message indicating the start of file writing."""
    logger.info("Writing files...")
    return "Logged start of file writing."

@function_tool
def log_finish_writing_files() -> str:
    """Logs a message indicating the completion of file writing."""
    logger.success("Finished writing files.") # Using success for completion
    return "Logged finish of file writing."

@function_tool
def log_checking_compliance() -> str:
    """Logs a message indicating the start of compliance checks."""
    logger.info("Checking compliance...")
    return "Logged start of compliance check."

@function_tool
def log_testing_plugin() -> str:
    """Logs a message indicating the start of plugin testing."""
    logger.info("Activating plugin simulation...") # Changed message slightly for clarity
    return "Logged start of plugin testing."

@function_tool
def log_planning() -> str:
    """Logs a message indicating the agent is planning/thinking."""
    logger.info("Planning...")
    return "Logged planning stage."

# --- Existing Tools (Modified) ---
@function_tool
def write_file(filename: str, content: str) -> str:
    # logger.info(f"Writing file: {filename}...") # Removed per-file log
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.debug(f"Successfully wrote {filename}") # Changed level to debug
        return f"Written {filename}"
    except Exception as e:
        logger.exception(f"Failed to write {filename}")
        return f"Error writing {filename}: {e}"

@function_tool
def docker_compose_up() -> str:
    logger.info("Running docker-compose up -d...")
    try:
        proc = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True, check=True)
        logger.success("Docker containers started.")
        logger.debug(f"docker-compose up output: {proc.stdout} {proc.stderr}")
        return proc.stdout + proc.stderr
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to run docker-compose up: {e}")
        stderr = e.stderr if hasattr(e, 'stderr') else ""
        stdout = e.stdout if hasattr(e, 'stdout') else ""
        return f"Error: {e}\nstdout: {stdout}\nstderr: {stderr}"

@function_tool
def activate_plugin(plugin_slug: str) -> str:
    # logger.info(f"Activating plugin: {plugin_slug}...") # Removed this log - covered by log_testing_plugin
    try:
        proc = subprocess.run(
            ["docker-compose", "exec", "-T", "wordpress", "wp", "plugin", "activate", plugin_slug],
            capture_output=True,
            text=True,
            check=True
        )
        logger.success(f"Plugin {plugin_slug} activated.")
        logger.debug(f"wp plugin activate output: {proc.stdout} {proc.stderr}")
        return proc.stdout + proc.stderr
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to activate plugin {plugin_slug}: {e}")
        stderr = e.stderr if hasattr(e, 'stderr') else ""
        stdout = e.stdout if hasattr(e, 'stdout') else ""
        return f"Error: {e}\nstdout: {stdout}\nstderr: {stderr}"

@function_tool
def list_plugins() -> str:
    logger.info("Listing plugins...")
    try:
        proc = subprocess.run(
            ["docker-compose", "exec", "-T", "wordpress", "wp", "plugin", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.success("Listed plugins.")
        logger.debug(f"wp plugin list output: {proc.stdout} {proc.stderr}")
        return proc.stdout + proc.stderr
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to list plugins: {e}")
        stderr = e.stderr if hasattr(e, 'stderr') else ""
        stdout = e.stdout if hasattr(e, 'stdout') else ""
        return f"Error: {e}\nstdout: {stdout}\nstderr: {stderr}"