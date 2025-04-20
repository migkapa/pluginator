import os
import sys
from openai_agents import Runner, UserMessage
from agents import manager_agent

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set. Please export your OpenAI API key as OPENAI_API_KEY.")
        sys.exit(1)

    print("=== WordPress Plugin Generator ===")
    prompt = input("Describe the plugin you want to generate: ")
    response = Runner.run(manager_agent, [UserMessage(content=prompt)])
    print("\n=== Generation Report ===")
    print(response.final_output)

if __name__ == "__main__":
    main()
