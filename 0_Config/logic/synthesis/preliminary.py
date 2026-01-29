import os
import shutil
import json
from ...prompts import preliminary_prompts # Import the new modular prompt file
from ...scripts.call_agent_task import call_sub_agent
from .critique import _run_critique
from .refinement import _run_refinement

def _load_synthesis_state():
    temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
    state_file = os.path.join(temp_dir, "synthesis_state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
    return None

def _save_synthesis_state(state):
    temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
    state_file = os.path.join(temp_dir, "synthesis_state.json")
    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def _run_single_preliminary_synthesis(source_input):
    """
    Helper function to run a single preliminary synthesis task via the Sub-Agent.
    """
    # Prepare Prompt
    context_source_file = "context_source.md"
    agent_instruction = preliminary_prompts.get_preliminary_prompt(context_source_file)

    # Prepare Input Files
    input_files = {}
    if os.path.exists(source_input):
        input_files[context_source_file] = source_input
    else:
        # If source_input is direct content, write to temp file first
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        temp_src = os.path.join(temp_dir, "temp_prelim_src.md")
        with open(temp_src, 'w', encoding='utf-8') as f:
            f.write(source_input)
        input_files[context_source_file] = temp_src

    # Dispatch
    print(f"[Status] Dispatching Sub-Agent Task (Generation)... Source: {os.path.basename(source_input) if os.path.exists(source_input) else 'Direct Input'}")
    result = call_sub_agent(agent_instruction, input_files=input_files)

    # Retrieve
    if result:
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        os.makedirs(temp_dir, exist_ok=True)
        final_output_path = os.path.join(temp_dir, f"preliminary_synthesis_{os.urandom(4).hex()}.md")
        with open(final_output_path, 'w', encoding='utf-8') as f:
            f.write(result)
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

def run_preliminary_workflow(source_input, resume=False):
    """
    Executes the full Preliminary Synthesis workflow (Chunking -> Generation -> Loop[Audit -> Refine]).
    """
    state = None
    if resume:
        # Check for existing state
        state = _load_synthesis_state()
        if state and state.get("source") == source_input:
            print(f"\n>>> RESUMING PRELIMINARY SYNTHESIS: {len(state['outputs'])}/{len(state['chunks'])} chunks complete.")
            chunk_paths = state["chunks"]
            output_paths = state["outputs"]
        else:
            print("[Warning] Resume requested but no matching state found or source changed. Starting fresh.")
            state = None

    if not state:
        # Fresh Start: Clear any stale state
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        state_file = os.path.join(temp_dir, "synthesis_state.json")
        if os.path.exists(state_file):
            os.remove(state_file)

        # Check size for chunking
        raw_lines = []
        if os.path.exists(source_input):
                with open(source_input, 'r', encoding='utf-8') as f:
                    raw_lines = f.readlines()
        else:
                raw_lines = source_input.splitlines(keepends=True)

        CHUNK_SIZE = 500
        line_count = len(raw_lines)

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
            
            # Initialize State
            state = {
                "source": source_input,
                "chunks": chunk_paths,
                "outputs": []
            }
            _save_synthesis_state(state)
        else:
            chunk_paths = [source_input]
            output_paths = []

    # --- PHASE 1: GENERATION & VERIFICATION ---
    for i in range(len(output_paths), len(chunk_paths)):
        chunk_path = chunk_paths[i]
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
        
        # Update state after each chunk
        if state:
            state["outputs"] = output_paths
            _save_synthesis_state(state)

    # Finalization
    if len(chunk_paths) > 1:
        print("Combining verified chunks...")
        final_draft_path = _combine_synthesis_files(output_paths)
        # Clear state upon completion
        temp_dir = os.environ.get("GEMINI_TEMP_DIR", ".")
        state_file = os.path.join(temp_dir, "synthesis_state.json")
        if os.path.exists(state_file):
            os.remove(state_file)
        
        print(f"Multi-Chunk Synthesis Complete. Output: {final_draft_path}")
        return True, f"Workflow Complete (Chunked).\nFinal Draft: {final_draft_path}"
    else:
        final_draft_path = output_paths[0]
        print(f"Preliminary Synthesis Complete. Output: {final_draft_path}")
        return True, f"Workflow Complete.\nFinal Draft: {final_draft_path}"

def run_combine_workflow(files):
    output_path = _combine_synthesis_files(files)
    return True, f"Combined {len(files)} files into: {output_path}\n\nNEXT STEP: Execute:\nsynthesis final \"{output_path}\""
