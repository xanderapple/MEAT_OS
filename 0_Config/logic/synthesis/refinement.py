import os
import shutil
from ...prompts import critique_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_refinement(source_input, draft_input, report_input):
    """
    Helper function to run a Refinement task via the Sub-Agent.
    """
    workspace_dir = os.path.join("0_Config", "Sub_Agent_Workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    context_source_file = "context_source.md"
    draft_file = "preliminary_draft.md"
    report_file = "critique_report.md"
    task_prompt_file = "task_prompt.md"
    task_output_file = "task_output.md"
    
    abs_context_source = os.path.join(workspace_dir, context_source_file)
    abs_draft = os.path.join(workspace_dir, draft_file)
    abs_report = os.path.join(workspace_dir, report_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    abs_task_output = os.path.join(workspace_dir, task_output_file)

    # 1. Stage Files
    if os.path.exists(source_input):
        shutil.copy(source_input, abs_context_source)
    else:
        with open(abs_context_source, 'w', encoding='utf-8') as f:
            f.write(source_input)

    if os.path.exists(draft_input):
        shutil.copy(draft_input, abs_draft)
    else:
        print(f"Draft file not found: {draft_input}")
        return None

    if os.path.exists(report_input):
        shutil.copy(report_input, abs_report)
    else:
        print(f"Report file not found: {report_input}")
        return None

    # 2. Generate Prompt
    agent_instruction = critique_prompts.get_refinement_prompt(context_source_file, draft_file, report_file, task_output_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(agent_instruction)

    # 3. Dispatch
    print(f"Dispatching Refinement to Sub-Agent...")
    call_sub_agent("__USE_EXISTING__")

    # 4. Retrieve
    if os.path.exists(abs_task_output):
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        final_refined_path = os.path.join(temp_dir, f"preliminary_synthesis_refined_{os.urandom(4).hex()}.md")
        shutil.move(abs_task_output, final_refined_path)
        return final_refined_path
    else:
        print("Sub-Agent failed to generate refined draft.")
        return None

def run_refinement_workflow(source_input, draft_input, report_input):
    refined_path = _run_refinement(source_input, draft_input, report_input)
    if refined_path:
        return True, f"Refinement Complete.\nNew Draft saved to: {refined_path}"
    else:
        return False, "Refinement failed."

