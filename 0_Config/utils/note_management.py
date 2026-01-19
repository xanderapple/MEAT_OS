import re
import os
import datetime

def create_structured_note(file_path: str, title: str, content: str, topics: list = None, tags: list = None, aliases: list = None):
    """
    Creates a new Markdown note with standard YAML frontmatter.
    """
    # Ensure the directory exists
    dir_name = os.path.dirname(file_path)
    os.makedirs(dir_name, exist_ok=True)

    # Prepare YAML fields
    yaml_topics = f"[{', '.join(topics)}]" if topics else "[]"
    yaml_tags = f"[{', '.join(tags)}]" if tags else "[]"
    yaml_aliases = f"[{', '.join(aliases)}]" if aliases else "[]"
    created_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construct YAML frontmatter
    frontmatter = f"""
---
Topics: {yaml_topics}
Tags: {yaml_tags}
Aliases: {yaml_aliases}
Created: {created_date}
---

# {title}
Created at [[{datetime.datetime.now().strftime("%B %dth, %Y")}]] {datetime.datetime.now().strftime("%H:%M")}

{content}
"""

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        print(f"Successfully created structured note: {file_path}")
        return True
    except Exception as e:
        print(f"Error creating structured note: {e}")
        return False

def extract_markdown_content(markdown_content: str, ignore_update_sections: bool = False) -> str:
    """
    Extracts the main content from a Markdown string, excluding YAML frontmatter,
    and specific sections like "References" or "Ambiguities and Contradictions".
    """
    lines = markdown_content.splitlines()
    cleaned_lines = []
    in_frontmatter = False
    frontmatter_delimiter_count = 0
    
    # First pass: remove YAML frontmatter and horizontal rules
    temp_lines = []
    for line in lines:
        if line.strip() == "---":
            frontmatter_delimiter_count += 1
            if frontmatter_delimiter_count == 1:
                in_frontmatter = True
                continue
            elif frontmatter_delimiter_count == 2 and in_frontmatter:
                in_frontmatter = False
                continue
            elif not in_frontmatter: # It's a horizontal rule, skip it
                continue
        
        if not in_frontmatter:
            temp_lines.append(line)
            
    # Second pass: remove specific sections
    final_content_lines = []
    ignoring = False
    for line in temp_lines:
        lower_line = line.strip().lower()

        if lower_line.startswith("## references") or \
           lower_line.startswith("### ⚠️ ambiguities and contradictions") or \
           lower_line.startswith("## related synthesis notes") or \
           lower_line.startswith("## original chat log") or \
           (ignore_update_sections and lower_line.startswith("## latest update")) or \
           (ignore_update_sections and lower_line.startswith("## update history")):
            ignoring = True
            continue
        
        # If we are currently ignoring and encounter a new main header, stop ignoring
        # This assumes sections to be ignored are always at the end or have distinct headers.
        if ignoring and (lower_line.startswith("# ") or lower_line.startswith("## ") or lower_line.startswith("### ")):
            # This is a new header, so we stop ignoring the previous section
            ignoring = False
            
        if not ignoring:
            if line.strip(): # Only add non-empty lines
                final_content_lines.append(line)
        
    return "\n".join(final_content_lines).strip()

def get_yaml_frontmatter(markdown_content: str) -> dict:
    """
    Extracts YAML frontmatter from Markdown content.
    """
    lines = markdown_content.splitlines()
    frontmatter_lines = []
    in_frontmatter = False
    frontmatter_delimiter_count = 0

    for line in lines:
        if line.strip() == "---":
            frontmatter_delimiter_count += 1
            if frontmatter_delimiter_count == 1:
                in_frontmatter = True
                continue
            elif frontmatter_delimiter_count == 2 and in_frontmatter:
                in_frontmatter = False
                break
        
        if in_frontmatter:
            frontmatter_lines.append(line)
            
    if frontmatter_lines:
        try:
            # We will need a YAML parser. Since we cannot install libraries,
            # we will assume a simple key-value parsing for now.
            # A more robust solution would require a YAML library.
            frontmatter = {}
            for fm_line in frontmatter_lines:
                if ":" in fm_line:
                    key, value = fm_line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
            return frontmatter
        except Exception as e:
            print(f"Warning: Could not parse YAML frontmatter: {e}")
            return {}
    return {}

