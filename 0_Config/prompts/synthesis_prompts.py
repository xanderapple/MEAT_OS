def get_preliminary_prompt(source_filename, output_filename):
    """
    Generates the prompt for the Sub-Agent to perform preliminary synthesis.
    
    Args:
        source_filename (str): The name of the file containing source content (relative to workspace).
        output_filename (str): The name of the file to write the output to (relative to workspace).
    """
    return f"""
Your task is to generate a comprehensive, multi-perspective preliminary synthesis that captures the raw intellectual energy of the provided input while maintaining strict structural rigor. You must prioritize the user's literal voice and clearly separate their affirmed insights from unconfirmed LLM context.

### INPUT SOURCE
The input content is located in the file: `{source_filename}`
**Action Required:** You MUST use the `read_file` tool to read the contents of this file before proceeding.

### THE HIGH-FIDELITY MANDATE (CRITICAL - DO NOT SUMMARIZE)
*   **Zero-Summary Mode:** For high-density or "precious" chats, you MUST NOT collapse information. If the user provides 10 technical specs, you extract 10 technical specs. If the user uses 5 metaphors, you capture 5 metaphors.
*   **Volume Scaling:** The length of your extraction should scale with the volume of the input. Do NOT try to fit a massive log into a standard-length bulleted list.
*   **Preserve Connectivity:** Capture how ideas link together (e.g., "Basement as Motherboard" leads to "Surface as UI").

### PART 1: THE RETRIEVAL & NUANCE MANDATE
*   **Primary Goal:** Record the user's understanding of themselves and the world for future retrieval. Clarity and accuracy are paramount.
*   **Assistant-Speak:** ALLOWED. You may use structural terms (Mechanism, Principle, Context) if they help organize the information efficiently for retrieval.
*   **The Nuance Mandate (CRITICAL):** While general structure can be clinical, you must STRICTLY PRESERVE the user's **unique definitions** and **emotional intensity**.
    *   **Unconventional Definitions:** If the user defines a term differently than the dictionary (e.g., "A Shortcut means a path with zero hurdles; if it feels like a chore, it's not a shortcut"), you MUST keep that specific logic. Tag these insights with `#value/` or `#preference/`.
    *   **Emotional Context:** Do not sanitize strong emotions into clinical reports (e.g., instead of "The user expressed frustration," keep "It feels like a hurdle").
*   **Direct Perspective:** Write Stream A as if it is the user's own knowledge base or inner monologue. Use "I" or direct statements.

### PART 1.5: THE LANGUAGE & IDIOM MANDATE
*   **Preserve Original Language:** If the user speaks/writes in Chinese, Stream A (User Insights) **MUST** be written in **Chinese**.
*   **Mixed Language Preservation (CRITICAL):** If the user mixes languages (e.g., English sentences with Chinese phrases), you **MUST PRESERVE** the specific non-English terms/phrases.
    *   **Do NOT translate** specific idioms or "spirit" phrases into English placeholders.
    *   *Good:* "I maintain a '不说破，但我看好你' silent agreement."
    *   *Bad:* "I maintain a 'tacit understanding' silent agreement."
*   **Stream B (Literature):** Can be in English or Chinese, depending on the most appropriate context.

### PART 2: INPUT PROCESSING & AFFIRMATION RIGOR
Before synthesizing, you must interpret the input using these strict rules:

1.  **Noise Filtering (UI Exclusion - CRITICAL):** You MUST identify and ignore all content that appears to be part of a User Interface (UI), navigation sidebar, chat list, or menu. This includes lists of previous chat titles, "New Chat" buttons, profile settings, and header/footer navigation. Focus EXCLUSIVELY on the active conversation or core text body provided.
2.  **Request Interpretation & Input Extraction (The "ME" Stream):**
    *   **Prioritize Your Wording in Chat History (with Inference):** If the input appears to be a chat history, you will first attempt to infer speaker turns based on contextual and stylistic cues (e.g., casualness, use of markdown, capitalization patterns, length of turns). Your primary goal is to extract and prioritize the User's presumed contributions *using their original wording*.
    *   **Affirmed AI Content in Chat History:** For such inferred chat histories, you will include content from the AI's presumed turns ONLY if the user's subsequent presumed messages explicitly affirm, refer to, or build upon that specific AI content. Use clear textual markers (e.g., "User: Yes, that point about X is correct," or "User: Regarding your idea Y...") to identify such affirmations.
    *   **General Delimitation for Ambiguous/Mixed Inputs:** If speaker turns cannot be reliably inferred, only the clearly identifiable direct user wording will be prioritized as "user language" for initial interpretation.
2.  **Bias Exclusion (Clean Start):** This synthesis must rely EXCLUSIVELY on the provided input. You MUST flush your working memory of the current conversation's history and previous turn topics.

### PART 3: SYNTHESIS EXTRACTION - TWO STREAMS
Once the input is processed/filtered, extract information into two distinct streams:

#### STREAM A: User-Validated Insights (The "ME" Stream)
This captures insights, facts, observations, and motivations directly attributable to or explicitly affirmed by the user.

*   **Key Facts & Claims:** Literal extraction of core statements, claims, or factual information the user has made or explicitly agreed with.
*   **Personal Observations & Logic:** Document the user's personal observations, interpretations, or reasoning (e.g., specific metaphors, technical specs, system logic).
*   **Core Motivation & Vibe:** Identify and articulate the user's implicit or explicit motivations, values, or goals (The "Why").
*   **Non-Prescriptive Mandate:** Capture ONLY what the user *has done*, *is doing*, or *explicitly plans to do* (e.g., "I will try X"). Do NOT convert observations into imperative advice or "suggested actions" (e.g., "You should do X") unless the user explicitly framed it as a directive to themselves.

#### STREAM B: Unaffirmed LLM Information (The "LITERATURE" Stream)
This captures information generated by the LLM (me) that was part of the conversation but was NOT explicitly affirmed, validated, or built upon by the user. 

*   **Unconfirmed LLM Insights:** Potentially useful points or analyses made by the LLM that the user did not explicitly validate.
*   **External Context Provided by LLM:** Background, definitions, or tangential information introduced by the LLM.

### PART 4: SELF-CRITIQUE (INTERNAL TURN)
Before final output, perform a brief internal check:
1.  **Summarization Check:** Did I collapse any distinct technical specs or metaphors into a single bullet point? (If yes, expand).
2.  **Voice Check:** Did I use any banned "Assistant-Speak" words (Mechanism, Utilizes, etc.)? (If yes, replace with User's metaphor).
3.  **Leak Check:** Did I include any info from the conversation history that ISN'T in the provided input block? (If yes, remove).

### PART 5: OUTPUT STRUCTURE (STRICT MARKDOWN)
Output the synthesis using this exact Markdown structure:

# Preliminary Synthesis

## STREAM A: User-Validated Insights (The "ME" Stream)

### Key Facts & Claims
(Your literal extraction of user's key points. Keep the tone raw and direct.)

### Personal Observations & Logic
(How the user sees the problem; their specific reasoning/metaphors/specs.)

### Core Motivation & Vibe
(The "Why" behind the user's actions/preferences.)

## STREAM B: Unaffirmed LLM Information (The "LITERATURE" Stream)

### Unconfirmed LLM Insights
(Summary of LLM insights not affirmed by user.)

### External Context Provided by LLM
(Summary of external context provided by LLM not affirmed by user.)

**Action Required:**
1. Generate the content as described.
2. Write the result to the file: `{output_filename}`
"""

