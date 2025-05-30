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

@function_tool
def test_with_playground(plugin_slug: str) -> str:
    """Test plugin using WordPress Playground in a headless browser.
    
    Args:
        plugin_slug: The plugin slug to test
    """
    try:
        # Import required libraries for browser automation
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            return "Error: Selenium not installed. Run: pip install selenium"
        
        # Check if plugin exists
        plugin_path = Path(f"./plugins/{plugin_slug}")
        if not plugin_path.exists():
            return f"Error: Plugin {plugin_slug} not found in ./plugins/"
        
        # Create a ZIP of the plugin for upload
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            zip_path = tmp_file.name
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(plugin_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, plugin_path.parent)
                    zipf.write(file_path, arcname)
        
        # Prepare the blueprint - using default configuration
        blueprint = {
            "landingPage": "/wp-admin/plugins.php",
            "login": True,
            "steps": [
                {
                    "step": "login",
                    "username": "admin",
                    "password": "password"
                },
                {
                    "step": "uploadFile",
                    "path": f"/wordpress/wp-content/uploads/{plugin_slug}.zip",
                    "data": {
                        "resource": "url",
                        "url": f"file://{zip_path}"
                    }
                },
                {
                    "step": "installPlugin",
                    "pluginData": {
                        "resource": "url",
                        "url": f"/wordpress/wp-content/uploads/{plugin_slug}.zip"
                    }
                },
                {
                    "step": "activatePlugin",
                    "pluginPath": f"{plugin_slug}/{plugin_slug}.php"
                }
            ]
        }
        
        # Convert blueprint to URL parameter
        import urllib.parse
        blueprint_json = json.dumps(blueprint)
        encoded_blueprint = urllib.parse.quote(blueprint_json)
        
        # Launch headless browser
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to WordPress Playground with blueprint
            playground_url = f"https://playground.wordpress.net/?blueprint={encoded_blueprint}"
            logger.info(f"Testing {plugin_slug} in WordPress Playground...")
            driver.get(playground_url)
            
            # Wait for WordPress to load
            wait = WebDriverWait(driver, 30)
            
            # Check if plugin activated successfully
            try:
                # Wait for admin dashboard or plugin page
                wait.until(EC.presence_of_element_located((By.ID, "wpadminbar")))
                
                # Navigate to plugins page if not already there
                if "/wp-admin/plugins.php" not in driver.current_url:
                    driver.get(driver.current_url.replace("/wp-admin/", "/wp-admin/plugins.php"))
                
                # Check for activation errors
                error_elements = driver.find_elements(By.CLASS_NAME, "error")
                if error_elements:
                    errors = [elem.text for elem in error_elements]
                    return f"Plugin activation failed with errors: {'; '.join(errors)}"
                
                # Check if plugin is in the active plugins list
                active_plugins = driver.find_elements(By.CSS_SELECTOR, ".active[data-plugin]")
                plugin_active = any(plugin_slug in elem.get_attribute("data-plugin") for elem in active_plugins)
                
                if plugin_active:
                    logger.success(f"Plugin {plugin_slug} successfully activated in WordPress Playground")
                    return f"Success: Plugin {plugin_slug} activated successfully in WordPress Playground"
                else:
                    return f"Warning: Plugin {plugin_slug} installed but may not be active"
                    
            except Exception as e:
                return f"Error during activation check: {str(e)}"
                
        finally:
            driver.quit()
            # Clean up temporary ZIP file
            try:
                os.unlink(zip_path)
            except:
                pass
                
    except Exception as e:
        logger.exception(f"Error testing plugin {plugin_slug} with WordPress Playground")
        return f"Error: {str(e)}"

