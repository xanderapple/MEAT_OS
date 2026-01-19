# rag_cli_utils.py

import re
import os
import datetime
import collections # ADDED THIS LINE

def parse_gemini_index_moc(moc_content: str, moc_file_path: str) -> dict:
    """
    Parses the content of a MOC file to extract a mapping of
    file paths to their metadata (title, tags, aliases, summary).

    Args:
        moc_content: The full content of the MOC file.
        moc_file_path: The path of the MOC file itself, relative to the vault root.

    Returns:
        A dictionary where keys are file paths (relative to vault root, without .md extension)
        and values are dictionaries containing 'title', 'tags', 'aliases', and 'summary_text'.
    """
    note_map = {}
    # Regex to capture: wikilink_path, wikilink_display_text, and then optional metadata string
    # E.g., - [[path|display]] -- Tags: #tag | Aliases: Alias | Summary: Summary text
    wikilink_and_meta_pattern = re.compile(
        r'\[\[(.*?)(?:\|(.*?))?\]\](?: -- (.*))?' # Non-greedy capture for path/display, then optional metadata
    )
    
    moc_base_dir = os.path.dirname(moc_file_path)

    for line in moc_content.splitlines():
        match = wikilink_and_meta_pattern.search(line)
        if match:
            linked_path_raw = match.group(1) # e.g., "1_Fleeting_Notes/Capture/Gemini_Interactions"
            display_text = match.group(2) if match.group(2) else os.path.splitext(os.path.basename(linked_path_raw))[0]
            metadata_str = match.group(3) # e.g., "Tags: #tag | Aliases: Alias | Summary: Summary text"

            # Normalize path separators for consistency
            normalized_linked_path = linked_path_raw.replace('/', os.sep).replace('\\', os.sep)
            resolved_path_no_ext = os.path.splitext(normalized_linked_path)[0]
            
            full_resolved_file_path_with_ext = resolved_path_no_ext + ".md"

            if os.path.exists(full_resolved_file_path_with_ext):
                note_metadata = {
                    'title': display_text,
                    'tags': [],
                    'aliases': [],
                    'summary': ''
                }

                if metadata_str:
                    tags_match = re.search(r'Tags:\s*(.*?)(?: \||$)', metadata_str, re.IGNORECASE)
                    if tags_match:
                        tags_raw = tags_match.group(1).replace('#', '').strip()
                        note_metadata['tags'] = [t.strip() for t in tags_raw.split(',') if t.strip()]

                    aliases_match = re.search(r'Aliases:\s*(.*?)(?: \||$)', metadata_str, re.IGNORECASE)
                    if aliases_match:
                        aliases_raw = aliases_match.group(1).strip()
                        note_metadata['aliases'] = [a.strip() for a in aliases_raw.split(',') if a.strip()]
                    
                    summary_match = re.search(r'Summary:\s*(.*?)(?: \||$)', metadata_str, re.IGNORECASE)
                    if summary_match:
                        note_metadata['summary'] = summary_match.group(1).strip()
                
                note_map[resolved_path_no_ext] = note_metadata # Key by resolved path
            else:
                print(f"Warning: Linked note not found: '{full_resolved_file_path_with_ext}' from MOC '{moc_file_path}'")

    return note_map

