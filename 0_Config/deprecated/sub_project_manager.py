import sys
import subprocess
from typing import List

# Helper to execute task commands via subprocess
def _execute_task_command(command_args: List[str]) -> (bool, str):
    full_command = [sys.executable, "0_Config/main_cli.py", "task"] + command_args
    result = subprocess.run(full_command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        return True, result.stdout.strip()
    else:
        return False, f"Error: {result.stderr.strip()}\n{result.stdout.strip()}"

# This file is kept for backward compatibility and to potentially house future high-level orchestration logic.
# The core functionalities have been moved to:
# - 0_Config/utils/project_management_utils.py
# - 0_Config/utils/chat_processing_utils.py
# - 0_Config/utils/file_utils.py

# Re-exporting for easier refactoring, but consumers should prefer direct imports from utils.
from .utils.project_management_utils import new_project, archive_project, set_project_status
from .utils.chat_processing_utils import process_chat_file
