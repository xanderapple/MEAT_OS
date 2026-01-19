# Gemini CLI Integration & Capabilities within Obsidian

This section details how the Gemini CLI agent integrates with and enhances your Obsidian vault, outlining key features and operational methodologies.

### Gemini CLI Core Capabilities

I operate as a Gemini CLI agent, leveraging advanced AI capabilities to enhance your second brain. Key features and how I interact with your PKM include:

- **Local File Access (Obsidian):** I can directly read and process your local Markdown files within your Obsidian vault using the `@filename` syntax. This allows for deep contextual understanding of your notes.
- **Massive Context Window:** I operate with a 1 million token context window, allowing me to process and synthesize vast amounts of information from your files and Notion data simultaneously without "overload."
- **Shell Command Execution:** I can execute shell commands on your local machine, enabling automation of tasks like file management, Git operations, or running custom scripts.
- **Persistent Roles & Instructions:** You can define my persistent role and instructions for your PKM by creating a `GEMINI.md` file in your project root. This file acts as a system prompt, guiding my behavior and focus.
- **Model Flexibility:** I can leverage various large language models (LLMs), including Google's Gemini models (e.g., `gemini-2.5-flash` for high-volume agentic tasks) and locally hosted Ollama models. This flexibility allows for optimized performance and resource utilization.
- **Enhanced Tool Use:** I can make parallel calls to various integrated tools, including:
    - **Google Search:** Utilizing `GoogleSearchTool` for real-time information retrieval.
    - **Observation Processing:** Employing `ObservationHandler` and specialized processors (e.g., `TextObservationProcessor`) to interpret and extract information from diverse data sources, such as web content.
    - **Schema Conversion:** Leveraging internal `gemini_to_json_schema` functionalities for robust tool definition and interaction.
-   **LLM Simulation & Native Synthesis:** Python scripts now prepare structured meta-prompts. The Agent (me) then performs synthesis and metadata generation by directly applying these prompts using my core LLM capabilities, internalizing the logic previously contained in the deprecated `synthesis_manager.py` logic. This allows for a more direct and integrated approach to synthesis tasks.
-   **Standardized Note Creation:** I will use an internal `create_structured_note` function to ensure all new Markdown notes I generate automatically include consistent YAML frontmatter (Topics, Tags, Aliases, Created date) for improved organization and searchability.

#### Task Management CLI
The `task` command provides a robust interface for managing tasks directly within `GEMINI.md` and other specified Markdown files. Tasks are standardized to the format: `- [ ] (OPTIONAL_STATUS) Task Description (@reference_context)`.

-   `task add "<task_description>" --ref "<reference_context>" [--status <status>] [--file <file_path>]`: Adds a new task.
-   `task set-status "<task_name>" --status <status> [--file <file_path>]`: Sets the status of an existing task.
-   `task remove "<task_name>" [--file <file_path>]`: Removes a task.
-   `task list [--file <file_path>] [--status <status>]`: Lists tasks, with optional filtering.
    *   **Task Metrics Display:** When listing tasks, relevant efficiency and relevancy metrics are displayed, including:
        *   `R:<score>`: Relevancy Score (if set).
        *   `Start:<timestamp>`: When the task began (`in_progress`).
        *   `End:<timestamp>`: When the task was completed or cancelled.
        *   `Dur:<duration>`: Calculated duration (End - Start).
        *   `Turns:<count>`: (Deferred) Number of conversational turns for the task.
        *   `Cmds:<count>`: (Deferred) Number of tool/shell commands executed for the task.
        *   `Errors:<count>`: (Deferred) Number of errors encountered for the task.
