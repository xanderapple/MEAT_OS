import argparse
import os
import re

def _update_gemini_session_handoff(summary_content: str):
    gemini_md_path = "GEMINI.md"
    
    try:
        with open(gemini_md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        handoff_section_start = -1
        handoff_section_end = -1
        
        # Find the start and end of the Session Handoff section
        for i, line in enumerate(lines):
            if "### Session Handoff" in line:
                handoff_section_start = i
            elif handoff_section_start != -1 and line.strip().startswith("###") and "Session Handoff" not in line:
                handoff_section_end = i
                break
        
        # If handoff section was at the end of the file
        if handoff_section_start != -1 and handoff_section_end == -1:
            handoff_section_end = len(lines)

        if handoff_section_start != -1:
            # Reconstruct the file: lines before + header + new summary + lines after
            new_lines.extend(lines[:handoff_section_start + 1]) # Keep lines before and the header
            new_lines.append(summary_content.strip() + "\n") # Add the new summary content
            
            # Add back the rest of the file from after the handoff section
            if handoff_section_end != -1:
                new_lines.extend(lines[handoff_section_end:])
            
        else: # "### Session Handoff" was not found, add it
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "# 📊 Project State & History" in line:
                    new_lines.append("\n### Session Handoff\n")
                    new_lines.append(summary_content.strip() + "\n")
                    inserted = True
            if not inserted: # Fallback: add to the very beginning if main header not found
                new_lines = ["# 📊 Project State & History\n", "\n### Session Handoff\n", summary_content.strip() + "\n"] + lines


        with open(gemini_md_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True, "Session Handoff summary successfully updated in GEMINI.md."
    except Exception as e:
        return False, f"Error updating GEMINI.md session handoff: {e}"


def handle_save_commands(args):
    if args.save_command == "handoff":
        # The agent provides the summary content via the --summary argument
        success, message = _update_gemini_session_handoff(args.summary)
        if success:
            print(message)
            return True, message
        else:
            print(f"Error: {message}")
            return False, message
    return False, "Unknown save command"


def add_save_parser(subparsers):
    save_parser = subparsers.add_parser("save", help="Commands for managing session state.")
    save_subparsers = save_parser.add_subparsers(dest="save_command", help="Available save commands")

    # save handoff subcommand
    handoff_parser = save_subparsers.add_parser("handoff", help="Write a session summary for handoff to the next session.")
    handoff_parser.add_argument("summary", help="The summary content for the session handoff.")
