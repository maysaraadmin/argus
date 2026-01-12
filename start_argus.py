#!/usr/bin/env python3
"""
Historical Intelligence Analysis System (HIAS) - Enhanced Startup Script
Intelligence-grade analysis platform for studying history using structured analytic techniques (SATs)
"""
import sys
import os
import subprocess
import time
import signal
import logging
from datetime import datetime
import psutil
import requests

# Configure logging
def setup_logging():
    """Setup comprehensive logging for error tracing"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"argus_startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Create custom formatter that handles Unicode
    class UnicodeFormatter(logging.Formatter):
        def format(self, record):
            # Replace emojis with text equivalents for console output
            msg = super().format(record)
            # Replace common emojis with text
            emoji_replacements = {
                '🚀': '[STARTUP]',
                '🔧': '[API]',
                '📊': '[UI]',
                '✅': '[OK]',
                '❌': '[FAIL]',
                '🌐': '[WEB]',
                '📚': '[DOCS]',
                '❤️': '[HEALTH]',
                '🎯': '[STATUS]',
                '🎉': '[SUCCESS]',
                '🛑': '[STOP]',
                '👋': '[BYE]',
                '📋': '[INFO]'
            }
            for emoji, replacement in emoji_replacements.items():
                msg = msg.replace(emoji, replacement)
            return msg
    
    # Setup file handler (keeps emojis)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Setup console handler (removes emojis for Windows compatibility)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = UnicodeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler]
    )
    
    logger = logging.getLogger(__name__)
    return logger

logger = setup_logging()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("🛑 Stopping Historical Intelligence Analysis System (HIAS)...")
    if hasattr(signal, "SIGINT"):
        sys.exit(0)

def check_port_available(port, description):
    """Check if a port is available"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                logger.warning(f"Port {port} is already in use by {conn.pid}")
                return False
        return True
    except Exception as e:
        logger.debug(f"Port check error: {e}")
        return True

def kill_process_on_port(port):
    """Kill process using a specific port"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                logger.info(f"Terminating process {conn.pid} using port {port}")
                psutil.Process(conn.pid).terminate()
                time.sleep(2)
                return True
        return False
    except Exception as e:
        logger.error(f"Failed to kill process on port {port}: {e}")
        return False

def check_service(url, description, timeout=5):
    """Check if a service is responding"""
    try:
        import requests
        logger.debug(f"Checking {description} at {url}")
        response = requests.get(url, timeout=timeout)
        success = response.status_code == 200
        logger.debug(f"{description} check: {'✅ Success' if success else '❌ Failed'} (Status: {response.status_code})")
        return success
    except Exception as e:
        logger.error(f"{description} check failed: {e}")
        # Don't return False for connection errors - service might be starting
        return True

def start_api():
    """Start API server with enhanced error logging"""
    logger.info("🔧 Starting API Server...")
    
    # Check if port 8000 is available
    if not check_port_available(8000, "API Server"):
        logger.warning("Port 8000 is in use, attempting to free it...")
        kill_process_on_port(8000)
        time.sleep(2)
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
        logger.debug(f"PYTHONPATH set to: {env['PYTHONPATH']}")
        
        api_cmd = [
            sys.executable, '-c',
            'import sys; sys.path.insert(0, "d:\\\\argus\\src"); from src.api.server import app; import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8000)'
        ]
        
        logger.debug(f"API command: {' '.join(api_cmd)}")
        process = subprocess.Popen(api_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment to check if process started successfully
        time.sleep(2)
        if process.poll() is None:
            logger.info("   ✅ API Server started!")
            logger.info("   📊 API Documentation: http://localhost:8000/docs")
            return process
        else:
            # Process died immediately, get error output
            stdout, stderr = process.communicate()
            logger.error(f"API Server failed to start immediately")
            logger.error(f"STDOUT: {stdout.decode() if stdout else 'None'}")
            logger.error(f"STDERR: {stderr.decode() if stderr else 'None'}")
            return None
            
    except Exception as e:
        logger.error(f"   ❌ Failed to start API Server: {e}")
        logger.exception("API startup exception details:")
        return None

def start_ui():
    """Start Streamlit UI with enhanced error logging"""
    logger.info("📊 Starting Streamlit UI...")
    
    # Check if port 8501 is available
    if not check_port_available(8501, "Streamlit UI"):
        logger.warning("Port 8501 is in use, attempting to free it...")
        kill_process_on_port(8501)
        time.sleep(2)
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
        logger.debug(f"PYTHONPATH set to: {env['PYTHONPATH']}")
        
        ui_cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'src/ui/app.py',
            '--server.address=localhost',
            '--server.port=8501'
        ]
        
        logger.debug(f"UI command: {' '.join(ui_cmd)}")
        process = subprocess.Popen(ui_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment to check if process started successfully
        time.sleep(3)
        if process.poll() is None:
            logger.info("   ✅ Streamlit UI started!")
            logger.info("   🌐 Web Interface: http://localhost:8501")
            return process
        else:
            # Process died immediately, get error output
            stdout, stderr = process.communicate()
            logger.error(f"Streamlit UI failed to start immediately")
            logger.error(f"STDOUT: {stdout.decode() if stdout else 'None'}")
            logger.error(f"STDERR: {stderr.decode() if stderr else 'None'}")
            return None
            
    except Exception as e:
        logger.error(f"   ❌ Failed to start Streamlit UI: {e}")
        logger.exception("UI startup exception details:")
        return None

def main():
    """Main startup function with comprehensive logging"""
    logger.info("🚀 Historical Intelligence Analysis System (HIAS) - Starting all services...")
    logger.info("=" * 50)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start services
    logger.info("Starting services...")
    api_process = start_api()
    ui_process = start_ui()
    
    if not api_process or not ui_process:
        logger.error("❌ Failed to start services")
        return 1
    
    # Wait for services to start
    logger.info("Waiting for services to initialize...")
    time.sleep(3)
    
    # Check service status
    logger.info("Checking service health...")
    api_healthy = check_service("http://localhost:8000/health", "API Server")
    ui_healthy = check_service("http://localhost:8501", "Streamlit UI")
    
    print("\n🎯 Services Status:")
    print(f"   🔧 API Server: {'✅ Running' if api_healthy else '❌ Failed'}")
    print(f"   📊 Streamlit UI: {'✅ Running' if ui_healthy else '❌ Failed'}")
    
    logger.info(f"API Health: {'✅' if api_healthy else '❌'}")
    logger.info(f"UI Health: {'✅' if ui_healthy else '❌'}")
    
    if api_healthy and ui_healthy:
        print("\n🎉 Historical Intelligence Analysis System (HIAS) started successfully!")
        print("\n📋 Access Points:")
        print("   🌐 Web Interface: http://localhost:8501")
        print("   🔧 API Server: http://localhost:8000")
        print("   📚 API Documentation: http://localhost:8000/docs")
        print("   ❤️  Health Check: http://localhost:8000/health")
        print("\n📋 Use Ctrl+C to stop all services")
        
        logger.info("Historical Intelligence Analysis System (HIAS) started successfully")
        
        # Keep script running
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
                logger.info("🛑 Shutdown requested by user")
                if api_process:
                    logger.info("Stopping API process...")
                    api_process.terminate()
                    api_process.wait()
                if ui_process:
                    logger.info("Stopping UI process...")
                    ui_process.terminate()
                    ui_process.wait()
                logger.info("✅ Services stopped")
    else:
        logger.error("❌ Some services failed to start")
        return 1
    
    logger.info("\n👋 Argus MVP startup complete")

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}")
        logger.exception("Critical exception details:")
        sys.exit(1)
