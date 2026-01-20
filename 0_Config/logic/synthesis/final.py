import os
import shutil
from ...prompts import final_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_single_final_synthesis(prelim_path, rag_path):
    """
    Runs the Sub-Agent to generate the Final Note.
    """
    workspace_dir = os.path.join("gemini_subagent", "workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Filenames in workspace
    prelim_file = "preliminary.md"
    rag_file = "rag_context.md"
    draft_file = "final_draft.md"
    task_prompt_file = "task_prompt.md"
    
    abs_prelim = os.path.join(workspace_dir, prelim_file)
    abs_rag = os.path.join(workspace_dir, rag_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    abs_draft = os.path.join(workspace_dir, draft_file)

    # 1. Stage Files
    shutil.copy(prelim_path, abs_prelim)
    if os.path.exists(rag_path):
        shutil.copy(rag_path, abs_rag)
    else:
        with open(abs_rag, 'w', encoding='utf-8') as f:
            f.write("No RAG context provided.")

    # 2. Generate Prompt
    prompt = final_prompts.get_final_prompt(prelim_file, rag_file, draft_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)

    # 3. Dispatch
    print("Dispatching Final Note Generation...")
    call_sub_agent("__USE_EXISTING__")

    # 4. Retrieve
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        shutil.move(abs_task_output, abs_draft)
        return abs_draft 
    return None

def _run_final_critique(draft_path):
    workspace_dir = os.path.join("gemini_subagent", "workspace")
    
    draft_file = "final_draft.md" # It's already there
    report_file = "critique_report.md"
    task_prompt_file = "task_prompt.md"
    
    abs_report = os.path.join(workspace_dir, report_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    
    prompt = final_prompts.get_final_critique_prompt(draft_file, report_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print("Dispatching Final Note Critique...")
    call_sub_agent("__USE_EXISTING__")
    
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        shutil.move(abs_task_output, abs_report)
        return abs_report
    return None

def _run_final_refinement(draft_path, report_path):
    workspace_dir = os.path.join("gemini_subagent", "workspace")
    
    draft_file = "final_draft.md"
    report_file = "critique_report.md"
    output_file = "final_draft_refined.md"
    task_prompt_file = "task_prompt.md"
    
    abs_output = os.path.join(workspace_dir, output_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    
    prompt = final_prompts.get_final_refinement_prompt(draft_file, report_file, output_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print("Dispatching Final Note Refinement...")
    call_sub_agent("__USE_EXISTING__")
    
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        # Move refined to draft for next loop
        shutil.move(abs_task_output, os.path.join(workspace_dir, draft_file))
        return os.path.join(workspace_dir, draft_file)
    return None

def extract_keywords_agent(file_path):
    """
    Runs a sub-agent task to extract keywords from a file.
    """
    workspace_dir = os.path.join("gemini_subagent", "workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    content_file = "keyword_source.md"
    output_file = "keywords.txt"
    task_prompt_file = "task_prompt.md"
    
    abs_content = os.path.join(workspace_dir, content_file)
    abs_output = os.path.join(workspace_dir, output_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    
    shutil.copy(file_path, abs_content)
    
    prompt = final_prompts.get_keyword_extraction_prompt(content_file, output_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print("Dispatching Keyword Extraction...")
    call_sub_agent("__USE_EXISTING__")
    
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        with open(abs_task_output, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def run_final_workflow(prelim_path, rag_path):
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
    MAX_RETRIES = 2
    for i in range(MAX_RETRIES):
        print(f"\n[Status] Audit Attempt {i+1}/{MAX_RETRIES}...")
        report = _run_final_critique(current_draft)
        
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
        new_draft = _run_final_refinement(current_draft, report)
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