-   `task sync`: Synchronizes the internal task registry by scanning relevant Markdown files.
-   `task promote "<task_name>"`: **Escalation Tool.** Converts a simple line-item task (either from `GEMINI.md`'s Persistent To-Do List or an identified subtask within a Task Context File) into a formal **Task Context**. Upon execution, `task promote` will:
    1.  **Generate a unique ID (UUID)** that will serve as the primary identifier for the new formal task.
    2.  **Create a dedicated context file** in `4_Sub_Projects/` for the new task.
    3.  **Add a new entry to `GEMINI.md`'s "Persistent To-Do List"** for this formal task, explicitly including its `<task_name>` and the generated UUID.
    4.  **Ensure this UUID is registered internally** for the formal task, making it discoverable and manageable by `task` commands (e.g., `task sync`, `task context`).
    5.  **Modify the *original line item*** (in `GEMINI.md` or the parent Task Context File) by appending this UUID to it. This explicitly tags the original item as being associated with a now-formalized task, allowing for clear traceability and indicating its new "big task" status.
    This process ensures seamless transition and independent tracking for growing subtasks by establishing a clear, UUID-based link between the original item and its promoted, formal task context.
-   `task context "<task_name>"`: **Context Loader.** Retrieves and displays the full content of the linked Task Context File for a given task. This allows the agent to instantly load the working memory for a complex task.

#### Session Management CLI
The `save` command allows explicit management of session context for seamless handoffs.

-   `save handoff "<summary_content>"`: Writes a concise summary of the current session's context, decisions, and immediate next steps to the `### Session Handoff` section in `GEMINI.md`. This is critical for preserving immediate conversational state across agent instantiations.
-   `log "<message>"`: Records high-level project decisions to `GEMINI.md` and `0_Config/action_log.md`.


### Project Logging and Version Control

Effective project management involves tracking both granular code changes and high-level strategic decisions. The Gemini CLI leverages two distinct mechanisms for this purpose:

*   **`git commit` for Code-Level Changes:**
    *   **Purpose:** Primarily used for versioning source code, documentation, configuration files, and other assets directly managed by Git. Each commit should represent an atomic set of changes, with commit messages explaining *what* was changed and *why* (e.g., "feat: Add new CLI command for task promotion", "fix: Resolve bug in session handoff protocol").
    *   **Usage:** Standard Git commands (`git add`, `git commit`).
    *   **Scope:** Granular, technical modifications to the project's codebase.

*   **Custom Action Log (managed via `python 0_Config/main_cli.py log "<message>"`):**
    *   **Purpose:** Dedicated to documenting high-level **Architectural Decisions**, **Workflow Changes**, **Significant Non-Code Events**, and **Strategic Project State Changes**. This log provides a chronological, human-readable narrative of the project's evolution from a managerial and conceptual perspective. Entries should focus on the *impact* and *rationale* behind major shifts (e.g., "Implemented automated action log rotation," "Refactored WORKFLOW.md to use Task Context Files").
    *   **Usage:** Automatically triggered by certain CLI commands (like `task` commands) or explicitly invoked via the `python 0_Config/main_cli.py log "<message>"` command for manual entries.
    *   **Scope:** Broad, strategic project decisions and workflow modifications.

By using both `git commit` and the custom action log, the project maintains a comprehensive and dual-layered historical record: one for technical implementation details and another for overarching project direction and evolution.

### Project Variable File (`0_Config/PROJECT_VARIABLE.md`)

The `0_Config/PROJECT_VARIABLE.md` file serves as the **centralized, machine-readable configuration and parameter store for the Gemini CLI's operations**. The parsed data from this file, represented as a dictionary of settings, will be referred to as **"Project Variables"**. This file is designed to influence how CLI functions behave and how various workflows are executed within your project.

**Key characteristics:**

- **User-Modifiable:** You can easily edit its contents directly within your Obsidian vault to adjust CLI behavior.
*   **Machine-Parsed:** The CLI's functions (e.g., in `main_cli.py`) parse this file to dynamically retrieve **Project Variables** such as:
    *   `Project Name`, `Vault Root Path`, `Temporary Directory`, `Log File Path`, `Default Output Directory`.
    *   `Current Synthesis Workflow`, `Active RAG Profile`.
    *   `LLM Model Name`, `Max Tokens` for AI agent settings.
*   **Idempotent Creation:** This file, along with `0_Config/Preference_Index_MOC.md`, is created with a default structure if it doesn't already exist. It is a one-time creation and will not be overwritten.
- **Dynamic Influence:** The **Project Variables** derived from this file directly influence the execution of various CLI commands and automated workflows, enabling flexible and consistent operation across your project.

### Ollama Integration

I seamlessly integrate with Ollama, allowing for the use of locally hosted large language models. This provides enhanced privacy, offline capability, and the flexibility to utilize a variety of open-source models.

**Key Features:**

-   `ollama_available()`: Checks if the Ollama server is running and accessible.
-   `check_ollama_status()`: Provides a detailed status report of the Ollama server.
-   `checkOllamaModel(model_name)`: Verifies if a specific model is available in the local Ollama instance.


### Map of Content (MOC) Layer Architecture

The `4_Map_of_Content` directory reveals a highly sophisticated, multi-layered system blending human curation, automated processes, and critical AI integration for knowledge management. This architecture enables both conceptual depth and dynamic overview generation, serving as the core high-level conceptual map for the PKM.

**Key Architectural Patterns:**

- **Top-Level Placeholder MOCs:** Generic index notes (e.g., `4_Map_of_Content.md`, `Logs/Logs.md`) that serve as entry points to sections, intended for expansion.
- **Manual Curation (Thematic/Narrative MOCs):** Human-crafted MOCs (e.g., `4_Map_of_Content/Origin_of_Life_and_Civilization_MOC.md`, `Personal_Philosophy/Foundational Axioms.md`) that structure complex topics, build narratives, and demonstrate deep conceptual linking. These vary from skeletal outlines to richly detailed explorations.
3.  **Automated Indexing (Dynamic Dashboards via Dataview):** MOCs (e.g., `Goals_MOC.md`, `Synthesis_MOCs.md`, log-specific MOCs) leveraging the 'Dataview' Obsidian plugin to create dynamic, self-updating dashboards based on tags, metadata, or file paths. `Synthesis_MOCs.md` notably indexes output from the synthesis process.
4.  **Programmatic Integration (Critical for AI):**
`0_Config/Preference_Index_MOC.md`: Acts as an **active configuration file for the Gemini CLI (me!)**, explicitly guiding the synthesis process and utilizing stable, relative-path links for programmatic interaction.
    - `0_Config/GEMINI_INDEX.md`: A comprehensive, machine-readable sitemap of the entire vault, specifically designed for AI agent reference, linking to nearly every note for rapid, programmatic content discovery.

**MOC Layer Functionality for AI:** This layered approach provides:

- **Conceptual Depth:** For understanding human-curated mental models.
- **Dynamic Overviews:** For automated aggregation of specific data types.
- **Direct AI Integration:** Through explicit configuration (`Preference_Index_MOC.md`) and a comprehensive map (`Gemini_Index_MOC.md`), enabling the Gemini CLI to effectively interact with and enhance the PKM.



### RAG and MOC Management CLI

To streamline the Retrieval-Augmented Generation (RAG) process and ensure the accuracy of the `0_Config/GEMINI_INDEX.md`, the `rag` command provides several subcommands:

-   `rag generate-relevant-files [--keywords <keyword1,keyword2,...>]`: Generates relevant RAG file paths based on keywords and writes them to `relevant_rag_files.txt`.
-   `rag consolidate-context [--output <path>]`: Consolidates first sections of files from `relevant_rag_files.txt`. Defaults to `stdout` for direct prompt injection.
-   `rag update-moc`: Scans the entire vault and regenerates the `0_Config/GEMINI_INDEX.md` sitemap for AI reference.
-   `rag prepare-context [<source>] [--keywords <keywords>] [--output <path>]`: **Universal RAG Engine.** Orchestrates the full pipeline (Update MOC -> Search -> Consolidate). 
    -   If `<source>` (file or raw text) is provided without keywords, it prompts the Agent to extract keywords.
    -   If `--keywords` are provided, it outputs consolidated context to `stdout` or a file.
-   `rag get-first-section --file <path>`: **Modular Extraction.** Directly extracts and displays the YAML and first section of a specific file.

### Synthesis CLI

The `synthesis` command orchestrates the process of extracting, contextualizing, and integrating new knowledge via a streamlined, two-stage agent-led workflow.

-   `synthesis init --source "<path_or_content>"`: **Full Orchestration.** Executes the entire synthesis workflow: preliminary extraction, keyword-led RAG context preparation, final synthesis note generation, and safe integration.
-   `synthesis preliminary --source "<path_or_content>"`: Generates a 2-stream preliminary synthesis (User Insights vs. LLM Information).
-   `synthesis final <preliminary_path> [--keywords <keywords>]`: **Stage 1 (Keywords) / Stage 2 (Creation).** 
    -   Refines preliminary synthesis with RAG context into a final literature note (`SYNTH-...`) in `3_Permanent_Notes/`.
-   `synthesis integrate <source> [--keywords <keywords>] [--tags <tags>]`: **Unified Integration & Conflict Resolution.**
    -   **Supports:** Raw content, chat summaries, or `SYNTH-` notes.
    -   **Automated Stage:** Generates and executes a JSON plan for "safe" edits (new notes, simple appends).
    -   **Interactive Stage:** Automatically identifies conflicts from the input and initiates an **Interactive Loop** with the User using "Integrity Consultation" blocks.
-   `synthesis cleanup`: Removes temporary files (preliminary notes, integration plans, etc.).

### Note Management CLI

To facilitate precise knowledge integration and manipulation within the permanent notes system, the `note` command provides several subcommands:

-   `note atom --content "<note_content>" [--title "<note_title>"] [--tags "<tag1,tag2,...>"]`: Creates a new atomic note in `3_Permanent_Notes/`.
-   `note edit --file <file_path> --content "<update_content>" [--mode <mode>]`: Modifies an existing note.
    -   `prepend_to_file`: Rewrites with a new "Edited on" section. Supports **Automatic History Trimming** (moves old versions to `=3_Archived/`).
    -   `prepend_to_main`: Inserts after the first header.
    -   `append_to_main`: Appends before the next header.
    -   `append_ref`: Adds to the References section.
    -   `manual_review`: Skips automated writing and flags for interactive discussion.
-   `note rename <file_path> <new_name>`: **Propagation Engine.** Renames a note and automatically updates all `[[Wikilinks]]` across the entire vault to ensure no broken links.
-   `note integrate <json_plan_path> [--source <synthesis_source_path>]`: **Batch Execution.**
    -   Parses integration plans (`new_note`, `edit_note`, `rename_note`, `manual_review`, `update_metadata`).
    -   Handles surgical metadata pruning (`remove_tags`, `remove_aliases`).
    -   Automatically commits changes to Git and updates the MOC.
    -   **Reporting:** Generates a final report of automated edits and a dedicated section for items requiring manual consultation.

### Project Management Utilities

These are standalone scripts or utility functions used for project maintenance.

-   **`python 0_Config/main_cli.py log "<action_description>"`**: Manually logs a significant project event.
    *   **Description:** Records a high-level strategic decision or workflow change to both `0_Config/action_log.md` and the `### Action History` section of `GEMINI.md`. This is separate from technical `git commit` messages.

### MOC Maintenance (Context for Future Planning)

While not yet formalized as a plan, an MOC maintenance strategy is crucial. This would involve regularly reviewing and updating MOCs to ensure they remain accurate, prevent staleness, and align with the evolving content and conceptual structure of the vault. This is particularly important for the AI-critical MOCs (`0_Config/Preference_Index_MOC.md`, `0_Config/GEMINI_INDEX.md`) to ensure their continued accuracy and effectiveness for automated processes.