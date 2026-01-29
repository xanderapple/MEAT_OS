import sys
import datetime
import os
import argparse
from ..utils.command_utils import execute_script
from ..utils.rag_cli_utils import extract_metadata_and_first_section
from ..utils.moc_management import update_gemini_index_moc


def add_rag_parser(subparsers):
    rag_parser = subparsers.add_parser("rag", help="Commands for Retrieval-Augmented Generation (RAG) utilities.")
    rag_subparsers = rag_parser.add_subparsers(dest="rag_command", help="Available RAG commands")

    # generate-relevant-files command
    generate_relevant_files_parser = rag_subparsers.add_parser("generate-relevant-files", help="Generates relevant RAG file paths based on keywords and writes them to relevant_rag_files.txt.")
    generate_relevant_files_parser.add_argument("--keywords", nargs='+', help="List of keywords to search for relevant files.")

    # consolidate-context command
    consolidate_context_parser = rag_subparsers.add_parser("consolidate-context", help="Consolidates content from files listed in relevant_rag_files.txt into consolidated_rag_context.md or stdout.")
    consolidate_context_parser.add_argument("--output", help="Optional: Path to the output file. If omitted, prints to stdout.")

    # update-moc command
    update_moc_parser = rag_subparsers.add_parser('update-moc', help='Scans the vault and regenerates the Gemini_Index_MOC.md.')

    # prepare-context command
    prepare_context_parser = rag_subparsers.add_parser("prepare-context", help="Orchestrates RAG context assembly. Can use a source file or direct keywords.")    
    prepare_context_parser.add_argument("source", nargs='?', help="Optional: Path to the source file or direct content.")
    prepare_context_parser.add_argument("--keywords", help="Optional: Comma-separated keywords for RAG.")
    prepare_context_parser.add_argument("--output", help="Optional: Path to output consolidated RAG context. If omitted, prints to stdout.")

    # get-first-section command
    get_first_section_parser = rag_subparsers.add_parser("get-first-section", help="Extracts and returns the first section (including YAML) of a single Markdown file.")
    get_first_section_parser.add_argument("--file", required=True, help="Path to the Markdown file.")

