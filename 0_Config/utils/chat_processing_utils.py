import os
import datetime
import re
import shutil
import time
from .file_utils import read_file_content # Ensure this is the correct import

def _format_preferences_prompt(preferences: str) -> str:
    """
    Helper to format the preferences prompt section to ensure they are treated as context, not rigid directives.
    """
    if not preferences:
        return ""
    
    return f"""
---
**User Context & Ongoing Interests (For Awareness Only):**
The following preferences and priorities represent the user's general interests and ongoing projects.
Your primary obligation is to synthesize the actual content of the chat provided below.
If a natural and relevant connection to these preferences arises directly from the chat content, then highlight that connection within your synthesis.
---
"""

def _construct_synthesis_prompt(perspective_name: str, input_content: str, preferences: str, rag_context: str) -> str:
    template_map = {
        "World View": "Templates/World_View_Meta_Prompt.md",
        "Human Realm": "Templates/Human_Realm_Meta_Prompt.md",
        "Value Challenge": "Templates/Value_Challenge_Meta_Prompt.md",
        "Implementation Plan": "Templates/Implementation_Plan_Meta_Prompt.md",
    }
    
    template_path = template_map.get(perspective_name)
    if not template_path:
        return f"Error: No template found for perspective '{perspective_name}'."

    template_content = read_file_content(template_path) # Using the existing read_file_content
    if not template_content:
        return f"Error: Could not read template file {template_path} for perspective '{perspective_name}'."

    # Integrate preferences prompt formatting
    full_prompt = _format_preferences_prompt(preferences)
    
    # Inject RAG context and input content into the template
    full_prompt += template_content.replace("<RAG_CONTEXT_PLACEHOLDER>", rag_context).replace("<INPUT_CONTENT_PLACEHOLDER>", input_content)
    
    return full_prompt
from .file_utils import read_file_content
from .llm_sim import llm_call
from .config_parsers import load_user_preferences, parse_project_context
from .moc_management import update_gemini_index_moc, update_preference_index_moc
from .rag_cli_utils import parse_gemini_index_moc, find_relevant_notes
from .note_management import (
    save_synthesis_note,
    create_synthesis_overview_note,
    update_chat_status
)

