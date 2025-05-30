import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Optional

# Imports
from plugin_agents import plugin_manager_agent as manager_agent
from loguru import logger

# Try to load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure Loguru with better formatting
logger.remove()

# Define log format based on verbosity
SIMPLE_FORMAT = "<level>{message}</level>"
DETAILED_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | {name}:{function}:{line} - <level>{message}</level>"

def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity setting."""
    logger.remove()
    
    if verbose:
        # Verbose mode: show all logs with detailed format
        logger.add(
            sys.stderr, 
            format=DETAILED_FORMAT, 
            level="DEBUG",
            colorize=True
        )
    else:
        # Normal mode: show only INFO and above with simple format
        logger.add(
            sys.stderr, 
            format=SIMPLE_FORMAT, 
            level="INFO",
            filter=lambda record: record["level"].name in ["INFO", "SUCCESS", "WARNING", "ERROR"],
            colorize=True
        )

# Attempt to import the OpenAI Agents SDK
try:
    from agents import Runner
except ImportError:
    logger.error("Missing 'agents' package. Install with 'pip install openai-agents'")
    sys.exit(1)

def validate_environment() -> tuple[bool, list[str]]:
    """Validate the environment setup and return status with issues."""
    issues = []
    
    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY not set. Please export your OpenAI API key.")
    
    # Check if plugins directory exists
    plugins_dir = Path("./plugins")
    if not plugins_dir.exists():
        try:
            plugins_dir.mkdir(exist_ok=True)
            logger.debug("Created plugins directory")
        except Exception as e:
            issues.append(f"Cannot create plugins directory: {e}")
    
    # Check if Docker is available (optional)
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.warning("Docker not available. Plugin activation testing will be simulated.")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("Docker not available. Plugin activation testing will be simulated.")
    
    # Check PHP CLI availability (optional)
    try:
        result = subprocess.run(
            ["php", "--version"], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.warning("PHP CLI not available. Syntax checking will be limited.")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("PHP CLI not available. Syntax checking will be limited.")
    
    return len(issues) == 0, issues

async def run_agent(prompt: str, max_retries: int = 3) -> Optional[str]:
    """Run the agent with retry logic."""
    for attempt in range(max_retries):
        try:
            logger.debug(f"Starting agent run (attempt {attempt + 1}/{max_retries})...")
            response = await Runner.run(manager_agent, prompt)
            logger.success("Agent run completed successfully.")
            return response.final_output
        except KeyboardInterrupt:
            logger.warning("Process interrupted by user.")
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {2 ** attempt} seconds...")
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error("All retry attempts exhausted.")
                raise
    return None

def main():
    """Main entry point with enhanced CLI support."""
    parser = argparse.ArgumentParser(
        description="WordPress Plugin Generator - AI-powered plugin creation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s -p "Create a contact form plugin"  # Direct prompt
  %(prog)s -p "SEO plugin" -v       # Verbose output
  %(prog)s --check                  # Check environment setup
  %(prog)s -p "Plugin description" --playground  # Test with WordPress Playground
  %(prog)s -p "Plugin description" --wp-check    # Run WordPress Plugin Check
  %(prog)s -p "Plugin description" --phpunit     # Generate and run PHPUnit tests
  %(prog)s -p "Plugin description" --all-tests   # Run all available tests
        """
    )
    
    parser.add_argument(
        "-p", "--prompt",
        help="Plugin description (skip interactive prompt)",
        type=str
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    parser.add_argument(
        "--check",
        help="Check environment setup and exit",
        action="store_true"
    )
    parser.add_argument(
        "--max-retries",
        help="Maximum retry attempts on failure (default: 3)",
        type=int,
        default=3
    )
    
    # Advanced testing options
    testing_group = parser.add_argument_group('Advanced Testing Options')
    testing_group.add_argument(
        "--playground",
        help="Test plugin with WordPress Playground (requires Selenium)",
        action="store_true"
    )
    testing_group.add_argument(
        "--wp-check",
        help="Run WordPress Plugin Check (requires Docker)",
        action="store_true"
    )
    testing_group.add_argument(
        "--phpunit",
        help="Generate and run PHPUnit tests (requires Docker)",
        action="store_true"
    )
    testing_group.add_argument(
        "--all-tests",
        help="Run all available advanced tests",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Environment check
    valid, issues = validate_environment()
    
    if args.check:
        logger.info("=== Environment Check ===")
        if valid:
            logger.success("✓ All required components are properly configured")
        else:
            logger.error("✗ Environment issues detected:")
            for issue in issues:
                logger.error(f"  - {issue}")
        
        # Show optional components status
        logger.info("\n=== Optional Components ===")
        logger.info("These enhance functionality but are not required:")
        
        try:
            import subprocess
            subprocess.run(["docker", "--version"], capture_output=True, check=True, timeout=2)
            logger.success("✓ Docker: Available (enables real plugin testing)")
        except:
            logger.warning("✗ Docker: Not available (testing will be simulated)")
        
        try:
            subprocess.run(["php", "--version"], capture_output=True, check=True, timeout=2)
            logger.success("✓ PHP CLI: Available (enables syntax checking)")
        except:
            logger.warning("✗ PHP CLI: Not available (syntax checking will be limited)")
        
        sys.exit(0 if valid else 1)
    
    # Check for critical issues
    if not valid:
        logger.error("Environment issues detected:")
        for issue in issues:
            logger.error(f"  - {issue}")
        sys.exit(1)
    
    logger.info("=== WordPress Plugin Generator ===")
    logger.info("AI-powered tool for creating production-ready WordPress plugins\n")
    
    # Get prompt
    if args.prompt:
        prompt = args.prompt
        logger.info(f"Using provided prompt: {prompt}")
    else:
        try:
            prompt = input("Describe the plugin you want to generate: ")
            if not prompt.strip():
                logger.error("No plugin description provided.")
                sys.exit(1)
        except (EOFError, KeyboardInterrupt):
            logger.info("\nOperation cancelled.")
            sys.exit(0)
    
    # Run the agent
    try:
        # Prepare testing options
        testing_options = {
            "playground": args.playground or args.all_tests,
            "wp_check": args.wp_check or args.all_tests,
            "phpunit": args.phpunit or args.all_tests
        }
        
        # Include testing options in the prompt
        enhanced_prompt = prompt
        if any(testing_options.values()):
            test_flags = []
            if testing_options["playground"]:
                test_flags.append("WordPress Playground testing")
            if testing_options["wp_check"]:
                test_flags.append("WordPress Plugin Check")
            if testing_options["phpunit"]:
                test_flags.append("PHPUnit tests")
            
            enhanced_prompt += f"\n\nPlease run the following advanced tests: {', '.join(test_flags)}"
        
        result = asyncio.run(run_agent(enhanced_prompt, args.max_retries))
        if result:
            logger.info("\n=== Generation Report ===")
            print(result)
            logger.success("\n✓ Plugin generation completed!")
            logger.info("Check the './plugins' directory for your generated plugin.")
        else:
            logger.error("Failed to generate plugin.")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error during plugin generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
