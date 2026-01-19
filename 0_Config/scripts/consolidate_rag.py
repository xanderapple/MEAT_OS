import os
import sys
import argparse
import io

# Force stdout to utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add utils to sys.path for standalone execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
from rag_cli_utils import extract_metadata_and_first_section
from file_utils import read_file_content

def consolidate_rag(relevant_files_path, output_path=None):
    """
    Consolidates the first section of multiple Markdown files.
    """
    if not os.path.exists(relevant_files_path):
        print(f"Error: {relevant_files_path} not found.")
        return False

    try:
        with open(relevant_files_path, 'r', encoding='utf-8') as f:
            relevant_files = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading {relevant_files_path}: {e}")
        return False

    consolidated_content = []
    vault_root = os.getcwd()

    for rel_path in relevant_files:
        full_path = os.path.join(vault_root, rel_path)
        content = read_file_content(full_path)
        
        if not content:
            print(f"Warning: Could not read {rel_path}. Skipping.")
            continue

        processed = extract_metadata_and_first_section(content)
        
        consolidated_content.append(f"\n\n--- Start RAG content from {rel_path} ---")
        consolidated_content.append(processed)
        consolidated_content.append(f"\n--- End RAG content from {rel_path} ---")

    final_output = "".join(consolidated_content)

    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_output)
            print(f"Successfully consolidated {len(relevant_files)} files to {output_path}")
        except Exception as e:
            print(f"Error writing to {output_path}: {e}")
            return False
    else:
        print(final_output)

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate first sections of Markdown files listed in a file.")
    parser.add_argument("--input", default="relevant_rag_files.txt", help="Path to the file listing relevant files.")
    parser.add_argument("--output", help="Optional: Path to the output consolidated file. If omitted, prints to stdout.")
    
    args = parser.parse_args()
    consolidate_rag(args.input, args.output)
