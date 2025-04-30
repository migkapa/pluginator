import os
import sys

# Imports
import asyncio
import os
import sys
from plugin_agents import plugin_manager_agent as manager_agent
from loguru import logger

# Try to load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure Loguru
logger.remove()
# Info-level handler with minimal format (only message)
logger.add(sys.stderr, format="<level>{message}</level>", level="INFO", filter=lambda record: record["level"].name in ["INFO", "SUCCESS"])
# Error-level handler with timestamp for clarity
logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level}</level> - {message}", level="ERROR")

# Attempt to import the OpenAI Agents SDK
try:
    from agents import Runner
except ImportError:
    logger.error("Missing 'agents' package. Install with 'pip install openai-agents'")
    sys.exit(1)

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not set. Please export your OpenAI API key as OPENAI_API_KEY.")
        sys.exit(1)

    logger.info("=== WordPress Plugin Generator ===")
    prompt = input("Describe the plugin you want to generate: ")
    try:
        logger.debug("Starting agent run...")
        response = asyncio.run(Runner.run(manager_agent, prompt))
        logger.success("Agent run finished successfully.")
    except Exception as e:
        logger.exception(f"ERROR during agent run: {e}")
        sys.exit(1)
    logger.info("\n=== Generation Report ===")
    print(response.final_output)

if __name__ == "__main__":
    main()
