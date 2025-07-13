"""
Streamlit Web UI for WordPress Plugin Generator
Beautiful, user-friendly interface for non-technical users to generate WordPress plugins.
"""

import streamlit as st
import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional

# Import our main functionality
from main import run_agent, validate_environment
from models import model_manager
from context_manager import context_manager
from monitoring_tools import get_performance_metrics, get_session_metrics
from agent_hooks import plugin_hooks


def init_page_config():
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title="WordPress Plugin Generator",
        page_icon="🔌",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/migkapa/pluginator',
            'Report a bug': 'https://github.com/migkapa/pluginator/issues',
            'About': """
            # WordPress Plugin Generator
            
            AI-powered tool for creating production-ready WordPress plugins.
            
            **Features:**
            - 🎯 Context-aware generation
            - 🔒 Security validation
            - 📊 Performance monitoring  
            - 🔄 Structured workflows
            
            Built with OpenAI Agents Python and Streamlit.
            """
        }
    )


def load_custom_css():
    """Load custom CSS for better styling."""
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    </style>
    """, unsafe_allow_html=True)


def show_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">🔌 WordPress Plugin Generator</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Create professional WordPress plugins with AI - no coding required!
        </p>
    </div>
    """, unsafe_allow_html=True)


def show_sidebar():
    """Display the sidebar with settings and information."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        models = [
            "gpt-4o",
            "gpt-4o-mini", 
            "claude-3-5-sonnet",
            "claude-3-5-haiku",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro"
        ]
        
        selected_model = st.selectbox(
            "🤖 AI Model",
            models,
            index=1,  # Default to gpt-4o-mini
            help="Choose the AI model for plugin generation. GPT-4o-mini is recommended for speed and cost-effectiveness."
        )
        
        # Advanced testing options
        st.subheader("🧪 Advanced Testing")
        test_playground = st.checkbox("WordPress Playground", help="Test plugin in WordPress Playground environment")
        test_plugin_check = st.checkbox("WordPress Plugin Check", help="Run official WordPress plugin validation")
        test_phpunit = st.checkbox("PHPUnit Testing", help="Generate and run PHPUnit tests")
        
        # Performance settings
        st.subheader("⚡ Performance")
        max_retries = st.slider("Max Retries", 1, 5, 3, help="Maximum retry attempts on failure")
        
        # API key status
        st.subheader("🔑 API Status")
        api_keys = model_manager.validate_api_keys()
        for provider, available in api_keys.items():
            status = "✅" if available else "❌"
            st.write(f"{status} {provider.capitalize()}")
        
        return {
            "model": selected_model,
            "testing": {
                "playground": test_playground,
                "wp_check": test_plugin_check, 
                "phpunit": test_phpunit
            },
            "max_retries": max_retries
        }


def show_feature_highlights():
    """Display feature highlights."""
    st.header("✨ Key Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Context Aware</h4>
            <p>Maintains context across the generation process for better results</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🔒 Security First</h4>
            <p>Built-in security validation and WordPress best practices</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Monitoring</h4>
            <p>Real-time performance tracking and detailed analytics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h4>🔄 Reliable</h4>
            <p>Structured workflows with error handling and recovery</p>
        </div>
        """, unsafe_allow_html=True)


def show_examples():
    """Display example plugin ideas."""
    with st.expander("💡 Plugin Ideas & Examples"):
        st.markdown("""
        **Simple Plugins:**
        - Contact form with email notifications
        - Image gallery with lightbox
        - FAQ section with accordion display
        - Social media sharing buttons
        
        **Intermediate Plugins:**
        - Event calendar with booking system
        - Product catalog with filtering
        - User registration with custom fields
        - Newsletter subscription with MailChimp integration
        
        **Advanced Plugins:**
        - E-commerce integration with payment processing
        - Learning management system (LMS)
        - Multi-vendor marketplace
        - Social network features
        
        **Example Descriptions:**
        - "Create a contact form plugin with name, email, phone, and message fields. Save submissions to database and send email notifications to admin."
        - "Build an image gallery plugin that displays photos in a grid layout with lightbox popup when clicked. Include categories and tags."
        - "Make an event calendar plugin where users can view upcoming events and register for them. Include email confirmations."
        """)