@function_tool
def run_plugin_check(plugin_slug: str) -> str:
    """Run WordPress Plugin Check tool via WP-CLI in Docker.
    
    Args:
        plugin_slug: The plugin slug to check
    """
    try:
        # First, check if plugin-check plugin is installed
        install_cmd = [
            "docker-compose", "exec", "-T", "wordpress", 
            "wp", "plugin", "install", "plugin-check", "--activate"
        ]
        subprocess.run(install_cmd, capture_output=True, text=True, timeout=60)
        
        # Run plugin check
        cmd = [
            "docker-compose", "exec", "-T", "wordpress",
            "wp", "plugin", "check", plugin_slug
        ]
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        
        logger.info(f"Plugin check completed for {plugin_slug}")
        return f"Plugin Check Results:\n{proc.stdout}"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Plugin check failed for {plugin_slug}")
        return f"Plugin check failed:\nstdout: {e.stdout}\nstderr: {e.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Plugin check timed out for {plugin_slug}"
    except FileNotFoundError:
        return "Error: docker-compose not found. Docker environment not available."
    except Exception as e:
        logger.exception(f"Error running plugin check for {plugin_slug}")
        return f"Error: {str(e)}"

@function_tool
def run_phpunit_tests(plugin_slug: str) -> str:
    """Run PHPUnit tests for the plugin if available.
    
    Args:
        plugin_slug: The plugin slug to test
    """
    try:
        # Check if tests directory exists
        test_path = Path(f"./plugins/{plugin_slug}/tests")
        if not test_path.exists():
            # Try alternative test paths
            alt_paths = [
                Path(f"./plugins/{plugin_slug}/test"),
                Path(f"./plugins/{plugin_slug}/phpunit")
            ]
            test_path = next((p for p in alt_paths if p.exists()), None)
            
            if test_path is None:
                return f"No tests directory found for plugin {plugin_slug}"
        
        # Check for PHPUnit configuration
        config_files = ["phpunit.xml", "phpunit.xml.dist", "phpunit.xml.dist"]
        plugin_root = Path(f"./plugins/{plugin_slug}")
        config_file = next((f for f in config_files if (plugin_root / f).exists()), None)
        
        # Prepare PHPUnit command
        cmd = [
            "docker-compose", "exec", "-T", "wordpress",
            "bash", "-c",
            f"cd /var/www/html/wp-content/plugins/{plugin_slug} && "
        ]
        
        # Check if PHPUnit is installed
        phpunit_check = subprocess.run(
            ["docker-compose", "exec", "-T", "wordpress", "which", "phpunit"],
            capture_output=True
        )
        
        if phpunit_check.returncode != 0:
            # Try to use Composer-installed PHPUnit
            if (plugin_root / "vendor/bin/phpunit").exists():
                cmd[-1] += "vendor/bin/phpunit"
            else:
                # Try to install PHPUnit via Composer
                logger.info("PHPUnit not found, attempting to install via Composer...")
                composer_cmd = [
                    "docker-compose", "exec", "-T", "wordpress",
                    "bash", "-c",
                    f"cd /var/www/html/wp-content/plugins/{plugin_slug} && "
                    "composer require --dev phpunit/phpunit"
                ]
                subprocess.run(composer_cmd, capture_output=True, timeout=120)
                cmd[-1] += "vendor/bin/phpunit"
        else:
            cmd[-1] += "phpunit"
        
        # Add config file if found
        if config_file:
            cmd[-1] += f" -c {config_file}"
        
        # Run the tests
        logger.info(f"Running PHPUnit tests for {plugin_slug}...")
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if proc.returncode == 0:
            logger.success(f"PHPUnit tests passed for {plugin_slug}")
            return f"PHPUnit tests passed:\n{proc.stdout}"
        else:
            logger.error(f"PHPUnit tests failed for {plugin_slug}")
            return f"PHPUnit tests failed:\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Error: PHPUnit tests timed out for {plugin_slug}"
    except FileNotFoundError:
        return "Error: docker-compose not found. Docker environment not available."
    except Exception as e:
        logger.exception(f"Error running PHPUnit tests for {plugin_slug}")
        return f"Error: {str(e)}"

