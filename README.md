 # WordPress Plugin Generator Agent System

 This project uses the OpenAI Agents SDK to create a multi-agent system that generates WordPress plugins, ensures compliance with coding standards, and tests the plugin in a WordPress Playground.

 ## Prerequisites

 - Docker and Docker Compose
 - Python 3.8+
 - OpenAI Agents SDK (e.g., `pip install openai-agents-sdk`)
 - Set your OpenAI API key:

   ```bash
   export OPENAI_API_KEY=your_api_key_here
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

 ```bash
 python main.py
 ```

 Follow the prompt to describe your plugin. The system will:

 1. Query the Plugin Spec Agent for plugin details.
 2. Generate plugin files via the File Generator Agent.
 3. Check coding standards compliance via the Compliance Agent.
 4. Start the WordPress Playground, activate and list the plugin via the Testing Agent.

 The final report will be displayed in the console.