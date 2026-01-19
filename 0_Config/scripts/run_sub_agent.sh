#!/bin/bash

# ------------------------------------------------------------------
# Run Sub-Agent (File-Based Workflow)
# ------------------------------------------------------------------
# Usage: ./run_sub_agent.sh "Your detailed instructions here"
# 
# Workflow:
# 1. Input string -> 'task_prompt.md'
# 2. Agent reads 'task_prompt.md'
# 3. Agent writes result -> 'task_output.md'
# ------------------------------------------------------------------

# Ensure we are running from the project root or scripts dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
WORKSPACE_ABS_PATH="$ROOT_DIR/0_Config/Sub_Agent_Workspace"

if [ -z "$1" ]; then
  echo "Usage: $0 \"<Prompt/Instructions>\""
  exit 1
fi

PROMPT_TEXT="$1"
PROMPT_FILE="task_prompt.md"
OUTPUT_FILE="task_output.md"

# 1. Prepare Workspace
mkdir -p "$WORKSPACE_ABS_PATH"
cd "$WORKSPACE_ABS_PATH" || exit

# 2. Write the user's prompt to a file (unless told to use existing)
if [ "$PROMPT_TEXT" == "__USE_EXISTING__" ]; then
    echo "Using existing '$PROMPT_FILE'..."
else
    echo "$PROMPT_TEXT" > "$PROMPT_FILE"
fi

echo "--------------------------------------------------"
echo "Sub-Agent Task Started"
echo "Input File:  $PROMPT_FILE"
echo "Output File: $OUTPUT_FILE"
echo "--------------------------------------------------"

# 3. Construct the Meta-Instruction
# We explicitly tell the agent what tools to use to minimize "thinking" errors.
# NOTE: We use 'read_file' to ensure proper encoding handling (avoiding mojibake).
META_PROMPT="SYSTEM TASK:
1. Use 'read_file' to read the content of '$PROMPT_FILE'.
2. Execute the instructions found in that text.
3. Use 'write_file' to save the final result into '$OUTPUT_FILE'.
4. Terminate the session immediately after writing the file."

# 4. Run Gemini
# --yolo: Auto-approve tool calls
# -m: Specify the model
gemini -m gemini-3-flash-preview --yolo "$META_PROMPT"

echo "--------------------------------------------------"
if [ -f "$OUTPUT_FILE" ]; then
    echo "Task Complete. Output content:"
    echo "--------------------------------------------------"
    cat "$OUTPUT_FILE"
    echo ""
    echo "--------------------------------------------------"
else
    echo "Error: Output file '$OUTPUT_FILE' was not created."
fi
