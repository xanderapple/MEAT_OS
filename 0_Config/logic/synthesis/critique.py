import os
import shutil
from ...prompts import critique_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_critique(source_input, draft_input):
    """
    Helper function to run a critique task via the Sub-Agent.
    """
    workspace_dir = os.path.join("gemini_subagent", "workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    context_source_file = "context_source.md"
    draft_file = "preliminary_draft.md"
    task_prompt_file = "task_prompt.md"
    task_output_file = "task_output.md"
    
    abs_context_source = os.path.join(workspace_dir, context_source_file)
    abs_draft = os.path.join(workspace_dir, draft_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    abs_task_output = os.path.join(workspace_dir, task_output_file)

    # 1. Stage Source
    if os.path.exists(source_input):
        shutil.copy(source_input, abs_context_source)
    else:
        with open(abs_context_source, 'w', encoding='utf-8') as f:
            f.write(source_input)

    # 2. Stage Draft
    if os.path.exists(draft_input):
        shutil.copy(draft_input, abs_draft)
    else:
        print(f"Draft file not found: {draft_input}")
        return None

    # 3. Generate Prompt
    agent_instruction = critique_prompts.get_critique_prompt(context_source_file, draft_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(agent_instruction)

    # 4. Dispatch
    print(f"Dispatching Critique to Sub-Agent...")
    call_sub_agent("__USE_EXISTING__")

    # 5. Retrieve
    if os.path.exists(abs_task_output):
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        final_report_path = os.path.join(temp_dir, f"critique_report_{os.urandom(4).hex()}.md")
        shutil.move(abs_task_output, final_report_path)
        return final_report_path
    else:
        print("Sub-Agent failed to generate critique report.")
        return None

def run_critique_workflow(source_input, draft_input):
    critique_path = _run_critique(source_input, draft_input)
    if critique_path:
        return True, f"Critique Complete.\nReport saved to: {critique_path}"
    else:
        return False, "Critique failed."

