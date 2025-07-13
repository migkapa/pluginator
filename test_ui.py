#!/usr/bin/env python3
"""
Test script to validate Streamlit UI components.
"""

def test_imports():
    """Test that all required imports work."""
    try:
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Streamlit and Plotly imports successful")
        
        # Test our app imports
        from main import run_agent, validate_environment
        from models import model_manager
        from context_manager import context_manager
        from monitoring_tools import get_performance_metrics
        print("✅ WordPress Plugin Generator imports successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_streamlit_app():
    """Test that the Streamlit app loads without errors."""
    try:
        # Import the app (this will test syntax)
        import streamlit_app
        print("✅ Streamlit app syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Streamlit app error: {e}")
        return False

def test_environment():
    """Test environment setup."""
    try:
        from main import validate_environment
        valid, issues = validate_environment()
        
        if valid:
            print("✅ Environment validation passed")
        else:
            print("⚠️  Environment issues detected:")
            for issue in issues:
                print(f"   • {issue}")
        
        return True
    except Exception as e:
        print(f"❌ Environment test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Streamlit UI Setup")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Streamlit App", test_streamlit_app),
        ("Environment", test_environment)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n📋 Testing {name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! UI is ready to launch.")
        print("\nTo start the web interface:")
        print("   python start_ui.py")
        print("   or")
        print("   streamlit run streamlit_app.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()