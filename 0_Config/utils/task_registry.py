from typing import List, Optional, Dict
import re
import os
import uuid
import datetime # Import datetime

class Task:
    def __init__(self, name: str, status: str, file_path: str, line_number: int, original_line: str, unique_id: Optional[str] = None,
                 relevancy_score: Optional[int] = None, # New field
                 time_started: Optional[datetime.datetime] = None, # New field
                 time_completed: Optional[datetime.datetime] = None, # New field
                 turn_count: Optional[int] = None, # New field
                 command_count: Optional[int] = None, # New field
                 error_count: Optional[int] = None): # New field
        self.name = name
        self.status = status
        self.file_path = file_path
        self.line_number = line_number # Line number in the file
        self.original_line = original_line # The full Markdown line
        self.unique_id = unique_id if unique_id else str(uuid.uuid4())

        # New metrics fields
        self.relevancy_score = relevancy_score
        self.time_started = time_started
        self.time_completed = time_completed
        self.turn_count = turn_count
        self.command_count = command_count
        self.error_count = error_count

    def to_markdown_line(self) -> str:
        # Reconstructs the markdown line based on current task state
        checkbox_char = " "
        status_tag = ""

        if self.status == "completed":
            checkbox_char = "x"
        elif self.status == "cancelled":
            checkbox_char = "c"
            status_tag = "(CANCELLED)"
        elif self.status == "in_progress":
            status_tag = "(IN PROGRESS)"
        elif self.status == "current":
            status_tag = "(CURRENT)"
        
        # Preserve original indentation
        indentation_match = re.match(r"^(\s*)-", self.original_line)
        indentation = indentation_match.group(1) if indentation_match else ""

        status_part = f" {status_tag}" if status_tag else ""
        
        # We assume self.name already contains the reference if it was parsed/added that way.
        # But we need to be careful not to double-append the ID comment if it's already in the name.
        clean_name = re.sub(r"\s*<!--\s*id:\s*([a-f0-9\-]+)\s*-->.*$", "", self.name).strip()

        return f"{indentation}- [{checkbox_char}]{status_part} {clean_name} <!-- id: {self.unique_id} -->\n"

    def __repr__(self):
        # Update __repr__ to show new fields for easier debugging
        return (f"Task(name='{self.name}', status='{self.status}', id='{self.unique_id}', "
                f"relevancy={self.relevancy_score}, started={self.time_started}, "
                f"completed={self.time_completed}, turns={self.turn_count}, "
                f"commands={self.command_count}, errors={self.error_count})")

class TaskRegistry:
    def __init__(self):
        self._tasks: Dict[str, Task] = {} # {unique_id: Task_object}

    def _parse_task_line(self, line: str, file_path: str, line_number: int) -> Optional[Task]:
        # Regex to capture:
        # Group 1: The full prefix including indentation and checkbox (e.g., "  - [ ]")
        # Group 2: The checkbox character itself (x, space, c)
        # Group 3: The optional status tag content without parentheses (e.g., "IN PROGRESS")
        # Group 4: The main task description part (including any references)
        # Group 5: The optional UUID comment (e.g., " <!-- id: 123-abc -->")
        # Group 6: The UUID itself
        task_regex = re.compile(
            r"^\s*-\s\[(x| |c)\]"  # Prefix and Checkbox char
            r"(\s*\((CURRENT|IN PROGRESS|pending|in_progress|completed|cancelled)\))?"  # Optional Status Tag
            r"(.*?)" # The main task description part
            r"(\s*<!--\s*id:\s*([a-f0-9\-]+)\s*-->)?\s*$" # Optional UUID comment
        )
        match = task_regex.match(line)
        if match:
            checkbox_char = match.group(1)
            status_tag_content = match.group(3)

            status = "pending"
            if checkbox_char == "x":
                status = "completed"
            elif checkbox_char == "c":
                status = "cancelled"
            elif status_tag_content:
                status = status_tag_content.lower().replace(" ", "_")
            
            task_name = match.group(4).strip()
            unique_id = match.group(6)

            return Task(name=task_name, status=status, file_path=file_path, line_number=line_number, original_line=line.strip(), unique_id=unique_id)
        return None

    def load_tasks_from_files(self, file_paths: List[str]):
        newly_parsed_tasks: Dict[str, Task] = {}
        for file_path in file_paths:
            if not os.path.exists(file_path):
                # print(f"Warning: File not found: {file_path}")
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f.readlines()):
                        task = self._parse_task_line(line, file_path, i)
                        if task:
                            newly_parsed_tasks[task.unique_id] = task
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        self._tasks = newly_parsed_tasks # Overwrite with newly parsed tasks

    def get_task_by_name(self, task_name: str, file_path: Optional[str] = None) -> List[Task]:
        matching_tasks = []
        # Support ID-based lookup if task_name looks like a UUID or is wrapped in [UUID]
        search_id = None
        uuid_match = re.search(r"([a-f0-9\-]{36})", task_name)
        if uuid_match:
            search_id = uuid_match.group(1)

        for task in self._tasks.values():
            # Filter by file first if provided
            if file_path and os.path.normpath(task.file_path) != os.path.normpath(file_path):
                continue
            
            # Match by ID
            if search_id and task.unique_id == search_id:
                matching_tasks.append(task)
                continue

            # Match by exact name
            if task.name == task_name:
                matching_tasks.append(task)
                continue
            
            # Match by substring (case-insensitive)
            if task_name.lower() in task.name.lower():
                matching_tasks.append(task)
                continue

        return matching_tasks

    def get_task_by_id(self, unique_id: str) -> Optional[Task]:
        return self._tasks.get(unique_id)

    def add_task(self, task: Task):
        self._tasks[task.unique_id] = task

    def update_task_status(self, unique_id: str, new_status: str):
        task = self._tasks.get(unique_id)
        if task:
            task.status = new_status
            return True
        return False

    def remove_task(self, unique_id: str):
        if unique_id in self._tasks:
            del self._tasks[unique_id]
            return True
        return False

    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())
