import os
import shutil
from ...prompts import final_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_single_final_synthesis(prelim_path, rag_path):
    """
    Runs the Sub-Agent to generate the Final Note.
    """
    # Prepare Prompt
    prelim_file = "preliminary.md"
    rag_file = "rag_context.md"
    prompt = final_prompts.get_final_prompt(prelim_file, rag_file)

    # Prepare Input Files
    input_files = {
        prelim_file: prelim_path,
        rag_file: rag_path if os.path.exists(rag_path) else "/dev/null"
    }

    # Dispatch
    print("Dispatching Final Note Generation...")
    result = call_sub_agent(prompt, input_files=input_files)

    # Retrieve
    if result:
        workspace_dir = os.path.join("gemini_subagent", "workspace")
        draft_file = os.path.join(workspace_dir, "final_draft.md")
        with open(draft_file, 'w', encoding='utf-8') as f:
            f.write(result)
        return draft_file
    return None

def _run_final_critique(draft_path, source_path):
    # Prepare Prompt
    draft_file = "final_draft.md" 
    source_file = "source_ground_truth.md"
    prompt = final_prompts.get_final_critique_prompt(draft_file, source_file)

    # Prepare Input Files
    input_files = {
        draft_file: draft_path,
        source_file: source_path if source_path and os.path.exists(source_path) else "/dev/null"
    }
        
    print("Dispatching Final Note Critique...")
    result = call_sub_agent(prompt, input_files=input_files)
    
    if result:
        workspace_dir = os.path.join("gemini_subagent", "workspace")
        report_file = os.path.join(workspace_dir, "critique_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(result)
        return report_file
    return None

def _run_final_refinement(draft_path, report_path, source_path):
    # Prepare Prompt
    draft_file = "final_draft.md"
    source_file = "source_ground_truth.md"
    report_file = "critique_report.md"
    prompt = final_prompts.get_final_refinement_prompt(draft_file, report_file, source_file)

    # Prepare Input Files
    input_files = {
        draft_file: draft_path,
        report_file: report_path,
        source_file: source_path if source_path and os.path.exists(source_path) else "/dev/null"
    }
    
    print("Dispatching Final Note Refinement...")
    result = call_sub_agent(prompt, input_files=input_files)
    
    if result:
        workspace_dir = os.path.join("gemini_subagent", "workspace")
        draft_out = os.path.join(workspace_dir, "final_draft.md")
        with open(draft_out, 'w', encoding='utf-8') as f:
            f.write(result)
        return draft_out
    return None

def extract_keywords_agent(file_path):
    """
    Runs a sub-agent task to extract keywords from a file.
    """
    content_file = "keyword_source.md"
    prompt = final_prompts.get_keyword_extraction_prompt(content_file)
    
    input_files = {
        content_file: file_path
    }
        
    print("Dispatching Keyword Extraction...")
    result_content = call_sub_agent(prompt, input_files=input_files)
    
    if result_content:
        return result_content.strip()
        
    return None

def run_final_workflow(prelim_path, rag_path, source_path=None):
    """
    Orchestrates the Final Note generation loop.
    """
    print("\n--- Starting Final Synthesis Loop ---")
    
    # 1. Generation
    print("[Status] Generating Final Note Draft...")
    current_draft = _run_single_final_synthesis(prelim_path, rag_path)
    if not current_draft:
        print("[Error] Final Note Generation Failed.")
        return False, "Final Note Generation Failed."
    print(f"[Status] Draft Generated: {current_draft}")
    
    # 2. Loop
    MAX_RETRIES = 1
    for i in range(MAX_RETRIES):
        print(f"\n[Status] Audit Attempt {i+1}/{MAX_RETRIES}...")
        report = _run_final_critique(current_draft, source_path)
        
        if not report:
            print("[Error] Critique failed. Proceeding with current draft.")
            break
            
        print(f"[Status] Critique Report: {report}")
            
        with open(report, 'r', encoding='utf-8') as f:
            content = f.read()
            if "VERDICT: PASS" in content:
                print("[Success] ✅ Final Note Verified.")
                # Move to Temp
                temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
                final_path = os.path.join(temp_dir, f"final_synthesis_{os.urandom(4).hex()}.md")
                shutil.copy(current_draft, final_path)
                return True, final_path
        
        print("[Status] ❌ Verification Failed. Refining...")
        new_draft = _run_final_refinement(current_draft, report, source_path)
        if new_draft:
            print(f"[Success] Refinement Successful: {new_draft}")
            current_draft = new_draft
        else:
            print("[Error] Refinement failed.")
            break
            
    # Fallback return
    temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
    final_path = os.path.join(temp_dir, f"final_synthesis_{os.urandom(4).hex()}.md")
    shutil.copy(current_draft, final_path)
    print(f"[Status] Workflow Ended. Final Output: {final_path}")
    return True, final_path
