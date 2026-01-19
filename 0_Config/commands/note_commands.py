import argparse
import os
import sys

# Modularized Logic Imports
from ..logic.note_core import create_atomic_note, edit_existing_note
from ..logic.note_metadata import update_note_metadata, propagate_rename
from ..logic.note_batch import execute_integration_plan
from ..utils.command_utils import execute_script

def add_note_parser(subparsers):
    note_parser = subparsers.add_parser("note", help="Commands for managing Obsidian notes.")
    note_subparsers = note_parser.add_subparsers(dest="note_command", help="Available note commands")

    # prepend-update command
    prepend_update_parser = note_subparsers.add_parser("prepend-update", help="Prepends content to a Markdown file after its YAML frontmatter.")
    prepend_update_parser.add_argument("file_path", help="The path to the Markdown file to update.")
    prepend_update_parser.add_argument("content", help="The content to prepend to the file.")

    # atom command
    atom_parser = note_subparsers.add_parser("atom", help="Creates a new atomic note.")
    atom_parser.add_argument("--content", required=True, help="The primary text content for the new atomic note.")
    atom_parser.add_argument("--title", help="An optional title for the note. If not provided, one will be generated.")
    atom_parser.add_argument("--tags", help="A comma-separated list of tags to add to the note's frontmatter.")

    # edit command
    edit_parser = note_subparsers.add_parser("edit", help="Modifies an existing note.")
    edit_parser.add_argument("--file", required=True, help="The path to the Markdown file to modify.")
    edit_parser.add_argument("--content", required=True, help="The content to add to the file.")
    edit_parser.add_argument("--mode", choices=['prepend_to_file', 'append_ref', 'prepend_to_main', 'append_to_main'], default='prepend_to_file', help="How to add the content.")
    edit_parser.add_argument("--title", help="Optional title for rephrasing context.")

    # integrate command
    integrate_parser = note_subparsers.add_parser("integrate", help="Executes batch note integration from a JSON plan.")
    integrate_parser.add_argument("plan", help="Path to the JSON file containing structured insights for integration.")
    integrate_parser.add_argument("--source", help="Optional: Path to the synthesis source file. If provided, reference links will be appended to all modified notes.")

    # rename command
    rename_parser = note_subparsers.add_parser("rename", help="Renames a note and propagates link changes across the vault.")
    rename_parser.add_argument("file_path", help="The current path to the Markdown note.")
    rename_parser.add_argument("new_name", help="The new filename (without .md extension).")


def handle_note_commands(args):
    if args.note_command == "prepend-update":
        script_path = "0_Config/scripts/prepend_update.py"
        script_args = [args.file_path, args.content]
        
        success, output = execute_script(script_path, script_args)
        if success:
            return True, f"Successfully prepended content to {args.file_path}."
        else:
            return False, f"Failed to prepend content to {args.file_path}: {output}"
            
    elif args.note_command == "atom":
        success, message, _ = create_atomic_note(args.content, args.title, args.tags)
        return success, message
            
    elif args.note_command == "edit":
        success, message, _ = edit_existing_note(args.file, args.content, args.mode, args.title)
        return success, message
            
    elif args.note_command == "rename":
        success, message = propagate_rename(args.file_path, args.new_name)
        return success, message
            
    elif args.note_command == "integrate":
        success, report = execute_integration_plan(args.plan, args.source)
        return success, report

    return False, "Unknown note command."
