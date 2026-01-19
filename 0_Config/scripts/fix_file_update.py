import os
import sys
import re
import subprocess

# Function to read a file with encoding fallback
def read_file_with_encoding_fallback(file_path):
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            sys.stderr.write(f"Error trying to read {file_path} with encoding {encoding}: {e}\n")
            continue
    sys.stderr.write(f"Error: Could not read {file_path} with any attempted encoding.\n")
    return None

def clean_file_to_original_state_robust(file_path: str):
    """
    Restores a file to its absolute original state by extracting the first YAML
    frontmatter and the content immediately following the first H1 heading,
    removing any extraneous content in between.
    """
    content = read_file_with_encoding_fallback(file_path)
    if content is None:
        return False

    yaml_frontmatter_pattern = re.compile(r"^(---.*?---\s*\n)", re.DOTALL)
    yaml_match = yaml_frontmatter_pattern.match(content)

    if yaml_match:
        original_yaml_block = yaml_match.group(1)
        content_after_yaml = content[yaml_match.end():]

        # Find the first H1 after the YAML frontmatter
        first_h1_match = re.search(r"^(#\s*.*)", content_after_yaml, re.MULTILINE)
        if first_h1_match:
            original_main_content_start_index = first_h1_match.start()
            original_main_content = content_after_yaml[original_main_content_start_index:]
            
            clean_original_file_content = f"{original_yaml_block}{original_main_content}"

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_original_file_content)
                sys.stdout.write(f"Restored {file_path} to its absolute clean state.\n")
                return True
            except Exception as e:
                sys.stderr.write(f"Error writing cleaned content to {file_path}: {e}\n")
                return False
    
    sys.stderr.write(f"Error: Could not restore {file_path} to clean state (YAML or H1 not found).\n")
    return False


def clean_and_reapply_update(file_path: str, update_content: str):
    """
    Cleans a file by removing any update blocks (restoring to original state) and
    then reapplies the update correctly using prepend_update.py.
    """
    if not clean_file_to_original_state_robust(file_path):
        return False

    # Now, reapply the update using prepend_update.py
    cmd = [
        sys.executable, # Use the current Python executable
        "0_Config/scripts/prepend_update.py",
        file_path,
        update_content
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            sys.stderr.write(f"Error reapplying update with prepend_update.py to {file_path}:\n{result.stderr}\n")
            return False
        sys.stdout.write(f"Successfully reapplied update to {file_path}.\n")
        return True
    except Exception as e:
        sys.stderr.write(f"Error running prepend_update.py for {file_path}: {e}\n")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python fix_file_update.py <file_path> <update_content_string>\n")
        sys.exit(1)

    target_file = sys.argv[1]
    update_content_string = " ".join(sys.argv[2:]) 

    if clean_and_reapply_update(target_file, update_content_string):
        print(f"File {target_file} corrected and updated successfully.")
    else:
        print(f"Failed to correct and update file {target_file}.")
        sys.exit(1)
