# Tag Definitions and Usage Guidelines

This file serves as the central repository for defining standard tags used throughout the Personal Knowledge Management (PKM) system. Adhering to these definitions ensures consistency, enhances findability, and enables reliable querying through tools like Dataview.

## How to Use This File

*   **Reference:** Consult this file before creating new tags to ensure consistency with existing conventions.
*   **Contribute:** If you identify a frequently used tag that is not defined here, or propose a new tag structure, add it to the appropriate section.
*   **Gemini's Role:** I (Gemini) will refer to this file when applying tags and will propose updates to it as the tagging system evolves.

## Tag Categories and Definitions

### 1. Hierarchical Tags

These tags use a `parent/child` or `category/subcategory` structure to provide logical grouping.

*   **`#type/<note-type>`**
    *   **Purpose:** Identifies the primary function or nature of a note.
    *   **Examples:**
        *   `#type/literature-note`: For notes summarizing external sources or synthesis outputs.
        *   `#type/atomic-note`: For fundamental, standalone concepts or ideas (permanent notes).
        *   `#type/project-note`: For notes directly related to a specific project.
        *   `#type/meeting-note`: For notes capturing information from meetings.
        *   `#type/fleeting-note`: For quick capture notes.
        *   `#type/log`: For system-generated or manually recorded log entries.
*   **`#status/<stage>`**
    *   **Purpose:** Indicates the current state or progress of a task, project, or note's development.
    *   **Examples:**
        *   `#status/in-progress`: Currently being worked on.
        *   `#status/pending-review`: Awaiting review or feedback.
        *   `#status/completed`: Work is finished.
        *   `#status/on-hold`: Work is temporarily paused.
*   **`#concept/<main-concept>`**
    *   **Purpose:** For primary conceptual tags where direct interlinking might be less formal or for broader categorization of core ideas.
    *   **Examples:**
        *   `#concept/AI-Agents`
        *   `#concept/PKM`
        *   `#concept/Ontology`
        *   `#concept/Knowledge-Graphs`
*   **`#source/<origin>`**
    *   **Purpose:** To denote the origin or type of source material.
    *   **Examples:**
        *   `#source/book`
        *   `#source/article`
        *   `#source/meeting`
        *   `#source/webpage`

### 2. Contextual Tags

These tags link notes to specific entities or contexts.

*   **`#project/<project-name>`**
    *   **Purpose:** Links notes to specific projects.
    *   **Examples:**
        *   `#project/Gemini-CLI-Development`
        *   `#project/Q4-Report-Generation`
*   **`#person/<name>`**
    *   **Purpose:** Connects notes to individuals.
    *   **Examples:**
        *   `#person/John-Doe`
        *   `#person/Jane-Smith`

### 3. Action/Intent Tags

These tags are used to flag notes requiring specific actions or indicating an intent.

*   **`#action/<verb>`**
    *   **Purpose:** To flag notes requiring a specific action.
    *   **Examples:**
        *   `#action/review`: Needs to be reviewed.
        *   `#action/refactor`: Needs structural or content improvement.
        *   `#action/summarize`: Needs summarization.

### 4. Log Event Tags

These tags are specifically for user-generated event logs, facilitating Dataview queries.

*   **`#log/<category>`**
    *   **Purpose:** To categorize individual event log entries.
    *   **Examples:**
        *   `#log/music`: For music listening logs.
        *   `#log/somatic`: For somatic state logs.
        *   `#log/reading`: For reading activity logs.

---
**Last Updated:** 2025-12-11