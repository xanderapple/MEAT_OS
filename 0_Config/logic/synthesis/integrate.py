import os
import shutil
from ...prompts import integrate_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_integrate_gen(rag_path, source_path, content_path, tags):
    workspace_dir = os.path.join("0_Config", "Sub_Agent_Workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    rag_file = "rag_context.md"
    source_file = "source_note.md"
    input_file = "input_content.md" # The synthesis note content
    json_file = "integration_plan.json"
    task_prompt_file = "task_prompt.md"
    
    abs_rag = os.path.join(workspace_dir, rag_file)
    abs_source = os.path.join(workspace_dir, source_file)
    abs_input = os.path.join(workspace_dir, input_file)
    abs_json = os.path.join(workspace_dir, json_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)

    # 1. Stage
    if os.path.exists(rag_path): shutil.copy(rag_path, abs_rag)
    else: open(abs_rag, 'w').close()

    if source_path and os.path.exists(source_path): shutil.copy(source_path, abs_source)
    else: open(abs_source, 'w').close()
    
    # Input content is usually a string or file
    if os.path.exists(content_path): shutil.copy(content_path, abs_input)
    else: 
        with open(abs_input, 'w', encoding='utf-8') as f:
            f.write(content_path) # Treat as string

    # 2. Prompt
    prompt = integrate_prompts.get_integrate_prompt(rag_file, source_file, input_file, json_file, tags)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)

    # 3. Dispatch
    print("Dispatching Integration Plan Generation...")
    call_sub_agent("__USE_EXISTING__")
    
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        shutil.move(abs_task_output, abs_json)
        return abs_json
    return None

def _run_integrate_critique(json_path):
    workspace_dir = os.path.join("0_Config", "Sub_Agent_Workspace")
    json_file = "integration_plan.json"
    report_file = "critique_report.md"
    task_prompt_file = "task_prompt.md"
    
    abs_report = os.path.join(workspace_dir, report_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    
    prompt = integrate_prompts.get_integrate_critique_prompt(json_file, report_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print("Dispatching Integration Critique...")
    call_sub_agent("__USE_EXISTING__")
    
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        shutil.move(abs_task_output, abs_report)
        return abs_report
    return None

def _run_integrate_refine(json_path, report_path):
    workspace_dir = os.path.join("0_Config", "Sub_Agent_Workspace")
    json_file = "integration_plan.json"
    report_file = "critique_report.md"
    output_file = "integration_plan_refined.json"
    task_prompt_file = "task_prompt.md"
    
    abs_output = os.path.join(workspace_dir, output_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    
    prompt = integrate_prompts.get_integrate_refinement_prompt(json_file, report_file, output_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
        
    print("Dispatching Integration Refinement...")
    call_sub_agent("__USE_EXISTING__")
    
    abs_task_output = os.path.join(workspace_dir, "task_output.md")
    if os.path.exists(abs_task_output):
        shutil.move(abs_task_output, os.path.join(workspace_dir, json_file))
        return os.path.join(workspace_dir, json_file)
    return None

def run_integrate_workflow(rag_path, source_path, content_path, tags=""):
    print("\n--- Starting Integration Plan Loop ---")
    
    current_json = _run_integrate_gen(rag_path, source_path, content_path, tags)
    if not current_json:
        return False, "Integration Plan Generation Failed."
        
    MAX_RETRIES = 2
    for i in range(MAX_RETRIES):
        print(f"\nAudit Attempt {i+1}/{MAX_RETRIES}...")
        report = _run_integrate_critique(current_json)
        if not report: break
        
        with open(report, 'r', encoding='utf-8') as f:
            if "VERDICT: PASS" in f.read():
                print("✅ Integration Plan Verified.")
                temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
                final_path = os.path.join(temp_dir, f"integration_output_{os.urandom(4).hex()}.json")
                shutil.copy(current_json, final_path)
                return True, final_path
        
        print("❌ Verification Failed. Refining...")
        new_json = _run_integrate_refine(current_json, report)
        if new_json: current_json = new_json
        else: break
    
    temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
    final_path = os.path.join(temp_dir, f"integration_output_{os.urandom(4).hex()}.json")
    shutil.copy(current_json, final_path)
    return True, final_path
