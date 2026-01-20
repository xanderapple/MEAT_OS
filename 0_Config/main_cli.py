import sys
import os
import argparse
import io

# Force utf-8 encoding for stdout and stderr
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the parent directory of 0_Config to sys.path if running as a script
if __name__ == "__main__" and __package__ is None:
    # This is a hack for when running main_cli.py directly.
    # It adds the project root to the sys.path so relative imports work.
    # For proper package usage, main_cli.py should be run as 'python -m 0_Config.main_cli'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # Go up one level from 0_Config
    sys.path.insert(0, project_root)
    # Adjust __package__ to enable relative imports to work as if it was imported
    # This might not always work perfectly for very complex package structures
    __package__ = "0_Config"



from .commands.synthesis_commands import add_synthesis_parser, handle_synthesis_commands
from .commands.note_commands import add_note_parser, handle_note_commands
from .commands.rag_commands import add_rag_parser, handle_rag_commands
from .commands.task_commands import add_task_parser, handle_task_commands
from .commands.save_commands import add_save_parser, handle_save_commands
from .commands.log_commands import add_log_parser, handle_log_commands
from .utils.config_parsers import parse_project_context


if __name__ == "__main__":
    # Load project variables
    project_variable_path = "0_Config/Context/PROJECT_VARIABLE.md"
    project_variables = parse_project_context(project_variable_path)

    parser = argparse.ArgumentParser(description="Gemini CLI for Obsidian PKM automation.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_synthesis_parser(subparsers)
    add_note_parser(subparsers)
    add_rag_parser(subparsers)
    add_task_parser(subparsers)
    add_save_parser(subparsers)
    add_log_parser(subparsers)


    args = parser.parse_args()


    if args.command == "synthesis":
        success, log_message = handle_synthesis_commands(args)
        if success and log_message:
            print(f"Agent Action Log: {log_message}")
        elif not success and log_message:
            print(f"Agent Action Error: {log_message}")
    elif args.command == "note":
        success, log_message = handle_note_commands(args)
        if success and log_message:
            print(f"Agent Action Log: {log_message}")
        elif not success and log_message:
            print(f"Agent Action Error: {log_message}")
    elif args.command == "rag":
        success, log_message = handle_rag_commands(args)
        if success and log_message:
            print(f"Agent Action Log: {log_message}")
        elif not success and log_message:
            print(f"Agent Action Error: {log_message}")
    elif args.command == "task":
        # The handle_task_commands function will return a tuple (success: bool, log_message: str)
        success, log_message = handle_task_commands(args)
        if success and log_message: # Only log if successful and there's a message to log
            # Here is where the agent would use its tool to log the action
            # For now, we'll just print it, as run_shell_command cannot be called directly from here
            print(f"Agent Action Log: {log_message}")
        elif not success and log_message:
            print(f"Agent Action Error: {log_message}")
    elif args.command == "save":
        success, log_message = handle_save_commands(args)
        if success and log_message:
            print(f"Agent Action Log: {log_message}")
        elif not success and log_message:
            print(f"Agent Action Error: {log_message}")
    elif args.command == "log":
        success, log_message = handle_log_commands(args)
        if success and log_message:
            print(f"Agent Action Log: {log_message}")
        elif not success and log_message:
            print(f"Agent Action Error: {log_message}")

