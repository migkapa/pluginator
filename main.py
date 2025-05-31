import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Optional

# Imports
from plugin_agents import plugin_manager_agent as manager_agent
from models import model_manager
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
    
    # Check API key based on selected model
    current_model = model_manager.current_model
    resolved_name = model_manager.resolve_model_name(current_model)
    provider = model_manager.get_provider_from_model(resolved_name)
    model_config = model_manager.get_model_config(resolved_name)
    
    # Check for appropriate API key
    if model_config.api_key_env_var:
        if not os.environ.get(model_config.api_key_env_var):
            provider_name = provider.upper()
            issues.append(
                f"{model_config.api_key_env_var} not set. Please export your {provider_name} API key "
                f"or set a different model with --model."
            )
    elif provider == "openai":
        # Default OpenAI check for models without explicit API key config
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
            # Increase max_turns to accommodate the additional workflow steps
            response = await Runner.run(manager_agent, prompt, max_turns=20)
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
  %(prog)s --list-models            # List available AI models
  
  # Using different models (optional)
  %(prog)s -p "Plugin description" --model gpt-4o-mini     # Use GPT-4o mini
  %(prog)s -p "Plugin description" --model claude-3-5-sonnet --disable-tracing
  %(prog)s -p "Plugin description" --model gemini-2.5-flash --temperature 0.5
  
  # Advanced testing
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
    
    # Model configuration options
    model_group = parser.add_argument_group('Model Configuration (Optional)')
    model_group.add_argument(
        "--model",
        help="Model to use (default: gpt-4o). Examples: gpt-4o-mini, claude-3-5-sonnet, gemini-2.5-flash",
        type=str,
        default=None
    )
    model_group.add_argument(
        "--list-models",
        help="List all available models and exit",
        action="store_true"
    )
    model_group.add_argument(
        "--temperature",
        help="Model temperature (0.0-2.0, default varies by model)",
        type=float,
        default=None
    )
    model_group.add_argument(
        "--disable-tracing",
        help="Disable tracing (useful for non-OpenAI models)",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle model configuration
    if args.disable_tracing:
        os.environ["DISABLE_TRACING"] = "true"
        logger.debug("Tracing disabled via CLI flag")
    
    if args.model:
        os.environ["DEFAULT_MODEL"] = args.model
        model_manager.current_model = args.model
        logger.info(f"Using model: {args.model}")
    
    # Handle --list-models
    if args.list_models:
        logger.info("=== Available Models ===\n")
        
        # Show shortcuts
        logger.info("📝 Model Shortcuts (convenient aliases):")
        models = model_manager.list_available_models()
        
        # Group by provider
        by_provider = {}
        for model in models:
            provider = model["provider"]
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(model)
        
        for provider, provider_models in sorted(by_provider.items()):
            logger.info(f"  {provider.upper()}:")
            for model in provider_models:
                features = []
                if model["supports_structured_outputs"]:
                    features.append("structured")
                if model["supports_multimodal"]:
                    features.append("multimodal")
                if model["supports_tools"]:
                    features.append("tools")
                
                feature_str = f" [{', '.join(features)}]" if features else ""
                logger.info(f"    • {model['shortcut']} → {model['full_name']}{feature_str}")
        
        # Show providers and capabilities
        logger.info("\n📦 Supported Providers:")
        providers = model_manager.get_supported_providers()
        for provider in providers:
            features = []
            if provider["supports_responses_api"]:
                features.append("responses-api")
            if provider["supports_structured_outputs"]:
                features.append("structured")
            if provider["supports_multimodal"]:
                features.append("multimodal")
            if provider["supports_tools"]:
                features.append("tools")
            
            feature_str = f" [{', '.join(features)}]" if features else ""
            api_key = f" (API key: {provider['api_key_env_var']})" if provider['api_key_env_var'] else ""
            logger.info(f"  • {provider['name']}{feature_str}{api_key}")
            if provider['notes']:
                logger.info(f"    {provider['notes']}")
        
        # Show how to use any LiteLLM model
        logger.info("\n🚀 Using Any LiteLLM Model:")
        logger.info("You can use any model supported by LiteLLM with the format:")
        logger.info("  litellm/provider/model-name")
        logger.info("\nExamples:")
        logger.info("  --model litellm/anthropic/claude-3-5-sonnet-20241022")
        logger.info("  --model litellm/groq/llama-3.1-8b-instant")
        logger.info("  --model litellm/cohere/command-r-plus")
        logger.info("\nSee all providers: https://docs.litellm.ai/docs/providers")
        
        # Show API key status
        logger.info("\n🔑 API Key Status:")
        api_keys = model_manager.validate_api_keys()
        for provider, available in api_keys.items():
            status = "✓ Available" if available else "✗ Not set"
            logger.info(f"  {provider.capitalize()}: {status}")
        
        sys.exit(0)
    
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
