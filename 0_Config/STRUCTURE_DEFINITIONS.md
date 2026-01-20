# PKM Structure & Naming Definitions

This document serves as the authoritative, machine-readable reference for the structural rules, naming conventions, and tagging hierarchies of the Gemini PKM system.

## I. Folder Structure & Purpose

1.  **`0_Config/` (Configuration & System)**:
    *   **Purpose:** Houses the system configuration, CLI scripts, meta-prompts, and AI-critical MOCs.
2.  **`1_Fleeting_Notes/` (Capture & Staging)**:
    *   **Purpose:** Raw, unprocessed thoughts and the automatic staging area for synthesis source files.
    *   **Auto-Migration:** Files provided to `synthesis init` from the root directory are automatically moved here for archival.
3.  **`2_Literature_Notes/` (External Knowledge)**:
    *   **Purpose:** Summaries and insights from external sources (Books, Articles) and Stream B context.
4.  **`3_Permanent_Notes/` (The Vault Core)**:
    *   **Purpose:** Home for atomic concepts and the historical record of intellectual events (`SYNTH-` notes).
5.  **`4_Map_of_Content/` (Navigation)**:
    *   **Purpose:** High-level thematic and narrative maps (MOCs).
6.  **`5_Tasks/` (Task Contexts)**:
    *   **Purpose:** Dedicated context files for formal Tasks. The concept of "Sub-Projects" is abolished.

## II. File Naming Conventions

### General Principles
*   **Human-Readable:** Use `Capitalized Name.md` with spaces for note titles. This matches the `# Title` in the YAML and ensures natural linking.
*   **Uniqueness:** Each filename must be unique within its directory.

### Specific Formats
1.  **Synthesis History (`3_Permanent_Notes/`)**:
    *   **Format:** `SYNTH-[YYYYMMDD]-Capitalized Title.md`
2.  **Atomic Notes (`3_Permanent_Notes/`)**:
    *   **Format:** `Capitalized Concept Name.md`
    *   **Example:** `Agentic PKM System.md`
3.  **Task Context Files (`4_Sub_Projects/`)**:
    *   **Format:** `[TaskName].md` or `[UUID].md`
4.  **Literature Notes (`2_Literature_Notes/`)**:
    *   **Format:** `[SourceTitle].md` or `[Topic]_Summary.md`
5.  **Map of Contents (`4_Map_of_Content/` or `0_Config/`)**:
    *   **Format:** `[Topic]_MOC.md` or `[Purpose]_Index.md`

## III. Tagging Hierarchy

### 1. Hierarchical Type & Status
*   **`#type/<note-type>`**: `#type/atomic-note`, `#type/literature-note`, `#type/project-note`, `#type/log`.
*   **`#status/<stage>`**: `#status/in-progress`, `#status/pending-review`, `#status/completed`.

### 2. Conceptual & Contextual
*   **`#concept/<topic>`**: For primary categorization (e.g., `#concept/ai`, `#concept/philosophy`).
*   **`#project/<name>`**: Links to specific initiatives.
*   **`#person/<name>`**: Connects to individuals.

### 3. Intent & Value (For Synthesis)
*   **`#value/<specific-value>`**: Captured user motivations (e.g., `#value/efficiency`).
*   **`#preference/<specific-pref>`**: User-stated preferences.
*   **`#need/<specific-need>`**: Identified requirements.
*   **`#action/<verb>`**: Functional action items (e.g., `#action/refactor`).

### 4. Log Events (Life Actions & Experiences)
*   **`#log/<category>`**: Used to capture specific, time-stamped events from your life. This is the primary capture point for **Living Experiences and Actions**.
    *   **Examples:** `#log/music`, `#log/somatic` (feelings/body), `#log/reading`, `#log/learning`, `#log/social`.
*   **Cue for Agent:** When you encounter descriptions of life events, completed tasks, or personal experiences in chat, automatically propose creating a new note in `3_Permanent_Notes/` with the `#log/` tag.

## IV. Metadata Standards (YAML)

All notes created by the Agent must include:
*   `title`: Clear, descriptive title.
*   `created`: YYYY-MM-DD.
*   `tags`: Relevant hierarchical tags.
*   `aliases`: List of alternative names.
*   `edited`: (Optional) YYYY-MM-DD.
