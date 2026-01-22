import os
import datetime
import argparse
import shutil
from ...scripts.call_agent_task import call_sub_agent
from ...prompts import final_prompts
from .preliminary import run_preliminary_workflow
from .final import run_final_workflow, extract_keywords_agent
from .integrate import run_integrate_workflow

# We need to import the RAG handler. 
# We do this inside the function to avoid potential top-level circular imports if any exist.

def run_init_workflow(source_path, input_mode="direct", resume_from=None):
    """
    Executes the FULL synthesis chain:
    Archive -> Preliminary -> Keywords -> RAG -> Final -> Integrate -> Apply
    If resume_from is provided, skips steps accordingly.
    """
    
    # --- STEP 0: ARCHIVE & SETUP ---
    final_source_path = source_path
    prelim_path = ""
    final_path = ""
    rag_output_path = os.path.join(os.environ.get("GEMINI_TEMP_DIR", "."), "consolidated_rag_context.md")

    if resume_from:
        if not os.path.exists(resume_from):
            return False, f"Resume file not found: {resume_from}"
        print(f"\n>>> RESUMING SYNTHESIS from: {resume_from}")
        
        # Detection logic
        base_resume = os.path.basename(resume_from)
        if base_resume.startswith("final_synthesis_"):
            print("[Status] Detected Final Synthesis. Skipping Steps 1-3.")
            final_path = resume_from
            # We still need RAG context for integration, try to find it or create dummy
            if not os.path.exists(rag_output_path):
                print("Warning: RAG context not found. Creating empty context for integration.")
                with open(rag_output_path, 'w', encoding='utf-8') as f:
                    f.write("No RAG context available (Resumed from Final).")
        else:
            print("[Status] Detected Preliminary Synthesis. Skipping Step 1.")
            prelim_path = resume_from
    else:
        # (Standard Archiving Logic)
        if os.path.exists(source_path):
            if os.path.dirname(source_path) == "":
                archive_dir = "=3_Archived"
                os.makedirs(archive_dir, exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                base_name = os.path.basename(source_path)
                new_filename = f"RAW-{timestamp}-{base_name}"
                new_path = os.path.join(archive_dir, new_filename)
                try:
                    os.rename(source_path, new_path)
                    print(f"Auto-Migrated source to: {new_path}")
                    final_source_path = new_path
                except Exception as e:
                    print(f"Warning: Failed to move source file: {e}")

    # --- STEP 1: PRELIMINARY ---
    if not prelim_path and not final_path:
        print("\n>>> STEP 1: PRELIMINARY SYNTHESIS")
        success_prelim, result_prelim = run_preliminary_workflow(final_source_path)
        if not success_prelim:
            return False, f"Preliminary Synthesis Failed: {result_prelim}"
        
        if "Final Draft: " in result_prelim:
            # More robust parsing
            prelim_path = result_prelim.split("Final Draft: ")[1].strip().split('\n')[0].strip()
        
        if not prelim_path or not os.path.exists(prelim_path):
            if os.path.exists(result_prelim): 
                 prelim_path = result_prelim
            else:
                 return False, f"Could not locate preliminary file from result: {result_prelim}"
        print(f"Preliminary File: {prelim_path}")

    # --- STEP 2 & 3: RAG & FINAL ---
    if not final_path:
        print("\n>>> STEP 2: RAG CONTEXT PREPARATION")
        keywords = extract_keywords_agent(prelim_path)
        if not keywords:
            keywords = "PKM, Synthesis"
        print(f"Keywords: {keywords}")
        
        from ...commands.rag_commands import handle_rag_commands
        rag_args = argparse.Namespace(rag_command="prepare-context", keywords=keywords, source=None, output=rag_output_path, limit=10)
        success_rag, rag_msg = handle_rag_commands(rag_args)
        if not success_rag:
            return False, f"RAG Preparation Failed: {rag_msg}"

        print("\n>>> STEP 3: FINAL SYNTHESIS NOTE")
        success_final, final_path = run_final_workflow(prelim_path, rag_output_path, final_source_path)
        if not success_final:
            return False, f"Final Synthesis Failed: {final_path}"
        print(f"Final Note: {final_path}")

    # --- STEP 4: INTEGRATION PLAN ---
    print("\n>>> STEP 4: INTEGRATION PLAN")
    # We use final_path (the Synthesis Note) as the reference for the integration plan
    success_int, json_path = run_integrate_workflow(rag_output_path, final_path, final_path, tags="")
    if not success_int:
        return False, f"Integration Plan Failed: {json_path}"
    print(f"Integration Plan: {json_path}")

    # --- STEP 5: APPLY INTEGRATION ---
    print("\n>>> STEP 5: APPLYING KNOWLEDGE INTEGRATION")
    from ...commands.note_commands import handle_note_commands
    # The 'source' here is what the new notes will link to. 
    # It MUST be the Permanent Synthesis Note (final_path), not the raw log.
    apply_args = argparse.Namespace(note_command="integrate", plan=json_path, source=final_path, verbose=True)
    success_apply, apply_msg = handle_note_commands(apply_args)
    
    if not success_apply:
        return False, f"Note Integration Failed: {apply_msg}"
    
    # --- STEP 6: AUTOMATIC CLEANUP ---
    print("\n>>> STEP 6: CLEANING UP TEMPORARY ARTIFACTS")
    from ...commands.synthesis_commands import handle_synthesis_commands
    cleanup_args = argparse.Namespace(synthesis_command="cleanup")
    handle_synthesis_commands(cleanup_args)
    
    return True, f"""
==================================================
SYNTHESIS CHAIN COMPLETE, APPLIED & CLEANED
==================================================

1. Source: {final_source_path}
2. Final Note: {final_path}
3. Integration Plan: {json_path}
4. Application Status: SUCCESS
5. Cleanup Status: SUCCESS

Log: {apply_msg}
"""
