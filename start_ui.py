#!/usr/bin/env python3
"""
Launch script for WordPress Plugin Generator Streamlit UI.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import plotly
        print("✅ Dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0", "plotly>=5.17.0"])
        return True

def check_environment():
    """Check if environment is properly configured."""
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("Please create a .env file with your API keys:")
        print("OPENAI_API_KEY=your_openai_key_here")
        print("ANTHROPIC_API_KEY=your_anthropic_key_here")
        return False
    
    # Check for basic API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found in .env file")
        print("Please add at least one API key to your .env file")
        return False
    
    if openai_key:
        print("✅ OpenAI API key found")
    if anthropic_key:
        print("✅ Anthropic API key found")
    
    return True

def launch_streamlit():
    """Launch the Streamlit application."""
    print("🚀 Launching WordPress Plugin Generator UI...")
    print("📱 The web interface will open in your browser")
    print("🔗 URL: http://localhost:8501")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")

def main():
    """Main entry point."""
    print("🔌 WordPress Plugin Generator - Web UI")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment
    if not check_environment():
        return
    
    # Launch Streamlit
    launch_streamlit()

if __name__ == "__main__":
    main()