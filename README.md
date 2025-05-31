# WordPress Plugin Generator - AI-Powered Plugin Creation Tool

An advanced WordPress plugin generator that uses OpenAI's Agents SDK to create production-ready plugins through an intelligent multi-agent workflow.

## Features

### 🚀 Enhanced Capabilities

- **Multi-Agent Architecture**: Specialized agents for specification gathering, code generation, compliance checking, and testing
- **Production-Ready Code**: Generates complete WordPress plugins following coding standards and best practices
- **Comprehensive File Operations**: Enhanced file handling with proper error management and directory operations
- **Compliance Checking**: Automated verification of WordPress coding standards and plugin guidelines
- **Syntax Validation**: PHP syntax checking when PHP CLI is available
- **Smart Retry Logic**: Automatic retry on failures with exponential backoff
- **Verbose Logging**: Detailed logging options for debugging and monitoring

### 📁 Generated Plugin Structure

```
plugins/
└── your-plugin-slug/
    ├── your-plugin-slug.php      # Main plugin file
    ├── readme.txt                 # WordPress readme
    ├── includes/                  # Core functionality
    │   ├── class-plugin-admin.php
    │   └── class-plugin-public.php
    ├── admin/                     # Admin assets
    │   ├── css/
    │   └── js/
    ├── public/                    # Frontend assets
    │   ├── css/
    │   └── js/
    └── languages/                 # Translations
        └── plugin.pot
```

## Prerequisites

### Required

- Python 3.9+
- OpenAI API key
- `pip` package manager

### Optional (Enhanced Features)

- **Docker & Docker Compose**: For real WordPress environment testing
- **PHP CLI**: For syntax validation of generated code

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pluginator.git
cd pluginator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
# Or create a .env file with: OPENAI_API_KEY=your-api-key-here
```

## 🤖 Model Support (New in v0.0.16)

The WordPress Plugin Generator now supports multiple AI models beyond OpenAI, including any model supported by LiteLLM (Anthropic, Google, Groq, Cohere, and many more).

### Default Model

By default, the generator uses OpenAI's `gpt-4o` model, which provides the best balance of capabilities and performance.

### Available Models

```bash
# List all available model shortcuts and providers
python main.py --list-models
```

#### Model Shortcuts (Convenient Aliases)

For convenience, we provide shortcuts for popular models:

**OpenAI Models:**
- `gpt-4o` (default) - Latest GPT-4 with vision, structured outputs, and tool support
- `gpt-4o-mini` - Faster and more cost-effective variant
- `o1-preview` - Advanced reasoning model (fixed temperature)
- `o1-mini` - Faster reasoning model (fixed temperature)

**Anthropic Models:**
- `claude-3-5-sonnet` - Latest Claude with strong capabilities
- `claude-3-5-haiku` - Fast and efficient Claude model
- `claude-3-opus` - Most capable Claude model

**Google Models:**
- `gemini-2.0-flash` - Fast Gemini model with good performance
- `gemini-1.5-pro` - Advanced Gemini model
- `gemini-1.5-flash` - Balanced Gemini model

**Other Models:**
- `llama-3.1-70b` - Meta's LLaMA via Groq
- `mixtral-8x7b` - Mistral model via Groq

#### Using Any LiteLLM Model

You can use **any model supported by LiteLLM** with the format:
```
litellm/provider/model-name
```

Examples:
```bash
# Anthropic models
--model litellm/anthropic/claude-3-5-sonnet-20241022
--model litellm/anthropic/claude-3-haiku-20240307

# Google models  
--model litellm/gemini/gemini-2.0-flash-exp
--model litellm/gemini/gemini-1.5-pro

# Groq models
--model litellm/groq/llama-3.1-8b-instant
--model litellm/groq/mixtral-8x7b-32768

# Cohere models
--model litellm/cohere/command-r-plus

# And many more providers...
```

See all supported providers at: https://docs.litellm.ai/docs/providers

### Using Alternative Models

#### Method 1: Command Line
```bash
# Use shortcuts
python main.py -p "Create a contact form plugin" --model claude-3-5-sonnet
python main.py -p "Create a SEO plugin" --model gemini-2.0-flash

# Use any LiteLLM model directly
python main.py -p "Create a plugin" --model litellm/groq/llama-3.1-70b-versatile

# With custom temperature and tracing disabled
python main.py -p "Create a plugin" --model claude-3-5-sonnet --temperature 0.5 --disable-tracing
```

#### Method 2: Environment Variables
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and set:
# DEFAULT_MODEL=claude-3-5-sonnet
# ANTHROPIC_API_KEY=your-anthropic-key

# Or use any LiteLLM model:
# DEFAULT_MODEL=litellm/groq/llama-3.1-70b-versatile
# GROQ_API_KEY=your-groq-key
```

### API Key Requirements

Different models require different API keys:

| Provider | Environment Variable | Get API Key | Shortcuts Available |
|----------|---------------------|-------------|-------------------|
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | ✓ |
| Anthropic | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | ✓ |
| Google | `GOOGLE_API_KEY` | [makersuite.google.com](https://makersuite.google.com) | ✓ |
| Groq | `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | ✓ |
| Cohere | `COHERE_API_KEY` | [dashboard.cohere.ai](https://dashboard.cohere.ai) | - |

### Installing LiteLLM Support (Optional)

To use non-OpenAI models, install the optional LiteLLM dependency:

```bash
pip install "openai-agents[litellm]==0.0.16"
```

### Model-Specific Considerations

1. **Structured Outputs**: Some models don't support structured JSON outputs. The generator will handle this gracefully but may occasionally produce invalid JSON with these models.

2. **Multimodal Support**: Not all models support image inputs. This doesn't affect the plugin generator as it works with text only.

3. **API Compatibility**: Non-OpenAI models use the Chat Completions API instead of the Responses API.

4. **Tracing**: When using non-OpenAI models, you may want to disable tracing with `--disable-tracing` to avoid authentication errors.

5. **Flexibility**: You can use any model name supported by LiteLLM - shortcuts are just for convenience!

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