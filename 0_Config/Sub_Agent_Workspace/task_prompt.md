
You are performing a "Safe Integration" of new information into your PKM vault.

### INPUTS
1. **RAG Context:** `rag_context.md`
2. **Input Content:** `input_content.md`

**Action Required:** You MUST use `read_file` to read BOTH files.

### MANDATES (CONTENT)

### PART 1: THE RETRIEVAL & NUANCE MANDATE
*   **Primary Goal:** Record the user's understanding of themselves and the world for future retrieval. Clarity and accuracy are paramount.
*   **Assistant-Speak:** ALLOWED. You may use structural terms (Mechanism, Principle, Context) if they help organize the information efficiently for retrieval.
*   **The Nuance Mandate (CRITICAL):** While general structure can be clinical, you must STRICTLY PRESERVE the user's **unique definitions** and **emotional intensity**.
    *   **Unconventional Definitions:** If the user defines a term differently than the dictionary (e.g., "A Shortcut means a path with zero hurdles; if it feels like a chore, it's not a shortcut"), you MUST keep that specific logic. Tag these insights with `#value/` or `#preference/`.
    *   **Emotional Context:** Do not sanitize strong emotions into clinical reports (e.g., instead of "The user expressed frustration," keep "It feels like a hurdle").
*   **First Person Mandate (CRITICAL):** You MUST write Stream A using the first person ("I"). This is my second brain; it should read like my own inner record of knowledge.
*   **Context Re-Injection (CRITICAL):** You MUST replace vague pronouns ("this", "it", "that") with the specific noun they refer to, ensuring every bullet point stands alone as a complete thought. (e.g., "I hate it" -> "I hate the lock screen toggle").

#### THE 5-DIMENSION TAGGING MANDATE (CRITICAL)
For every insight in Stream A, you MUST classify it into one or more of these 5 dimensions if applicable, applying the specific Tagging pattern:

1.  **VALUE** (Abstract Principles/Ideals): `#value/<concept>` (e.g., `#value/efficiency`).
2.  **PREFERENCE** (Specific Likes/Dislikes): `#preference/<specifics>` (e.g., `#preference/cli-workflow`).
3.  **NEED** (Requirements/Deficits): `#need/<requirement>` (e.g., `#need/low-latency`).
4.  **ACTION** (Intents/Next Steps): `#action/<verb>` (e.g., `#action/refactor`).
5.  **EXPERIENCE** (The Context/Event): `#log/<category>` (e.g., `#log/somatic`).

### PART 1.5: THE LANGUAGE MANDATE (CHINESE INPUT)
*   **Preserve Original Language:** If the user speaks/writes in Chinese, Stream A (User Insights) **MUST** be written in **Chinese** to capture the nuance. Do NOT translate the user's voice into English.
*   **Stream B (Literature):** Can be in English or Chinese, depending on the most appropriate context, but generally defaults to the language of the input or standard English for technical definitions if clearer.

### STRATEGY (CRITICAL)
1.  **Analyze the "Structured Extraction" Section:** Use this section of the input as the primary source for identifying new updates.
2.  **Values, Preferences, and Needs (TAG ONLY):** Do NOT create new atomic notes for these concepts unless the user is explicitly providing a formal definition or philosophical stance. Instead, apply the relevant hierarchical tag (e.g., `#value/efficiency`, `#preference/cli`) to the source synthesis note or the related log note.
3.  **Handle Life Events (#log/):** You do NOT need to create separate log notes for every event. The `#log/` tag within the synthesis note is often sufficient context. ONLY create or update a separate log note in `6_Logs/` if the experience is a significant, recurring theme or if the user explicitly mentions a previous log note by name.
4.  **Atomic Notes:** Create ONLY if the concept is "Totally Different" or a new entity.

### JSON OUTPUT FORMAT (STRICT)
You must output a JSON array of objects.

Types:
1.  `new_note`: { "type": "new_note", "directory": "...", "content": "...", "title": "...", "tags": "..." }
2.  `edit_note`: { "type": "edit_note", "file": "...", "content": "...", "mode": "prepend_to_main"|"append_to_main"|"manual_review" }
3.  `manual_review`: { "type": "manual_review", "affected_files": [...], "content": "..." }
4.  `update_metadata`: { "type": "update_metadata", "file": "...", "add_tags": [...], ... }

**Escape Newlines:** You MUST escape newlines in content strings as `
`.

**Action Required:**
1. Generate the JSON content.
2. Write the RAW JSON to `integration_plan.json`.
