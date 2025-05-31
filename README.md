# WordPress Plugin Generator - AI-Powered Plugin Creation Tool

An advanced WordPress plugin generator that uses OpenAI's Agents SDK to create production-ready plugins through an intelligent multi-agent workflow.

## Table of Contents

- [Features](#-features)
- [What's New in v0.0.16](#-whats-new-in-v0016)
- [Quick Start](#-quick-start)
- [Model Support](#-model-support-enhanced-in-v0016)
- [Installation](#-installation)
- [Usage](#usage)
- [Examples](#examples)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Multi-Agent Architecture**: Specialized AI agents for different aspects of plugin development
- **Complete Plugin Generation**: Creates all necessary files, including PHP, CSS, JS, and documentation
- **WordPress Standards Compliant**: Follows WordPress coding standards and best practices
- **Interactive Development**: Built-in testing and refinement capabilities
- **Production Ready**: Generates plugins that can be immediately deployed
- **Flexible AI Models**: Support for OpenAI, Anthropic Claude, Google Gemini, local Ollama models, and more

## 🆕 What's New in v0.0.16

### 🚀 **Multi-Model AI Support**
- **Any LiteLLM Model**: Use OpenAI, Anthropic, Google, Groq, Cohere, and 20+ other providers
- **Local Ollama Support**: Run completely free models locally (deepseek-r1, llama3.2, etc.)
- **Flexible Model Selection**: No hardcoded restrictions - use any model with simple format
- **Smart Provider Detection**: Automatically detects and configures model providers

### 🔧 **Enhanced CLI**
- **New Flags**: `--model`, `--list-models`, `--temperature`, `--disable-tracing`
- **Better Discovery**: `--list-models` shows all supported providers and examples
- **Environment Config**: Set default models and API keys in `.env` file

### 📚 **Improved Documentation**
- **[Quick Start Guide](QUICKSTART.md)**: Step-by-step setup for each AI provider
- **Provider Comparison**: Performance, cost, and capability tables
- **Troubleshooting**: Common issues and solutions for each provider

### 🔄 **Migration from v0.0.11**
```bash
# Update your installation
pip install "openai-agents[litellm]==0.0.16"

# Your existing usage still works
python main.py -p "Create a plugin"

# New: Try different models
python main.py --model claude-3-5-haiku-20241022 -p "Create a plugin"
python main.py --model ollama/deepseek-r1:14b -p "Create a plugin"  # Free!
```

## 🤖 Model Support (Enhanced in v0.0.16)

The WordPress Plugin Generator supports **any AI model via LiteLLM**, including OpenAI, Anthropic, Google, local Ollama models, and many more providers.

### Default Model

By default, the generator uses OpenAI's `gpt-4o` model, which provides the best balance of capabilities and performance.

### Supported Providers

| Provider | Example Models | API Key Required | Notes |
|----------|---------------|------------------|-------|
| **OpenAI** | gpt-4o, gpt-4o-mini, o1-preview | ✅ OPENAI_API_KEY | Best overall performance |
| **Ollama** | ollama/llama3.2:latest, ollama/deepseek-r1:14b | ❌ None | Free, runs locally |
| **Anthropic** | claude-3-5-sonnet, claude-3-5-haiku | ✅ ANTHROPIC_API_KEY | Excellent for complex tasks |
| **Google** | litellm/gemini/gemini-1.5-flash | ✅ GOOGLE_API_KEY | Strong multimodal capabilities |
| **Groq** | litellm/groq/llama-3.1-70b-versatile | ✅ GROQ_API_KEY | Ultra-fast inference |

### Quick Model Examples

```bash
# List all available models and providers
python main.py --list-models

# OpenAI (default) - best reliability
python main.py --model gpt-4o -p "Create a plugin"

# Ollama (free) - privacy-focused local models
python main.py --model ollama/deepseek-r1:14b -p "Create a plugin"

# Claude (premium) - excellent for complex logic
python main.py --model claude-3-5-haiku-20241022 --disable-tracing -p "Create a plugin"

# Custom temperature for different creativity levels
python main.py --model gpt-4o --temperature 0.3 -p "Create a precise plugin"
```

**📖 Full Setup Guide:** For detailed installation and configuration instructions for each provider, see the **[Quick Start Guide](QUICKSTART.md)**.

### Installing LiteLLM Support

To use non-OpenAI models, install the optional LiteLLM dependency:

```bash
pip install "openai-agents[litellm]==0.0.16"
```

## 🚀 Quick Start

### 🎯 New to AI Models? Start Here!

For detailed setup instructions for all AI providers (OpenAI, Ollama, Claude, etc.), see our **[📖 Quick Start Guide](QUICKSTART.md)**.

### Basic Usage
```bash
# Default OpenAI usage (requires OPENAI_API_KEY)
python main.py -p "Create a contact form plugin with name, email, and message fields"

# Try alternative models - see QUICKSTART.md for full setup
python main.py --model ollama/deepseek-r1:14b -p "Create a plugin"  # Free local model
python main.py --model claude-3-5-haiku-20241022 -p "Create a plugin"  # High-quality Claude  
python main.py --model gpt-4o-mini -p "Create a plugin"  # Fast OpenAI model

# Discover all available models
python main.py --list-models
```

**🔗 For complete setup instructions:** See **[📖 Quick Start Guide](QUICKSTART.md)**  
**🎯 For real-world examples:** See **[📖 Examples & Use Cases](EXAMPLES.md)**

## Usage

### Interactive Mode (Default)

```bash
python main.py
```

### Command Line Mode

```bash
# Generate a plugin with direct prompt
python main.py -p "Create a contact form plugin with email notifications"

# Generate with verbose output
python main.py -p "SEO optimization plugin" -v

# Use a different model
python main.py -p "Custom post type plugin" --model claude-3-5-sonnet

# Use any LiteLLM model with custom settings
python main.py -p "Plugin description" --model litellm/groq/llama-3.1-70b-versatile --temperature 0.3

# Check environment setup
python main.py --check

# List all available models and shortcuts
python main.py --list-models

# Custom retry attempts
python main.py -p "Custom post type plugin" --max-retries 5
```

### Advanced Testing Options

The generator supports several advanced testing methods to ensure your plugin works correctly:

```bash
# Test with WordPress Playground (requires Selenium)
python main.py -p "Your plugin description" --playground

# Run WordPress Plugin Check (requires Docker)
python main.py -p "Your plugin description" --wp-check

# Generate and run PHPUnit tests (requires Docker)
python main.py -p "Your plugin description" --phpunit

# Run all available tests
python main.py -p "Your plugin description" --all-tests
```

### Command Line Options

#### Basic Options
- `-p, --prompt`: Plugin description (skip interactive prompt)
- `-v, --verbose`: Enable verbose output with detailed logging
- `--check`: Check environment setup and exit
- `--max-retries`: Maximum retry attempts on failure (default: 3)

#### Advanced Testing Options
- `--playground`: Test plugin with WordPress Playground in a headless browser
- `--wp-check`: Run the official WordPress Plugin Check tool
- `--phpunit`: Generate PHPUnit test bootstrap and run tests
- `--all-tests`: Run all available advanced tests

## Testing Methods

### 1. Basic Testing (Always Run)
- **PHP Syntax Check**: Validates PHP syntax using `php -l`
- **Static Code Analysis**: Analyzes code for potential issues without execution

### 2. WordPress Playground Testing
Tests your plugin in a real WordPress environment using a headless browser.

**Requirements:**
- Selenium: `pip install selenium webdriver-manager`
- Chrome or Chromium browser

**What it does:**
- Creates a ZIP of your plugin
- Uploads and activates it in WordPress Playground
- Verifies successful activation
- Reports any activation errors

### 3. WordPress Plugin Check
Runs the official WordPress Plugin Check tool to ensure compliance with WordPress guidelines.

**Requirements:**
- Docker and Docker Compose
- Running: `docker-compose up -d`

**What it checks:**
- WordPress coding standards
- Security best practices
- Performance optimizations
- Accessibility requirements

### 4. PHPUnit Testing
Generates and runs unit tests for your plugin.

**Requirements:**
- Docker and Docker Compose
- Running: `docker-compose up -d`

**What it does:**
- Generates PHPUnit bootstrap and configuration
- Creates sample test files
- Runs the test suite
- Reports test results

## Agent Workflow

1. **Planning Phase**: Analyzes requirements and prepares the workflow
2. **Specification Collection**: Gathers detailed plugin requirements
3. **Code Generation**: Creates complete plugin codebase
4. **File Writing**: Saves all files with proper structure
5. **Compliance Checking**: Verifies WordPress standards
6. **Testing**: Validates syntax and simulates activation
7. **Reporting**: Provides comprehensive generation report

## Enhanced Tools

### File Operations
- `write_file`: Enhanced file writing with error handling
- `read_file`: Safe file reading with encoding support
- `list_files`: Directory listing with pattern matching
- `ensure_directory`: Safe directory creation
- `delete_file`: File deletion with existence checking

### WordPress Tools
- `docker_compose_up`: Docker environment management
- `activate_plugin`: Plugin activation with timeout support
- `list_plugins`: Enhanced plugin listing with JSON output
- `check_plugin_syntax`: PHP syntax validation

### WordPress Testing Tools
- `test_with_playground`: Test plugins using WordPress Playground in a headless browser
- `run_plugin_check`: Run WordPress Plugin Check tool via WP-CLI
- `run_phpunit_tests`: Execute PHPUnit tests for plugins
- `generate_phpunit_bootstrap`: Generate PHPUnit test configuration

## Examples

### Basic Contact Form Plugin

```bash
python main.py -p "Create a simple contact form plugin with spam protection"
```

### Advanced Custom Post Type with Full Testing

```bash
# With all tests enabled
python main.py -p "Create a plugin for managing team members with custom post type, taxonomies, and Gutenberg blocks" --all-tests
```

### WooCommerce Extension with Specific Tests

```bash
# Only WordPress Playground and Plugin Check
python main.py -p "Create a WooCommerce extension that adds custom product fields" --playground --wp-check
```

## Enhanced Progress Feedback

The generator now provides detailed progress updates during plugin creation:

1. **Planning Phase**: Shows requirements analysis
2. **Specification Details**: Displays plugin name, slug, and features
3. **File Generation**: Reports number of files created
4. **Writing Progress**: Shows each file as it's written
5. **Compliance Summary**: Reports errors, warnings, and suggestions
6. **Testing Status**: Shows which tests are running and their results

## Troubleshooting

### Environment Issues

Run the environment check:
```bash
python main.py --check
```

### Common Issues

1. **API Key Not Found**
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

2. **Docker Not Available**
   - Install Docker Desktop or Docker Engine
   - Testing will be simulated without Docker

3. **PHP Syntax Checking Failed**
   - Install PHP CLI: `brew install php` (macOS) or `apt install php-cli` (Ubuntu)

### Verbose Mode

For detailed debugging information:
```bash
python main.py -p "your plugin description" -v
```

## Development

### Project Structure

```
pluginator/
├── main.py              # Enhanced CLI entry point
├── plugin_agents.py     # Multi-agent definitions
├── tools.py            # Enhanced tool implementations
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # WordPress test environment with WP-CLI & PHPUnit
└── plugins/           # Generated plugins directory
```

### Enhanced Docker Environment

The `docker-compose.yml` now includes:
- **WP-CLI**: Pre-installed WordPress command-line interface
- **PHPUnit**: Unit testing framework for WordPress plugins
- **Composer**: PHP dependency management
- **PHPMyAdmin**: Optional database management interface (port 8080)
- **Debug Mode**: WordPress debug logging enabled

### Testing Generated Plugins

#### 1. WordPress Playground Testing

Test your plugin in a browser-based WordPress environment:

```bash
# The generator can automatically test with WordPress Playground
# This uses Selenium to verify plugin activation
```

#### 2. WordPress Plugin Check

Run the official WordPress Plugin Check tool:

```bash
# Start Docker environment
docker-compose up -d

# Plugin will be automatically checked during generation
# Or manually run: docker-compose exec wordpress wp plugin check <plugin-slug>
```

#### 3. PHPUnit Testing

Generate and run unit tests:

```bash
# Generator can create PHPUnit bootstrap files
# Tests run automatically in Docker environment
```

### Adding New Tools

1. Create a new function in `tools.py`:
```python
@function_tool
def your_custom_tool(param: str) -> str:
    """Tool description for the agent.
    
    Args:
        param: Parameter description
    """
    # Implementation
    return result
```

2. Add the tool to the appropriate agent in `plugin_agents.py`

### Customizing Agents

Agents can be customized by modifying their:
- Instructions
- Model settings (temperature, model version)
- Output types (Pydantic models)
- Available tools

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- Built with [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- WordPress coding standards and best practices
- Community feedback and contributions

## 📦 Installation

### Prerequisites

- Python 3.9+
- An API key for your chosen AI provider (see [Quick Start Guide](QUICKSTART.md))

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/pluginator.git
cd pluginator

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with LiteLLM support for all models
pip install "openai-agents[litellm]==0.0.16"

# Install other dependencies
pip install -r requirements.txt

# Set up environment (copy and edit)
cp env.example .env
# Edit .env with your API keys and model preferences
```

### OpenAI-Only Installation (Smaller)

If you only plan to use OpenAI models:

```bash
pip install openai-agents==0.0.16
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key-here"
```

### Optional Enhancements

- **Docker & Docker Compose**: For testing plugins in real WordPress environments
- **PHP CLI**: For syntax validation of generated code
- **Ollama**: For free local AI models (see [Quick Start Guide](QUICKSTART.md))

### Verify Installation

```bash
# Check that everything is working
python main.py --list-models

# Test with a simple plugin
python main.py -p "Create a simple hello world widget plugin"
```