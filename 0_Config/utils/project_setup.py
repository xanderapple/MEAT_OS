import os

def initialize_project(vault_root: str) -> None:
    """
    Initializes a new project by creating essential configuration files if they don't exist.

    Args:
        vault_root: The root directory of the Obsidian vault (project root).
    """
    project_variable_path = os.path.join(vault_root, "0_Config/PROJECT_VARIABLE.md")
    preference_moc_path = os.path.join(vault_root, "0_Config/Context/Preference_Index.md")

    # Ensure 0_Config directory exists
    os.makedirs(os.path.dirname(project_variable_path), exist_ok=True)
    # Ensure 3_Map_of_Content directory exists
    os.makedirs(os.path.dirname(preference_moc_path), exist_ok=True)

    # Create PROJECT_VARIABLE.md if it doesn't exist
    if not os.path.exists(project_variable_path):
        print(f"Creating default {project_variable_path}...")
        default_project_variable_content = """---
Tags: config, project
---

# Project Variables

This file defines project-specific configurations and context for the Gemini CLI.

## General Settings
- **Project Name:** Meat
- **Vault Root Path:** C:\\XANAX\\Meat
- **Temporary Directory:** C:\\Users\\dell\\.gemini\\tmp\\
- **Log File Path:** 0_Config/Context/action_log.md
- **Default Output Directory:** output/

## Active Workflows
- **Current Synthesis Workflow:** RAG Synthesis
- **Active RAG Profile:** Default

## AI Agent Settings
- **LLM Model Name:** gemini-2.5-flash
- **Max Tokens:** 1000000
"""
        with open(project_variable_path, 'w', encoding='utf-8') as f:
            f.write(default_project_variable_content)
        print(f"Successfully created {project_variable_path}")
    else:
        print(f"{project_variable_path} already exists. Skipping creation.")

    # Create Preference_Index_MOC.md if it doesn't exist
    if not os.path.exists(preference_moc_path):
        print(f"Creating default {preference_moc_path}...")
        default_preference_moc_content = """---
Tags: moc, preference, config
---

# Preference Index MOC

This MOC serves as the active configuration file for guiding the RAG synthesis process. It defines various preferences, constraints, and instructions that influence the tone, priority, and structure of the generated synthesis outputs.

## Behavioral Constraints
- **Tone:** Neutral, Objective
- **Verbosity:** Detailed
- **Audience:** Technical
- **Perspective:** Third-person

## Content Prioritization
- **Keywords to emphasize:**
    - RAG
    - Synthesis
    - Obsidian
    - PKM
- **Topics to prioritize:**
    - AI Integration
    - Knowledge Management
    - Workflow Automation

## Output Structure Preferences
- **Include Summary:** Yes
- **Include Key Takeaways:** Yes
- **Include Ambiguities/Contradictions:** Yes
- **Reference Style:** Wikilinks

## Source Prioritization
- **Preferred sources:**
    - `2_Literature_Notes/Experience/Chat_Synthesis/`
    - `2_Literature_Notes/Knowledge/`
"""
        with open(preference_moc_path, 'w', encoding='utf-8') as f:
            f.write(default_preference_moc_content)
        print(f"Successfully created {preference_moc_path}")
    else:
        print(f"{preference_moc_path} already exists. Skipping creation.")

    print("Project initialization complete.")