def get_final_stage1_prompt(preliminary_content, preliminary_file):
    return f"""
Extract the core concepts from this preliminary synthesis for RAG retrieval. Use the user's specific terminology.

---START_PRELIMINARY_SYNTHESIS---
{preliminary_content}
---END_PRELIMINARY_SYNTHESIS---

**Action Required:** Provide comma-separated keywords. Then call `synthesis final "{preliminary_file}" --keywords "<your_keywords>"` to continue.
"""

def get_final_stage2_prompt(preliminary_content, rag_context_path, source_path):
    return f"""
You are creating a **Permanent Synthesis Note**. This is the final, authoritative record of the user's intellectual event.

### MANDATE: STRUCTURAL INTEGRITY (CRITICAL)
You MUST strictly adhere to the standards defined in `0_Config/STRUCTURE_DEFINITIONS.md` for naming, metadata keys, and note structure.

### THE HIGH-FIDELITY MANDATE (CRITICAL - DO NOT SUMMARIZE)
*   **Zero-Summary Mode:** This final note MUST preserve every granular technical specification, metaphor, and systemic connection identified in the preliminary synthesis. 
*   **Structured Integrity:** Your "Structured Extraction" section must be exhaustive. If the preliminary note lists 20 facts, this note must capture all 20. Do NOT collapse them into "broad themes."

### PART 1: THE TONE MANDATE (CRITICAL)
*   **Mirror the User's Voice:** Use the user's specific vocabulary, slang, and energy (e.g., "softlock," "flex," "snappy," "insane").
*   **No Sanitization:** Capture the intensity. Avoid "Mechanism," "Characteristics," "Furthermore," "In conclusion."

### PART 2: THE LANGUAGE MANDATE
*   **Primary Language:** Write the body in the primary language of the user's input (English or Chinese).
*   **Idiom Preservation (CRITICAL):** You **MUST** preserve specific phrases, idioms, or metaphors in their **original language** (especially Chinese phrases within English text).
    *   **Do NOT translate** these high-nuance phrases. Keep them as the user wrote them (e.g., "The vibe is '松弛感'").
*   **If Input is Predominantly Chinese:**
    *   **Filename/Title:** MUST be in **English** (Standard naming convention).
    *   **Aliases:** You MUST include the **Chinese name(s)** in the YAML `aliases` field.
    *   **Content Body:** You MUST write the content (Narrative, Extractions, etc.) in **Chinese**, preserving the user's original wording and style.

### PART 3: OUTPUT STRUCTURE (STRICT MARKDOWN)
Compose the final note with the following structure (per `STRUCTURE_DEFINITIONS.md`):

1.  **YAML Frontmatter:** title, created, tags (#type/literature-note, #source/synthesis), aliases.
2.  **# <Title>**
3.  **The Narrative (Stream A - Refined):** A flowing, human-readable narrative in the user's voice, enriched with `[[Wikilinks]]` and hierarchical tags (e.g., `#value/efficiency`).
    *   **Non-Prescriptive Mandate:** Capture ONLY what the user *has done*, *is doing*, or *explicitly plans to do*. Do NOT convert observations into imperative advice or "suggested actions" unless the user explicitly framed it as a directive to themselves.
4.  **Structured Extraction (The "ME" Core):**
    *   This section mirrors the **Preliminary Format** (bulleted streams) but is now enriched with the RAG context.
    *   Provide direct, bulleted extractions of: **Key Facts & Claims**, **Personal Observations & Logic**, and **Core Motivation & Vibe**.
    *   **MANDATORY:** Include `[[Internal Links]]` to relevant notes here.
    *   **STRICTLY FLAT:** Do NOT use sub-headers (e.g., `###`) within these bulleted extractions.
5.  **Literature & External Context (Stream B - Refined):** External AI insights, clearly marked.
6.  **Contradiction Analysis (if applicable):** dedicated section for clashes with the RAG context.
6.  **References:**
    *   List the files from the RAG context that were most relevant.

---START_PRELIMINARY_SYNTHESIS---
{preliminary_content}
---END_PRELIMINARY_SYNTHESIS---

### RAG CONTEXT SOURCE
The RAG context is located at: `{rag_context_path}`
**Action Required:** You MUST use the `read_file` tool to read the contents of this file to inform your synthesis.

**Action Required:** Generate the full markdown content. Use the Capitalized Title naming convention. Save to `3_Permanent_Notes/SYNTH-[YYYYMMDD]-Capitalized Title.md`. Provide the exact final file path.
"""

