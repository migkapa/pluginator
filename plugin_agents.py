from agents import Agent, ModelSettings
from tools import (
    write_file,
    docker_compose_up,
    activate_plugin,
    list_plugins,
    log_start_writing_files,
    log_finish_writing_files,
    log_checking_compliance,
    log_testing_plugin,
    log_planning
)
from pydantic import BaseModel
from typing import List, Optional

# Pydantic models for structured inputs/outputs
class PluginSpec(BaseModel):
    name: str
    slug: str
    description: str
    version: str
    author: str

class PluginFile(BaseModel):
    path: str    # e.g., "plugin-slug/plugin-slug.php" or "plugin-slug/readme.txt"
    content: str # Full content of the file

class ComplianceReport(BaseModel):
    passed: bool            # True if all checks passed
    issues: List[str]       # List of compliance issues or guideline violations (empty list if none)

class TestReport(BaseModel):
    activated: bool         # True if plugin activation succeeded
    errors: List[str]       # Any errors encountered during activation (empty list if none)

# Define each agent in the multi-agent system:

# 1. Agent to gather and validate plugin specifications from the user
plugin_spec_agent = Agent(
    name="Plugin Specification Agent",
    instructions=(
        "You are an agent that collects WordPress plugin metadata and functional requirements from a user. "
        "Ask the user for any missing information among plugin name, slug, description, and a short list of functional requirements or key features. "
        "If no version is provided, use '1.0.0'. If no author provided, use 'Anonymous'. "
        "Ensure the slug is lowercase with hyphens (e.g., 'My Plugin' -> 'my-plugin'). "
        "After gathering the information, output exactly one PluginSpec object containing name, slug, description (including the functional requirements), version, and author in JSON format."
    ),
    output_type=PluginSpec,
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0.2)
)

# 2. Agent to generate plugin files from the specification
file_generator_agent = Agent(
    name="Plugin File Generator Agent",
    instructions=(
        "You are an agent that generates **complete** WordPress plugin code from a given PluginSpec. "
        "Your goal is to deliver a *production-ready* plugin that implements the core functionality described in PluginSpec.description. "
        "Follow WordPress coding standards and plugin directory guidelines.\n\n"
        "Mandatory deliverables:\n"
        "• Main plugin PHP file (`<slug>/<slug>.php`) with: full plugin header; security check; activation/deactivation hooks; full implementation of described features; proper sanitization/escaping; text-domain loaded.\n"
        "• readme.txt with all standard sections (Description, Installation, Changelog, etc.).\n"
        "• Additional PHP/JS/asset files required for the functionality (e.g., settings page, Gutenberg sidebar, REST endpoints). Place them in sub-folders (admin/, public/, build/, assets/).\n"
        "• Internationalization: wrap user-facing strings with translation functions and load text domain.\n"
        "• Follow GPLv2 license.\n\n"
        "Implementation guidance (adapt as needed to match PluginSpec):\n"
        "1. Settings page under the Settings menu to configure options (e.g., API keys).\n"
        "2. Gutenberg or Classic metabox/side-panel to display or regenerate data.\n"
        "3. REST API or AJAX routes secured with nonces/capability checks.\n"
        "4. Front-end integration that adds output to the_content via filters.\n"
        "5. Use namespaces or unique function prefixes based on slug.\n\n"
        "Output **only** a JSON array of PluginFile objects. Do NOT include explanations."
    ),
    output_type=List[PluginFile],
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0.2)
)

# 3. Agent to check compliance of generated files with WordPress standards and guidelines
compliance_agent = Agent(
    name="Plugin Compliance Agent",
    instructions=(
        "You are an agent that reviews WordPress plugin files for coding standards compliance and directory guidelines. "
        "You will be given a list of PluginFile objects representing the plugin's files and their contents. "
        "Check the following:\n"
        "- **Required Headers**: The main plugin file should have all required header fields (Plugin Name, Description, Version, Author (if provided), License, License URI, etc.). Verify that 'Requires at least', 'Tested up to', and 'Requires PHP' are specified either in the header or the readme. \n"
        "- **GPL Compliance**: Ensure the plugin is licensed under GPLv2 or later (the header and readme should indicate a GPL-compatible license). No proprietary or incompatible license content should be present.\n"
        "- **Coding Standards**: Verify the PHP code follows WordPress Coding Standards (https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/). For example, proper indentation with tabs, correct brace placement, sanitization and escaping where applicable, and use of the plugin's slug as a prefix for function names or class names to avoid collisions. Ensure there's an `if (!defined('ABSPATH')) exit;` check at the top of executable files for security.\n"
        "- **Plugin Directory Guidelines**: Check that the plugin doesn't violate any plugin repository rules. This includes: having a valid readme.txt with required sections (short description, description, installation, changelog, etc.), no spam or malicious code, no calls to third-party services without user consent, and overall that it appears safe and well-structured. "
        "Also ensure that any text strings are ready for translation (i.e., using internationalization functions and correct text domain) if applicable.\n"
        "List any issues or violations found in the 'issues' array, with clear descriptions. If everything looks good, 'issues' should be empty. "
        "Finally, output a ComplianceReport object with passed=True/False and the list of issues."
    ),
    output_type=ComplianceReport,
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0)
)

