from . import mandates

def get_final_prompt(preliminary_filename, rag_context_filename, output_filename):
    """
    Generates the prompt for the Sub-Agent to generate the Final Permanent Synthesis Note.
    """
    return f"""
You are creating a **Permanent Synthesis Note**. This is the final, authoritative record of the user's intellectual event.

### INPUTS
1. **Preliminary Synthesis:** `{preliminary_filename}`
2. **RAG Context:** `{rag_context_filename}`

**Action Required:** You MUST use `read_file` to read BOTH files.

### MANDATES (CRITICAL)

{mandates.HIGH_FIDELITY_MANDATE}

{mandates.VOICE_MANDATE}

{mandates.TAGGING_MANDATE}

{mandates.LANGUAGE_MANDATE}

### PART 2: STRUCTURAL INTEGRITY
You MUST strictly adhere to the standards defined in `0_Config/STRUCTURE_DEFINITIONS.md`.
*   **Title:** Must be descriptive and capitalized.
*   **YAML:** Must include `tags`, `aliases`, `created`.

### PART 3: OUTPUT STRUCTURE (STRICT MARKDOWN)
Compose the final note with the following structure:

1.  **YAML Frontmatter:** title, created, tags (#type/literature-note, #source/synthesis), aliases.
2.  **# <Title>**
3.  **The Narrative (Stream A - Refined):** A flowing, human-readable narrative in the **First Person ("I")**, enriched with `[[Wikilinks]]` and hierarchical tags.
4.  **Structured Extraction (The "ME" Core):**
    *   Direct, bulleted extractions of: **Key Facts & Beliefs**, **Personal Observations & Logic**, and **Core Motivation & Vibe**.
    *   **MANDATORY:** Include `[[Internal Links]]` to relevant notes here.
    *   **STRICTLY FLAT:** Do NOT use sub-headers (e.g., `###`) within these bulleted extractions.
5.  **Literature & External Context (Stream B - Refined):** External AI insights, clearly marked.
6.  **Contradiction Analysis (if applicable):** dedicated section for clashes with the RAG context.
7.  **References:**
    *   List the files from the RAG context that were most relevant.

**Action Required:**
1. Generate the content.
2. Write the result to `{output_filename}`.
"""

def get_final_critique_prompt(draft_filename, output_filename):
    return f"""
Your task is to audit a **Final Permanent Synthesis Note**.

### INPUT
**Draft Note:** `{draft_filename}`

**Action Required:** Read the file.

### AUDIT CRITERIA

1.  **Voice Check:** Does the "Narrative" section use "I" (First Person)? If "The User", FAIL.
2.  **Tagging Check:** Are there `#value/`, `#preference/`, etc. tags?
3.  **Structure Check:**
    *   Is there valid YAML frontmatter?
    *   Is the "Structured Extraction" section FLAT (no sub-headers)?
4.  **Link Check:** Are there `[[Wikilinks]]` to other notes?

### OUTPUT STRUCTURE

# Final Note Critique

## VERDICT: [PASS / FAIL]

## Evidence
*   **Voice:** [Quote]
*   **Tags:** [List found tags or "None"]
*   **Structure:** [Pass/Fail]

## Feedback
(Instructions for refinement)

**Action Required:** Write report to `{output_filename}`.
"""

def get_final_refinement_prompt(draft_filename, feedback_filename, output_filename):
    return f"""
Refine the Final Synthesis Note based on the critique.

### INPUTS
1. **Draft:** `{draft_filename}`
2. **Critique:** `{feedback_filename}`

**Action Required:** Rewrite the note to fix the violations. Output to `{output_filename}`.
"""

def get_keyword_extraction_prompt(content_filename, output_filename):
    return f"""
Extract search keywords from the provided content for RAG retrieval.

### INPUT
**Content:** `{content_filename}`

**Action Required:**
1. Read the file.
2. Identify the core topics, technical terms, and entities.
3. Output a **Comma-Separated List** of keywords (e.g., "Knowledge Graph, Python, Obsidian, API").
4. Write ONLY the keywords to `{output_filename}`.
"""
