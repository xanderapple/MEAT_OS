import argparse
import os
import re

from ..utils.rag_cli_utils import parse_gemini_index_moc, find_relevant_notes # Assuming these exist
from ..utils.config_parsers import parse_project_context # To get Gemini_Index_MOC path
from ..utils.refinement_processor import process_refinement_analysis_file # New import for refinement processor

def _read_file_content(file_path: str) -> str:
    """
    Reads the content of a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""


def add_rag_parser(subparsers):
    rag_parser = subparsers.add_parser("rag", help="Commands for Retrieval-Augmented Generation (RAG) utilities.")
    rag_subparsers = rag_parser.add_subparsers(dest="rag_command", help="Available RAG commands")

    # test-retrieval command
    test_retrieval_parser = rag_subparsers.add_parser("test-retrieval", help="Test the RAG context retrieval mechanism.")
    test_retrieval_parser.add_argument("--topics", nargs='*', help="List of topics to search for (e.g., 'topic1' 'topic2').")
    test_retrieval_parser.add_argument("--tags", nargs='*', help="List of tags to search for (e.g., 'tag1' 'tag2').")
    test_retrieval_parser.add_argument("--show-content", action="store_true", help="Display the full consolidated RAG context content.") # New argument

    # process-refinement command
    process_refinement_parser = rag_subparsers.add_parser("process-refinement", help="Process a Refinement Analysis file to execute suggestions.")
    process_refinement_parser.add_argument("refinement_analysis_file_path", help="Path to the Refinement Analysis Markdown file.")


def handle_rag_commands(args):
    if args.rag_command == "test-retrieval":
        search_topics = []
        if args.topics:
            search_topics.extend(args.topics)
        if args.tags:
            search_topics.extend(args.tags)

        if not search_topics:
            print("Error: Please provide at least one topic or tag to search for using --topics or --tags.")
            return

        print(f"Testing RAG retrieval for topics/tags: {', '.join(search_topics)}")
        
        # Get project context to find Gemini_Index_MOC path
        project_variable_path = "0_Config/PROJECT_VARIABLE.md"
        project_variables = parse_project_context(project_variable_path)
        gemini_index_moc_path = project_variables.get("paths", {}).get("gemini_index_moc_path")

        if not gemini_index_moc_path or not os.path.exists(gemini_index_moc_path):
            print(f"Error: Gemini Index MOC not found at '{gemini_index_moc_path}'. Cannot test RAG retrieval.")
            return

        # Read content of Gemini Index MOC
        moc_content = _read_file_content(gemini_index_moc_path)
        if not moc_content:
            print(f"Error: Gemini Index MOC at '{gemini_index_moc_path}' is empty. Cannot test RAG retrieval.")
            return

        # 1. Parse Gemini_Index_MOC
        note_map = parse_gemini_index_moc(moc_content, gemini_index_moc_path)
        
        # 2. Find relevant notes
        relevant_note_paths_no_ext = find_relevant_notes(search_topics, note_map)
        
        # 3. Read and consolidate content of relevant notes
        rag_context_content = ""
        if relevant_note_paths_no_ext:
            rag_context_content += "\n--- Relevant Knowledge from Vault ---\n"
            print("\n--- Identified Relevant Notes ---")
            for note_path_no_ext in relevant_note_paths_no_ext:
                note_full_path = note_path_no_ext + ".md"
                note_content = _read_file_content(note_full_path)
                if note_content:
                    # Only add to consolidated content if we intend to show it
                    if args.show_content: # Only add to rag_context_content if it will be displayed
                        rag_context_content += f"\n### Source: {os.path.basename(note_full_path)}\n"
                        rag_context_content += note_content
                        rag_context_content += "\n---\n"
                    print(f"- {note_full_path}")
                else:
                    print(f"Warning: Could not read content for '{note_full_path}'. Skipping.")
            if args.show_content: # Only add this footer if content was actually collected for display
                rag_context_content += "\n-----------------------------------\n"
        else:
            print("No relevant notes found for the given topics/tags.")

        if args.show_content:
            print("\n--- Consolidated RAG Context Content (Truncated if long) ---")
            if len(rag_context_content) > 1000: # Truncate if longer than 1000 characters
                print(rag_context_content[:1000] + "\n... (content truncated) ...")
            else:
                print(rag_context_content)
        else:
            if rag_context_content: # Only print this if there was content but we're not showing it
                print("\nConsolidated RAG context content generated (use --show-content to display).")
    elif args.rag_command == "process-refinement":
        vault_root_path = os.getcwd()
        process_refinement_analysis_file(args.refinement_analysis_file_path, vault_root_path)
