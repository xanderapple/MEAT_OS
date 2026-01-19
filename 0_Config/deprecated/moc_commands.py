import argparse
import os
from ..utils.moc_management import update_gemini_index_moc

def add_moc_parser(subparsers):
    moc_parser = subparsers.add_parser('moc', help='Manages Map of Content (MOC) related operations.')
    moc_subparsers = moc_parser.add_subparsers(dest='moc_command', help='MOC commands')

    # Update Index command
    update_index_parser = moc_subparsers.add_parser('update-index', help='Scans the vault and regenerates the Gemini_Index_MOC.md.')
    update_index_parser.set_defaults(func=run_update_index)

def run_update_index(args):
    """Handler for the 'moc update-index' command."""
    # Assuming the script is run from the project root
    vault_root = os.getcwd() 
    output_moc_path = "4_Map_of_Content/Gemini_Index_MOC.md" # Updated path

    update_gemini_index_moc(vault_root=vault_root, output_moc_path=output_moc_path)
    return True, "Updated Gemini Index MOC."

def handle_moc_commands(args):
    """Dispatches moc commands to their respective handlers."""
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        print("No MOC command specified. Use 'moc --help' for options.")
        return False, "No MOC command specified."