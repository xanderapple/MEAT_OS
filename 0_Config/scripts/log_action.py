import sys
import re
import os
import shutil
from datetime import datetime

def log_action(log_message):
    gemini_md_path = "GEMINI.md" # Assuming this script is run from the project root or similar
    action_log_path = "0_Config/action_log.md" # Path to the continuous action log file
    archive_dir = "0_Config/logs_archive"
    MAX_LOG_LINES = 300

    dated_log_entry = f"- [{datetime.now().strftime('%Y-%m-%d')}] {log_message}"

    # --- Update GEMINI.md ---
    try:
        with open(gemini_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # If GEMINI.md doesn't exist, we can't update its history, but we should still log to action_log.md
        print(f"Warning: {gemini_md_path} not found. Skipping GEMINI.md update.")
        gemini_updated = False
        gemini_update_error = True
        # For this context, we will exit if GEMINI.md is not found, as it's critical.
        sys.exit(1)


    action_history_pattern = re.compile(r'(### Action History\n)(.*?)(?=\n###|\Z)', re.DOTALL)
    match = action_history_pattern.search(content)

    if not match:
        print(f"Error: '### Action History' section not found in {gemini_md_path}.")
        sys.exit(1)

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
        print(f"Error writing to {gemini_md_path}: {e}")
        gemini_updated = False
        gemini_update_error = True


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
            
            # Create fresh file
            with open(action_log_path, 'w', encoding='utf-8') as f:
                pass # Create empty file

        with open(action_log_path, 'a', encoding='utf-8') as f:
            f.write(dated_log_entry + '\n')
        action_log_updated = True
    except Exception as e:
        print(f"Error appending to {action_log_path}: {e}")
        action_log_updated = False

    # --- Final print statement ---
    if gemini_updated and action_log_updated:
        print(f"Action \"{log_message}\" has been logged to GEMINI.md and {action_log_path}{archived_message}.")
    elif gemini_updated:
        print(f"Action \"{log_message}\" has been logged to GEMINI.md, but failed to log to {action_log_path}.")
    elif action_log_updated:
        print(f"Action \"{log_message}\" has been logged to {action_log_path}{archived_message}, but failed to log to GEMINI.md.")
    else:
        print(f"Action \"{log_message}\" failed to log to both GEMINI.md and {action_log_path}.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log_action.py \"Your log message here.\"")
        sys.exit(1)
    
    message = sys.argv[1]
    log_action(message)