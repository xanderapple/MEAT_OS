import subprocess
import sys
import re

def execute_script(command: str, args: list = None) -> (bool, str):
    """Helper to execute shell commands or Python scripts via subprocess."""
    if args is None:
        args = []
    
    if command.endswith(".py"): # Assume it's a Python script
        full_command = [sys.executable, command] + args
    else: # Assume it's a shell command (e.g., git)
        full_command = [command] + args

    result = subprocess.run(full_command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        return False, f"Error executing {command} {' '.join(args)}: {result.stderr.strip()}\n{result.stdout.strip()}"

def sanitize_filename(text):
    """Remove invalid characters and replace spaces with underscores for consistency."""
    text = re.sub(r'[<>:"/\\|?*]', '', text).strip()
    text = text.replace(' ', '_')
    return text