def compare_content_for_inconsistency(new_content: str, existing_content: str, topics: list, tags: list) -> (bool, str):
    """
    Compares new content with existing content for potential factual inconsistencies
    based on keywords and direct phrases.
    """
    inconsistency_found = False
    report_message = []

    # 1. Direct Phrase Matching (simple for now)
    # This is a very rudimentary check. A real implementation would involve sentence tokenization.
    new_sentences = [s.strip() for s in re.split(r'[.!?]', new_content) if s.strip()]
    existing_sentences = [s.strip() for s in re.split(r'[.!?]', existing_content) if s.strip()]

    # Check if any significant phrase from new content is explicitly contradicted in existing content
    # For a simple implementation, we can look for negation keywords around shared terms.
    # This is a heuristic and will have false positives/negatives.
    
    # Let's use topics and tags as keywords to watch for
    keywords_to_watch = list(set(topics + tags))
    
    for keyword in keywords_to_watch:
        if keyword.lower() in new_content.lower() and keyword.lower() in existing_content.lower():
            # Very basic check: look for negation words nearby
            negation_words = ["not", "no", "never", "contradict", "disagree"]
            
            new_context = re.findall(r'\b(?:\w+\W+){0,3}' + re.escape(keyword) + r'(?:\W+\w+){0,3}\b', new_content, re.IGNORECASE)
            existing_context = re.findall(r'\b(?:\w+\W+){0,3}' + re.escape(keyword) + r'(?:\W+\w+){0,3}\b', existing_content, re.IGNORECASE)
            
            new_has_negation = any(neg_word in c.lower() for c in new_context for neg_word in negation_words)
            existing_has_negation = any(neg_word in c.lower() for c in existing_context for neg_word in negation_words)

            if new_has_negation != existing_has_negation:
                inconsistency_found = True
                report_message.append(
                    f"Potential inconsistency around keyword '{keyword}': "
                    f"New content context suggests {{'negation' if new_has_negation else 'affirmation'}}, "
                    f"while existing content suggests {{'negation' if existing_has_negation else 'affirmation'}}."
                )
    
    # 2. Check for explicit contradiction phrases within the new content
    explicit_contradiction_patterns = [
        r"this contradicts", r"contrary to", r"however, old information states",
        r"this differs from", r"discrepancy with"
    ]
    
    for pattern in explicit_contradiction_patterns:
        if re.search(pattern, new_content, re.IGNORECASE):
            inconsistency_found = True
            report_message.append(f"New content contains explicit contradiction phrase: '{pattern}'.")

    return inconsistency_found, "\n".join(report_message) if report_message else "No explicit inconsistencies detected."

