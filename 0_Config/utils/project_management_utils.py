import os
import datetime
import shutil
import subprocess
import sys
from typing import List, Optional
import uuid # Import uuid

from .file_utils import read_file_content # Using the new utility

# Helper to execute task commands via subprocess
def _execute_task_command(command_args: List[str]) -> (bool, str):
    full_command = [sys.executable, "0_Config/main_cli.py", "task"] + command_args
    result = subprocess.run(full_command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        return False, f"Error: {result.stderr.strip()}\n{result.stdout.strip()}"

def create_task_context_file(project_name: str, task_uuid: Optional[str] = None) -> (str, str):
    """
    Creates a new Task Context File with a standard template, incorporating a UUID.
    Returns its relative path and the UUID.
    """
    sub_projects_dir = "4_Sub_Projects"
    os.makedirs(sub_projects_dir, exist_ok=True)

    if task_uuid is None:
        task_uuid = str(uuid.uuid4())

    # Sanitize file name and append UUID for uniqueness
    safe_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(" ", "_")
    project_file_name = f"{safe_name}_{task_uuid}.md" # Append UUID to filename
    project_file_path = os.path.join(sub_projects_dir, project_file_name)

    template_content = f"""# Task Context: {project_name}
Task ID: {task_uuid}

## Objective
(A clear and concise description of the task's goal)

## Subtasks & Progress
- [ ] Analyze requirements
- [ ] Implement solution
- [ ] Verify results

## Context & Notes
(Key information, decisions, and scratchpad)
""" 

    if os.path.exists(project_file_path):
        print(f"Warning: Task Context File already exists at {project_file_path}. Skipping creation.")
        return project_file_path, task_uuid # Return existing path and UUID

    with open(project_file_path, 'w', encoding='utf-8') as f:
        f.write(template_content)

    print(f"Successfully created new Task Context File: {project_file_path}")
    return project_file_path, task_uuid

def new_project(project_name: str):
    """
    Creates a new Task Context File and adds it to GEMINI.md.
    """
    project_file_path, task_uuid = create_task_context_file(project_name) # Unpack UUID
    
    # Use task add CLI command to add task to GEMINI.md
    print(f"Adding task '{project_name}' to Persistent To-Do List in GEMINI.md...")
    # The task name in GEMINI.md will be "project_name [UUID] (@path/to/file)"
    project_task_name_in_gemini = f"{project_name} [{task_uuid}] (@{project_file_path})" # Include UUID
    success, msg = _execute_task_command(["add", project_task_name_in_gemini, "--status", "in_progress", "--file", "GEMINI.md"]) 
    if success:
        print(f"Successfully added: {msg}")
    else:
        print(f"Error adding task to GEMINI.md: {msg}")

    # Trigger task sync after creation
    print("Triggering task sync to update registry...")
    success, msg = _execute_task_command(["sync"])
    if success:
        print(f"Task sync successful: {msg}")
    else:
        print(f"Task sync failed: {msg}")


def archive_project(project_name: str):
    """
    Archives a completed Task Context File.
    """
    sub_projects_dir = "4_Sub_Projects"
    archive_dir = os.path.join(sub_projects_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    project_file_path = os.path.join(sub_projects_dir, f"{project_name}.md")
    
    if not os.path.exists(project_file_path):
        print(f"Error: Task Context File not found at {project_file_path}")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    archived_project_file_path = os.path.join(archive_dir, f"{project_name}_{timestamp}.md")

    os.rename(project_file_path, archived_project_file_path)

    print(f"Successfully archived Task Context File to: {archived_project_file_path}")

    # Use task remove CLI command to remove project from GEMINI.md
    print(f"Removing task '{project_name}' from Persistent To-Do List in GEMINI.md...")
    project_task_name_in_gemini = f"{project_name} (@4_Sub_Projects/{project_name}.md)" # Construct the full name here for consistency
    success, msg = _execute_task_command(["remove", project_task_name_in_gemini, "--file", "GEMINI.md"]) # MODIFIED LINE
    if success:
        print(f"Successfully removed: {msg}")
    else:
        print(f"Error removing task from GEMINI.md: {msg}")
    
    # Trigger task sync after archiving
    print("Triggering task sync to update registry...")
    success, msg = _execute_task_command(["sync"])
    if success:
        print(f"Task sync successful: {msg}")
    else:
        print(f"Task sync failed: {msg}")


def set_project_status(project_name: str, status: str):
    """
    Sets the status of a Task Context in GEMINI.md's Persistent To-Do List
    and triggers a task sync.
    """
    # Construct the full task name as it appears in GEMINI.md for projects
    full_project_task_name = f"{project_name} (@4_Sub_Projects/{project_name}.md)" 
    
    print(f"Setting status of task '{project_name}' to '{status}' in GEMINI.md...")
    success, msg = _execute_task_command(["set-status", full_project_task_name, "--file", "GEMINI.md", "--status", status])
    if success:
        print(f"Successfully set status: {msg}")
        if status == "completed": # ADD THIS BLOCK
            print(f"Removing completed task '{project_name}' from Persistent To-Do List in GEMINI.md...")
            remove_success, remove_msg = _execute_task_command(["remove", full_project_task_name, "--file", "GEMINI.md"])
            if remove_success:
                print(f"Successfully removed: {remove_msg}")
            else:
                print(f"Error removing completed task: {remove_msg}")
    else:
        print(f"Error setting status for task '{project_name}': {msg}")
    
    # Trigger task sync after updating project status
    print("Triggering task sync to update registry...")
    success, msg = _execute_task_command(["sync"])
    if success:
        print(f"Task sync successful: {msg}")
    else:
        print(f"Task sync failed: {msg}")