@function_tool
def generate_phpunit_bootstrap(plugin_slug: str) -> str:
    """Generate a basic PHPUnit bootstrap file for WordPress plugin testing.
    
    Args:
        plugin_slug: The plugin slug to generate bootstrap for
    """
    try:
        plugin_path = Path(f"./plugins/{plugin_slug}")
        if not plugin_path.exists():
            return f"Error: Plugin {plugin_slug} not found"
        
        # Create tests directory if it doesn't exist
        tests_dir = plugin_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Generate bootstrap.php
        bootstrap_content = f"""<?php
/**
 * PHPUnit bootstrap file for {plugin_slug}
 */

// Define test constants
define( 'WP_TESTS_PHPUNIT_POLYFILLS_PATH', dirname( __DIR__ ) . '/vendor/yoast/phpunit-polyfills' );

// Get WordPress tests directory
$_tests_dir = getenv( 'WP_TESTS_DIR' );
if ( ! $_tests_dir ) {{
    $_tests_dir = rtrim( sys_get_temp_dir(), '/\\\\' ) . '/wordpress-tests-lib';
}}

// Forward custom PHPUnit Polyfills configuration
if ( ! file_exists( $_tests_dir . '/includes/functions.php' ) ) {{
    echo "Could not find $_tests_dir/includes/functions.php" . PHP_EOL;
    exit( 1 );
}}

// Give access to tests_add_filter() function
require_once $_tests_dir . '/includes/functions.php';

/**
 * Manually load the plugin being tested
 */
function _manually_load_plugin() {{
    require dirname( dirname( __FILE__ ) ) . '/{plugin_slug}.php';
}}
tests_add_filter( 'muplugins_loaded', '_manually_load_plugin' );

// Start up the WP testing environment
require $_tests_dir . '/includes/bootstrap.php';
"""
        
        bootstrap_file = tests_dir / "bootstrap.php"
        bootstrap_file.write_text(bootstrap_content)
        
        # Generate sample test file
        sample_test_content = f"""<?php
/**
 * Sample test case for {plugin_slug}
 */

class SampleTest extends WP_UnitTestCase {{
    
    /**
     * Test that the plugin is loaded
     */
    public function test_plugin_loaded() {{
        $this->assertTrue( function_exists( 'your_plugin_function' ) );
    }}
    
    /**
     * Test plugin activation
     */
    public function test_plugin_activation() {{
        // Add your activation tests here
        $this->assertTrue( true );
    }}
}}
"""
        
        sample_test_file = tests_dir / "test-sample.php"
        sample_test_file.write_text(sample_test_content)
        
        # Generate phpunit.xml.dist
        phpunit_config = f"""<?xml version="1.0" encoding="UTF-8"?>
<phpunit
    bootstrap="tests/bootstrap.php"
    backupGlobals="false"
    colors="true"
    convertErrorsToExceptions="true"
    convertNoticesToExceptions="true"
    convertWarningsToExceptions="true"
>
    <testsuites>
        <testsuite name="{plugin_slug}">
            <directory prefix="test-" suffix=".php">./tests/</directory>
        </testsuite>
    </testsuites>
    <php>
        <const name="WP_TESTS_DOMAIN" value="{plugin_slug}.test"/>
        <const name="WP_TESTS_EMAIL" value="admin@{plugin_slug}.test"/>
        <const name="WP_TESTS_TITLE" value="{plugin_slug} Test"/>
        <const name="WP_PHP_BINARY" value="php"/>
    </php>
</phpunit>
"""
        
        phpunit_file = plugin_path / "phpunit.xml.dist"
        phpunit_file.write_text(phpunit_config)
        
        logger.success(f"Generated PHPUnit test files for {plugin_slug}")
        return f"Successfully generated PHPUnit bootstrap and configuration files in {plugin_path}"
        
    except Exception as e:
        logger.exception(f"Error generating PHPUnit bootstrap for {plugin_slug}")
        return f"Error: {str(e)}"