def update_existing_note(existing_note_path: str, new_content: str, source_reference: str, inconsistency_report: str = None) -> None:
    """
    Appends new information to an existing note in a "Latest Update" section,
    moving old main content into an "Update History" section.
    """
    try:
        with open(existing_note_path, 'r', encoding='utf-8') as f:
            full_existing_content = f.read()
    except FileNotFoundError:
        print(f"Error: Existing note not found at {existing_note_path}")
        return

    # Extract frontmatter and main content
    frontmatter = get_yaml_frontmatter(full_existing_content)
    main_content_before_update = extract_markdown_content(full_existing_content, ignore_update_sections=True)
    
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Construct the "Latest Update" section
    latest_update_section = f"""
## Latest Update ({current_timestamp}) - Source: {source_reference}
{new_content}
"""

    # Add inconsistency report if provided
    if inconsistency_report and inconsistency_report != "No explicit inconsistencies detected.":
        latest_update_section += f"\n### ⚠️ Potential Inconsistencies with Existing Content\n{inconsistency_report}\n"

    # Construct or update the "Update History" section
    # Need to check if Update History already exists
    # Use raw string for regex pattern to avoid invalid escape sequence warning
    update_history_pattern = re.compile(r'## Update History.*', re.DOTALL | re.IGNORECASE)
    update_history_match = update_history_pattern.search(full_existing_content)

    new_update_history_entry = f"""
### Update Entry ({current_timestamp}) - Source: {source_reference}
{main_content_before_update.strip()}
"""

    if update_history_match:
        # Prepend new entry to existing Update History
        # Find where to insert the new entry: directly after the "## Update History" header
        history_start_idx = update_history_match.start()
        
        # Get the content before the Update History section
        content_before_history = full_existing_content[:history_start_idx]
        
        # Get the Update History section itself
        existing_history_section = full_existing_content[history_start_idx:]
        
        # Insert the new entry
        updated_history_section = existing_history_section.replace("## Update History", f"## Update History\n{new_update_history_entry}", 1)
        
        # The content without old history is the part before the history section
        content_without_old_history = content_before_history
        
    else:
        # Create new Update History section
        updated_history_section = f"""
## Update History
{new_update_history_entry}
"""
        content_without_old_history = full_existing_content

    # Reassemble the note
    # Remove old "Latest Update" section if it exists, before adding the new one.
    # This also means we need to remove the old Latest Update from content_without_old_history
    # Use raw string for regex pattern to avoid invalid escape sequence warning
    latest_update_pattern = re.compile(r'## Latest Update.*?(?=## Update History|\Z)', re.DOTALL | re.IGNORECASE)
    # Lookahead ensures it stops before Update History or end of string

    # Find and remove the old Latest Update section from content_without_old_history
    content_without_latest_update = latest_update_pattern.sub("", content_without_old_history)
    
    # Reconstruct YAML frontmatter string
    frontmatter_str = "---" + "\n" + "\n".join([f"{k}: {v}" for k, v in frontmatter.items()]) + "\n---" + "\n\n"

    # Assemble the final content
    # Ensure there's a clean break before adding new sections
    # Strip any extra newlines that might have accumulated before appending
    final_content = f"{frontmatter_str}{extract_markdown_content(content_without_latest_update.strip())}\n{latest_update_section}\n{updated_history_section}"

    with open(existing_note_path, 'w', encoding='utf-8') as f:
        f.write(final_content)


def save_synthesis_note(topic_slug: str, note_type: str, note_content: str, base_directory: str = "2_Literature_Notes/Experience/Chat_Synthesis") -> str:
    """
    Saves a synthesis note to the specified base directory.
    Uses topic_slug and note_type for consistent naming, robust to missing titles.

    Args:
        topic_slug: The topic slug derived from the chat title (e.g. "RAG_Workflow").
        note_type: The type of synthesis note (e.g., "World View", "Human Realm").
        note_content: The full Markdown content of the synthesis note.
        base_directory: The base path where the note should be saved.

    Returns:
        The full path to the saved note, or None if saving failed.
    """
    
    # Normalize note_type for directory name
    type_dir = note_type.replace('_', ' ').title() # e.g., "World View"
    
    # Sanitize inputs
    safe_slug = re.sub(r'[^\w\-_\. ]', '', topic_slug).replace(' ', '_')
    safe_type = re.sub(r'[^\w\-_\. ]', '', note_type).replace(' ', '_')
    
    # Construct filename: Type-Date-Topic.md
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    filename = f"{safe_type}-{current_date}-{safe_slug}.md"
    
    # Determine the full directory path (create if it doesn't exist)
    full_dir_path = os.path.join(base_directory, type_dir) 
    os.makedirs(full_dir_path, exist_ok=True)

    file_path = os.path.join(full_dir_path, filename)
    
    # Check if content has a title. If not, prepend one.
    if not re.search(r'^#\s', note_content, re.MULTILINE):
         title_display = topic_slug.replace('_', ' ')
         note_content = f"# {note_type}: {title_display}\n\n{note_content}"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        print(f"Successfully saved synthesis note to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving synthesis note {file_path}: {e}")
        return None


