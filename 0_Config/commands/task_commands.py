import argparse
import re
import os
from ..utils.task_registry import TaskRegistry, Task
from ..utils.project_management_utils import create_task_context_file # ADD THIS IMPORT
from typing import List, Optional
import subprocess
import sys
import datetime # Required for timestamps
import uuid # Required for UUID generation

# Helper to execute task commands via subprocess
def _execute_task_command(command_args: List[str]) -> (bool, str):
    full_command = [sys.executable, "0_Config/main_cli.py", "task"] + command_args
    result = subprocess.run(full_command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        return False, f"Error: {result.stderr.strip()}\n{result.stdout.strip()}"

def add_task_parser(subparsers):
    task_parser = subparsers.add_parser("task", help="Commands for managing tasks in GEMINI.md or sub-project files.")
    task_subparsers = task_parser.add_subparsers(dest="task_command", help="Available task commands")

    # set-status command
    set_status_parser = task_subparsers.add_parser("set-status", help="Set the status of a task.")
    set_status_parser.add_argument("task_name", help="The full description of the task or a unique substring.")
    set_status_parser.add_argument("--status", choices=["pending", "in_progress", "completed", "current", "cancelled"], required=True, help="The new status for the task.")
    set_status_parser.add_argument("--file", help="Optional: Path to the Markdown file containing the task. Defaults to GEMINI.md.")

    # add command
    add_parser = task_subparsers.add_parser("add", help="Add a new task. Automatically creates a Task Context File.")
    # Changed to nargs='+' for bulk adding
    add_parser.add_argument("task_description", nargs='+', help="The description(s) of the new task(s). Enclose each task in quotes if it contains spaces.")
    add_parser.add_argument("--status", choices=["pending", "in_progress", "completed", "current", "cancelled"], default="pending", help="Optional: Initial status for the task. Defaults to pending.")
    add_parser.add_argument("--file", help="Optional: Path to the Markdown file where the task should be added. Defaults to GEMINI.md.")

    # remove command
    remove_parser = task_subparsers.add_parser("remove", help="Remove a task.")
    remove_parser.add_argument("task_name", help="The full description of the task or a unique substring.")
    remove_parser.add_argument("--file", help="Optional: Path to the Markdown file containing the task. Defaults to GEMINI.md.")

    # list command
    list_parser = task_subparsers.add_parser("list", help="List tasks.")
    list_parser.add_argument("--file", help="Optional: Path to the Markdown file to list tasks from. Defaults to GEMINI.md.")
    list_parser.add_argument("--status", choices=["pending", "in_progress", "completed", "current", "cancelled"], help="Optional: Filter tasks by status.")

    # sync parser
    sync_parser = task_subparsers.add_parser("sync", help="Synchronize the internal task registry by scanning relevant Markdown files.")

    # promote command
    promote_parser = task_subparsers.add_parser("promote", help="Escalate a simple task (legacy or manual) to a Task Context, creating a dedicated file.")
    promote_parser.add_argument("task_name", help="The name of the task to promote.")
    promote_parser.add_argument("--file", help="Optional: Source file of the task. Defaults to GEMINI.md.")

    # context command
    context_parser = task_subparsers.add_parser("context", help="Retrieve the context (content of the linked file) for a task.")
    context_parser.add_argument("task_name", help="The name of the task.")
    context_parser.add_argument("--file", help="Optional: Source file of the task. Defaults to GEMINI.md.")


def _get_files_to_scan() -> List[str]:
    """Helper function to determine all relevant files for task scanning."""
    files = ["GEMINI.md"]
    dirs_to_scan = ["4_Sub_Projects", "5_Sub_Projects"]
    for sub_projects_dir in dirs_to_scan:
        if os.path.exists(sub_projects_dir):
            for entry in os.listdir(sub_projects_dir):
                full_path = os.path.join(sub_projects_dir, entry)
                if entry.endswith(".md") and os.path.isfile(full_path):
                    files.append(full_path)
    return files

def _apply_task_change_to_file(task: Task, new_status: Optional[str] = None, remove: bool = False, new_name: Optional[str] = None) -> (bool, str):
    """
    Applies the change to the actual Markdown file.
    If new_status is provided, updates the task line.
    If new_name is provided, updates the task name (useful for appending ref).
    If remove is True, removes the task line.
    """
    try:
        with open(task.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        target_line_index = task.line_number

        # IMPORTANT: Check if the line number is still valid and if the original line content matches.
        if target_line_index >= len(lines) or lines[target_line_index].strip() != task.original_line.strip():
            # Fallback: Search for UUID if the strict line match fails
            found_by_uuid = False
            for i, line in enumerate(lines):
                # We expect the Task object's unique_id to be the UUID if available
                if task.unique_id and task.unique_id in line:
                    target_line_index = i
                    found_by_uuid = True
                    break
            
            if not found_by_uuid:
                return False, f"File '{task.file_path}' changed externally at line {task.line_number} or line content mismatch. Please run 'task sync' and retry."

        if remove:
            del lines[target_line_index]
        else:
            if new_status:
                task.status = new_status # Update the task object's status
            if new_name:
                task.name = new_name # Update task name
                # If the name is updated, the original_line should reflect the new name for future comparisons
                # This is important for tasks that are modified to include UUIDs
                task.original_line = task.to_markdown_line() # <-- ADDED THIS LINE
            lines[target_line_index] = task.to_markdown_line() # Use the Task object to generate the new line

        with open(task.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True, ""
    except Exception as e:
        return False, str(e)



def handle_task_commands(args):
    # Initialize the TaskRegistry
    registry = TaskRegistry()
    
    if args.task_command == "sync":
        files_to_scan = _get_files_to_scan()
        print(f"Scanning {len(files_to_scan)} files for tasks...")
        registry.load_tasks_from_files(files_to_scan)
        print(f"Task registry synchronized. Loaded {len(registry.get_all_tasks())} tasks.")
        return True, f"Task registry synchronized. Loaded {len(registry.get_all_tasks())} tasks."

    # For other commands that might need the registry populated first
    if args.task_command in ["set-status", "remove", "list", "promote", "context"]:
        files_to_scan = _get_files_to_scan()
        registry.load_tasks_from_files(files_to_scan)

    # ... [Existing 'add', 'set-status', 'remove', 'list' logic] ...
    
    target_file = getattr(args, 'file', "GEMINI.md") # Default for add
    if not target_file: target_file = "GEMINI.md"

    message = ""
    success = False

    if args.task_command == "add":
        # Load tasks to maintain a consistent registry state, though 'add' directly modifies file first
        files_to_scan = _get_files_to_scan()
        registry.load_tasks_from_files(files_to_scan) 

        tasks_added_count = 0
        all_new_tasks_content = [] 

        for task_description_item in args.task_description:
            # 1. Create Context File IMMEDIATELY, now returns UUID
            context_file_path, task_uuid = create_task_context_file(task_description_item)
            
            # 2. Append ref to name and UUID for GEMINI.md entry
            task_text_with_ref = f"{task_description_item} [{task_uuid}] (@{context_file_path})"

            # 3. Create dummy task object, passing the UUID
            new_task_obj = Task(name=task_text_with_ref, status=args.status, 
                                file_path=target_file, line_number=-1, original_line="", unique_id=task_uuid)
            
            # 4. Generate Markdown line
            new_task_line_content = new_task_obj.to_markdown_line()
            all_new_tasks_content.append(new_task_line_content)

        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return False, f"Error reading file {target_file}: {e}"

        updated_lines = list(lines)
        insert_index = -1
        if target_file == "GEMINI.md":
            persistent_todo_list_header = "### Persistent To-Do List"
            for i, line in enumerate(lines):
                if persistent_todo_list_header in line:
                    insert_index = i + 1
                    while insert_index < len(lines) and lines[insert_index].strip() != "" and not lines[insert_index].startswith("###"):
                        insert_index += 1
                    break
        
        if insert_index == -1:
            if updated_lines and not updated_lines[-1].endswith('\n'):
                updated_lines[-1] += '\n'
            updated_lines.extend(all_new_tasks_content)
        else:
            for i, new_task_line in enumerate(all_new_tasks_content):
                updated_lines.insert(insert_index + i, new_task_line)
        
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            success = True
            registry.load_tasks_from_files(files_to_scan) # Reload registry to pick up new tasks
            message = f"Added {len(args.task_description)} task(s) to {target_file} with Context Files created."
            print(message)
            return success, message
        except Exception as e:
            return False, f"Error writing to file {target_file}: {e}"

    elif args.task_command == "set-status":
        matching_tasks = registry.get_task_by_name(args.task_name, args.file)
        if not matching_tasks:
            return False, f"Error: Task '{args.task_name}' not found in registry."
        elif len(matching_tasks) > 1:
            msg = f"Error: Task '{args.task_name}' is ambiguous. Matches:"
            for t in matching_tasks: msg += f"\n  - '{t.name}' in '{t.file_path}'"
            print(msg)
            return False, msg
        
        task_to_update = matching_tasks[0]
        
        # Record time_started/time_completed based on status change
        if args.status == "in_progress" and task_to_update.time_started is None:
            task_to_update.time_started = datetime.datetime.now()
        elif args.status in ["completed", "cancelled"] and task_to_update.time_completed is None:
            task_to_update.time_completed = datetime.datetime.now()
            # If task is completed and was in progress, ensure time_started is set
            if task_to_update.status == "in_progress" and task_to_update.time_started is None:
                task_to_update.time_started = task_to_update.time_completed # Fallback to completion time

        if args.status == "completed" and os.path.normpath(task_to_update.file_path) == os.path.normpath("GEMINI.md"):
            print(f"Removing completed task '{task_to_update.name}' from GEMINI.md...")
            success, msg = _apply_task_change_to_file(task_to_update, remove=True)
            if success: registry.remove_task(task_to_update.unique_id)
            print(msg)
            return success, msg
        else:
            # Update Task object in registry with new time fields
            registry.update_task_status(task_to_update.unique_id, args.status)
            registry.get_task_by_id(task_to_update.unique_id).time_started = task_to_update.time_started
            registry.get_task_by_id(task_to_update.unique_id).time_completed = task_to_update.time_completed

            success, msg = _apply_task_change_to_file(task_to_update, args.status)
            print(msg)
            return success, msg

    elif args.task_command == "remove":
        matching_tasks = registry.get_task_by_name(args.task_name, args.file)
        if not matching_tasks:
            return False, f"Error: Task '{args.task_name}' not found."
        elif len(matching_tasks) > 1:
            return False, "Error: Task name ambiguous."
        
        task_to_remove = matching_tasks[0]
        registry.remove_task(task_to_remove.unique_id)
        success, msg = _apply_task_change_to_file(task_to_remove, remove=True)
        print(msg)
        return success, msg

    elif args.task_command == "list":
        all_tasks = registry.get_all_tasks()
        filtered_tasks = []
        if args.status:
            target_status = args.status.lower().replace(" ", "_")
            filtered_tasks = [t for t in all_tasks if t.status == target_status]
        else:
            filtered_tasks = all_tasks

        if args.file:
            fp_filter = os.path.normpath(args.file)
            filtered_tasks = [t for t in filtered_tasks if os.path.normpath(t.file_path) == fp_filter]

        print(f"Tasks ({len(filtered_tasks)} found):")
        for task in filtered_tasks:
            status_disp = task.status.replace("_", " ").title()
            
            # Prepare metrics for display
            metrics_disp = []
            if task.relevancy_score is not None:
                metrics_disp.append(f"R:{task.relevancy_score}")
            if task.time_started:
                metrics_disp.append(f"Start:{task.time_started.strftime('%Y-%m-%d %H:%M')}")
            if task.time_completed:
                metrics_disp.append(f"End:{task.time_completed.strftime('%Y-%m-%d %H:%M')}")
                if task.time_started:
                    duration = task.time_completed - task.time_started
                    metrics_disp.append(f"Dur:{str(duration).split('.')[0]}") # Remove microseconds
            
            # For now, turn_count, command_count, error_count are not explicitly tracked in task_commands.py
            # but are part of the Task object. We'll display them if they have values.
            if task.turn_count is not None:
                metrics_disp.append(f"Turns:{task.turn_count}")
            if task.command_count is not None:
                metrics_disp.append(f"Cmds:{task.command_count}")
            if task.error_count is not None:
                metrics_disp.append(f"Errors:{task.error_count}")

            metrics_string = f" ({', '.join(metrics_disp)})" if metrics_disp else ""

            print(f"[{status_disp}] {task.name}{metrics_string} (File: {task.file_path})")
        return True, ""

    elif args.task_command == "promote":
        matching_tasks = registry.get_task_by_name(args.task_name, args.file)
        if not matching_tasks:
            return False, f"Error: Task '{args.task_name}' not found."
        elif len(matching_tasks) > 1:
            return False, "Error: Task name ambiguous."
        
        task_to_promote = matching_tasks[0]
        
        # check if already has context
        if "(@" in task_to_promote.name:
             return False, f"Task '{task_to_promote.name}' already has a context reference."

        # Create context file
        context_file_path = create_task_context_file(task_to_promote.name)
        
        # Update task name to include ref
        new_name = f"{task_to_promote.name} (@{context_file_path})"
        
        success, msg = _apply_task_change_to_file(task_to_promote, new_name=new_name)
        if success:
            print(f"Successfully promoted task. Context file created at {context_file_path}")
            return True, f"Promoted task '{task_to_promote.name}'"
        else:
            return False, f"Failed to update task line: {msg}"

    elif args.task_command == "context":
        matching_tasks = registry.get_task_by_name(args.task_name, args.file)
        if not matching_tasks:
            return False, f"Error: Task '{args.task_name}' not found."
        elif len(matching_tasks) > 1:
            return False, "Error: Task name ambiguous."
        
        task = matching_tasks[0]
        # Extract ref
        ref_match = re.search(r"\(@(.*?)\)", task.name)
        if not ref_match:
             print("Task does not have a linked context file.")
             return True, "No context linked."
        
        context_path = ref_match.group(1)
        if not os.path.exists(context_path):
             return False, f"Error: Linked context file '{context_path}' not found."
        
        try:
            with open(context_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"--- Context for '{task.name}' ---\n")
            print(content)
            print("\n-----------------------------------")
            return True, "Context displayed."
        except Exception as e:
            return False, f"Error reading context file: {e}"

    return False, "Unknown command"