async def generate_plugin_async(description: str, config: Dict[str, Any]):
    """Generate plugin asynchronously with proper error handling."""
    try:
        # Set model
        model_manager.current_model = config["model"]
        
        # Create testing options
        testing_options = config["testing"]
        
        # Run the generation
        result = await run_agent(
            prompt=description,
            max_retries=config["max_retries"],
            testing_options=testing_options
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_generation_interface():
    """Main plugin generation interface."""
    st.header("🚀 Generate Your Plugin")
    
    # Plugin description input
    description = st.text_area(
        "Describe your plugin:",
        height=150,
        placeholder="Describe what your plugin should do. Be specific about features, functionality, and any special requirements...\n\nExample: Create a contact form plugin with name, email, and message fields. Save submissions to the database and send email notifications to admin when a new submission is received.",
        help="Provide a detailed description of your plugin. The more specific you are, the better the result will be."
    )
    
    # Quick suggestion buttons
    st.markdown("**Quick suggestions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Contact Form"):
            st.session_state.description = "Create a contact form plugin with name, email, phone, and message fields. Save submissions to database and send email notifications to admin."
    
    with col2:
        if st.button("🖼️ Image Gallery"):
            st.session_state.description = "Build an image gallery plugin that displays photos in a responsive grid layout with lightbox popup. Include categories and image upload functionality."
    
    with col3:
        if st.button("📅 Event Calendar"):
            st.session_state.description = "Create an event calendar plugin where users can view upcoming events, register for events, and receive email confirmations."
    
    with col4:
        if st.button("❓ FAQ Section"):
            st.session_state.description = "Make an FAQ plugin with collapsible questions and answers, search functionality, and admin interface to manage FAQs."
    
    # Use session state for description if set by buttons
    if "description" in st.session_state:
        description = st.session_state.description
        st.rerun()
    
    return description


def show_generation_progress(description: str, config: Dict[str, Any]):
    """Handle the generation process with progress tracking."""
    if st.button("🚀 Generate Plugin", type="primary", use_container_width=True):
        if not description.strip():
            st.error("Please provide a description of your plugin.")
            return
        
        # Validate environment
        valid, issues = validate_environment()
        if not valid:
            st.error("Environment validation failed:")
            for issue in issues:
                st.error(f"• {issue}")
            return
        
        # Show generation progress
        with st.container():
            st.markdown("### 🔄 Generating Your Plugin...")
            
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_text = st.empty()
            
            # Create columns for metrics
            col1, col2, col3 = st.columns(3)
            
            start_time = time.time()
            
            # Run generation
            with st.spinner("Initializing plugin generation..."):
                status_text.text("🚀 Starting generation process...")
                progress_bar.progress(10)
                
                # Create event loop for async execution
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Update progress periodically
                    progress_updates = [
                        (20, "📋 Analyzing requirements..."),
                        (30, "🔍 Validating specifications..."), 
                        (40, "⚙️ Generating code structure..."),
                        (60, "📝 Creating plugin files..."),
                        (70, "🔒 Running security checks..."),
                        (80, "✅ Validating compliance..."),
                        (90, "📦 Packaging plugin..."),
                    ]
                    
                    # Simulate progress updates (in real app, you'd get these from hooks)
                    import threading
                    import random
                    
                    def update_progress():
                        for progress, message in progress_updates:
                            time.sleep(random.uniform(2, 4))  # Simulate work
                            progress_bar.progress(progress)
                            status_text.text(message)
                            
                            elapsed = time.time() - start_time
                            time_text.text(f"⏱️ Elapsed: {elapsed:.1f}s")
                            
                            # Update metrics
                            with col1:
                                st.metric("Progress", f"{progress}%")
                            with col2:
                                st.metric("Time", f"{elapsed:.1f}s")
                            with col3:
                                st.metric("Model", config["model"])
                    
                    # Start progress updates in background
                    progress_thread = threading.Thread(target=update_progress)
                    progress_thread.daemon = True
                    progress_thread.start()
                    
                    # Run the actual generation
                    result = loop.run_until_complete(generate_plugin_async(description, config))
                    
                    # Complete progress
                    progress_bar.progress(100)
                    elapsed = time.time() - start_time
                    
                    if result["success"]:
                        status_text.text("✅ Plugin generated successfully!")
                        time_text.text(f"⏱️ Total time: {elapsed:.1f}s")
                        
                        # Show success message
                        st.success("🎉 Plugin generated successfully!")
                        
                        # Display the result
                        show_generation_results(result["result"], elapsed)
                        
                    else:
                        status_text.text("❌ Generation failed")
                        st.error(f"Generation failed: {result['error']}")
                        
                        # Show error details and suggestions
                        show_error_details(result["error"])
                    
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                    show_error_details(str(e))
                
                finally:
                    loop.close()


def show_generation_results(result: str, elapsed_time: float):
    """Display the generation results with download options."""
    st.markdown("---")
    st.header("🎉 Plugin Ready!")
    
    # Parse the result to extract key information
    lines = result.split('\n')
    plugin_name = "Unknown Plugin"
    zip_path = None
    
    for line in lines:
        if "Plugin Name:" in line or "Plugin Created:" in line:
            plugin_name = line.split(":")[-1].strip()
        elif ".zip" in line and "file://" in line:
            # Extract ZIP file path
            import re
            zip_match = re.search(r'file://([^)]+\.zip)', line)
            if zip_match:
                zip_path = zip_match.group(1)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️</h3>
            <h4>Generation Time</h4>
            <p>{:.1f} seconds</p>
        </div>
        """.format(elapsed_time), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📦</h3>
            <h4>Plugin Name</h4>
            <p>{}</p>
        </div>
        """.format(plugin_name), unsafe_allow_html=True)
    
    with col3:
        files_count = result.count("Writing") + result.count("Generated")
        st.markdown("""
        <div class="metric-card">
            <h3>📁</h3>
            <h4>Files Created</h4>
            <p>{} files</p>
        </div>
        """.format(files_count), unsafe_allow_html=True)
    
    with col4:
        status = "✅ Success" if "successfully" in result.lower() else "⚠️ Partial"
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <h4>Status</h4>
            <p>{}</p>
        </div>
        """.format(status), unsafe_allow_html=True)
    
    # Download section
    st.subheader("📥 Download Your Plugin")
    
    if zip_path and os.path.exists(zip_path):
        # Read the ZIP file for download
        with open(zip_path, "rb") as file:
            zip_data = file.read()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.download_button(
                label="📦 Download Plugin ZIP",
                data=zip_data,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            st.metric("File Size", f"{len(zip_data) / 1024:.1f} KB")
    
    # Installation instructions
    with st.expander("📋 Installation Instructions"):
        st.markdown("""
        ### How to install your plugin:
        
        1. **Download** the ZIP file using the button above
        2. **Login** to your WordPress admin dashboard
        3. **Navigate** to Plugins → Add New
        4. **Click** "Upload Plugin" button
        5. **Choose** the downloaded ZIP file
        6. **Click** "Install Now"
        7. **Click** "Activate Plugin"
        
        ### Need help?
        - Check the plugin's readme.txt file for specific instructions
        - Ensure your WordPress version is compatible
        - Contact support if you encounter any issues
        """)
    
    # Detailed generation report
    with st.expander("📊 Detailed Generation Report"):
        st.code(result, language="text")


def show_error_details(error_message: str):
    """Show detailed error information and suggestions."""
    st.markdown("---")
    st.header("❌ Generation Failed")
    
    # Common error patterns and solutions
    error_solutions = {
        "API key": {
            "title": "🔑 API Key Issue",
            "description": "The selected model's API key is missing or invalid.",
            "solutions": [
                "Check your .env file for the correct API key",
                "Verify the API key is valid and has sufficient credits",
                "Try a different model that has a valid API key"
            ]
        },
        "timeout": {
            "title": "⏱️ Timeout Error", 
            "description": "The generation process took too long to complete.",
            "solutions": [
                "Try again with a simpler plugin description",
                "Increase the max retries setting",
                "Check your internet connection"
            ]
        },
        "max turns": {
            "title": "🔄 Max Turns Exceeded",
            "description": "The agent needed more conversation turns than allowed.",
            "solutions": [
                "Simplify your plugin description",
                "Be more specific about requirements",
                "Try a different AI model"
            ]
        }
    }
    
    # Find matching error type
    error_type = None
    for key in error_solutions:
        if key.lower() in error_message.lower():
            error_type = key
            break
    
    if error_type:
        solution = error_solutions[error_type]
        st.markdown(f"""
        <div class="warning-message">
            <h4>{solution['title']}</h4>
            <p>{solution['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("💡 Suggested Solutions:")
        for solution_text in solution["solutions"]:
            st.write(f"• {solution_text}")
    
    # Show full error details
    with st.expander("🔍 Technical Details"):
        st.code(error_message, language="text")
    
    # Suggest retry with different settings
    st.info("💡 **Tip**: Try simplifying your description or selecting a different AI model.")


def show_analytics_dashboard():
    """Display analytics and performance dashboard."""
    st.header("📊 Analytics Dashboard")
    
    try:
        # Get performance metrics
        metrics = get_performance_metrics()
        
        if metrics.get("overall_health"):
            health = metrics["overall_health"]
            
            # Health status
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("System Health", f"{health['success_rate']:.1f}%")
            with col2:
                st.metric("Total Runs", health['total_runs'])
            with col3:
                st.metric("Total Errors", health['total_errors'])
            with col4:
                status_color = "🟢" if health['status'] == "healthy" else "🟡" if health['status'] == "degraded" else "🔴"
                st.metric("Status", f"{status_color} {health['status'].title()}")
            
            # Performance charts
            if metrics.get("agent_performance"):
                st.subheader("⚡ Agent Performance")
                
                perf_data = metrics["agent_performance"]
                agents = list(perf_data.keys())
                avg_times = [perf_data[agent]["avg_duration"] for agent in agents]
                
                # Create performance chart
                fig = px.bar(
                    x=agents,
                    y=avg_times,
                    title="Average Agent Execution Time",
                    labels={"x": "Agent", "y": "Time (seconds)"}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent activity
            if metrics.get("recent_activity"):
                st.subheader("📈 Recent Activity")
                activity = metrics["recent_activity"]
                
                # Create activity pie chart
                if activity.get("event_types"):
                    event_types = list(activity["event_types"].keys())
                    event_counts = list(activity["event_types"].values())
                    
                    fig = px.pie(
                        values=event_counts,
                        names=event_types,
                        title="Event Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No performance data available yet. Generate a plugin to see analytics!")
    
    except Exception as e:
        st.warning(f"Analytics data unavailable: {str(e)}")


def show_session_history():
    """Display session history and context management."""
    st.header("📋 Session History")
    
    try:
        contexts = context_manager.list_contexts()
        
        if contexts:
            st.subheader(f"Recent Sessions ({len(contexts)} total)")
            
            for ctx in contexts[:10]:  # Show last 10 sessions
                with st.expander(f"🔗 {ctx.get('plugin_name', 'Unknown Plugin')} - {ctx.get('session_id', '')[:8]}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Phase:** {ctx.get('current_phase', 'Unknown')}")
                        st.write(f"**Progress:** {ctx.get('progress', 0):.1f}%")
                    
                    with col2:
                        st.write(f"**Started:** {ctx.get('start_time', 'Unknown')}")
                        st.write(f"**Plugin:** {ctx.get('plugin_name', 'N/A')}")
                    
                    with col3:
                        if st.button(f"View Details", key=f"details_{ctx.get('session_id', '')}"):
                            # Show session metrics
                            session_metrics = get_session_metrics(ctx.get('session_id', ''))
                            st.json(session_metrics)
        else:
            st.info("No session history available. Generate a plugin to start tracking sessions!")
    
    except Exception as e:
        st.warning(f"Session history unavailable: {str(e)}")


def main():
    """Main Streamlit application."""
    # Initialize page
    init_page_config()
    load_custom_css()
    
    # Show header
    show_header()
    
    # Get sidebar configuration
    config = show_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Generate", "✨ Features", "📊 Analytics", "📋 History"])
    
    with tab1:
        show_examples()
        description = show_generation_interface()
        show_generation_progress(description, config)
    
    with tab2:
        show_feature_highlights()
        
        # Technical details
        with st.expander("🔧 Technical Details"):
            st.markdown("""
            ### OpenAI Agents Python Integration
            
            This application leverages advanced AI agent capabilities:
            
            - **Context Injection**: Maintains session state across generation
            - **Security Guardrails**: Validates code for WordPress security best practices
            - **Agent Hooks**: Monitors performance and tracks metrics
            - **Agent Handoffs**: Coordinates between specialized agents
            
            ### Supported Models
            
            - **OpenAI**: GPT-4o, GPT-4o-mini, o1-preview, o1-mini
            - **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku
            - **Google**: Gemini 2.0 Flash, Gemini 1.5 Pro
            - **Groq**: Llama 3.1 70B, Mixtral 8x7B
            - **Ollama**: Local models (requires Ollama server)
            
            ### Architecture
            
            Built using:
            - **Streamlit**: Modern web interface
            - **OpenAI Agents Python**: Advanced agent capabilities
            - **LiteLLM**: Multi-provider model support
            - **Plotly**: Interactive charts and visualizations
            """)
    
    with tab3:
        show_analytics_dashboard()
    
    with tab4:
        show_session_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit and OpenAI Agents Python</p>
        <p>
            <a href="https://github.com/migkapa/pluginator" target="_blank">GitHub</a> | 
            <a href="https://github.com/migkapa/pluginator/issues" target="_blank">Report Issues</a> |
            <a href="https://github.com/migkapa/pluginator/wiki" target="_blank">Documentation</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()