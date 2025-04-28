#!/usr/bin/env python3
"""
One-click installation and run script for SimpleResumeApp
"""

import os
import sys
import subprocess
import platform
import time
import signal
import psutil

def is_venv():
    """Check if running in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} ({proc.name()}) running on port {port}")
                    os.kill(proc.pid, signal.SIGTERM)
                    time.sleep(1)
                    if psutil.pid_exists(proc.pid):
                        os.kill(proc.pid, signal.SIGKILL)
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False

def main():
    """Main function to install and run the app"""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=== SimpleResumeApp Installation and Run Script ===")
    
    # Check if psutil is installed, if not install it
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        print("psutil installed successfully")
    
    # Check if running in a virtual environment
    if not is_venv():
        print("Creating and activating virtual environment...")
        
        # Create virtual environment if it doesn't exist
        venv_dir = os.path.join(script_dir, "venv")
        if not os.path.exists(venv_dir):
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        
        # Determine the path to the Python executable in the virtual environment
        if platform.system() == "Windows":
            python_executable = os.path.join(venv_dir, "Scripts", "python.exe")
            activate_script = os.path.join(venv_dir, "Scripts", "activate")
        else:
            python_executable = os.path.join(venv_dir, "bin", "python")
            activate_script = os.path.join(venv_dir, "bin", "activate")
        
        # Re-run this script using the Python executable from the virtual environment
        if os.path.exists(python_executable):
            print(f"Restarting script with virtual environment Python: {python_executable}")
            os.execl(python_executable, python_executable, *sys.argv)
        else:
            print(f"Error: Virtual environment Python executable not found at {python_executable}")
            sys.exit(1)
    
    # If we get here, we're running in the virtual environment
    print("Running in virtual environment")
    
    # Install dependencies
    print("Installing dependencies...")
    requirements_file = os.path.join(script_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Dependencies installed successfully")
    else:
        print("Warning: requirements.txt not found, installing minimal dependencies")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio", "openai", "google-generativeai", "weasyprint", "python-dotenv"])
    
    # Kill any process running on port 53630
    kill_process_on_port(53630)
    
    # Start the application
    print("Starting SimpleResumeApp...")
    app_file = os.path.join(script_dir, "app.py")
    if os.path.exists(app_file):
        subprocess.check_call([
            sys.executable, 
            app_file, 
            "--host", "0.0.0.0", 
            "--port", "53630", 
            "--allow-iframe", 
            "--allow-cors"
        ])
    else:
        print(f"Error: app.py not found at {app_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()