def find_relevant_notes(search_topics: list, note_map: dict) -> list:
    """
    Finds relevant notes based on search topics by looking up in the richer note_map.
    Prioritizes notes from specific folders if relevant.

    Args:
        search_topics: A list of keywords or topics to search for.
        note_map: A dictionary where keys are file paths (no .md) and values are
                  dictionaries containing 'title', 'tags', 'aliases', and 'summary'.

    Returns:
        A list of file paths (no .md) of notes deemed relevant and prioritized.
    """
    ranked_relevant_notes = collections.defaultdict(int) # Stores {file_path: score}
    
    # Define high-priority RAG folders
    priority_folders = [
        "2_Literature_Notes/Personal/Preferences/",
        "0_Config/" # Configuration files are also high priority context
    ]

    for topic in search_topics:
        normalized_topic = topic.replace(' ', '_').lower() # Normalize topic for matching
        
        for file_path, metadata in note_map.items():
            score = 0
            # Check against title, tags, aliases, summary
            if normalized_topic in metadata['title'].lower():
                score += 3 # Higher score for title match
            
            for tag in metadata['tags']:
                if normalized_topic in tag.lower():
                    score += 2
            
            for alias in metadata['aliases']:
                if normalized_topic in alias.lower():
                    score += 2
            
            if normalized_topic in metadata['summary'].lower():
                score += 1

            # Check if topic is part of the path
            if normalized_topic in file_path.lower().replace(os.sep, '_'):
                score += 1
            
            # Apply priority boost for specific folders if a match was found
            if score > 0: # Only boost if there's an initial match
                for p_folder in priority_folders:
                    if file_path.startswith(p_folder):
                        score += 10 # Significant boost for priority folders

            if score > 0:
                ranked_relevant_notes[file_path] += score
    
    # Sort notes by score (descending) and then alphabetically by path
    sorted_relevant_notes = sorted(ranked_relevant_notes.items(), key=lambda item: (item[1], item[0]), reverse=True)
    
    # Return just the file paths
    return [file_path for file_path, score in sorted_relevant_notes]





































# Example usage (for testing purposes, remove in final script if not needed)






def extract_markdown_content(markdown_text: str) -> str:
    """
    Extracts the core content from a Markdown string by removing YAML frontmatter.

    Args:
        markdown_text: The full Markdown content, potentially with YAML frontmatter.

    Returns:
        The Markdown content with YAML frontmatter removed.
    """
    frontmatter_match = re.match(r'---\s*\n(.*?)\n---\s*\n(.*)', markdown_text, re.DOTALL)
    if frontmatter_match:
        # Group 1 is frontmatter, Group 2 is content after frontmatter
        return frontmatter_match.group(2).strip()
    return markdown_text.strip() # No frontmatter found, return original content

def extract_metadata_and_first_section(content: str) -> str:
    """
    Extracts the YAML metadata and the first section (Main Body) of the note.
    A 'Section' is defined by the first Header found (e.g. # Title).
    The extraction stops before the NEXT Header of the SAME level.
    If no headers are found, or only one header exists, returns the whole file.
    """
    if not content:
        return ""

    # 1. Identify YAML Frontmatter
    yaml_end_pos = 0
    if content.startswith("---"):
        # Find ending ---
        try:
            # Look for the second --- using regex to ensure it's a standalone line
            # We search from index 3 to skip the first one
            match = re.search(r'^---$', content[3:], re.MULTILINE)
            if match:
                yaml_end_pos = match.end() + 3 
            else:
                pass # Malformed or unclosed YAML
        except:
            pass
    
    # 2. Find the first Header in the remaining content (The Main Body Start)
    body_content_start_index = yaml_end_pos
    body_content = content[body_content_start_index:]
    
    # Regex for headers: ^#{1,6} space
    # Find the FIRST header match
    first_header_match = re.search(r'^(#{1,6})\s', body_content, re.MULTILINE)
    
    if not first_header_match:
        # No headers found. Return the whole file (Metadata + Content).
        return content

    header_level = len(first_header_match.group(1))
    # Position of the first header relative to body_content
    first_header_rel_pos = first_header_match.start()
    
    # 3. Find the NEXT header of the SAME level to determine where to cut
    # We search starting strictly AFTER the start of the first header
    regex_pattern = r'^#{' + str(header_level) + r'}\s'
    
    # Search in the substring following the first header's start
    # We add 1 to skip the initial '#' character of the found header so we don't match it again
    search_start_offset = first_header_rel_pos + 1
    next_header_match = re.search(regex_pattern, body_content[search_start_offset:], re.MULTILINE)
    
    if next_header_match:
        # Found a subsequent section of the same level.
        # The cut point (relative to body_content) is:
        # search_start_offset + match position
        cut_point_rel = search_start_offset + next_header_match.start()
        
        # Calculate absolute cut point
        absolute_cut_point = body_content_start_index + cut_point_rel
        
        return content[:absolute_cut_point].strip()
    else:
        # No subsequent section of the same level found.
        # Return everything (Metadata + First Section/Whole Body).
        return content


