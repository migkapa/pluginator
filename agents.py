from openai_agents import Agent
from tools import write_file, docker_compose_up, activate_plugin, list_plugins

# Plugin Specification Agent
plugin_spec_agent = Agent(
    name="plugin_spec_agent",
    instructions=(
        "You are an expert WordPress plugin designer. "
        "Ask the user for the plugin details (name, slug, description, version, author, features) "
        "and return a JSON object with these fields."
    ),
    tools=[],
)

# File Generator Agent
file_generator_agent = Agent(
    name="file_generator_agent",
    instructions=(
        "You are an experienced WordPress developer. "
        "Given a JSON specification for a WordPress plugin, generate all necessary plugin files "
        "following WordPress Plugin Handbook and PHP coding standards. "
        "Return a JSON array of objects with 'filename' and 'content'."
    ),
    tools=[write_file],
)

# Compliance Agent
compliance_agent = Agent(
    name="compliance_agent",
    instructions=(
        "You are a WordPress coding standards compliance checker. "
        "Given the generated plugin file contents, verify they comply with WordPress Plugin and PHP coding standards. "
        "Return 'compliant' if no issues, otherwise return a list of issues."
    ),
    tools=[],
)

# Testing Agent
testing_agent = Agent(
    name="testing_agent",
    instructions=(
        "You are a testing agent. Start the WordPress Playground, activate the plugin by its slug, "
        "and list installed plugins to verify activation. "
        "Use the provided tools and return success or failure with details."
    ),
    tools=[docker_compose_up, activate_plugin, list_plugins],
)

# Manager Agent
manager_agent = Agent(
    name="plugin_manager_agent",
    instructions=(
        "You orchestrate the WordPress plugin creation workflow. "
        "1) Use spec_agent to obtain plugin specification. "
        "2) Use file_generator to generate plugin files. "
        "3) Use compliance_checker to verify coding standards. "
        "4) Use tester to test plugin in WordPress Playground. "
        "Return a final report summarizing each step."
    ),
    tools=[
        plugin_spec_agent.as_tool(
            tool_name="spec_agent",
            tool_description="Generate plugin specification based on user input"
        ),
        file_generator_agent.as_tool(
            tool_name="file_generator",
            tool_description="Generate plugin files"
        ),
        compliance_agent.as_tool(
            tool_name="compliance_checker",
            tool_description="Check coding standards compliance"
        ),
        testing_agent.as_tool(
            tool_name="tester",
            tool_description="Run tests in WordPress Playground"
        ),
    ],
)