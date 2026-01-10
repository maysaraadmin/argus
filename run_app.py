#!/usr/bin/env python3
"""
Simple startup script for Argus MVP
"""
import sys
import os
import subprocess

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Start the Argus MVP application"""
    print("🚀 Starting Argus MVP...")
    print("=" * 50)
    
    # Check dependencies
    try:
        import streamlit
        import fastapi
        import networkx
        import pandas
        print("✅ All dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return
    
    print("\n🌐 Starting Streamlit UI...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/ui/app.py",
            "--server.address=0.0.0.0",
            "--server.port=8501"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Argus MVP stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
