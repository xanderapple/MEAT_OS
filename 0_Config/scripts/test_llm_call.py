import os
import sys
import google.generativeai as genai

# Add the project root to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir) # Add current directory (project root)
sys.path.insert(0, os.path.join(script_dir, '0_Config')) # Add 0_Config as a path

# Correct the import path to llm_sim
from utils.llm_sim import llm_call # Now it should find utils in 0_Config

test_prompt = "Hello Gemini, what is the capital of France?"

if __name__ == "__main__":
    # You might need to pass the API key explicitly or ensure GEMINI_API_KEY is set in your environment
    api_key = os.environ.get("GEMINI_API_KEY") 
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    print(f"Testing single LLM call with prompt: '{test_prompt}'")
    response = llm_call(test_prompt, api_key=api_key)
    print("\n--- LLM Response ---")
    print(response)
    print("--------------------")