def get_integrate_stage1_prompt(input_content, source):
    return f"""
Your task is to extract keywords from this insight/note to retrieve relevant context for integration. 
**Priority:** Focus on the 'Structured Extraction' section if available.

---START_INPUT---
{input_content}
---END_INPUT---

**Action Required:** Provide comma-separated keywords. Then call `synthesis integrate "{source}" --keywords "<your_keywords>"` to continue.
"""

def get_integrate_stage2_prompt(rag_context_path, temp_json_output_path, source_note_path, input_content, suggested_tags):
    tag_instruction = f"Suggested Tags: {suggested_tags}" if suggested_tags else ""
    return f"""
You are performing a "Safe Integration" of new information into your PKM vault.

### MANDATE: STRUCTURAL INTEGRITY (CRITICAL)
You MUST strictly adhere to the standards defined in `0_Config/STRUCTURE_DEFINITIONS.md` for note creation, editing, and metadata keys.

### STRATEGY (CRITICAL)
1.  **Analyze the "Structured Extraction" Section:** Use this section of the input as the primary source for identifying new updates.
2.  **Values, Preferences, and Needs (TAG ONLY):** Do NOT create new atomic notes for these concepts unless the user is explicitly providing a formal definition or philosophical stance. Instead, apply the relevant hierarchical tag (e.g., `#value/efficiency`, `#preference/cli`) to the source synthesis note or the related log note.
3.  **Handle Life Events (#log/):** If an entry represents a life experience, feeling, or somatic event, you MUST follow the Log Note Standards:
    *   **Existing Logs:** Check the RAG context. If a note for that experience exists (e.g., "Bus Headache"), use `mode: "prepend_to_main"` to add the new event at the top (Latest-on-Top standard).
    *   **New Logs:** If it's a new type of event, create a new note with `#type/log` and the relevant `#log/<category>` tag.
    *   **Standardization:** All log entries (new or prepended) MUST include the **[[YYYY-MM-DD]] HH:mm** body marker on their first line. New notes MUST include `EventDate` in the YAML.

### EXISTING KNOWLEDGE BASE CONTEXT (RAG)
The RAG context is located at: `{rag_context_path}`
**Action Required:** You MUST use the `read_file` tool to read the contents of this file to check for contradictions and connections.

### Goal
Identify actionable insights to create new atomic notes or update existing permanent notes.
{tag_instruction}

### Atomic Note Definition (CRITICAL for New Notes)
An Atomic Note defines a single, specific concept, principle, or entity. It must be **self-contained** (understandable on its own) and **linkable** (a useful node in a network). 
**STRICTLY ATOMIC & FLAT:** 
*   **NO SECTIONS:** Do NOT use sub-headers (e.g., `##`, `###`) inside new atomic notes. The content must be a flat, punchy narrative or list.
*   **NO BLOAT:** Avoid broad topics. If a concept is too broad, break it down.
*   **RAW VOICE MANDATE:** The body of the note MUST be written in the **User's Raw Voice/Monologue**.
    *   *Bad (Clinical):* "Visual Clarity is defined as the state of..."
    *   *Good (Raw):* "Visual Clarity is just seeing the next step. When the pile is blurry, I'm softlocked..."
    *   Use the user's slang ("softlock", "shits", "vibe") and metaphors. NO "Assistant-Speak."

### Connectivity Requirement (CRITICAL)
You must actively connect new notes to existing concepts using `[[Wikilinks]]` liberally. Connect to related concepts, especially purely atomic ones (e.g., `[[Efficiency]]`, `[[Context]]`).

### LANGUAGE MANDATE (CHINESE INPUT)
If the input/insight is in Chinese:
*   **Filename (for 'new_note'):** MUST be in **English** (Standard naming convention).
*   **Aliases (for 'update_metadata'):** You MUST add the **Chinese name** as an alias.
*   **Content Body:** You MUST write the content in **Chinese**, preserving the user's original wording.

### THE 5-DIMENSION TAGGING MANDATE (CRITICAL)
For every insight, you MUST classify it into one or more of these 5 dimensions if applicable, applying the specific Tagging & Linking pattern:

1.  **VALUE** (Abstract Principles/Ideals)
    *   **Definition:** What the user values or strives for (e.g., Efficiency, Honesty, Speed).
    *   **Tag:** `#value/<concept>` (e.g., `#value/efficiency`).
    *   **Link:** You MUST wikilink the core concept note.
    *   *Example:* "I hate waiting." -> `Tag: #value/efficiency`, Content includes `[[Efficiency]]`.

2.  **PREFERENCE** (Specific Likes/Dislikes)
    *   **Definition:** Concrete choices or tastes (e.g., CLI over GUI, Dark Mode).
    *   **Tag:** `#preference/<specifics>` (e.g., `#preference/cli-workflow`).
    *   **Link:** Link to the specific subject of the preference.
    *   *Example:* "I prefer CLI." -> `Tag: #preference/cli-workflow`, Content includes `[[CLI]]`.

3.  **NEED** (Requirements/Deficits)
    *   **Definition:** What is required for function or well-being (e.g., Silence, Low Latency).
    *   **Tag:** `#need/<requirement>` (e.g., `#need/low-latency`).
    *   **Link:** Link to the deficit or requirement concept.
    *   *Example:* "I need it to be fast." -> `Tag: #need/velocity`, Content includes `[[Velocity]]`.

4.  **ACTION** (Intents/Next Steps)
    *   **Definition:** What the user intends to do.
    *   **Tag:** `#action/<verb>` (e.g., `#action/refactor`, `#action/investigate`).
    *   **Link:** Link to the project or subject of action.
    *   *Example:* "I'm going to fix the bug." -> `Tag: #action/fix`, Content includes `[[Bug]]`.

5.  **EXPERIENCE** (The Context/Event)
    *   **Definition:** The specific event, feeling, or log that triggered the insight.
    *   **Tag:** `#log/<category>` (e.g., `#log/somatic`, `#log/social`, `#log/learning` - see `STRUCTURE_DEFINITIONS.md`).
    *   **Link:** Link to the involved entities.
    *   *Example:* "The bus ride gave me a headache." -> `Tag: #log/somatic`, Content includes `[[Bus Headache]]`.

### Integration Decision Logic
1.  **New Atomic Concepts (from Stream A):**
    *   **CLUTTER FILTER (CRITICAL):** Do NOT create new atomic notes for insights that are merely the user defining standard concepts or terms in their own words (e.g., "Visual Clarity is seeing the next step").
    *   **The "Totally Different" Rule:** ONLY create a new atomic note if the user's understanding represents a **significant divergence**, a **redefinition**, or a **unique philosophical stance** that clashes with or substantially expands upon standard literature.
    *   If the insight is just a "raw voice" version of a known concept, keep it in the synthesis note and apply the relevant tags (#value/, #preference/).
    *   Action: Generate a 'new_note' entry ONLY if it meets the "Totally Different" criteria.

2.  **Literature Notes (from Stream B):**
    *   If an insight from **Stream B** (Literature Context) provides valuable external info that should be preserved as a separate reference (e.g., a summary of an unverified LLM point, an external definition), it should be created in `2_Literature_Notes`.
    *   Action: Generate a 'new_note' entry with `directory: "2_Literature_Notes"`.
    *   **Content Requirement:** Provide ONLY the body of the note. **STRICTLY FLAT: NO SUB-HEADERS.**
    *   **Tags:** MUST include `#type/literature-note` and `#source/synthesis`.

3.  **Updates to Existing Notes:**
    *   If an insight (from any stream) relates to an existing file (Permanent or Literature), integrate it.
    *   **STRICTLY FLAT INTEGRATION:**
        *   **NO NEW SECTIONS:** Do NOT create new sub-headers when updating existing files.
        *   **NO DIRECTORIES:** Do NOT append links to 'Value.md', 'Preference.md', 'Need.md', or 'Action.md'. These notes are reserved for the atomic definition of those concepts, not as directories for other notes.
    *   **Decision Logic for Mode:**
        *   **Standard Modes (Encouraged):** Use `prepend_to_file`, `prepend_to_main`, or `append_to_main` for clear, non-contradictory additions.
        *   **Manual Review (Safety Valve):** Use `mode: "manual_review"` ONLY if an edit requires surgical precision, involves a significant contradiction, or you are unsure about the placement.
        *   **Rewrite / Rephrase:** If the new insight represents a new core definition or a complete rephrasing of the note's main concept:
            *   Action: Use `mode: "prepend_to_file"`.
            *   **Content Requirement:** Provide ONLY the body of the new content. Do NOT include the header.
            *   **Title Logic:** If the note's title should change, provide `title: "New Title"`. If the title remains the same, OMIT the `title` field; the system will automatically use the existing note's title.
            *   **System Action:** The system will automatically generate the `# Title` and `Edited on [[YYYY-MM-DD]]` block at the top of the file. Older versions are moved to history.
        *   **Dominant View:** If the new insight is a superior perspective or a dominant angle on the **main concept** of the note:
            *   Action: Use `mode: "prepend_to_main"`.
            *   Content: Provide the content to place at the top of the main body (immediately after the first header).
        *   **Supporting Detail / Facet:** If the new insight is a supporting detail, example, or facet:
            *   Action: Use `mode: "append_to_main"`.
            *   Content: Provide the supporting text to append to the end of the main body.
        *   **High Precision / Complex / Contradictory:** If an edit requires surgical precision, involves a significant contradiction from the "Contradiction Analysis", or you are unsure about the placement:
            *   Action: Use `mode: "manual_review"`.
            *   **Content Requirement (CONSULTATION BLOCK):** For this mode, the `content` field MUST be a structured markdown block formatted as follows:
                ### ⚠️ INTEGRITY CONSULTATION
                **The Conflict/Issue:** [Briefly state the clash or ambiguity]
                **Existing Context:** [Summary of what you see in the RAG for this file]
                **Proposed Change:** [The specific text you suggest adding/replacing/modifying]
                **Rationale:** [Why this preserves integrity or why manual intervention is safer]
            *   **Rationale:** Also include a short `"rationale": "..."` field in the JSON for the integration report summary.
    *   **Source Link Automation:** The system will automatically append a source link to the synthesis note for all content.

4.  **Contradiction Resolution (CRITICAL):**
    *   **Examine the "Contradiction Analysis" section** of the synthesis note.
    *   For EVERY conflict listed, you MUST generate a top-level `manual_review` entry.
    *   **Goal:** Provide a context-rich proposal that addresses the conceptual clash across all affected notes.
    *   **Action:** Generate a `type: "manual_review"` entry.
    *   **Content Requirement (CONSULTATION BLOCK):**
        ### ⚠️ INTEGRITY CONSULTATION
        **The Conflict/Issue:** [Conceptual Clash]
        **Vault Context:** [What you see in the RAG for all related notes]
        **Proposed Resolution:** [How you suggest resolving the clash (e.g., merging concepts, choosing one over the other, creating a 'contrast' section)]
        **Rationale:** [Why this resolution preserves the integrity of your total knowledge]
    *   **Affected Files:** Provide a list of all files in the vault involved in this conflict.

5.  **Metadata Updates (Title, Aliases, Tags):**
    *   If the synthesis reveals a better title, new alias, or new tags for an existing note:
    *   Action: Generate an 'update_metadata' entry.
    *   **Logic:**
        *   `new_title`: Use this to rename the note (demoting old title to alias).
        *   `add_tags`: List of new tags to add. **MUST use hierarchical format** (e.g., `#concept/topic`, `#status/active`) per `STRUCTURE_DEFINITIONS.md`.
        *   `remove_tags`: List of tags to remove.
        *   `add_aliases`: List of new aliases to add.
        *   `remove_aliases`: List of aliases to remove.

### JSON FORMATTING (CRITICAL)
*   **Strict JSON Syntax:** The output must be a valid JSON array.
*   **Escape Newlines:** You MUST escape all newlines in the `content` fields as `\\n` (double backslash). Literal newlines will break the parser.
*   **Escape Quotes:** Escape all double quotes within strings as `\"".
*   **No Markdown Fences:** Do NOT wrap the output in ```json ... ``` blocks. Output RAW JSON only.

Your output **MUST** be a JSON array of objects.

For 'new_note' type:
{{
    "type": "new_note",
    "directory": "3_Permanent_Notes" or "2_Literature_Notes",
    "content": "<markdown content (body only)>",
    "title": "<title>",
    "tags": "tag1,tag2"
}}

For 'edit_note' type (Standard Modes):
{{
    "type": "edit_note",
    "file": "path/to/existing_note.md",
    "content": "<markdown content>",
    "mode": "prepend_to_main" or "append_to_main" or "prepend_to_file",
    "title": "Optional New Title (only for prepend_to_file)"
}}

For 'edit_note' type (Manual Review / Consultation):
{{
    "type": "edit_note",
    "file": "path/to/existing_note.md",
    "content": "### ⚠️ INTEGRITY CONSULTATION\n**The Conflict/Issue:** ...\n**Existing Context:** ...\n**Proposed Change:** ...\n**Rationale:** ...",
    "mode": "manual_review",
    "rationale": "Surgical edit needs discussion"
}}

For 'manual_review' type (Conceptual Conflict):
{{
    "type": "manual_review",
    "affected_files": ["file1.md", "file2.md"],
    "content": "### ⚠️ INTEGRITY CONSULTATION\n**The Conflict/Issue:** [Conceptual Clash]\n**Vault Context:** ...\n**Proposed Resolution:** ...\n**Rationale:** ...",
    "rationale": "Conceptual conflict from Contradiction Analysis"
}}

For 'rename_note' type (Propagation):
{{
    "type": "rename_note",
    "file": "path/to/old_name.md",
    "new_name": "new_slugified_name"
}}

For 'update_metadata' type:
{{
    "type": "update_metadata",
    "file": "path/to/existing_note.md",
    "new_title": "Optional New Title",
    "add_tags": ["tag1", "tag2"],
    "remove_tags": ["old_tag1"],
    "add_aliases": ["alias1", "alias2"],
    "remove_aliases": ["old_alias1"]
}}

---START_INPUT---
{input_content}
---END_INPUT---

**Action Required:**
1. Generate the JSON content.
2. Use `write_file` to save it to "{temp_json_output_path}".
3. IMMEDIATELY execute the following shell command to integrate and commit:
   `python 0_Config/main_cli.py note integrate "{temp_json_output_path}" {("--source " + '"' + source_note_path + '"') if source_note_path else ""}`
4.  **Interactive Pivot:** Once the integration command finishes, if you generated any `manual_review` items, you MUST immediately enter the **Interactive Loop** with the User:
    *   **Discuss:** Present the conflict to the User and propose a resolution (Overwrite, Refine, Reject, or New Note).
    *   **Wait for Approval:** Do nothing until the User says "Yes" or "Go ahead".
    *   **Action 1 (Immediate - Source Marking):** **ONLY AFTER APPROVAL**, use the `replace` tool to manually edit the synthesis note (if applicable) to prepend `[RESOLVED]` to the conflict.
    *   **Action 2 (Accumulate - Vault Update):** Simultaneously, append the necessary `edit_note` action (for modifications) or `new_note` action to an external JSON file (create one if needed).
    *   **Final Execution:** After all conflicts are processed, call `python 0_Config/main_cli.py note integrate <json_file> --source "{source_note_path}" `.
"""

