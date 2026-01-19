import os
import re
import sys

# Define the parse_gemini_index_moc_content function
def parse_gemini_index_moc_content(moc_content: str, moc_file_path: str) -> dict:
    note_map = {}
    # Corrected wikilink_pattern to escape '[' and ']'
    wikilink_pattern = re.compile(r'\[\[(.*?)\]\]') 
    
    vault_root = os.getcwd() 

    for line in moc_content.splitlines():
        matches = wikilink_pattern.findall(line)
        for match in matches:
            parts = match.split('|')
            linked_content = parts[0]

            normalized_linked_content = linked_content.replace('/', os.sep).replace('\\', os.sep)

            if os.path.isabs(normalized_linked_content): 
                full_path_abs = os.path.normpath(normalized_linked_content)
            elif normalized_linked_content.startswith(os.sep) or normalized_linked_content.startswith('/'): 
                full_path_abs = os.path.normpath(os.path.join(vault_root, normalized_linked_content[1:])) 
            else: 
                full_path_abs = os.path.normpath(os.path.join(vault_root, normalized_linked_content))
            
            relative_path_no_ext = os.path.relpath(full_path_abs, vault_root)
            if relative_path_no_ext.endswith('.md'):
                relative_path_no_ext = relative_path_no_ext[:-3]

            note_map[linked_content] = relative_path_no_ext
            
    return note_map

# Keywords extracted from input_content
keywords = [
    "emotion", "stress", "coping", "grounding", "habit", "externalize",
    "auditory", "music", "cuddle", "comfort", "self-soothing",
    "AI", "Gemini", "PKM", "workflow", "distraction", "mindfulness",
    "journaling", "breathing", "scenery", "podcasts", "audiobooks",
    "soundscapes", "instrumental", "weighted", "warmth", "butterfly",
    "fluctuating"
]

# Convert keywords to lowercase for case-insensitive matching
lower_keywords = [k.lower() for k in keywords]

# Read the content of Gemini_Index_MOC.md
moc_file_path = "4_Map_of_Content/Gemini_Index_MOC.md"
vault_root = os.getcwd() 
try:
    with open(os.path.join(vault_root, moc_file_path), 'r', encoding='utf-8') as f:
        gemini_index_moc_content = f.read()
except FileNotFoundError:
    print(f"Error: {moc_file_path} not found.")
    sys.exit(1)

# Parse the MOC content
note_map = parse_gemini_index_moc_content(gemini_index_moc_content, moc_file_path)

# Filter relevant files
relevant_rag_file_paths = set()
for wikilink_key, relative_path_no_ext in note_map.items():
    file_path_with_ext = relative_path_no_ext + '.md' # Add .md back for file existence check

    key_match = False
    for keyword in lower_keywords:
        if keyword in wikilink_key.lower():
            key_match = True
            break
    
    path_match = False
    for keyword in lower_keywords:
        if keyword in file_path_with_ext.lower():
            path_match = True
            break

    if key_match or path_match:
        full_absolute_path = os.path.join(vault_root, file_path_with_ext)
        if os.path.exists(full_absolute_path):
            relevant_rag_file_paths.add(file_path_with_ext) # Add the relative path with .md

# Write the relevant file paths to relevant_rag_files.txt
output_file_name = "relevant_rag_files.txt"
try:
    with open(output_file_name, 'w', encoding='utf-8') as outfile:
        for f_path in sorted(list(relevant_rag_file_paths)):
            outfile.write(f"{f_path}\n")
except Exception as e:
    print(f"Error writing to {output_file_name}: {e}")
    sys.exit(1)

print(f"Successfully identified and wrote relevant RAG file paths to {output_file_name}")
