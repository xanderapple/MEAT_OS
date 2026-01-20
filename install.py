import os
import shutil
import argparse
import sys

# Configuration
SOURCE_CONFIG_DIR = "0_Config"
TARGET_CONFIG_DIR = "0_Config"

# Files that should NEVER be overwritten if they exist in target
PROTECTED_FILES = [
    "PROJECT_VARIABLE.md",
    "action_log.md",
    "GEMINI.md",
    "GEMINI_INDEX.md",
    "Preference_Index.md"
]

# Directories that should be skipped/preserved
PROTECTED_DIRS = [
    "logs_archive",
    "Sub_Agent_Workspace",
    "__pycache__",
    ".git",
    ".obsidian"
]

def install_meat_os(target_root, dry_run=False):
    """
    Installs/Updates MEAT_OS logic into the target Vault.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, SOURCE_CONFIG_DIR)
    target_path = os.path.join(target_root, TARGET_CONFIG_DIR)

    print(f"[*] Installing MEAT_OS...")
    print(f"    Source: {source_path}")
    print(f"    Target: {target_path}")

    if not os.path.exists(source_path):
        print(f"[!] Error: Source directory '{source_path}' not found.")
        return

    if not os.path.exists(target_path):
        print(f"[*] Target directory '{target_path}' does not exist. Creating...")
        if not dry_run:
            os.makedirs(target_path)

    # Walk through source directory
    for root, dirs, files in os.walk(source_path):
        # Calculate relative path to mirror structure
        rel_path = os.path.relpath(root, source_path)
        
        # Determine target directory for this iteration
        if rel_path == ".":
            current_target_dir = target_path
        else:
            current_target_dir = os.path.join(target_path, rel_path)

        # Filter out protected directories from traversal to avoid entering them
        dirs[:] = [d for d in dirs if d not in PROTECTED_DIRS]
        
        # Create directories in target
        for d in dirs:
            d_path = os.path.join(current_target_dir, d)
            if not os.path.exists(d_path):
                print(f"[+] Creating directory: {d_path}")
                if not dry_run:
                    os.makedirs(d_path)

        # Process files
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(current_target_dir, f)

            # Handle Protected Files
            if f in PROTECTED_FILES:
                if os.path.exists(dst_file):
                    print(f"[-] Skipping protected file: {f}")
                    continue
            
            # Special Handling: Templates
            if f == "PROJECT_VARIABLE.template.md":
                real_config = os.path.join(current_target_dir, "PROJECT_VARIABLE.md")
                if not os.path.exists(real_config):
                    print(f"[+] Bootstrap: Copying template to {real_config}")
                    if not dry_run:
                        shutil.copy2(src_file, real_config)
                # We also copy the template itself as reference
            
            # Normal Copy (Overwrite)
            # Only copy if different (timestamp/size) could be an optimization, 
            # but for logic updates, we usually want to force ensure we have the latest code.
            # However, printing "Updating" vs "Up to date" is nice.
            
            should_copy = True
            if os.path.exists(dst_file):
                # Simple check: timestamp or size? 
                # Logic updates: always overwrite is safer to ensure consistency.
                pass
            
            if should_copy:
                print(f"[^] Updating: {os.path.join(rel_path, f)}")
                if not dry_run:
                    shutil.copy2(src_file, dst_file)

    print("[*] Installation Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install/Update MEAT_OS logic to a Vault.")
    parser.add_argument("--target", required=True, help="Path to the Vault root directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making changes")
    
    args = parser.parse_args()
    
    install_meat_os(args.target, args.dry_run)