def create_synthesis_overview_note(
    topic_slug: str,
    synthesis_notes: dict,
    base_directory: str = "2_Literature_Notes/Experience/Chat_Synthesis"
) -> str:
    """
    Generates and saves a Synthesis Overview note based on a template, linking to related synthesis outputs.

    Args:
        topic_slug: The slug/title of the topic.
        synthesis_notes: Dictionary mapping note types (keys) to file paths (values).
        base_directory: The base path where the note should be saved.

    Returns:
        The full path to the saved overview note, or None if saving failed.
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_datetime_full = datetime.datetime.now().strftime("%B %d, %Y %H:%M")

    # Sanitize title for filename usage
    safe_slug = re.sub(r'[^\w\-_\. ]', '', topic_slug).replace(' ', '_')
    overview_title = f"Synthesis Overview: {topic_slug.replace('_', ' ')}"

    # Helper to get path or empty string
    def get_link(key):
        return f"[[{synthesis_notes.get(key, '')}]]" if key in synthesis_notes else ""

    overview_content = f"""
---
Topics: []
Tags: synthesis, overview
Aliases:
Created: {current_date}
---

# {overview_title}
Created at [[{current_datetime_full}]]

## Summary
<!-- Provide a concise summary of the entire synthesis process and its findings. -->

## Synthesis Modules
*   **World View:** {get_link("World View")}
*   **Human Realm:** {get_link("Human Realm")}
*   **Value Challenge:** {get_link("Value Challenge")}
*   **Implementation Plan:** {get_link("Implementation Plan")}

---
## Key Insights
<!-- List the most important insights and conclusions drawn from the synthesis. -->

"""

    # Determine the full directory path (create if it doesn't exist)
    full_dir_path = os.path.join(base_directory, "Synthesis_Overview") 
    os.makedirs(full_dir_path, exist_ok=True)

    file_path = os.path.join(full_dir_path, f"{safe_slug}_Overview.md")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(overview_content)
        print(f"Successfully saved Synthesis Overview note to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving Synthesis Overview note {file_path}: {e}")
        return None

def update_chat_status(chat_file_path: str, status: str) -> bool:
    """
    Updates the 'status' field in the YAML frontmatter of a Markdown file.
    """
    try:
        with open(chat_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {chat_file_path}")
        return False

    frontmatter_start = -1
    frontmatter_end = -1
    in_frontmatter = False
    
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                frontmatter_start = i
                in_frontmatter = True
            else:
                frontmatter_end = i
                break
    
    if frontmatter_start == -1 or frontmatter_end == -1:
        print(f"Warning: No valid YAML frontmatter found in {chat_file_path}. Appending status.")
        # If no frontmatter, append a new one
        new_frontmatter = ["---\n", f"status: {status}\n", "---\n"]
        with open(chat_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_frontmatter + lines)
        return True

    # Check if 'status' key already exists
    status_found = False
    for i in range(frontmatter_start + 1, frontmatter_end):
        if lines[i].strip().startswith("status:"):
            lines[i] = f"status: {status}\n"
            status_found = True
            break
    
    if not status_found:
        # Insert 'status' key before the end of frontmatter
        lines.insert(frontmatter_end, f"status: {status}\n")

    try:
        with open(chat_file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Successfully updated status in {chat_file_path} to '{status}'.")
        return True
    except Exception as e:
        print(f"Error updating status in {chat_file_path}: {e}")
        return False