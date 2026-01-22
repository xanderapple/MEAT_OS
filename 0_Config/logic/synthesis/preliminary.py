import os
import shutil
from ...prompts import preliminary_prompts # Import the new modular prompt file
from ...scripts.call_agent_task import call_sub_agent
from .critique import _run_critique
from .refinement import _run_refinement

def _run_single_preliminary_synthesis(source_input):
    """
    Helper function to run a single preliminary synthesis task via the Sub-Agent.
    """
    workspace_dir = os.path.join("gemini_subagent", "workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    
    context_source_file = "context_source.md"
    task_prompt_file = "task_prompt.md"
    task_output_file = "task_output.md"
    
    abs_context_source = os.path.join(workspace_dir, context_source_file)
    abs_task_prompt = os.path.join(workspace_dir, task_prompt_file)
    abs_task_output = os.path.join(workspace_dir, task_output_file)

    # Stage Source
    content_to_stage = ""
    if os.path.exists(source_input):
        try:
            with open(source_input, 'r', encoding='utf-8') as f:
                content_to_stage = f.read()
        except Exception as e:
            print(f"Error reading source file: {e}")
            return None
    else:
        content_to_stage = source_input

    with open(abs_context_source, 'w', encoding='utf-8') as f:
        f.write(content_to_stage)

    # Generate Prompt
    agent_instruction = preliminary_prompts.get_preliminary_prompt(context_source_file)
    with open(abs_task_prompt, 'w', encoding='utf-8') as f:
        f.write(agent_instruction)

    # Dispatch
    print(f"[Status] Dispatching Sub-Agent Task (Generation)... Source: {os.path.basename(source_input) if os.path.exists(source_input) else 'Direct Input'}")
    call_sub_agent("__USE_EXISTING__")

    # Retrieve
    if os.path.exists(abs_task_output):
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        final_output_path = os.path.join(temp_dir, f"preliminary_synthesis_{os.urandom(4).hex()}.md")
        shutil.move(abs_task_output, final_output_path)
        return final_output_path
    else:
        print("Sub-Agent failed to generate output.")
        return None

def _combine_synthesis_files(file_list):
    """
    Helper function to combine multiple synthesis files.
    """
    combined_content = "# Combined Preliminary Synthesis\n\n"
    for i, fpath in enumerate(file_list):
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_content += f"## --- CHUNK {i+1} ---\n{content}\n\n"
        else:
            print(f"Warning: File {fpath} not found during combination.")

    temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
    output_path = os.path.join(temp_dir, f"preliminary_combined_{os.urandom(4).hex()}.md")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    return output_path

def run_preliminary_workflow(source_input):
    """
    Executes the full Preliminary Synthesis workflow (Chunking -> Generation -> Loop[Audit -> Refine]).
    """
    # Check size for chunking
    raw_lines = []
    if os.path.exists(source_input):
            with open(source_input, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()
    else:
            raw_lines = source_input.splitlines(keepends=True)

    CHUNK_SIZE = 500
    line_count = len(raw_lines)

    final_draft_path = ""

    # --- PHASE 1: GENERATION ---
    if line_count > CHUNK_SIZE:
        print(f"Input is large ({line_count} lines). Splitting into chunks...")
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        
        chunk_paths = []
        output_paths = []
        
        # 1. Create Chunks
        for i in range(0, line_count, CHUNK_SIZE):
            chunk_lines = raw_lines[i:i + CHUNK_SIZE]
            chunk_content = "".join(chunk_lines)
            chunk_filename = f"chunk_{i // CHUNK_SIZE}_{os.path.basename(source_input) if os.path.exists(source_input) else 'raw'}.md"
            chunk_path = os.path.join(temp_dir, chunk_filename)
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk_content)
            chunk_paths.append(chunk_path)

        # 2. Process Each Chunk
        for i, chunk_path in enumerate(chunk_paths):
            print(f"Processing Chunk {i+1}/{len(chunk_paths)}...")
            result_path = _run_single_preliminary_synthesis(chunk_path)
            
            if not result_path:
                return False, f"Failed to process chunk {i+1}."

            # --- PER-CHUNK AUDIT & REFINE ---
            MAX_RETRIES = 1
            current_chunk_draft = result_path
            
            for attempt in range(1, MAX_RETRIES + 1):
                print(f"[Status] Chunk {i+1} - Attempt {attempt}/{MAX_RETRIES}: Running Critique...")
                critique_path = _run_critique(chunk_path, current_chunk_draft)
                
                if not critique_path:
                    print(f"[Error] Chunk {i+1} critique failed. Proceeding.")
                    break
                
                with open(critique_path, 'r', encoding='utf-8') as f:
                    if "VERDICT: PASS" in f.read():
                        print(f"[Success] ✅ Chunk {i+1} Verified.")
                        break
                    else:
                        print(f"[Status] ❌ Chunk {i+1} FAIL. Refining...")
                        refined_path = _run_refinement(chunk_path, current_chunk_draft, critique_path)
                        if refined_path:
                            current_chunk_draft = refined_path
                        else:
                            break
            
            output_paths.append(current_chunk_draft)

        # 3. Combine
        print("Combining verified chunks...")
        final_draft_path = _combine_synthesis_files(output_paths)
        print(f"Multi-Chunk Synthesis Complete. Output: {final_draft_path}")
        return True, f"Workflow Complete (Chunked).\nFinal Draft: {final_draft_path}"

    else:
        # Standard Single File
        result_path = _run_single_preliminary_synthesis(source_input)
        if not result_path:
            return False, "Synthesis failed."
        
        # --- SINGLE FILE AUDIT & REFINE ---
        MAX_RETRIES = 1
        current_draft = result_path
        
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"[Status] Single File - Attempt {attempt}/{MAX_RETRIES}: Running Critique...")
            critique_path = _run_critique(source_input, current_draft)
            
            if not critique_path: break
            
            with open(critique_path, 'r', encoding='utf-8') as f:
                if "VERDICT: PASS" in f.read():
                    print(f"[Success] ✅ Draft Verified.")
                    break
                else:
                    print(f"[Status] ❌ Draft FAIL. Refining...")
                    refined_path = _run_refinement(source_input, current_draft, critique_path)
                    if refined_path: current_draft = refined_path
                    else: break
        
        final_draft_path = current_draft
        print(f"Preliminary Synthesis Complete. Output: {final_draft_path}")
        return True, f"Workflow Complete.\nFinal Draft: {final_draft_path}"

def run_combine_workflow(files):
    output_path = _combine_synthesis_files(files)
    return True, f"Combined {len(files)} files into: {output_path}\n\nNEXT STEP: Execute:\nsynthesis final \"{output_path}\""
