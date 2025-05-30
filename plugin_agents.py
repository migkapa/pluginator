from agents import Agent, ModelSettings
from tools import (
    write_file,
    read_file,
    list_files,
    ensure_directory,
    delete_file,
    check_plugin_syntax,
    docker_compose_up,
    activate_plugin,
    list_plugins,
    log_start_writing_files,
    log_finish_writing_files,
    log_checking_compliance,
    log_testing_plugin,
    log_planning
)
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Enhanced Pydantic models for structured inputs/outputs
class PluginSpec(BaseModel):
    name: str = Field(description="Human-readable plugin name")
    slug: str = Field(description="WordPress plugin slug (lowercase, hyphens)")
    description: str = Field(description="Plugin description including key features")
    version: str = Field(default="1.0.0", description="Plugin version")
    author: str = Field(default="Anonymous", description="Plugin author name")
    author_uri: Optional[str] = Field(default=None, description="Author website URL")
    requires_at_least: str = Field(default="5.8", description="Minimum WordPress version")
    tested_up_to: str = Field(default="6.7", description="Maximum tested WordPress version")
    requires_php: str = Field(default="7.4", description="Minimum PHP version")
    features: List[str] = Field(default_factory=list, description="List of key features")

class PluginFile(BaseModel):
    path: str = Field(description="File path relative to plugin directory")
    content: str = Field(description="Full content of the file")
    description: Optional[str] = Field(default=None, description="Brief description of the file's purpose")

class ComplianceIssue(BaseModel):
    severity: str = Field(description="Issue severity: error, warning, or info")
    category: str = Field(description="Issue category: header, security, coding-standards, etc.")
    description: str = Field(description="Detailed description of the issue")
    file: Optional[str] = Field(default=None, description="Affected file")
    line: Optional[int] = Field(default=None, description="Line number where issue occurs")

class ComplianceReport(BaseModel):
    passed: bool = Field(description="True if all critical checks passed")
    issues: List[ComplianceIssue] = Field(default_factory=list, description="List of compliance issues")
    summary: Dict[str, int] = Field(default_factory=dict, description="Count of issues by severity")

class TestReport(BaseModel):
    activated: bool = Field(description="True if plugin activation succeeded")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    php_syntax_valid: bool = Field(default=True, description="True if PHP syntax is valid")
    performance_notes: List[str] = Field(default_factory=list, description="Performance considerations")

# Define each agent in the multi-agent system:

# 1. Enhanced agent to gather and validate plugin specifications
plugin_spec_agent = Agent(
    name="Plugin Specification Agent",
    instructions=(
        "You are an expert WordPress plugin consultant who gathers comprehensive plugin specifications. "
        "Your role is to:\n"
        "1. Collect all necessary metadata (name, slug, description, version, author details)\n"
        "2. Ensure the slug follows WordPress conventions (lowercase, hyphens, no spaces)\n"
        "3. Extract and list specific features from the user's description\n"
        "4. Set appropriate WordPress and PHP version requirements\n"
        "5. Ask clarifying questions if the description is vague or missing key functionality details\n\n"
        "Focus on understanding:\n"
        "- The plugin's primary purpose and target users\n"
        "- Specific features and functionality required\n"
        "- Any integrations with WordPress features (Gutenberg, REST API, etc.)\n"
        "- Performance and security requirements\n\n"
        "Output a complete PluginSpec object with all fields properly filled."
    ),
    output_type=PluginSpec,
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.3)
)

# 2. Enhanced agent to generate plugin files with better structure
file_generator_agent = Agent(
    name="Plugin File Generator Agent",
    instructions=(
        "You are an expert WordPress plugin developer who creates production-ready, well-structured plugins. "
        "Generate a complete WordPress plugin implementing ALL features specified in PluginSpec.\n\n"
        "Required deliverables:\n"
        "1. **Main Plugin File** (`<slug>/<slug>.php`):\n"
        "   - Complete plugin header with all metadata\n"
        "   - Security check: `if (!defined('ABSPATH')) exit;`\n"
        "   - Plugin class using namespace or unique prefix\n"
        "   - Activation/deactivation hooks\n"
        "   - Text domain loading\n"
        "   - Main initialization logic\n\n"
        "2. **readme.txt** with all sections:\n"
        "   - Description, Installation, FAQ, Screenshots, Changelog\n"
        "   - Proper markdown formatting\n"
        "   - All metadata matching plugin header\n\n"
        "3. **Additional Files** (as needed):\n"
        "   - `includes/class-<slug>-admin.php` - Admin functionality\n"
        "   - `includes/class-<slug>-public.php` - Frontend functionality\n"
        "   - `admin/js/` and `admin/css/` - Admin assets\n"
        "   - `public/js/` and `public/css/` - Frontend assets\n"
        "   - `languages/<slug>.pot` - Translation template\n\n"
        "Best Practices:\n"
        "- Use WordPress coding standards (tabs, proper spacing)\n"
        "- Implement proper sanitization and escaping\n"
        "- Use nonces for all forms and AJAX calls\n"
        "- Add capability checks for admin functions\n"
        "- Include inline documentation\n"
        "- Follow single responsibility principle\n"
        "- Use WordPress APIs (Settings, Options, Database)\n\n"
        "Output ONLY a JSON array of PluginFile objects, no explanations."
    ),
    output_type=List[PluginFile],
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.2)
)

