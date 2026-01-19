import os
import argparse
from ..utils.project_setup import initialize_project
from ..utils.moc_management import update_gemini_index_moc, update_preference_index_moc
from ..utils.project_management_utils import new_project, archive_project, set_project_status # ADD set_project_status

def handle_project_commands(args):
    if args.project_command == "create-config":
        vault_root_path = os.getcwd()
        initialize_project(vault_root_path)
    elif args.project_command == "update-moc":
        vault_root_path = os.getcwd()
        update_gemini_index_moc(vault_root_path)
    elif args.project_command == "update-preferences-moc":
        vault_root_path = os.getcwd()
        update_preference_index_moc(vault_root_path)
    elif args.project_command == "new":
        new_project(args.project_name)
    elif args.project_command == "archive":
        archive_project(args.project_name)
    elif args.project_command == "set-status": # ADD THIS BLOCK
        set_project_status(args.project_name, args.status)
    elif args.project_command == "init":
        print("Placeholder for Task Context initialization. This command is not yet implemented.")

def add_project_subparser(subparsers):
    project_parser = subparsers.add_parser("project", help="Manage Task Context operations (formerly sub-projects).")
    project_subparsers = project_parser.add_subparsers(dest="project_command", help="Project commands")

    # Project create-config subcommand
    create_config_parser = project_subparsers.add_parser("create-config", help="Create default configuration files (PROJECT_VARIABLE.md, Preference_Index_MOC.md).")

    # Project init subcommand (for sub-projects)
    init_parser = project_subparsers.add_parser("init", help="Initialize a new Task Context (not yet implemented).")

    # Project new subcommand
    new_parser = project_subparsers.add_parser("new", help="Create a new Task Context File.")
    new_parser.add_argument("project_name", help="The name of the new Task Context.")

    # Project archive subcommand
    archive_parser = project_subparsers.add_parser("archive", help="Archive a completed Task Context File.")
    archive_parser.add_argument("project_name", help="The name of the Task Context to archive.")

    # Project set-status subcommand # ADD THIS BLOCK
    set_status_parser = project_subparsers.add_parser("set-status", help="Set the status of a Task Context.")
    set_status_parser.add_argument("project_name", help="The name of the Task Context.")
    set_status_parser.add_argument("--status", choices=["pending", "in_progress", "completed", "current", "cancelled"], required=True, help="The new status for the Task Context.")

    # Project update-moc subcommand
    update_moc_parser = project_subparsers.add_parser("update-moc", help="Update the Gemini_Index_MOC.md file.")

    # Project update-preferences-moc subcommand
    update_preferences_moc_parser = project_subparsers.add_parser("update-preferences-moc", help="Update the Preference_Index_MOC.md file by generating a dynamic table of preferences.")
