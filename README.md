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

# Check environment setup
python main.py --check

# Custom retry attempts
python main.py -p "Custom post type plugin" --max-retries 5
```

### Command Line Options

- `-p, --prompt`: Plugin description (skip interactive prompt)
- `-v, --verbose`: Enable verbose output with detailed logging
- `--check`: Check environment setup and exit
- `--max-retries`: Maximum retry attempts on failure (default: 3)

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

## Examples

### Basic Contact Form Plugin

```bash
python main.py -p "Create a simple contact form plugin with spam protection"
```

### Advanced Custom Post Type

```bash
python main.py -p "Create a plugin for managing team members with custom post type, taxonomies, and Gutenberg blocks" -v
```

### WooCommerce Extension

```bash
python main.py -p "Create a WooCommerce extension that adds custom product fields and displays them on the frontend"
```

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
├── docker-compose.yml  # WordPress test environment
└── plugins/           # Generated plugins directory
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