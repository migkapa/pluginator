# 🔌 WordPress Plugin Generator - Web UI

Beautiful, user-friendly web interface for the WordPress Plugin Generator. Perfect for non-technical users who want to create professional WordPress plugins using AI.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit plotly
```

### 2. Set Up API Keys
Create a `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Launch the Web UI
```bash
# Option 1: Use the launcher script
python start_ui.py

# Option 2: Direct Streamlit command
streamlit run streamlit_app.py
```

### 4. Open Your Browser
Navigate to: http://localhost:8501

## ✨ Features

### 🎯 **User-Friendly Interface**
- Clean, modern design optimized for non-technical users
- Intuitive plugin description input with examples
- Real-time progress tracking during generation
- One-click plugin download

### 🤖 **AI Model Selection**
- Support for multiple AI models (OpenAI, Anthropic, Google, Groq)
- Automatic model switching based on API key availability
- Performance-optimized model recommendations

### 🧪 **Advanced Testing Options**
- WordPress Playground integration
- Official WordPress Plugin Check
- PHPUnit test generation and execution
- Configurable testing workflows

### 📊 **Analytics & Monitoring**
- Real-time performance metrics
- Session history and context tracking
- Interactive charts and visualizations
- System health monitoring

### 🔒 **Security & Compliance**
- Built-in security validation
- WordPress coding standards compliance
- Malicious pattern detection
- Safe code generation practices

## 🎨 Interface Overview

### **Main Generation Tab**
- Plugin description input with smart suggestions
- Quick-start templates for common plugin types
- Real-time progress tracking with detailed status updates
- Instant plugin download upon completion

### **Features Tab**
- Overview of OpenAI Agents Python capabilities
- Technical documentation and architecture details
- Supported models and provider information

### **Analytics Tab**
- System performance metrics and health status
- Agent execution time analysis
- Recent activity and event distribution
- Interactive performance charts

### **History Tab**
- Session tracking and context management
- Previous plugin generation history
- Detailed session metrics and reports

## 🛠️ Configuration

### **Sidebar Settings**
- **AI Model**: Choose from available models based on your API keys
- **Advanced Testing**: Enable WordPress Playground, Plugin Check, or PHPUnit
- **Performance**: Configure retry attempts and timeout settings
- **API Status**: Real-time display of API key availability

### **Customization**
- Edit `.streamlit/config.toml` for theme and server settings
- Modify `streamlit_app.py` for custom features
- Add new quick-start templates in the interface

## 🎯 Plugin Ideas & Examples

The interface includes built-in examples for:

**Simple Plugins:**
- Contact forms with database storage
- Image galleries with lightbox display
- FAQ sections with search functionality
- Social media integration widgets

**Advanced Plugins:**
- E-commerce integration
- Event management systems
- Learning management platforms
- Multi-vendor marketplaces

## 🔧 Technical Stack

- **Frontend**: Streamlit for modern web interface
- **Backend**: OpenAI Agents Python for advanced AI capabilities
- **Visualization**: Plotly for interactive charts and analytics
- **AI Models**: Multi-provider support via LiteLLM
- **Security**: Built-in guardrails and validation systems

## 📱 Mobile Support

The interface is fully responsive and works on:
- Desktop computers (optimal experience)
- Tablets (fully functional)
- Mobile phones (basic functionality)

## 🚨 Troubleshooting

### **Common Issues**

**"No API keys found"**
- Ensure your `.env` file exists in the project root
- Verify API keys are correctly formatted
- Check that at least one API key is valid

**"Dependencies missing"**
- Run: `pip install streamlit plotly`
- For full functionality: `pip install -r requirements.txt`

**"Port already in use"**
- Change port: `streamlit run streamlit_app.py --server.port 8502`
- Or kill existing process: `pkill -f streamlit`

**"Generation fails"**
- Check API key validity and credits
- Try a simpler plugin description
- Switch to a different AI model

### **Performance Tips**

- Use **GPT-4o-mini** for faster, cost-effective generation
- Keep plugin descriptions concise but specific
- Enable only necessary advanced testing options
- Clear browser cache if interface becomes slow

## 🤝 Contributing

The web UI is part of the open-source WordPress Plugin Generator project:

- **Report Issues**: [GitHub Issues](https://github.com/migkapa/pluginator/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/migkapa/pluginator/discussions)
- **Documentation**: [Project Wiki](https://github.com/migkapa/pluginator/wiki)

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Streamlit and OpenAI Agents Python**