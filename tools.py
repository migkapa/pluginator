from agents import function_tool
import subprocess
import os
import shutil
import json
from typing import List, Dict, Any
from loguru import logger
import asyncio
from pathlib import Path

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

# --- Enhanced File Tools ---
@function_tool
def write_file(filename: str, content: str) -> str:
    """Write content to a file with proper error handling and directory creation.
    
    Args:
        filename: Path to the file to write
        content: Content to write to the file
    """
    try:
        # Ensure the directory exists
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file with UTF-8 encoding
        filepath.write_text(content, encoding='utf-8')
        
        logger.debug(f"Successfully wrote {filename} ({len(content)} bytes)")
        return f"Successfully written {filename}"
    except PermissionError:
        error_msg = f"Permission denied writing to {filename}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except OSError as e:
        error_msg = f"OS error writing {filename}: {e}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        logger.exception(f"Unexpected error writing {filename}")
        return f"Error writing {filename}: {str(e)}"

@function_tool
def read_file(filename: str) -> str:
    """Read the contents of a file.
    
    Args:
        filename: Path to the file to read
    """
    try:
        filepath = Path(filename)
        if not filepath.exists():
            return f"Error: File {filename} does not exist"
        
        content = filepath.read_text(encoding='utf-8')
        logger.debug(f"Successfully read {filename} ({len(content)} bytes)")
        return content
    except PermissionError:
        error_msg = f"Permission denied reading {filename}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except UnicodeDecodeError:
        error_msg = f"Unable to decode {filename} as UTF-8"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        logger.exception(f"Error reading {filename}")
        return f"Error reading {filename}: {str(e)}"

@function_tool
def list_files(directory: str, pattern: str = "*") -> str:
    """List files in a directory matching a pattern.
    
    Args:
        directory: Directory path to list
        pattern: Glob pattern to match files (default: "*")
    """
    try:
        dirpath = Path(directory)
        if not dirpath.exists():
            return f"Error: Directory {directory} does not exist"
        
        files = list(dirpath.glob(pattern))
        file_list = [str(f.relative_to(dirpath)) for f in files if f.is_file()]
        
        logger.debug(f"Listed {len(file_list)} files in {directory}")
        return json.dumps(file_list, indent=2)
    except Exception as e:
        logger.exception(f"Error listing files in {directory}")
        return f"Error listing files: {str(e)}"

@function_tool
def ensure_directory(directory: str) -> str:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
        return f"Directory ensured: {directory}"
    except PermissionError:
        error_msg = f"Permission denied creating directory {directory}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        logger.exception(f"Error ensuring directory {directory}")
        return f"Error: {str(e)}"

@function_tool
def delete_file(filename: str) -> str:
    """Delete a file if it exists.
    
    Args:
        filename: Path to the file to delete
    """
    try:
        filepath = Path(filename)
        if filepath.exists():
            filepath.unlink()
            logger.debug(f"Deleted file: {filename}")
            return f"Deleted {filename}"
        else:
            return f"File {filename} does not exist"
    except PermissionError:
        error_msg = f"Permission denied deleting {filename}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        logger.exception(f"Error deleting {filename}")
        return f"Error: {str(e)}"

# --- Enhanced Subprocess Tools ---
@function_tool
async def run_command_async(command: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run a command asynchronously with timeout support.
    
    Args:
        command: Command and arguments as a list
        timeout: Timeout in seconds (default: 300)
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.terminate()
            await process.wait()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": ""
            }
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode('utf-8', errors='replace'),
            "stderr": stderr.decode('utf-8', errors='replace')
        }
    except Exception as e:
        logger.exception(f"Error running command: {' '.join(command)}")
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }

@function_tool
def docker_compose_up(detached: bool = True, build: bool = False) -> str:
    """Start Docker Compose services with enhanced options.
    
    Args:
        detached: Run containers in detached mode (default: True)
        build: Build images before starting containers (default: False)
    """
    logger.info("Running docker-compose up...")
    try:
        cmd = ["docker-compose", "up"]
        if detached:
            cmd.append("-d")
        if build:
            cmd.append("--build")
            
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.success("Docker containers started.")
        logger.debug(f"docker-compose up output: {proc.stdout}")
        if proc.stderr:
            logger.debug(f"docker-compose stderr: {proc.stderr}")
        return f"Success: {proc.stdout}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run docker-compose up: {e}")
        return f"Error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"
    except FileNotFoundError:
        error_msg = "docker-compose command not found. Please ensure Docker Compose is installed."
        logger.error(error_msg)
        return f"Error: {error_msg}"

@function_tool
def activate_plugin(plugin_slug: str, network_wide: bool = False) -> str:
    """Activate a WordPress plugin with enhanced options.
    
    Args:
        plugin_slug: The plugin slug to activate
        network_wide: Whether to activate the plugin network-wide (default: False)
    """
    try:
        cmd = ["docker-compose", "exec", "-T", "wordpress", "wp", "plugin", "activate", plugin_slug]
        if network_wide:
            cmd.append("--network")
            
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.success(f"Plugin {plugin_slug} activated.")
        logger.debug(f"wp plugin activate output: {proc.stdout}")
        return f"Success: {proc.stdout}"
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout: Plugin activation took too long for {plugin_slug}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to activate plugin {plugin_slug}: {e}")
        return f"Error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"
    except FileNotFoundError:
        error_msg = "docker-compose command not found"
        logger.error(error_msg)
        return f"Error: {error_msg}"

@function_tool
def list_plugins(status: str = "all") -> str:
    """List WordPress plugins with filtering options.
    
    Args:
        status: Filter by plugin status (all, active, inactive, must-use, drop-in)
    """
    logger.info(f"Listing plugins with status: {status}...")
    try:
        cmd = ["docker-compose", "exec", "-T", "wordpress", "wp", "plugin", "list"]
        if status != "all":
            cmd.extend(["--status", status])
        cmd.append("--format=json")
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # Parse JSON output for better formatting
        try:
            plugins = json.loads(proc.stdout)
            logger.success(f"Listed {len(plugins)} plugins.")
            return json.dumps(plugins, indent=2)
        except json.JSONDecodeError:
            # Fallback to raw output if not JSON
            logger.success("Listed plugins.")
            return proc.stdout
            
    except subprocess.TimeoutExpired:
        error_msg = "Timeout: Listing plugins took too long"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list plugins: {e}")
        return f"Error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"
    except FileNotFoundError:
        error_msg = "docker-compose command not found"
        logger.error(error_msg)
        return f"Error: {error_msg}"

@function_tool
def check_plugin_syntax(plugin_path: str) -> str:
    """Check PHP syntax of a plugin file.
    
    Args:
        plugin_path: Path to the plugin PHP file to check
    """
    try:
        cmd = ["php", "-l", plugin_path]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode == 0:
            logger.success(f"PHP syntax OK for {plugin_path}")
            return f"Syntax OK: {proc.stdout}"
        else:
            logger.error(f"PHP syntax errors in {plugin_path}")
            return f"Syntax Error: {proc.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Error: Syntax check timed out for {plugin_path}"
    except FileNotFoundError:
        return "Error: PHP CLI not found. Please ensure PHP is installed."
    except Exception as e:
        logger.exception(f"Error checking syntax for {plugin_path}")
        return f"Error: {str(e)}"