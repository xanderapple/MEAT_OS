import sys
import os

# Bridge to the gemini_subagent submodule
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from gemini_subagent.sub_agent import call_sub_agent
except ImportError:
    # Fallback for different execution contexts
    sys.path.append(os.path.join(project_root, "gemini_subagent"))
    try:
        from sub_agent import call_sub_agent
    except ImportError:
        def call_sub_agent(prompt):
            print("Error: gemini_subagent module not found.")
            return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python call_agent_task.py "<Prompt Text or File Path>"')
        sys.exit(1)
    
    input_val = sys.argv[1]
    
    # Check if input is a file path
    if os.path.isfile(input_val):
        try:
            with open(input_val, 'r', encoding='utf-8') as f:
                user_prompt = f.read()
        except Exception as e:
            print(f"Error reading prompt file: {e}")
            sys.exit(1)
    else:
        user_prompt = " ".join(sys.argv[1:])
    
    call_sub_agent(user_prompt)
