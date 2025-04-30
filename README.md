# WordPress Plugin Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

An AI-powered multi-agent system that generates WordPress plugins based on simple descriptions, checks for compliance with coding standards, and tests them in a WordPress Playground environment.

## Features

- **Plugin Specification Agent**: Collects requirements and converts them into structured specifications
- **File Generator Agent**: Creates all necessary WordPress plugin files based on specifications
- **Compliance Agent**: Checks generated code against WordPress coding standards
- **Testing Agent**: Simulates plugin activation in a WordPress environment

## Prerequisites

- Docker and Docker Compose
- Python 3.8+

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/wordpress-plugin-generator.git
   cd wordpress-plugin-generator
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   Alternatively, create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## WordPress Playground

Start the WordPress environment:

```bash
docker-compose up -d
```

This will start:
- MySQL database
- WordPress site on http://localhost:8000
- Plugins directory mounted at `./plugins`

## Usage

Run the generator:

```bash
python main.py
```

Follow the prompt to describe your plugin. The system will:

1. Query the Plugin Spec Agent for plugin details
2. Generate plugin files via the File Generator Agent
3. Check coding standards compliance via the Compliance Agent
4. Start the WordPress Playground, activate and list the plugin via the Testing Agent

The final report will be displayed in the console.

## Example

```
=== WordPress Plugin Generator ===
Describe the plugin you want to generate: A contact form plugin with email notifications and spam protection

[... output shows the generator working ...]

=== Generation Report ===
Plugin 'Contact Form Plus' (v1.0.0) has been successfully generated!
- 5 files created in plugins/contact-form-plus/
- Compliance check: PASSED
- Activation test: PASSED
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built using [OpenAI Agents SDK](https://github.com/openai/agents)
- Powered by GPT-4