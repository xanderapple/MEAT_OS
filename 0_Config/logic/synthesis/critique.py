import os
import shutil
from ...prompts import critique_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_critique(source_input, draft_input):
    """
    Helper function to run a critique task via the Sub-Agent.
    """
    # Prepare Prompt
    context_source_file = "context_source.md"
    draft_file = "preliminary_draft.md"
    agent_instruction = critique_prompts.get_critique_prompt(context_source_file, draft_file)

    # Prepare Input Files
    input_files = {}
    if os.path.exists(source_input):
        input_files[context_source_file] = source_input
    else:
        temp_src = os.path.join(os.environ.get("GEMINI_TEMP_DIR", "."), "temp_critique_src.md")
        with open(temp_src, 'w', encoding='utf-8') as f:
            f.write(source_input)
        input_files[context_source_file] = temp_src

    if os.path.exists(draft_input):
        input_files[draft_file] = draft_input
    else:
        print(f"Draft file not found: {draft_input}")
        return None

    # Dispatch
    print(f"Dispatching Critique to Sub-Agent...")
    result = call_sub_agent(agent_instruction, input_files=input_files)

    # Retrieve
    if result:
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        final_report_path = os.path.join(temp_dir, f"critique_report_{os.urandom(4).hex()}.md")
        with open(final_report_path, 'w', encoding='utf-8') as f:
            f.write(result)
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

