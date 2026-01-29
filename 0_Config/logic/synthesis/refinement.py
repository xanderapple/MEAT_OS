import os
import shutil
from ...prompts import critique_prompts
from ...scripts.call_agent_task import call_sub_agent

def _run_refinement(source_input, draft_input, report_input):
    """
    Helper function to run a Refinement task via the Sub-Agent.
    """
    # Prepare Prompt
    context_source_file = "context_source.md"
    draft_file = "preliminary_draft.md"
    report_file = "critique_report.md"
    agent_instruction = critique_prompts.get_refinement_prompt(context_source_file, draft_file, report_file)

    # Prepare Input Files
    input_files = {}
    if os.path.exists(source_input):
        input_files[context_source_file] = source_input
    else:
        temp_src = os.path.join(os.environ.get("GEMINI_TEMP_DIR", "."), "temp_refine_src.md")
        with open(temp_src, 'w', encoding='utf-8') as f:
            f.write(source_input)
        input_files[context_source_file] = temp_src

    if os.path.exists(draft_input):
        input_files[draft_file] = draft_input
    else:
        print(f"Draft file not found: {draft_input}")
        return None

    if os.path.exists(report_input):
        input_files[report_file] = report_input
    else:
        print(f"Report file not found: {report_input}")
        return None

    # Dispatch
    print(f"Dispatching Refinement to Sub-Agent...")
    result = call_sub_agent(agent_instruction, input_files=input_files)

    # Retrieve
    if result:
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        final_refined_path = os.path.join(temp_dir, f"preliminary_synthesis_refined_{os.urandom(4).hex()}.md")
        with open(final_refined_path, 'w', encoding='utf-8') as f:
            f.write(result)
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

