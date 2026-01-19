import argparse
from ..utils.chat_processing_utils import process_chat_file

def add_chat_parser(subparsers):
    chat_parser = subparsers.add_parser("process-chat", help="Process a raw chat file.")
    chat_parser.add_argument("file_path", help="The path to the raw chat file.")
    chat_parser.add_argument("--api-key", help="Optional: Your Gemini API key. Overrides GEMINI_API_KEY environment variable.")

def handle_chat_commands(args):
    if args.command == "process-chat":
        process_chat_file(args.file_path, api_key=args.api_key)
