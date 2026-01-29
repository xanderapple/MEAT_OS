import os
import shutil
from ...prompts import integrate_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_integrate_gen(rag_path, source_path, content_path, tags):
    # Prepare Prompt
    rag_file = "rag_context.md"
    source_file = "source_note.md"
    input_file = "input_content.md"
    prompt = integrate_prompts.get_integrate_prompt(rag_file, source_file, input_file, tags)

    # Prepare Input Files
    input_files = {
        rag_file: rag_path,
        source_file: source_path if source_path else "/dev/null"
    }
    
    # Handle content_path (could be string or path)
    if os.path.exists(content_path):
        input_files[input_file] = content_path
    else:
        temp_input = os.path.join(os.environ.get("GEMINI_TEMP_DIR", "."), "temp_integrate_input.md")
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(content_path)
        input_files[input_file] = temp_input

    # Dispatch
    print("Dispatching Integration Plan Generation...")
    result = call_sub_agent(prompt, input_files=input_files)
    
    if result:
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        json_file = os.path.join(temp_dir, f"integration_plan_{os.urandom(4).hex()}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(result)
        return json_file
    return None

def _run_integrate_critique(json_path, source_path, rag_path):
    # Prepare Prompt
    json_file = "integration_plan.json"
    source_file = "source_ground_truth.md"
    rag_file = "rag_context.md"
    prompt = integrate_prompts.get_integrate_critique_prompt(json_file, source_file, rag_file)

    # Prepare Input Files
    input_files = {
        json_file: json_path,
        source_file: source_path if source_path else "/dev/null",
        rag_file: rag_path if rag_path else "/dev/null"
    }

    # Dispatch
    print("Dispatching Integration Audit...")
    result = call_sub_agent(prompt, input_files=input_files)
    
    if result:
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        report_file = os.path.join(temp_dir, f"critique_report_{os.urandom(4).hex()}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(result)
        return report_file
    return None

def _run_integrate_refine(json_path, report_path, source_path):
    # Prepare Prompt
    json_file = "integration_plan.json"
    source_file = "source_ground_truth.md"
    report_file = "critique_report.md"
    prompt = integrate_prompts.get_integrate_refinement_prompt(json_file, report_file, source_file)

    # Prepare Input Files
    input_files = {
        json_file: json_path,
        report_file: report_path,
        source_file: source_path if source_path else "/dev/null"
    }

    # Dispatch
    print("Dispatching Integration Refinement...")
    result = call_sub_agent(prompt, input_files=input_files)
    
    if result:
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        json_out = os.path.join(temp_dir, f"integration_plan_refined_{os.urandom(4).hex()}.json")
        with open(json_out, 'w', encoding='utf-8') as f:
            f.write(result)
        return json_out
    return None

def run_integrate_workflow(rag_path, source_path, content_path, tags=""):
    print("\n--- Starting Integration Plan Loop ---")
    
    current_json = _run_integrate_gen(rag_path, source_path, content_path, tags)
    if not current_json:
        return False, "Integration Plan Generation Failed."
        
    MAX_RETRIES = 1
    for i in range(MAX_RETRIES):
        print(f"\nAudit Attempt {i+1}/{MAX_RETRIES}...")
        report = _run_integrate_critique(current_json, source_path, rag_path)
        if not report: break
        
        with open(report, 'r', encoding='utf-8') as f:
            if "VERDICT: PASS" in f.read():
                print("✅ Integration Plan Verified.")
                temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
                final_path = os.path.join(temp_dir, f"integration_output_{os.urandom(4).hex()}.json")
                shutil.copy(current_json, final_path)
                return True, final_path
        
        print("❌ Verification Failed. Refining...")
        new_json = _run_integrate_refine(current_json, report, source_path)
        if new_json: current_json = new_json
        else: break
    
    temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
    final_path = os.path.join(temp_dir, f"integration_output_{os.urandom(4).hex()}.json")
    shutil.copy(current_json, final_path)
    return True, final_path