def process_chat_file(file_path: str, api_key: str = None):
    """
    Processes a raw chat file, generates metadata, renames and moves the file,
    and then triggers the multi-perspective synthesis using a STATEFUL approach.
    """
    # Initialize these variables at the start to ensure they are always defined
    preferences_for_llm = "" 
    rag_context_content = "" 

    # First, update the Gemini Index MOC to ensure RAG context is fresh
    print("Updating Gemini Index MOC...")
    vault_root_path = os.getcwd()
    update_gemini_index_moc(vault_root_path)
    print("Gemini Index MOC updated.")

    # Update Preference Index MOC
    print("Updating Preference Index MOC...")
    update_preference_index_moc(vault_root_path)
    print("Preference Index MOC updated.")

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Determine if the file is already a processed chat log
    is_processed_chat_log = False
    final_chat_log_path = ""
    
    chat_logs_dir = "1_Fleeting_Notes/Capture/Chat_Logs"
    if os.path.dirname(file_path) == chat_logs_dir:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_start = f.read(100) # Read first 100 characters to check for YAML frontmatter
                if content_start.startswith("---"):
                    is_processed_chat_log = True
                    final_chat_log_path = file_path
                    print(f"File {file_path} is already a processed chat log. Skipping copy/rename/metadata injection.")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return

    if not is_processed_chat_log:
        content = read_file_content(file_path) # Use local helper function

        # --- LLM call to generate title and tags ---
        title_tags_prompt = f"""Given the following chat content, please generate a concise title and a list of relevant tags (keywords).
        Respond in JSON format with "title" and "tags" keys.
        Example: {{'title': 'Example Title', 'tags': ['tag1', 'tag2']}}

        Chat Content:
        {content}
        """
        title_tags_response = llm_call(title_tags_prompt, api_key=api_key)

        if title_tags_response.startswith("Error:"):
            print(f"Failed to generate title and tags: {title_tags_response}")
            return

        try:
            import json
            # Use regex to extract JSON string from markdown code block
            json_match = re.search(r"```json\n(.*)\n```", title_tags_response, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                json_string = title_tags_response # Fallback if no markdown block

            parsed_response = json.loads(json_string)
            title = parsed_response.get("title", "Untitled Chat")
            tags = parsed_response.get("tags", [])
        except json.JSONDecodeError:
            print(f"Error parsing title and tags JSON response: {title_tags_response}")
            title = "Untitled Chat"
            tags = []
        # ---------------------------------------------------------

        # --- Load User Preferences ---
        preferences_dir = "2_Literature_Notes/Personal/Preferences/"
        preference_moc_path = "0_Config/Context/Preference_Index.md"
        loaded_preferences = load_user_preferences(preferences_dir, preference_moc_path)
        
        # Format preferences for LLM prompt
        # Initialize preferences_for_llm here so it's always defined
        preferences_for_llm = "" 
        if loaded_preferences:
            preferences_for_llm += "\n--- User Preferences ---\n"
            for key, value in loaded_preferences.items():
                if key == "unstructured_preferences" and value:
                    preferences_for_llm += f"\n{value}\n"
                elif isinstance(value, dict) and value:
                    preferences_for_llm += f"### {key.replace('_', ' ').title()}\n"
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list):
                            preferences_for_llm += f"- {sub_key.replace('_', ' ').title()}: {', '.join(sub_value)}\n"
                        else:
                            preferences_for_llm += f"- {sub_key.replace('_', ' ').title()}: {sub_value}\n"
            preferences_for_llm += "\n------------------------\n"
        # ---------------------------

        # --- RAG Context Retrieval ---
        rag_context_content = "" 
        # Get project context to find Gemini_Index_MOC path
        project_variable_path = "0_Config/PROJECT_VARIABLE.md"
        project_variables = parse_project_context(project_variable_path)
        gemini_index_moc_path = project_variables.get("paths", {}).get("gemini_index_moc_path")

        if not gemini_index_moc_path or not os.path.exists(gemini_index_moc_path):
            print(f"Warning: Gemini Index MOC not found at '{gemini_index_moc_path}'. RAG context will be empty.")
        else:
            # Read content of Gemini Index MOC
            moc_content = read_file_content(gemini_index_moc_path)
            if not moc_content:
                print(f"Warning: Gemini Index MOC at '{gemini_index_moc_path}' is empty. RAG context will be empty.")
            else:
                # 1. Parse Gemini_Index_MOC
                note_map = parse_gemini_index_moc(moc_content, gemini_index_moc_path) # Pass both content and path
                
                # 2. Extract search topics from chat title and tags
                search_topics = [title] + tags # Combine title and tags as search topics
                
                # 3. Find relevant notes
                relevant_note_paths = find_relevant_notes(search_topics, note_map)
                
                # --- NEW: Filter relevant_note_paths to include only literature notes (excluding chat synthesis paths) ---
                filtered_relevant_note_paths = [
                    path for path in relevant_note_paths 
                    if path.startswith("2_Literature_Notes/") and not path.startswith("2_Literature_Notes/Experience/Chat_Synthesis/")
                ]
                # --- END NEW ---

                # 4. Read and consolidate content of relevant notes
                if filtered_relevant_note_paths: # Use filtered paths
                    rag_context_content += "\n--- Relevant Knowledge from Vault ---\n"
                    for note_path in filtered_relevant_note_paths: # Use filtered paths
                        note_content = read_file_content(note_path + ".md") # Add .md extension to read file
                        if note_content:
                            # Optional: Extract relevant sections from the note_content if it's too large
                            # For now, we'll include the whole note, up to a certain limit if needed
                            rag_context_content += f"\n### Source: {os.path.basename(note_path)}.md\n"
                            rag_context_content += note_content
                            rag_context_content += "\n---\n"
                rag_context_content += "\n-----------------------------------\n"
        # ---------------------------------

        # Create the new filename
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        sanitized_title = re.sub(r'[^\w\-_\. ]', '', title).replace(' ', '_')
        new_filename = f"{date_str}_{sanitized_title}.md"
        final_chat_log_path = os.path.join(chat_logs_dir, new_filename)

        # Ensure the chat_logs_dir exists
        os.makedirs(chat_logs_dir, exist_ok=True)

        # Copy the file
        shutil.copy(file_path, final_chat_log_path)
        print(f"Copied file to: {final_chat_log_path}")

        # --- LLM call to generate YAML frontmatter ---
        yaml_prompt = f"""Given the following information, generate YAML frontmatter for an Obsidian note.
        Include 'id' (unix timestamp), 'date' (YYYY-MM-DD), 'topic', 'source' (always "Gemini Chat"), 'type' (always "LLM/Chat"), 'project' (always "Gemini Integration"), and 'tags'.
        The tags should be a comma-separated string.
        Ensure the output is valid YAML frontmatter, starting and ending with '---'.
        Crucially, ensure that any string values containing colons, commas, or other special YAML characters are enclosed in double quotes. For example, 'key: value, with: colon' should be 'key: "value, with: colon"'.

        Topic: "{title}"
        Tags: "{', '.join(tags)}"
        Chat Content:
        {content}
        """
        yaml_response = llm_call(yaml_prompt, api_key=api_key)

        if yaml_response.startswith("Error:"):
            print(f"Failed to generate YAML frontmatter: {yaml_response}")
            return
        
        # Assume LLM returns valid YAML, trim any extra text if necessary
        # and ensure it starts and ends with '---'
        generated_yaml = yaml_response.strip()
        
        # Remove markdown code block delimiters if present
        if generated_yaml.startswith("```yaml"):
            generated_yaml = generated_yaml[7:]
        elif generated_yaml.startswith("```"):
            generated_yaml = generated_yaml[3:]
        
        if generated_yaml.endswith("```"):
            generated_yaml = generated_yaml[:-3]
        
        generated_yaml = generated_yaml.strip()

        if not generated_yaml.startswith("---"):
            generated_yaml = "---\n" + generated_yaml
        if not generated_yaml.endswith("---"):
            generated_yaml = generated_yaml + "\n---"
        
        yaml_frontmatter = generated_yaml + "\n" # Add a newline after the closing ---
        # -----------------------------------------------------------

        # Prepend the YAML frontmatter
        with open(final_chat_log_path, 'r+', encoding='utf-8') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(yaml_frontmatter + content)
        
        print(f"Added YAML frontmatter to: {final_chat_log_path}")
    else: # If already processed, we need to read its content to pass to synthesis
        content = read_file_content(file_path) # Use local helper function
        # Extract title and tags from frontmatter for already processed chat logs
        frontmatter_match = re.match(r'---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_str = frontmatter_match.group(1)
            try:
                import yaml
                frontmatter_data = yaml.safe_load(frontmatter_str)
                title = frontmatter_data.get('topic', "Untitled Chat")
                tags_str = frontmatter_data.get('tags', "")
                tags = [t.strip() for t in tags_str.split(',') if t.strip()] if isinstance(tags_str, str) else tags_str
            except yaml.YAMLError:
                print(f"Error parsing YAML in {file_path}. Defaulting title and tags.")
                title = "Untitled Chat"
                tags = []
        else:
            title = "Untitled Chat"
            tags = []
        sanitized_title = re.sub(r'[^\w\-_\. ]', '', title).replace(' ', '_')


    # --- STATEFUL PARALLEL SYNTHESIS ---
    print(f"Synthesizing perspectives for '{title}'...")
    
    # We use a unique slug for this synthesis batch
    topic_slug = sanitized_title

    synthesis_notes_paths = {}

    # 1. World View
    print("  Synthesizing World View (Deltas)...")
    world_view_prompt = _construct_synthesis_prompt("World View", content, preferences_for_llm, rag_context_content)
    if world_view_prompt.startswith("Error:"):
        print(world_view_prompt)
    else:
        world_view_output = llm_call(world_view_prompt, api_key=api_key)
        if not world_view_output.startswith("Error:"):
            path = save_synthesis_note(topic_slug, "World View", world_view_output)
            if path: synthesis_notes_paths["World View"] = path

    # 2. Human Realm
    print("  Synthesizing Human Realm (Needs)...")
    human_realm_prompt = _construct_synthesis_prompt("Human Realm", content, preferences_for_llm, rag_context_content)
    if human_realm_prompt.startswith("Error:"):
        print(human_realm_prompt)
    else:
        human_realm_output = llm_call(human_realm_prompt, api_key=api_key)
        if not human_realm_output.startswith("Error:"):
            path = save_synthesis_note(topic_slug, "Human Realm", human_realm_output)
            if path: synthesis_notes_paths["Human Realm"] = path

    # 3. Value Challenge
    print("  Synthesizing Value Challenge (Alignment)...")
    value_challenge_prompt = _construct_synthesis_prompt("Value Challenge", content, preferences_for_llm, rag_context_content)
    if value_challenge_prompt.startswith("Error:"):
        print(value_challenge_prompt)
    else:
        value_challenge_output = llm_call(value_challenge_prompt, api_key=api_key)
        if not value_challenge_output.startswith("Error:"):
            path = save_synthesis_note(topic_slug, "Value Challenge", value_challenge_output)
            if path: synthesis_notes_paths["Value Challenge"] = path

    # 4. Implementation Plan
    print("  Synthesizing Implementation Plan (Actions)...")
    implementation_plan_prompt = _construct_synthesis_prompt("Implementation Plan", content, preferences_for_llm, rag_context_content)
    if implementation_plan_prompt.startswith("Error:"):
        print(implementation_plan_prompt)
    else:
        implementation_plan_output = llm_call(implementation_plan_prompt, api_key=api_key)
        if not implementation_plan_output.startswith("Error:"):
            path = save_synthesis_note(topic_slug, "Implementation Plan", implementation_plan_output)
            if path: synthesis_notes_paths["Implementation Plan"] = path

    # 5. Create Overview Note
    if synthesis_notes_paths:
        overview_path = create_synthesis_overview_note(topic_slug, synthesis_notes_paths)
        print(f"  Created Synthesis Overview: {overview_path}")
        
        # 6. Update Status of Original File
        update_chat_status(final_chat_log_path, "✨ synthesized")
        print(f"  Marked {final_chat_log_path} as synthesized.")
    
    print("Chat processing complete.")