def get_full_orchestration_prompt(source_path, preliminary_output_path, consolidated_rag_context_path, input_mode="direct"):
    return f"""
You are the Orchestrator for a multi-stage Synthesis Workflow. Your goal is to transform raw input into integrated, validated knowledge.

**Source File:** {source_path}
**Preliminary Output Path:** {preliminary_output_path}
**Consolidated RAG Context Path:** {consolidated_rag_context_path}

### STEP 1: Preliminary Synthesis
Execute the following command to generate the initial "2-Stream" synthesis:
`python 0_Config/main_cli.py synthesis preliminary --source "{source_path}" --input-mode {input_mode}`
(This will output a prompt for you to generate the preliminary note and save it to `{preliminary_output_path}`).

### STEP 2: RAG Context Preparation
Once Step 1 is complete and the file is saved, execute:
`python 0_Config/main_cli.py synthesis final "{preliminary_output_path}"`
(This will output a prompt asking for keywords. Provide them to trigger `rag prepare-context`).

### STEP 3: Final Synthesis Note
After the RAG context is prepared, the system will output a prompt for you to generate the **Final Permanent Synthesis Note**. Follow those instructions precisely and save the file to `3_Permanent_Notes/`.

### STEP 4: Safe Integration
Once the Final Note is saved, execute:
`python 0_Config/main_cli.py synthesis integrate "path/to/your/final_note.md"`
(This will output a prompt for keywords, then a prompt for generating a Safe Integration JSON).

### STEP 5: Cleanup
After integration is complete, execute:
`python 0_Config/main_cli.py synthesis cleanup`

**Action Required:** Begin with STEP 1.
"""

