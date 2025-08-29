"""
WordPress Plugin Generator - Simple Web Interface
Clean, focused interface for generating WordPress plugins with AI.
"""

import streamlit as st
import asyncio
import os
import time
from pathlib import Path

# Import our main functionality
from main import run_agent, validate_environment
from models import model_manager


def init_page():
    """Initialize page configuration."""
    st.set_page_config(
        page_title="WordPress Plugin Generator",
        page_icon="🔌",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Simple CSS for clean design
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #1B5E7B;
    }
    .api-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def get_latest_models():
    """Get the latest available models for each provider."""
    return {
        "OpenAI": {
            "gpt-4o": "GPT-4o (Latest)",
            "gpt-4o-mini": "GPT-4o Mini (Fast & Cost-effective)",
            "gpt-4-turbo": "GPT-4 Turbo",
            "o1-preview": "o1-preview (Reasoning)",
            "o1-mini": "o1-mini (Reasoning)"
        },
        "Anthropic": {
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (Latest)",
            "claude-3-5-haiku-20241022": "Claude 3.5 Haiku (Fast)",
            "claude-3-opus-20240229": "Claude 3 Opus (Most Capable)"
        },
        "Google": {
            "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Latest)",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-flash": "Gemini 1.5 Flash"
        },
        "Groq": {
            "llama-3.1-70b-versatile": "Llama 3.1 70B (Fast)",
            "mixtral-8x7b-32768": "Mixtral 8x7B"
        },
        "Ollama": {
            "llama3.2:latest": "Llama 3.2 (Local)",
            "codellama:latest": "Code Llama (Local)",
            "deepseek-r1:latest": "DeepSeek R1 (Local)"
        }
    }


def format_model_name(provider, model_key):
    """Format model name for the backend."""
    if provider == "OpenAI":
        return model_key
    elif provider == "Anthropic":
        return f"litellm/anthropic/{model_key}"
    elif provider == "Google":
        return f"litellm/gemini/{model_key}"
    elif provider == "Groq":
        return f"litellm/groq/{model_key}"
    elif provider == "Ollama":
        return f"ollama/{model_key}"
    else:
        return model_key


def show_api_key_section():
    """Show API key input section."""
    st.markdown('<div class="api-section">', unsafe_allow_html=True)
    st.subheader("🔑 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
    
    with col2:
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password", 
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="Get your API key from https://console.anthropic.com/"
        )
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    
    google_key = st.text_input(
        "Google API Key (Optional)",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Get your API key from https://makersuite.google.com/app/apikey"
    )
    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_model_selection():
    """Show provider and model selection."""
    st.subheader("🤖 AI Model Selection")
    
    models = get_latest_models()
    
    # Provider selection
    provider = st.selectbox(
        "Choose AI Provider",
        options=list(models.keys()),
        index=0,  # Default to OpenAI
        help="Select the AI provider you want to use"
    )
    
    # Model selection based on provider
    provider_models = models[provider]
    model_key = st.selectbox(
        f"Choose {provider} Model",
        options=list(provider_models.keys()),
        format_func=lambda x: provider_models[x],
        index=0,  # Default to first model
        help=f"Select the specific {provider} model to use"
    )
    
    # Format the model name for backend
    formatted_model = format_model_name(provider, model_key)
    
    return provider, formatted_model


async def generate_plugin_async(description: str, model: str):
    """Generate plugin asynchronously."""
    try:
        # Set the model
        model_manager.current_model = model
        
        # Run the generation
        result = await run_agent(
            prompt=description,
            max_retries=3,
            testing_options={}
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_generation_interface(model):
    """Main plugin generation interface."""
    st.subheader("📝 Plugin Description")
    
    description = st.text_area(
        "Describe your WordPress plugin:",
        height=120,
        placeholder="Example: Create a contact form plugin with name, email, and message fields. Save submissions to the database and send email notifications to the admin.",
        help="Be specific about what features you want in your plugin"
    )
    
    if st.button("🚀 Generate Plugin", type="primary"):
        if not description.strip():
            st.error("Please describe your plugin first.")
            return
        
        # Validate environment
        valid, issues = validate_environment()
        if not valid:
            st.error("Setup issues detected:")
            for issue in issues:
                st.error(f"• {issue}")
            return
        
        # Show generation progress
        with st.container():
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            start_time = time.time()
            
            # Run generation
            try:
                status_text.text("🚀 Starting plugin generation...")
                progress_bar.progress(20)
                
                # Create event loop for async execution
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Update progress
                status_text.text("⚙️ Generating plugin code...")
                progress_bar.progress(50)
                
                # Run the actual generation
                result = loop.run_until_complete(generate_plugin_async(description, model))
                
                progress_bar.progress(100)
                elapsed = time.time() - start_time
                
                if result["success"]:
                    status_text.text("✅ Plugin generated successfully!")
                    
                    st.success(f"🎉 Plugin generated in {elapsed:.1f} seconds!")
                    
                    # Show download section
                    show_download_section(result["result"])
                    
                else:
                    status_text.text("❌ Generation failed")
                    st.error(f"Generation failed: {result['error']}")
                    
                    # Show troubleshooting tips
                    show_error_help(result['error'])
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                show_error_help(str(e))
            
            finally:
                if 'loop' in locals():
                    loop.close()


def show_download_section(result: str):
    """Show plugin download section."""
    st.subheader("📦 Download Your Plugin")
    
    # Extract ZIP file path from result
    import re
    zip_match = re.search(r'file://([^)]+\.zip)', result)
    
    if zip_match:
        zip_path = zip_match.group(1)
        
        if os.path.exists(zip_path):
            # Read the ZIP file
            with open(zip_path, "rb") as file:
                zip_data = file.read()
            
            # Download button
            st.download_button(
                label="📥 Download Plugin ZIP",
                data=zip_data,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
                type="primary"
            )
            
            st.success("Plugin ready for download!")
            
            # Simple installation instructions
            with st.expander("📋 Installation Instructions"):
                st.markdown("""
                1. Download the ZIP file above
                2. Go to WordPress Admin → Plugins → Add New
                3. Click "Upload Plugin" and select the ZIP file
                4. Click "Install Now" then "Activate"
                """)
    
    else:
        st.warning("Plugin generated but ZIP file not found. Check the generation log above.")


def show_error_help(error_message: str):
    """Show helpful error information."""
    st.subheader("💡 Troubleshooting")
    
    if "api key" in error_message.lower():
        st.info("**API Key Issue**: Make sure you've entered a valid API key for your selected provider.")
    elif "timeout" in error_message.lower():
        st.info("**Timeout**: Try simplifying your plugin description or try again.")
    elif "max turns" in error_message.lower():
        st.info("**Too Complex**: Try breaking down your plugin into simpler features.")
    else:
        st.info("**General Error**: Try a different AI model or simplify your description.")


def main():
    """Main application."""
    init_page()
    
    # Header
    st.markdown('<h1 class="main-header">🔌 WordPress Plugin Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">Generate professional WordPress plugins with AI</p>', unsafe_allow_html=True)
    
    # API Key Section
    show_api_key_section()
    
    # Model Selection
    provider, model = show_model_selection()
    st.session_state.provider = provider
    st.session_state.model = model
    
    # Plugin Generation
    show_generation_interface()
    
    # Footer
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #999; font-size: 0.9rem;">Built with Streamlit • Open Source</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()