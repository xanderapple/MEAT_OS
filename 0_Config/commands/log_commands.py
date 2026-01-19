import argparse
import sys
import re
import os
import shutil
from datetime import datetime

def log_action(log_message):
    gemini_md_path = "GEMINI.md" 
    action_log_path = "0_Config/action_log.md" 
    archive_dir = "0_Config/logs_archive"
    MAX_LOG_LINES = 300

    dated_log_entry = f"- [{datetime.now().strftime('%Y-%m-%d')}] {log_message}"

    # --- Update GEMINI.md ---
    try:
        with open(gemini_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return False, f"Error: {gemini_md_path} not found."

    action_history_pattern = re.compile(r'(### Action History\n)(.*?)(?=\n###|\Z)', re.DOTALL)
    match = action_history_pattern.search(content)

    if not match:
        return False, f"Error: '### Action History' section not found in {gemini_md_path}."

    history_start_tag = match.group(1)
    current_history_raw = match.group(2)
    
    current_log_entries = [entry.strip() for entry in current_history_raw.split('\n') if entry.strip()]
    current_log_entries.append(dated_log_entry)

    if len(current_log_entries) > 15:
        current_log_entries = current_log_entries[-15:]

    updated_history_section = history_start_tag + '\n'.join(current_log_entries) + '\n'
    new_gemini_content = action_history_pattern.sub(updated_history_section, content)

    try:
        with open(gemini_md_path, 'w', encoding='utf-8') as f:
            f.write(new_gemini_content)
        gemini_updated = True
    except Exception as e:
        return False, f"Error writing to {gemini_md_path}: {e}"


    # --- Log Rotation & Append to 0_Config/action_log.md ---
    action_log_updated = False
    archived_message = ""
    
    try:
        current_lines = 0
        if os.path.exists(action_log_path):
            with open(action_log_path, 'r', encoding='utf-8') as f:
                current_lines = sum(1 for line in f)
        
        if current_lines >= MAX_LOG_LINES:
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_path = os.path.join(archive_dir, f"action_log_{timestamp}.md")
            shutil.move(action_log_path, archive_path)
            archived_message = f" (Log archived to {archive_path})"
            
            with open(action_log_path, 'w', encoding='utf-8') as f:
                pass 

        with open(action_log_path, 'a', encoding='utf-8') as f:
            f.write(dated_log_entry + '\n')
        action_log_updated = True
    except Exception as e:
        return False, f"Error appending to {action_log_path}: {e}"

    if gemini_updated and action_log_updated:
        return True, f"Action \"{log_message}\" has been logged to GEMINI.md and {action_log_path}{archived_message}."
    else:
        return False, "Failed to log action completely."

def add_log_parser(subparsers):
    log_parser = subparsers.add_parser("log", help="Log a project action.")
    log_parser.add_argument("messages", nargs='+', help="The message(s) to log.")

def handle_log_commands(args):
    # Iterate through each message and log it
    results = []
    all_success = True
    for message in args.messages:
        success, res_message = log_action(message)
        results.append(res_message)
        if not success:
            all_success = False
    
    return all_success, "\n".join(results)