# 3. Enhanced compliance agent with detailed checking
compliance_agent = Agent(
    name="Plugin Compliance Agent",
    instructions=(
        "You are a WordPress plugin reviewer who ensures plugins meet all standards and guidelines. "
        "Perform a comprehensive review of the provided plugin files.\n\n"
        "Check Categories:\n"
        "1. **Plugin Header** (Error if missing):\n"
        "   - All required fields present and valid\n"
        "   - Version numbers properly formatted\n"
        "   - License must be GPL-compatible\n\n"
        "2. **Security** (Error for violations):\n"
        "   - ABSPATH check in all PHP files\n"
        "   - Proper nonce usage for forms/AJAX\n"
        "   - Data sanitization and escaping\n"
        "   - No direct file access\n"
        "   - No eval() or system() calls\n\n"
        "3. **Coding Standards** (Warning for violations):\n"
        "   - WordPress PHP coding standards\n"
        "   - Proper indentation (tabs, not spaces)\n"
        "   - Function/class naming conventions\n"
        "   - File organization\n\n"
        "4. **Best Practices** (Info for suggestions):\n"
        "   - Internationalization ready\n"
        "   - Proper hook usage\n"
        "   - Database queries using $wpdb\n"
        "   - Options API usage\n\n"
        "5. **Performance** (Warning/Info):\n"
        "   - Asset loading optimization\n"
        "   - Database query efficiency\n"
        "   - Caching implementation\n\n"
        "Create ComplianceIssue objects for each finding with appropriate severity.\n"
        "Set passed=False only if there are 'error' severity issues.\n"
        "Include a summary count of issues by severity."
    ),
    output_type=ComplianceReport,
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.1)
)

# 4. Enhanced testing agent with syntax checking
testing_agent = Agent(
    name="Plugin Testing Agent",
    instructions=(
        "You are a WordPress QA engineer who tests plugins for functionality and compatibility. "
        "Analyze the plugin files to predict activation behavior and identify potential issues.\n\n"
        "Testing Steps:\n"
        "1. **Syntax Validation**:\n"
        "   - Check PHP syntax in all .php files\n"
        "   - Validate JSON in any .json files\n"
        "   - Check for parse errors\n\n"
        "2. **Dependency Analysis**:\n"
        "   - Required PHP version compatibility\n"
        "   - WordPress version compatibility\n"
        "   - External library dependencies\n"
        "   - Required PHP extensions\n\n"
        "3. **Activation Simulation**:\n"
        "   - Check for fatal errors on activation\n"
        "   - Database table creation issues\n"
        "   - File/directory permission requirements\n"
        "   - Hook conflicts\n\n"
        "4. **Runtime Analysis**:\n"
        "   - Memory usage concerns\n"
        "   - Potential timeout issues\n"
        "   - Error handling adequacy\n\n"
        "5. **Performance Considerations**:\n"
        "   - Database query efficiency\n"
        "   - Asset loading optimization\n"
        "   - Caching implementation\n\n"
        "Set activated=False if any fatal errors would occur.\n"
        "Include all errors, warnings, and performance notes in the report."
    ),
    output_type=TestReport,
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.1)
)

# 5. Enhanced plugin manager with better orchestration
plugin_manager_agent = Agent(
    name="Plugin Manager Agent",
    instructions=(
        "You are the Plugin Manager orchestrating the WordPress plugin creation workflow. "
        "Guide the process professionally and ensure high-quality output.\n\n"
        "Workflow Steps:\n"
        "1. **Planning Phase**:\n"
        "   - Call log_planning to indicate planning\n"
        "   - Analyze user requirements\n\n"
        "2. **Specification Collection**:\n"
        "   - Call collect_plugin_spec to gather detailed requirements\n"
        "   - Ensure spec is complete and valid\n\n"
        "3. **Code Generation**:\n"
        "   - Call generate_plugin_files with the PluginSpec\n"
        "   - Review generated files for completeness\n\n"
        "4. **File Writing**:\n"
        "   - Call log_start_writing_files\n"
        "   - Create plugin directory: ensure_directory('./plugins/<slug>')\n"
        "   - Write each file using write_file\n"
        "   - Call log_finish_writing_files\n\n"
        "5. **Compliance Checking**:\n"
        "   - Call log_checking_compliance\n"
        "   - Read written files if needed for verification\n"
        "   - Call check_compliance with file list\n"
        "   - Check PHP syntax using check_plugin_syntax for main file\n\n"
        "6. **Testing Phase**:\n"
        "   - Call log_testing_plugin\n"
        "   - Call test_plugin with file list\n"
        "   - If Docker available, attempt real activation\n\n"
        "7. **Final Report**:\n"
        "   - Summarize the entire process\n"
        "   - Highlight successes and any issues\n"
        "   - Provide next steps for the user\n\n"
        "Maintain a professional tone and provide clear, actionable feedback."
    ),
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.1),
    tools=[
        # Logging tools
        log_planning,
        log_start_writing_files,
        log_finish_writing_files,
        log_checking_compliance,
        log_testing_plugin,
        # File operation tools
        write_file,
        read_file,
        list_files,
        ensure_directory,
        delete_file,
        check_plugin_syntax,
        # Agent tools
        plugin_spec_agent.as_tool(
            tool_name="collect_plugin_spec",
            tool_description="Collects comprehensive plugin specifications from the user"
        ),
        file_generator_agent.as_tool(
            tool_name="generate_plugin_files",
            tool_description="Generates complete plugin codebase from specifications"
        ),
        compliance_agent.as_tool(
            tool_name="check_compliance",
            tool_description="Performs comprehensive compliance and standards checking"
        ),
        testing_agent.as_tool(
            tool_name="test_plugin",
            tool_description="Tests plugin for activation errors and performance issues"
        ),
        # Docker/WordPress tools
        docker_compose_up,
        activate_plugin,
        list_plugins,
    ]
)