if __name__ == "__main__":
    # Simulate moc_content from a file read
    mock_moc_content = """
# Gemini_Index_MOC

## [[3_Map_of_Content/3_Map_of_Content]]
- [[Chemistry_and_Cosmology_MOC]]
- [[Future_Potentials_MOC]]

### [[2_Literature_Notes/Knowledge/Applied_Optics/Applied_Optics]]
- [[Astigmatic_beam]]
- [[Image_Formation]]
- [[Introduction]]
- [[Working_with_Human_Eyes]]
"""
    
    parsed_notes = parse_gemini_index_moc(mock_moc_content, "3_Map_of_Content/Gemini_Index_MOC.md")
    print("Parsed Notes:", parsed_notes)

    search_topics = ["Image_Formation", "Chemistry"]
    found_notes = find_relevant_notes(search_topics, parsed_notes)
    print("Found Notes for topics", search_topics, ":", found_notes)
    
    search_topics_path = ["Applied Optics"] # Simulating a search for folder
    found_notes_path = find_relevant_notes(search_topics_path, parsed_notes)
    print("Found Notes for topics", search_topics_path, ":", found_notes_path)

    print("\n--- Testing extract_markdown_content ---")
    mock_markdown_with_frontmatter = """
---
Topics: []
Tags: synthesis, world_view
Aliases:
Created: 2025-11-20
Source: [[chat_file]], [[synthesis_overview_file]]
---

# My World View
Created at [[November 20th, 2025]] 10:00

## Core Principles
This is a core principle.
Another principle.

## Key Beliefs
A key belief.

---

### ⚠️ Ambiguities and Contradictions
This is an ambiguity.

## References
1. [[chat_file|Original Chat Log]]
2. [[synthesis_overview_file|Synthesis Overview]]

## Related Synthesis Notes
1. [[world_view_file|World View]]

## Original Chat Log
1. [[chat_file|Original Chat]]
"""
    extracted_content = extract_markdown_content(mock_markdown_with_frontmatter)
    print("Extracted Content:")
    print(extracted_content)

    print("\n--- Testing get_yaml_frontmatter ---")
    frontmatter = get_yaml_frontmatter(mock_markdown_with_frontmatter)
    print("Extracted Frontmatter:", frontmatter)
    
    print("\n--- Testing compare_content_for_inconsistency ---")
    new_content_for_compare = """
    This new concept is revolutionary and fundamentally changes our understanding of physics.
    It contradicts the old theory that stated energy is always conserved in all systems.
    """
    existing_content_for_compare = """
    The old theory states that energy is always conserved in all closed systems.
    This is a fundamental principle of physics.
    """
    
    is_inconsistent, report = compare_content_for_inconsistency(
        extract_markdown_content(new_content_for_compare), # Ensure content is cleaned
        extract_markdown_content(existing_content_for_compare), # Ensure content is cleaned
        topics=["physics", "energy conservation"],
        tags=["theory", "conservation"]
    )
    print(f"Comparison 1: Inconsistent: {is_inconsistent}, Report: {report}")

    new_content_for_compare_2 = """
    Energy is always conserved. This aligns with existing beliefs.
    """
    existing_content_for_compare_2 = """
    Energy is always conserved in closed systems.
    """
    is_inconsistent_2, report_2 = compare_content_for_inconsistency(
        extract_markdown_content(new_content_for_compare_2), # Ensure content is cleaned
        extract_markdown_content(existing_content_for_compare_2), # Ensure content is cleaned
        topics=["physics", "energy"],
        tags=["conservation"]
    )
    print(f"Comparison 2: Inconsistent: {is_inconsistent_2}, Report: {report_2}")
    
    print("\n--- Testing update_existing_note ---")
    # Create a mock existing note for testing
    mock_existing_note_path = "mock_existing_note.md"
    mock_existing_note_content = """
---
Topics: [Science]
Tags: theory, physics
Created: 2023-01-01
---

# Theory of Everything
This note discusses the current understanding of the Theory of Everything.
It is a complex topic.

## Latest Update (2024-01-01 10:00) - Source: [[Initial Chat]]
Initial thoughts on the theory.
"""
    with open(mock_existing_note_path, 'w', encoding='utf-8') as f:
        f.write(mock_existing_note_content)

    new_update_content = "Recent advancements suggest a new perspective on quantum gravity."
    source_ref = "[[New Synthesis Overview]]"
    inconsistency_report_mock = "Potential inconsistency: 'quantum gravity' is now central."

    print(f"Updating {mock_existing_note_path} with new content...")
    update_existing_note(mock_existing_note_path, new_update_content, source_ref, inconsistency_report_mock)

    with open(mock_existing_note_path, 'r', encoding='utf-8') as f:
        updated_note_content = f.read()
    print("\n--- Updated mock_existing_note.md content ---")
    print(updated_note_content)
    
    # Clean up mock file
    os.remove(mock_existing_note_path)

    # Test with a note that has no existing update sections
    mock_existing_note_path_2 = "mock_existing_note_2.md"
    mock_existing_note_content_2 = """
---
Topics: [Philosophy]
Tags: concept
Created: 2023-02-01
---

# Concept of Being
A fundamental philosophical concept.
"""
    with open(mock_existing_note_path_2, 'w', encoding='utf-8') as f:
        f.write(mock_existing_note_content_2)
    
    new_update_content_2 = "New insights into the nature of existence."
    source_ref_2 = "[[Philosophy Synthesis]]"
    
    print(f"\nUpdating {mock_existing_note_path_2} with new content (no existing update sections)...")
    update_existing_note(mock_existing_note_path_2, new_update_content_2, source_ref_2)
    
    with open(mock_existing_note_path_2, 'r', encoding='utf-8') as f:
        updated_note_content_2 = f.read()
    print("\n--- Updated mock_existing_note_2.md content ---")
    print(updated_note_content_2)
    
    # Clean up mock file
    os.remove(mock_existing_note_path_2)

    print("\n--- Testing save_synthesis_note ---")
    mock_world_view_content = """
---
Topics: []
Tags: synthesis, world_view
Aliases:
Created: 2025-11-20
Source: [[chat_file]], [[synthesis_overview_file]]
---

# Test World View Synthesis
Created at [[November 20th, 2025]] 10:00

## Core Principles
This is a test core principle.

## Key Beliefs
A test key belief.
"""
    base_save_dir = "2_Literature_Notes/Experience/Chat_Synthesis"
    
    saved_path = save_synthesis_note(mock_world_view_content, "World_View", base_save_dir)
    print(f"Saved World View note path: {saved_path}")

    # Clean up mock file and directory
    if saved_path and os.path.exists(saved_path):
        os.remove(saved_path)
        # Attempt to remove the directory if it's empty
        try:
            os.rmdir(os.path.dirname(saved_path))
        except OSError:
            pass # Directory not empty, ignore
    
    # Test for Human Realm
    mock_human_realm_content = """
---
Topics: []
Tags: synthesis, human_realm
Aliases:
Created: 2025-11-20
Source: [[chat_file_hr]], [[synthesis_overview_file_hr]]
---

# Test Human Realm Analysis
Created at [[November 20th, 2025]] 10:00

## Societal Structures
Test societal structures.

## Cultural Norms
Test cultural norms.
"""
    saved_path_hr = save_synthesis_note(mock_human_realm_content, "Human_Realm", base_save_dir)
    print(f"Saved Human Realm note path: {saved_path_hr}")

    if saved_path_hr and os.path.exists(saved_path_hr):
        os.remove(saved_path_hr)
        try:
            os.rmdir(os.path.dirname(saved_path_hr))
        except OSError:
            pass

    # Test for Value Challenge
    mock_value_challenge_content = """
---
Topics: []
Tags: synthesis, value_challenge
Aliases:
Created: 2025-11-20
Source: [[chat_file_vc]], [[synthesis_overview_file_vc]]
---

# Test Value Challenge Dilemma
Created at [[November 20th, 2025]] 10:00

## Core Values in Conflict
Test core values in conflict.

## Ethical Dilemmas
Test ethical dilemmas.
"""
    saved_path_vc = save_synthesis_note(mock_value_challenge_content, "Value_Challenge", base_save_dir)
    print(f"Saved Value Challenge note path: {saved_path_vc}")

    if saved_path_vc and os.path.exists(saved_path_vc):
        os.remove(saved_path_vc)
        try:
            os.rmdir(os.path.dirname(saved_path_vc))
        except OSError:
            pass
    
    print("\n--- Testing fill_template_with_args ---")
    mock_template = """
<%*
	ttitle = tp.file.title
	if (title.startsWith("Untitled")) {
		title = await tp.system.prompt("Title of Synthesis Overview");
		await tp.file.rename(`${title}`);
		}
	R += "---"
%>
Topics: [{topics_list}]
Tags: synthesis, overview, {tags_list}
Aliases:
Created: <% tp.file.creation_date("YYYY-MM-DD") %>
Original Chat File: [[<% tp.file.arg("chat_file") %>]]
World View: [[<% tp.file.arg("world_view_file") %>]]
Human Realm: [[<% tp.file.arg("human_realm_file") %>]]
Value Challenge: [[<% tp.file.arg("value_challenge_file") %>]]
Implementation Plan: [[<% tp.file.arg("implementation_plan_file") %>]]
---

# <%* tR += `${title}` %>
Created at [[<% tp.file.creation_date("MMMM Do, YYYY") %>]] <% tp.file.creation_date("HH:mm") %>

## Summary of Synthesis
<!-- Provide a concise summary of the entire synthesis process and its findings. -->

## Key Takeaways
<!-- List the most important insights and conclusions drawn from the synthesis. -->
"""
    mock_args = {
        "title": "My Test Synthesis Overview",
        "chat_file": "1_Fleeting_Notes/Capture/Chat_Logs/my_chat.md",
        "world_view_file": "2_Literature_Notes/Experience/Chat_Synthesis/World_View/My_World_View.md",
        "human_realm_file": "2_Literature_Notes/Experience/Chat_Synthesis/Human_Realm/My_Human_Realm.md",
        "value_challenge_file": "2_Literature_Notes/Experience/Chat_Synthesis/Value_Challenge/My_Value_Challenge.md",
        "implementation_plan_file": "2_Literature_Notes/Personal/Action/RAG_Tasks/My_Implementation_Plan.md",
        "topics_list": "Topic1, Topic2",
        "tags_list": "tag1, tag2"
    }

    filled_mock_template = fill_template_with_args(mock_template, mock_args)
    print("\n--- Filled Template Content ---")
    print(filled_mock_template)
    
    mock_human_realm_template_content = """
<%*
	ttitle = tp.file.title
	if (title.startsWith("Untitled")) {
		title = await tp.system.prompt("Title of Human Realm Synthesis");
		await tp.file.rename(`${title}`);
		}
	R += "---"
%>
Topics: []
Tags: synthesis, human_realm
Aliases:
Created: <% tp.file.creation_date("YYYY-MM-DD") %>
Source: [[<% tp.file.arg("chat_file") %>]], [[<% tp.file.arg("synthesis_overview_file") %>]]
---

# <%* tR += `${title}` %>
Created at [[<% tp.file.creation_date("MMMM Do, YYYY") %>]] <% tp.file.creation_date("HH:mm") %>

## Societal Structures
<!-- Analyze the relevant societal structures and systems. -->

## Cultural Norms
<!-- Explore the cultural norms, values, and traditions at play. -->

## Psychological Aspects
<!-- Delve into the psychological factors and human behaviors involved. -->

## Individual & Collective Impact
<!-- Discuss the impact on individuals and the collective human experience. -->

---
### ⚠️ Ambiguities and Contradictions
<!-- Report any identified ambiguities or contradictions (between chat, retrieved context, internal synthesis, or during note updates) here. -->

---
## References
1. [[<% tp.file.arg("chat_file") %>|Original Chat Log]]
2. [[<% tp.file.arg("synthesis_overview_file") %>|Synthesis Overview]]
"""
    
    mock_human_realm_args = {
        "title": "Impact of AI on Society",
        "chat_file": "1_Fleeting_Notes/Capture/Chat_Logs/ai_ethics_chat.md",
        "synthesis_overview_file": "2_Literature_Notes/Experience/Chat_Synthesis/Synthesis_Overview/AI_Ethics_Overview.md"
    }

    filled_human_realm_template = fill_template_with_args(mock_human_realm_template_content, mock_human_realm_args)
    print("\n--- Filled Human Realm Template Content ---")
    print(filled_human_realm_template)
