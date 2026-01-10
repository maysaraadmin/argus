#!/usr/bin/env python3
"""
Argus MVP - Start all services
"""
import sys
import os
import subprocess
import time

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Stopping Argus MVP...")
    if hasattr(signal, "SIGINT"):
        sys.exit(0)

def start_api():
    """Start API server"""
    print("🔧 Starting API Server...")
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
    
    api_cmd = [
        sys.executable, '-c',
        'import sys; sys.path.insert(0, "d:\\argus\\src"); '
        'from src.api.server import app; '
        'import uvicorn; '
        'uvicorn.run(app, host="localhost", port=8000)'
    ]
    
    try:
        process = subprocess.Popen(api_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("   ✅ API Server started!")
        print("   📊 API Documentation: http://localhost:8000/docs")
        return process
    except Exception as e:
        print(f"   ❌ Failed to start API Server: {e}")
        return None

def start_ui():
    """Start Streamlit UI"""
    print("📊 Starting Streamlit UI...")
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
    
    ui_cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        'src/ui/app.py',
        '--server.address=localhost',
        '--server.port=8501'
    ]
    
    try:
        process = subprocess.Popen(ui_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("   ✅ Streamlit UI started!")
        print("   🌐 Web Interface: http://localhost:8501")
        return process
    except Exception as e:
        print(f"   ❌ Failed to start Streamlit UI: {e}")
        return None

def check_service(url, description, timeout=5):
    """Check if a service is responding"""
    try:
        import requests
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    """Main startup function"""
    print("🚀 Argus MVP - Starting all services...")
    print("=" * 50)
    
    # Set up signal handler
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start services
    api_process = start_api()
    ui_process = start_ui()
    
    if not api_process or not ui_process:
        print("❌ Failed to start services")
        return 1
    
    # Wait for services to start
    time.sleep(3)
    
    # Check service status
    api_healthy = check_service("http://localhost:8000/health", "API Server")
    ui_healthy = check_service("http://localhost:8501", "Streamlit UI")
    
    print("\n🎯 Services Status:")
    print(f"   🔧 API Server: {'✅ Running' if api_healthy else '❌ Failed'}")
    print(f"   📊 Streamlit UI: {'✅ Running' if ui_healthy else '❌ Failed'}")
    
    if api_healthy and ui_healthy:
        print("\n🎉 All services started successfully!")
        print("\n📋 Access Points:")
        print("   🌐 Web Interface: http://localhost:8501")
        print("   🔧 API Server: http://localhost:8000")
        print("   📚 API Documentation: http://localhost:8000/docs")
        print("   ❤️  Health Check: http://localhost:8000/health")
        print("\n📋 Use Ctrl+C to stop all services")
        
        # Keep script running
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
            if api_process:
                api_process.terminate()
                api_process.wait()
            if ui_process:
                ui_process.terminate()
                ui_process.wait()
            print("✅ Services stopped")
    else:
        print("\n❌ Some services failed to start")
        return 1
    
    print("\n👋 Argus MVP startup complete")

if __name__ == "__main__":
    main()
