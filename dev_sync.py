import os
import shutil
import argparse
import sys

# Configuration
REPO_ROOT = os.path.dirname(os.path.abspath(__file__)) # _system/MEAT_OS
VAULT_ROOT = os.path.dirname(os.path.dirname(REPO_ROOT)) # MEAT (Grandparent of MEAT_OS)
REPO_CONFIG_DIR = os.path.join(REPO_ROOT, "0_Config")
LIVE_CONFIG_DIR = os.path.join(VAULT_ROOT, "0_Config")

# Files that should NEVER be synced back to repo (User Data)
PROTECTED_FILES = [
    "PROJECT_VARIABLE.md",
    "action_log.md",
    "GEMINI_INDEX.md",
    "Preference_Index.md",
    "GEMINI.md",
    "notion_commands.py",
    "notion_api.py",
    "NOTION.md"
]

PROTECTED_DIRS = [
    "logs_archive",
    "Sub_Agent_Workspace",
    "__pycache__",
    ".git",
    ".obsidian",
    "Context" # We don't sync Context folder back, except for templates
]

def sync_live_to_repo(dry_run=False):
    """
    Pushes changes from Live Vault (0_Config) -> MEAT_OS Repo.
    """
    print(f"[*] Syncing Live Logic -> MEAT_OS Repo...")
    print(f"    Source (Live): {LIVE_CONFIG_DIR}")
    print(f"    Target (Repo): {REPO_CONFIG_DIR}")

    if not os.path.exists(LIVE_CONFIG_DIR):
        print(f"[!] Error: Live config not found at {LIVE_CONFIG_DIR}")
        return

    # Walk through LIVE directory
    for root, dirs, files in os.walk(LIVE_CONFIG_DIR):
        rel_path = os.path.relpath(root, LIVE_CONFIG_DIR)
        
        # Target dir in Repo
        if rel_path == ".":
            current_target_dir = REPO_CONFIG_DIR
        else:
            current_target_dir = os.path.join(REPO_CONFIG_DIR, rel_path)

        # Skip protected directories
        # We manually check if we are IN a protected dir or one of its subdirs
        # Special case: 'Context' folder contains user data, but also templates we might want to update?
        # Actually, for now, let's assume we DO NOT sync Context back unless we explicitly whitelist templates.
        # But 'Context' contains PROJECT_VARIABLE.template.md. 
        
        # Filter traversal
        dirs[:] = [d for d in dirs if d not in PROTECTED_DIRS]
        
        # If we are in root, we might want to check into Context for templates
        if rel_path == ".":
            # Manually handle Context/PROJECT_VARIABLE.template.md if needed
            # For simplicity, this script focuses on LOGIC (py, prompts).
            pass

        # Process files
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(current_target_dir, f)

            # Ignore protected files (User Data)
            if f in PROTECTED_FILES:
                continue
            
            # Special handling for templates in Context if we were traversing it, but we are skipping Context.
            
            # If file doesn't exist in Repo, ask/warn? 
            # Or just copy if it's code.
            # For now, strict update: Only update if exists in Repo or is a .py/.md file that looks like logic.
            
            # Let's just mirror for now, but exclude known user data.
            
            if os.path.exists(dst_file):
                # Update existing file
                print(f"[^] Updating Repo: {os.path.join(rel_path, f)}")
                if not dry_run:
                    shutil.copy2(src_file, dst_file)
            else:
                # New file?
                # If it's a python file or logic markdown, add it.
                if f.endswith(".py") or (f.endswith(".md") and "Template" in rel_path):
                     print(f"[+] Adding New File to Repo: {os.path.join(rel_path, f)}")
                     if not dry_run:
                        # Ensure dir exists
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy2(src_file, dst_file)

    # Special handling for templates in Context (since we skipped Context dir)
    # If we updated PROJECT_VARIABLE.template.md in Live Context, sync it back.
    live_template = os.path.join(LIVE_CONFIG_DIR, "Context", "PROJECT_VARIABLE.template.md")
    repo_template = os.path.join(REPO_CONFIG_DIR, "Context", "PROJECT_VARIABLE.template.md")
    
    if os.path.exists(live_template) and os.path.exists(repo_template):
         print(f"[^] Updating Template: Context/PROJECT_VARIABLE.template.md")
         if not dry_run:
             shutil.copy2(live_template, repo_template)

    # --- Sync gemini_subagent ---
    LIVE_AGENT_DIR = os.path.join(VAULT_ROOT, "gemini_subagent")
    REPO_AGENT_DIR = os.path.join(REPO_ROOT, "gemini_subagent")
    
    print(f"[*] Syncing Live Agent -> MEAT_OS Repo...")
    if os.path.exists(LIVE_AGENT_DIR):
        for root, dirs, files in os.walk(LIVE_AGENT_DIR):
            rel_path = os.path.relpath(root, LIVE_AGENT_DIR)
            
            # Target dir
            if rel_path == ".":
                current_target_dir = REPO_AGENT_DIR
            else:
                current_target_dir = os.path.join(REPO_AGENT_DIR, rel_path)

            # Filter dirs
            dirs[:] = [d for d in dirs if d not in ["workspace", "__pycache__", ".git"]]
            
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(current_target_dir, f)
                
                if f.endswith(".pyc"): continue
                if f == ".DS_Store": continue

                if os.path.exists(dst_file):
                    print(f"[^] Updating Repo Agent: {os.path.join(rel_path, f)}")
                    if not dry_run:
                        shutil.copy2(src_file, dst_file)
                else:
                    if f.endswith(".py") or f.endswith(".sh") or f == "README.md":
                        print(f"[+] Adding New Agent File: {os.path.join(rel_path, f)}")
                        if not dry_run:
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            shutil.copy2(src_file, dst_file)

    print("[*] Sync Complete. Verify changes in _system/MEAT_OS before committing.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dev Tool: Sync Live Logic back to Repo.")
    parser.add_argument("--push", action="store_true", help="Push changes from Live -> Repo")
    parser.add_argument("--dry-run", action="store_true", help="Simulate push")
    
    args = parser.parse_args()
    
    if args.push:
        sync_live_to_repo(args.dry_run)
    else:
        print("Usage: python dev_sync.py --push [--dry-run]")