def handle_rag_commands(args):
    if args.rag_command == "generate-relevant-files":
        if not args.keywords:
            return False, "Error: Please provide at least one keyword using --keywords."
        
        # Join keywords with comma for the script
        keywords_str = ",".join(args.keywords)
        script_args = [keywords_str] # Pass as a single argument string

        print(f"Executing generate-relevant-files command with keywords: {keywords_str}")
        success, output = execute_script("0_Config/scripts/get_relevant_rag_files.py", script_args)
        if success:
            return True, f"Generated relevant RAG files:\n{output}"
        else:
            return False, f"Failed to generate relevant RAG files:\n{output}"

    elif args.rag_command == "consolidate-context":
        script_args = []
        if args.output:
            script_args = ["--output", args.output]
        
        success, output = execute_script("0_Config/scripts/consolidate_rag.py", script_args)
        if success:
            return True, f"Consolidated RAG context:\n{output}"
        else:
            return False, f"Failed to consolidate RAG context:\n{output}"
    
    elif args.rag_command == "update-moc":
        vault_root = os.getcwd() 
        output_moc_path = "0_Config/Context/GEMINI_INDEX.md" 
        update_gemini_index_moc(vault_root=vault_root, output_moc_path=output_moc_path)
        return True, "Updated Gemini Index MOC."
    
    elif args.rag_command == "prepare-context":
        source_input = args.source
        output_path = args.output
        
        # 1. Call rag update-moc
        update_gemini_index_moc(vault_root=os.getcwd(), output_moc_path="0_Config/Context/GEMINI_INDEX.md")

        if args.keywords:
            # Keywords provided, skip Agent extraction and proceed to generate-relevant-files and consolidate-context
            keywords_for_script = args.keywords
            
            # Call rag generate-relevant-files
            generate_success, generate_output = handle_rag_commands(argparse.Namespace(rag_command="generate-relevant-files", keywords=keywords_for_script.split(',')))
            if not generate_success:
                return False, f"Failed to generate relevant files: {generate_output}"
            
            # Call rag consolidate-context
            # Note: We need to capture the output if we want to return it.
            # handle_rag_commands for consolidate-context prints to stdout.
            # To capture it here, we temporarily redirect sys.stdout or call the script directly.
            
            from io import StringIO
            import sys as original_sys
            
            captured_stdout = StringIO()
            original_stdout = original_sys.stdout
            try:
                original_sys.stdout = captured_stdout
                # Call consolidate-context WITHOUT output path so it prints content to stdout
                consolidate_success, consolidate_msg = handle_rag_commands(argparse.Namespace(rag_command="consolidate-context", output=None))
            finally:
                original_sys.stdout = original_stdout
            
            if not consolidate_success:
                return False, f"Failed to consolidate context: {consolidate_msg}"
            
            # captured_stdout now contains the success message from handle_rag_commands wrapper AND the script output
            # Actually, handle_rag_commands returns the output string if success.
            # But wait, execute_script captures stdout.
            
            # Let's rely on the return value of handle_rag_commands for content, 
            # BUT handle_rag_commands wraps the output in "Consolidated RAG context:\n..."
            
            # Actually, looking at handle_rag_commands logic for consolidate-context:
            # success, output = execute_script(...)
            # return True, f"Consolidated RAG context:\n{output}"
            
            # So consolidate_msg ALREADY contains the content!
            # We don't need to capture stdout if we trust the return value.
            
            # Let's verify: execute_script returns (True, stdout_content).
            # So consolidate_msg = "Consolidated RAG context:\n" + stdout_content
            
            # We can just strip the prefix.
            raw_content = consolidate_msg.replace("Consolidated RAG context:\n", "", 1)
            
            # Inject Keywords Header
            header = f"# Active RAG Keywords\n> {args.keywords}\n\n"
            final_content = header + raw_content
            
            if output_path:
                 with open(output_path, 'w', encoding='utf-8') as f:
                     f.write(final_content)
                 return True, f"RAG context prepared and saved to {output_path}."
            else:
                 return True, final_content
        
        elif source_input:
            # Keywords not provided, but source (file or content) is.
            content = ""
            if os.path.exists(source_input):
                try:
                    with open(source_input, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    return False, f"Error reading file {source_input}: {e}"
            else:
                content = source_input

            # Prepare meta-prompt for Agent to extract keywords
            agent_instruction_keywords = f"""
Your task is to extract key keywords and concepts from the provided content to retrieve relevant context from the knowledge base (RAG).

### EXTRACTION STRATEGY
Extract a unified list of strong, specific keywords and concepts that:
1.  **Represent User Intent:** Capture the core concepts, validated points, and underlying motivations expressed by the user.
2.  **Provide Necessary Context:** Include broader thematic keywords from external info only if they are necessary to understand or locate related concepts in the vault.

Combine these into a single list of comma-separated keywords, optimized for searching the knowledge base.
Example: "keyword1, keyword2, long phrase with keywords"

---START_CONTENT---
{content}
---END_CONTENT---

**Action Required:** Provide a comma-separated list of keywords. Then call `rag prepare-context --keywords "<your_keywords>" --output "consolidated_rag_context.md"` to continue.
"""
            # For this CLI agent, we will print this instruction, and the agent will respond with keywords.
            print(agent_instruction_keywords)
            
            return True, "Agent Instruction: Provide comma-separated keywords based on the above content. Once provided, call rag prepare-context with --keywords and --output to complete this step."
        
        else:
            return False, "Error: Either --keywords or a source (file or content) must be provided for prepare-context."
    
    elif args.rag_command == "get-first-section":
        file_path = args.file
        from ..utils.rag_cli_utils import extract_metadata_and_first_section
        from ..utils.file_utils import read_file_content
        
        content = read_file_content(file_path)
        if not content:
            # Error message already printed by read_file_content
            return False, "Failed to read file."
        
        first_section = extract_metadata_and_first_section(content)
        print(first_section)
        return True, "Extracted first section."

    return False, "Unknown RAG command."