from . import mandates

def get_integrate_prompt(rag_context_filename, source_note_filename, input_content_filename, suggested_tags=""):
    """
    Generates the prompt for the Sub-Agent to generate the Safe Integration JSON.
    """
    return f"""
You are performing a "Safe Integration" of new information into your PKM vault.

### INPUTS
1. **RAG Context:** `{rag_context_filename}`
2. **Input Content:** `{input_content_filename}`
3. **Source Reference:** `{source_note_filename}`

**Action Required:** You MUST use `read_file` to read ALL THREE files.

### MANDATES (CONTENT)

{mandates.VOICE_MANDATE}

{mandates.TAGGING_MANDATE}

{mandates.LANGUAGE_MANDATE}

### STRATEGY (CRITICAL)
1.  **Analyze the "Structured Extraction" Section:** Use this section of the input as the primary source for identifying new updates.
2.  **Values, Preferences, and Needs (TAG ONLY):** Do NOT create new atomic notes for these concepts unless the user is explicitly providing a formal definition or philosophical stance. Instead, apply the relevant hierarchical tag (e.g., `#value/efficiency`, `#preference/cli`) to the source synthesis note or the related log note.
3.  **Handle Life Events (#log/):** You do NOT need to create separate log notes for every event. The `#log/` tag within the synthesis note is often sufficient context. ONLY create or update a separate log note in `6_Logs/` if the experience is a significant, recurring theme or if the user explicitly mentions a previous log note by name.
4.  **Atomic Notes:** Create ONLY if the concept is "Totally Different" or a new entity.

### JSON OUTPUT FORMAT (STRICT - DO NOT IGNORE)
You MUST output a VALID JSON ARRAY of objects. 

**CRITICAL STRUCTURAL RULES:**
1.  **ARRAY WRAPPER:** The entire output MUST be wrapped in `[` and `]`.
2.  **SEPARATE OBJECTS:** Each operation (new note, edit note, etc.) MUST be a separate object `{ ... }` within the array, separated by commas. 
3.  **NO MERGING:** Do NOT merge multiple operations into a single object. 
4.  **NO RAW NEWLINES:** All newlines within string values MUST be escaped as `\n`. 
5.  **NO RAW QUOTES:** All double quotes inside content strings MUST be escaped as `\"`.
6.  **VALID JSON ONLY:** The output must be parseable by standard JSON libraries. 

Types:
1.  `new_note`: {{ "type": "new_note", "directory": "...", "content": "...", "title": "...", "tags": "..." }}
2.  `edit_note`: {{ "type": "edit_note", "file": "...", "content": "...", "mode": "prepend_to_main"|"append_to_main"|"manual_review" }}
3.  `manual_review`: {{ "type": "manual_review", "affected_files": [...], "content": "..." }}
4.  `update_metadata`: {{ "type": "update_metadata", "file": "...", "add_tags": [...], ... }}

"""

def get_integrate_critique_prompt(json_filename, source_note_filename):
    return f"""
Audit the Integration JSON Plan against the original source.

### INPUTS
1. **JSON Plan:** `{json_filename}`
2. **Original Source:** `{source_note_filename}`

**Action Required:** Read BOTH files.

### AUDIT CRITERIA
1.  **JSON Syntax (CRITICAL):** Is it valid JSON? Check for raw unescaped newlines inside string values (which is invalid). Ensure all newlines are `\n`.
2.  **Clutter Check:** Are there `new_note` entries for simple definitions that should be tags? (e.g., a note for "Efficiency" when `#value/efficiency` is better).
3.  **Voice Check:** Do the `content` fields use "I" (First Person)?
4.  **Destructive Check:** Are there `edit_note` entries with empty content?

### OUTPUT STRUCTURE

# Integration Critique

## VERDICT: [PASS / FAIL]

## Evidence
*   **Clutter:** [List unnecessary new notes]
*   **Syntax:** [Pass/Fail]
*   **Voice:** [Quote from content field]

## Feedback
(Instructions for refinement)
"""

def get_integrate_refinement_prompt(json_filename, feedback_filename, source_note_filename):
    return f"""
Refine the Integration JSON based on the critique and the original source.

### INPUTS
1. **JSON Draft:** `{json_filename}`
2. **Critique:** `{feedback_filename}`
3. **Original Source:** `{source_note_filename}`

**Action Required:** Rewrite the JSON to fix violations while ensuring all insights from the source are captured.
"""
