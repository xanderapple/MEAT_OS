#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    # 1. Get Clipboard content
    try:
        content = subprocess.check_output(['termux-clipboard-get'], encoding='utf-8')
    except Exception as e:
        print(f"Error reading clipboard: {e}", file=sys.stderr)
        sys.exit(1)
        
    if not content.strip():
        print("Clipboard is empty.", file=sys.stderr)
        sys.exit(1)
        
    print(f"[*] Captured {len(content)} characters from clipboard.")
    
    # 2. Path to main CLI
    cli_path = os.path.join(os.getcwd(), "0_Config/main_cli.py")
    
    # 3. Call synthesis integrate
    # We pass the content directly as a string argument. 
    # For very large content, we might write to a temp file first, 
    # but synthesis integrate handles string inputs well.
    try:
        print("[*] Forwarding to Synthesis Workflow...")
        # We use a list for subprocess to handle shell escaping safely
        cmd = [sys.executable, cli_path, "synthesis", "integrate", content]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Synthesis failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
