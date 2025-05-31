# 🚀 Quick Start Guide: AI Models for WordPress Plugin Generator

This guide will help you get up and running with different AI models in just a few minutes.

## 🎯 30-Second Quick Start

### Option 1: OpenAI (Default - Just Works)
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Generate a plugin
python main.py -p "Create a contact form plugin"
```

### Option 2: Local Ollama (Free, No API Key)
```bash
# Install Ollama from https://ollama.ai
# Then pull and run a model
ollama pull deepseek-r1:14b
python main.py --model ollama/deepseek-r1:14b -p "Create a plugin"
```

### Option 3: Claude (High Quality)
```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Generate with Claude
python main.py --model claude-3-5-haiku-20241022 --disable-tracing -p "Create a plugin"
```

## 📋 Provider-Specific Setup

### 🤖 OpenAI (Recommended for Beginners)

**Pros:** Best reliability, most features, excellent documentation  
**Cons:** Requires API costs  

```bash
# 1. Get API key from https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-your-key-here"

# 2. Use default model
python main.py -p "Create a SEO optimization plugin"

# 3. Or specify model explicitly
python main.py --model gpt-4o-mini -p "Create a faster plugin"
```

### 🏠 Ollama (Best for Privacy & Free Usage)

**Pros:** Completely free, runs locally, no data sent to external servers  
**Cons:** Requires local setup, performance depends on your hardware  

```bash
# 1. Install Ollama from https://ollama.ai
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start Ollama service
ollama serve

# 3. Pull a recommended model (in a new terminal)
ollama pull deepseek-r1:14b

# 4. Generate plugin
python main.py --model ollama/deepseek-r1:14b -p "Create a blog management plugin"

# Alternative smaller model (faster but less capable)
ollama pull llama3.2:latest
python main.py --model ollama/llama3.2:latest -p "Create a simple widget"
```

**Recommended Ollama Models:**
- `deepseek-r1:14b` - Best balance of quality and speed
- `llama3.2:latest` - Fastest, good for simple tasks
- `codellama:latest` - Specialized for code generation

### 🧠 Anthropic Claude (Best for Complex Logic)

**Pros:** Excellent reasoning, great for complex tasks, thoughtful responses  
**Cons:** Requires API costs, may need tracing disabled  

```bash
# 1. Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 2. Generate with Claude (note the --disable-tracing flag)
python main.py --model claude-3-5-haiku-20241022 --disable-tracing -p "Create an advanced analytics plugin"

# 3. For more complex tasks, use the larger model
python main.py --model claude-3-5-sonnet-20241022 --disable-tracing -p "Create a complex e-commerce plugin"
```

### 🌟 Google Gemini (Good Balance)

**Pros:** Fast, good quality, competitive pricing  
**Cons:** Requires API setup  

```bash
# 1. Get API key from https://makersuite.google.com/app/apikey
export GOOGLE_API_KEY="AIza-your-key-here"

# 2. Generate with Gemini
python main.py --model litellm/gemini/gemini-1.5-flash -p "Create a content management plugin"

# 3. For higher quality (slower)
python main.py --model litellm/gemini/gemini-1.5-pro -p "Create a sophisticated plugin"
```

### ⚡ Groq (Ultra-Fast)

**Pros:** Extremely fast responses, good for rapid prototyping  
**Cons:** Requires API setup, limited model selection  

```bash
# 1. Get API key from https://console.groq.com/keys
export GROQ_API_KEY="gsk-your-key-here"

# 2. Generate with Groq (very fast)
python main.py --model litellm/groq/llama-3.1-70b-versatile -p "Create a fast plugin prototype"
```

## 🛠️ Common Commands & Tips

### Model Discovery
```bash
# See all available models and providers
python main.py --list-models

# Check which API keys you have configured
python main.py --check  # (if this option exists)
```

### Customization
```bash
# Custom temperature (0.0 = focused, 1.0 = creative)
python main.py --model ollama/deepseek-r1:14b --temperature 0.3 -p "Create a precise plugin"

# Verbose output to see what's happening
python main.py --model claude-3-5-haiku-20241022 --disable-tracing -p "Create a plugin" -v

# Different output format or style
python main.py --model gpt-4o -p "Create a plugin with modern ES6 JavaScript"
```

### Environment Setup
```bash
# Copy the example environment file
cp env.example .env

# Edit .env to set your preferred default model and API keys
# Then you can just run:
python main.py -p "Create a plugin"
```

## 🐛 Troubleshooting

### Common Issues & Solutions

#### "API key not found" or authentication errors
```bash
# Make sure your API key is set correctly
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# For Claude models, try disabling tracing
python main.py --model claude-3-5-haiku-20241022 --disable-tracing -p "test"
```

#### Ollama not responding
```bash
# Make sure Ollama is running
ollama serve

# Check if your model is downloaded
ollama list

# Pull the model if missing
ollama pull deepseek-r1:14b
```

#### Model gets stuck or produces poor output
```bash
# Try a larger/better model
python main.py --model gpt-4o -p "your prompt"  # Instead of gpt-4o-mini

# Lower the temperature for more focused output
python main.py --model ollama/deepseek-r1:14b --temperature 0.2 -p "your prompt"

# Check if your prompt is clear and specific
python main.py --model gpt-4o -p "Create a WordPress plugin that adds a contact form with name, email, and message fields"
```

#### Installation issues
```bash
# If you get LiteLLM import errors
pip install "openai-agents[litellm]==0.0.16"

# If other dependencies are missing
pip install -r requirements.txt
```

## 🎯 Which Model Should I Use?

### For Different Use Cases:

| **Use Case** | **Recommended Model** | **Command** |
|--------------|----------------------|-------------|
| **Learning/Testing** | Ollama (free) | `--model ollama/deepseek-r1:14b` |
| **Production Plugins** | OpenAI GPT-4o | `--model gpt-4o` |
| **Fast Prototyping** | OpenAI GPT-4o Mini | `--model gpt-4o-mini` |
| **Complex Logic** | Claude Sonnet | `--model claude-3-5-sonnet-20241022 --disable-tracing` |
| **Budget-Conscious** | Ollama or Groq | `--model ollama/llama3.2:latest` |
| **Privacy-Focused** | Ollama | `--model ollama/deepseek-r1:14b` |

### Performance vs Cost:

- **🆓 Free**: Ollama models (local)
- **💰 Cheap**: gpt-4o-mini, claude-3-5-haiku
- **💰💰 Premium**: gpt-4o, claude-3-5-sonnet
- **⚡ Fast**: Groq models, gemini-1.5-flash

## 🚀 Next Steps

1. **Pick a model** from the options above
2. **Set up your API key** (or install Ollama)
3. **Test with a simple plugin**:
   ```bash
   python main.py --model YOUR_CHOSEN_MODEL -p "Create a simple hello world widget plugin"
   ```
4. **Explore the generated code** in the `plugins/` directory
5. **Try more complex prompts** for advanced plugins

Happy plugin generating! 🎉 