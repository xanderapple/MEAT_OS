import argparse
import os
import subprocess
import sys
import datetime
import re # For slugifying title
import json # For parsing agent's structured output
import yaml # For safe YAML parsing
import glob # For cleaning up files

# Modularized Logic Imports
from ..logic.synthesis import run_preliminary_workflow, run_critique_workflow, run_combine_workflow, run_refinement_workflow
from ..logic.synthesis.final import run_final_workflow, extract_keywords_agent
from ..logic.synthesis.integrate import run_integrate_workflow
from ..logic.synthesis.init import run_init_workflow

# Modularized Prompt Imports (Still needed for final/integrate/init)
from ..prompts import synthesis_prompts, critique_prompts
from ..utils.command_utils import execute_script, sanitize_filename
from ..scripts.call_agent_task import call_sub_agent
import shutil

# New import for moc management
from ..utils.moc_management import update_gemini_index_moc

def add_synthesis_parser(subparsers):
    synthesis_parser = subparsers.add_parser("synthesis", help="Commands for orchestrating synthesis workflows.")
    synthesis_subparsers = synthesis_parser.add_subparsers(dest="synthesis_command", help="Available synthesis commands")

    # preliminary command (Unified Workflow)
    preliminary_parser = synthesis_subparsers.add_parser("preliminary", help="Generates, Audits, or Refines a preliminary synthesis.")
    preliminary_parser.add_argument("--source", required=True, help="Path to input file or direct content.")
    preliminary_parser.add_argument("--draft", help="Optional: Path to an existing draft (triggers Audit mode).")
    preliminary_parser.add_argument("--report", help="Optional: Path to an existing critique report (triggers Refine mode).")
    preliminary_parser.add_argument("--input-mode", choices=['direct', 'reference'], default='direct', help="Deprecated. Kept for CLI compatibility.")
    
    # critique command
    critique_parser = synthesis_subparsers.add_parser("critique", help="Audits a preliminary synthesis using the Sub-Agent.")
    critique_parser.add_argument("draft", help="Path to the preliminary draft file.")
    critique_parser.add_argument("--source", required=True, help="Path to the original source file.")

    # final command
    final_parser = synthesis_subparsers.add_parser("final", help="Refines preliminary synthesis with RAG context. Stage 1: extract keywords. Stage 2: create note.")   
    final_parser.add_argument("preliminary", help="Path to the preliminary synthesis file.")
    final_parser.add_argument("--keywords", help="Optional: Comma-separated keywords to trigger internal RAG and Final Note prompt.")
    final_parser.add_argument("--source", help="Optional: Path to the original source fleeting note.")
    final_parser.add_argument("--skip-rag", action="store_true", help="Optional: Skip RAG generation and use existing consolidated_rag_context.md.")

    # integrate command (Generator for Safe Integration)
    integrate_parser = synthesis_subparsers.add_parser("integrate", help="Generates JSON plan and executes note integrate. Stage 1: keywords. Stage 2: integrate.")    
    integrate_parser.add_argument("source", help="The idea (raw content) or path to SYNTH-... note.")
    integrate_parser.add_argument("--keywords", help="Optional: Comma-separated keywords to trigger internal RAG and Integration prompt.")
    integrate_parser.add_argument("--tags", help="Optional: Initial tags to suggest.")

    # combine command
    combine_parser = synthesis_subparsers.add_parser("combine", help="Combines multiple preliminary synthesis files into one.")
    combine_parser.add_argument("files", nargs="+", help="List of preliminary synthesis files to combine.")

    # init command
    init_parser = synthesis_subparsers.add_parser("init", help="Executes the full synthesis workflow from input to knowledge integration.")
    init_parser.add_argument("--source", required=True, help="Path to input file or direct content for the full synthesis workflow.")
    init_parser.add_argument("--input-mode", choices=['direct', 'reference'], default='direct', help="How to handle the source input.")
    init_parser.add_argument("--resume-from", help="Optional: Path to an existing preliminary synthesis file to skip Step 1.")

    # cleanup command
    cleanup_parser = synthesis_subparsers.add_parser("cleanup", help="Deletes temporary synthesis artifacts (preliminary files, consolidated context, integration plans).")