# 4. Agent to test the plugin by simulating a WordPress environment activation
testing_agent = Agent(
    name="Plugin Testing Agent",
    instructions=(
        "You are an agent that tests a WordPress plugin in a fresh WordPress environment. "
        "You will be given the list of PluginFile objects for the plugin. "
        "Simulate the following steps:\n"
        "1. Set up a WordPress environment (for example, using a WordPress Playground or a Docker Compose environment) and copy the plugin files into the wp-content/plugins/<slug> directory.\n"
        "2. Activate the plugin using WP-CLI (e.g., run `wp plugin activate <slug>`).\n"
        "3. Observe the activation process for any errors or warnings (for instance, PHP fatal errors, syntax errors, or missing dependencies). If the activation fails, capture the error messages (e.g., any fatal error output or WP-CLI error) in the report. If it succeeds, confirm that the plugin activated successfully.\n"
        "4. You do not actually need to run code, but infer from the plugin files whether any runtime issues would occur on activation.\n"
        "After simulating these steps, output a TestReport object. Set 'activated' to True if the plugin would activate without errors, or False if errors are encountered. Include any error messages or stack traces in the 'errors' list (if none, leave it empty)."
    ),
    output_type=TestReport,
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0)
)

# 5. Agent to orchestrate the entire plugin generation and review process
plugin_manager_agent = Agent(
    name="Plugin Manager Agent",
    instructions=(
        "You are the Plugin Manager Agent, responsible for orchestrating the multi-step WordPress plugin creation process. "
        "Your task is to coordinate with other agents (tools) to gather requirements, generate the plugin, ensure compliance, test it, and then report the results to the user.\\n\\n"
        "Corrected Steps to follow:\n"
        "0. Call `log_planning` to indicate the planning phase.\n"
        "1. Call `collect_plugin_spec` to get PluginSpec.\n"
        "2. Call `generate_plugin_files` with PluginSpec to get PluginFile list.\n"
        "3. Call `log_start_writing_files`. Then, for each PluginFile, call `write_file` to save it to './plugins/'. Finally, call `log_finish_writing_files`.\\n"
        "4. Call `log_checking_compliance`, then call `check_compliance` with the PluginFile list to get ComplianceReport.\\n"
        "5. Call `log_testing_plugin`, then call `test_plugin` with the PluginFile list to get TestReport (simulated activation).\\n"
        "6. Compile a final report for the user based on ComplianceReport and TestReport.\\n\\n"
        "Make sure to execute these steps in order. Only produce the final user-facing report after completing all steps. The final report should include the plugin name and version, indicate whether the plugin passed compliance checks and activation testing, and either congratulate the user on a successful plugin or inform them of any issues found."
    ),
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0),
    tools=[
        log_planning,
        plugin_spec_agent.as_tool(
            tool_name="collect_plugin_spec",
            tool_description="Collects plugin metadata from the user and returns a PluginSpec."
        ),
        file_generator_agent.as_tool(
            tool_name="generate_plugin_files",
            tool_description="Generates all plugin files from a given PluginSpec."
        ),
        log_start_writing_files,
        log_finish_writing_files,
        log_checking_compliance,
        log_testing_plugin,
        write_file,
        compliance_agent.as_tool(
            tool_name="check_compliance",
            tool_description="Checks the plugin files for coding standards and plugin directory guideline compliance."
        ),
        testing_agent.as_tool(
            tool_name="test_plugin",
            tool_description="Activates the plugin in a test environment to ensure it works without errors."
        ),
        docker_compose_up,
        activate_plugin,
        list_plugins,
    ]
)