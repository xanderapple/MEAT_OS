import os
import re
import sys

# Define the parse_gemini_index_moc_content function locally for the script
def parse_gemini_index_moc_content(moc_content: str, moc_file_path: str) -> dict:
    note_map = {}
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
            file_path_for_map = relative_path_no_ext + '.md' if not relative_path_no_ext.endswith('.md') else relative_path_no_ext

            # Store both path and the context (the full line containing tags/aliases)
            note_map[linked_content] = {
                'path': file_path_for_map,
                'context': line
            }
            
    return note_map

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Keywords are provided as a comma-separated string in sys.argv[1]
        raw_keywords = sys.argv[1].split(',')
        keywords = [k.strip() for k in raw_keywords if k.strip()]
    else:
        # Fallback to internal keywords if no argument provided
        # This block can be removed if keywords are always expected from CLI
        keywords = [
            "emotion", "emotions", "fluctuating", "irritation", "mistake", "absurd", "calmed", "feelings",
            "coping", "grounding", "habit", "externalize",
            "auditory", "sense", "music", "distraction",
            "cuddle", "comfort", "reassurance", "soothing", "self-soothing", "solitary",
            "stress", "physiological response", "wellness", "mental", "somatic",
            "Human Realm", "Value", "Need", "Motivation", "Philosophy", "Experience", "Personal"
        ]

    # Convert keywords to lowercase for case-insensitive matching
    lower_keywords = [k.lower() for k in keywords]

    # Read the content of Gemini_Index_MOC.md
    # Assuming moc_file_path is always relative to vault_root (os.getcwd())
    moc_file_path = "0_Config/Context/GEMINI_INDEX.md" 
    vault_root = os.getcwd() 
    try:
        with open(os.path.join(vault_root, moc_file_path), 'r', encoding='utf-8') as f:
            gemini_index_moc_content = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: {moc_file_path} not found.\n")
        sys.exit(1)

    # Parse the MOC content
    note_map = parse_gemini_index_moc_content(gemini_index_moc_content, moc_file_path)

    # Filter relevant files
    relevant_rag_file_paths = set()
    for wikilink_key, data in note_map.items():
        file_path_with_ext = data['path']
        context_line = data['context']

        if not file_path_with_ext.endswith('.md'):
            continue 

        # RESTRICTION: Only Literature and Permanent Notes
        if not (file_path_with_ext.startswith('2_Literature_Notes') or file_path_with_ext.startswith('3_Permanent_Notes')):
            continue

        # Target text now includes the full MOC line (with aliases/tags)
        target_text = (wikilink_key + " " + file_path_with_ext + " " + context_line).lower()
        
        match_found = False
        for keyword in lower_keywords:
            if not keyword or len(keyword) < 3:
                continue
                
            # If the keyword has spaces, treat it as an AND search for all words
            if ' ' in keyword:
                words = [w for w in keyword.split() if len(w) > 2]
                if all(word in target_text for word in words):
                    match_found = True
                    break
            # Otherwise, use exact phrase/word match
            elif keyword in target_text:
                match_found = True
                break

        if match_found:
            full_absolute_path = os.path.join(vault_root, file_path_with_ext)
            if os.path.exists(full_absolute_path):
                relevant_rag_file_paths.add(file_path_with_ext) 

    

        # Write the relative paths of the relevant files directly to relevant_rag_files.txt

        output_file_name = "relevant_rag_files.txt"

        relevant_list = sorted(list(relevant_rag_file_paths))

        try:

            with open(output_file_name, 'w', encoding='utf-8') as outfile:

                for f_path in relevant_list:

                    outfile.write(f"{f_path}\n")

        except Exception as e:

            sys.stderr.write(f"Error writing to {output_file_name}: {e}\n")

            sys.exit(1)

    

    sys.stdout.write(f"Successfully identified and wrote {len(relevant_list)} relevant RAG file paths to {output_file_name}\n")

    