def handle_synthesis_commands(args):
    if args.synthesis_command == "preliminary":
        # Mode Selection based on arguments
        if args.source and args.draft and args.report:
            # Mode: Refine (Explicit)
            success, msg = run_refinement_workflow(args.source, args.draft, args.report)
            return success, msg
        elif args.source and args.draft:
            # Mode: Audit (Critique)
            success, msg = run_critique_workflow(args.source, args.draft)
            return success, msg
        elif args.source:
            # Mode: Auto-Pilot (Generate -> Loop[Audit -> Refine])
            success, msg = run_preliminary_workflow(args.source)
            return success, msg
        else:
            return False, "Invalid arguments for preliminary command."

    elif args.synthesis_command == "combine":
        success, msg = run_combine_workflow(args.files)
        return success, msg

    elif args.synthesis_command == "final":
        preliminary_file = args.preliminary
        keywords = args.keywords
        skip_rag = args.skip_rag

        if not os.path.exists(preliminary_file):
            return False, f"Error: Preliminary synthesis file not found at {preliminary_file}"

        try:
            with open(preliminary_file, 'r', encoding='utf-8') as f:
                preliminary_content = f.read()
        except Exception as e:
            return False, f"Error reading preliminary file: {e}"

        if skip_rag:
             # Stage 2 (Skip RAG): Use existing context
            temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
            rag_output_path = os.path.join(temp_dir, "consolidated_rag_context.md")
            
            if not os.path.exists(rag_output_path):
                 return False, f"Error: --skip-rag used but {rag_output_path} not found."

            success, final_path = run_final_workflow(preliminary_file, rag_output_path)
            if success:
                return True, f"Final Synthesis Note Generated: {final_path}\n\nNEXT STEP: synthesis integrate \"{final_path}\""
            else:
                return False, f"Final Synthesis Failed: {final_path}"

            agent_instruction_final = synthesis_prompts.get_final_stage2_prompt(preliminary_content, rag_output_path, args.source)
            print(agent_instruction_final)
            return True, "Agent Instruction: Generate and save the Final Synthesis Note using existing RAG context."

        if not keywords:
            print("Auto-extracting keywords...")
            keywords = extract_keywords_agent(preliminary_file)
            if not keywords:
                keywords = "PKM" # Fallback
            print(f"Keywords: {keywords}")

        # Stage 2: Prepare RAG and prompt for Final Note creation
        print(f"Generating RAG context for refinement using keywords: {keywords}")
        from .rag_commands import handle_rag_commands
        
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        rag_output_path = os.path.join(temp_dir, "consolidated_rag_context.md")
        
        # We explicitly ask for output to a file
        success_rag, rag_msg = handle_rag_commands(argparse.Namespace(rag_command="prepare-context", keywords=keywords, source=None, output=rag_output_path, limit=10))

        if not success_rag:
            return False, f"RAG preparation failed: {rag_msg}"

        success, final_path = run_final_workflow(preliminary_file, rag_output_path)
        if success:
            return True, f"Final Synthesis Note Generated: {final_path}\n\nNEXT STEP: synthesis integrate \"{final_path}\""
        else:
            return False, f"Final Synthesis Failed: {final_path}"

    elif args.synthesis_command == "integrate":
        source = args.source
        keywords = args.keywords
        suggested_tags = args.tags
        
        input_content = ""
        source_note_path = ""
        
        if os.path.exists(source):
            with open(source, 'r', encoding='utf-8') as f:
                input_content = f.read()
            source_note_path = source
        else:
            input_content = source
            source_note_path = None

        if not keywords:
            print("Auto-extracting keywords...")
            kw_source_path = source_note_path
            if not kw_source_path:
                temp_kw_file = os.path.join(os.environ.get("GEMINI_TEMP_DIR", "."), "temp_kw_source.md")
                with open(temp_kw_file, 'w', encoding='utf-8') as f:
                     f.write(input_content)
                kw_source_path = temp_kw_file
            
            keywords = extract_keywords_agent(kw_source_path)
            if not keywords:
                 keywords = "PKM"
            print(f"Keywords: {keywords}")

        # Stage 2: Prepare RAG and prompt for JSON Integration
        print(f"Generating RAG context for integration using keywords: {keywords}")
        from .rag_commands import handle_rag_commands
        
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        rag_output_path = os.path.join(temp_dir, "consolidated_rag_context.md")

        # We explicitly ask for output to a file
        success_rag, rag_msg = handle_rag_commands(argparse.Namespace(rag_command="prepare-context", keywords=keywords, source=None, output=rag_output_path, limit=10))

        if not success_rag:
            return False, f"RAG preparation failed: {rag_msg}"

        success, json_path = run_integrate_workflow(rag_output_path, source_note_path, input_content, suggested_tags)
        
        if success:
            # Warn about conflicts for next step
            warning_msg = ""
            if "## Contradiction Analysis" in input_content and not re.search(r"## Contradiction Analysis\s*\n\s*$", input_content):
                    warning_msg = f"\n\n⚠️  CONFLICTS DETECTED: Review 'manual_review' items."

            return True, f"""Integration Plan Generated: {json_path}
{warning_msg}

ACTION REQUIRED: Execute the following to apply changes:
note integrate "{json_path}" {"--source " + '"' + source_note_path + '"' if source_note_path else ""}

FINAL STEP: Run `synthesis cleanup`."""
        else:
            return False, f"Integration Plan Generation Failed: {json_path}"

    elif args.synthesis_command == "init":
        success, msg = run_init_workflow(args.source, args.input_mode, args.resume_from)
        return success, msg

    elif args.synthesis_command == "cleanup":
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        patterns = [
            os.path.join(temp_dir, "preliminary_synthesis_*.md"),
            os.path.join(temp_dir, "chunk_*.md"),
            os.path.join(temp_dir, "prelim_chunk_*.md"),
            os.path.join(temp_dir, "preliminary_combined_*.md"),
            os.path.join(temp_dir, "integration_output_*.json"),
            os.path.join(temp_dir, "conflict_resolution_output_*.json"),
            os.path.join(temp_dir, "relevant_rag_files.txt"),
            os.path.join(temp_dir, "critique_report_*.md"),
            "preliminary_synthesis_*.md",
            "final_synthesis_*.md",
            "preliminary_combined_*.md",
            "critique_report_*.md",
            "consolidated_rag_context.md",
            "create_integration_json.py",
            "relevant_rag_files.txt"
        ]
        
        removed_files = []
        for pattern in patterns:
            files = glob.glob(pattern)
            for f in files:
                try:
                    os.remove(f)
                    removed_files.append(f)
                except Exception as e:
                    print(f"Error deleting {f}: {e}")
        
        if removed_files:
            msg = f"Successfully cleaned up {len(removed_files)} temporary files:\n" + "\n".join([f"  - {os.path.basename(f)}" for f in removed_files])
            return True, msg
        else:
            return True, "No temporary synthesis files found for cleanup."

    return False, "Unknown synthesis command."
