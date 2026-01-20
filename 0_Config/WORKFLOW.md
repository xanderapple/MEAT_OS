# Gemini Agent Workflow: How I Operate

This document outlines the internal workflow and directives that govern my (Gemini) operations within your project. It serves as a guide to my behavior, ensuring consistency, state integrity, and efficient task execution.

## I.0. Initial Session Protocol
**Critical Directive: Contextual First Response**
Upon initialization or at the start of a new session, I **MUST** meticulously review the `### Session Handoff` section within `GEMINI.md`, and the `### Action History` to fully integrate the previous session's context, outstanding tasks, and strategic insights into my initial understanding and first response. This ensures continuity and prevents loss of information across sessions.

## I. Mandatory Execution Workflow (Meta-Prompt/CoT)

**Critical Directive: Self-Documentation First**
Anytime a significant change is made to my capabilities, workflow, or any internal directives, I **MUST** immediately update the relevant documentation (especially `WORKFLOW.md` and `GEMINI.md`) to reflect these changes before proceeding with any other tasks. This ensures my operational self-awareness and consistency are always up-to-date.

For any request that involves multi-step planning, state management, or file modifications, I follow this non-negotiable 5-step procedure:

### Step 1: Analysis & State Update
1.  **Analyze Request & Assess Complexity:** I determine if your intent is a project state change (task completion, new task, file modification) or a simple conversation.
    *   For simple, single-step tasks (estimated < 3 turns), I execute them directly and log the action to the "Action History" in `GEMINI.md`. These are not added to the "Persistent To-Do List."
    *   For complex, multi-turn logic (estimated > 3 turns), I **MUST** treat this as a formal Task requiring context preservation.
    *   **Task Escalation Protocol:** If a "simple" task (originally estimated < 3 turns) reaches the 3rd turn of execution or encounters unexpected complexity/scope expansion, I **MUST** immediately escalate it to a formal Task.
        *   **Action:** I will pause execution and use the `task add "<task_description>" --ref "<reference_context>"` command to create a new formal task and its associated Task Context File. The `task_description` will summarize progress to date, and the `reference_context` will point to the relevant part of the conversation if applicable. After formalization, I will proceed with the now-structured task.2.  **Manage To-Do List & Context Files:**
    *   **Context Persistence Rule (The "3-Turn" Rule):** If a task requires more than 3 turns to complete, I **MUST** create a dedicated Task Context File (Markdown) to preserve the context, objective, and current state. This ensures the goal is not lost if the context window is reset.
    *   **Task Structure:**
        *   **Tasks:** High-level objectives tracked in the "Persistent To-Do List" in `GEMINI.md`.
        *   **Subtasks:** Detailed steps or components of a Task, managed *exclusively* within the specific Task Context File.
        *   **NO Sub-Projects:** The concept of "Sub-Projects" is abolished. Complex goals are handled as Tasks with detailed Context Files containing Subtasks.
    *   **Execution:**
        *   When a task is formally added to the "Persistent To-Do List" in `GEMINI.md` (via the `task add` CLI command), it **automatically creates a dedicated Task Context File** in `4_Sub_Projects/`. This file serves as the central hub for tracking objectives, subtasks, progress, and notes for that task.
        *   If a line-item task in the "Persistent To-Do List" (in `GEMINI.md`) or a subtask within an existing Task Context File requires its own dedicated context due to growing complexity, I use `task promote "<task_name>"` to formalize it. This command will generate a unique ID (UUID) for the new formal task, create its dedicated Task Context File, add a new entry to `GEMINI.md` (explicitly including the task name and its UUID), ensure this UUID is registered internally, and then modify the original line item by appending this UUID for clear traceability.
        *   **Context File Utilization:** For any active (in_progress) task, I **MUST** continuously consult, update, and leverage its dedicated Task Context File for all relevant information, including objectives, subtasks, progress, decisions, and any critical context required for task completion. This file serves as the primary working memory for the task.
        *   When a task is complete, I use `task remove` to clear it from `GEMINI.md` and archive or update the status of the Context File.
        *   **Contextual Relevance Scoring (Conceptual):** To enhance fluid workflow and agentic use, the agent should dynamically assess the relevance of information within the Task Context File. This can be achieved by:
            *   **Recency:** Prioritizing sections or entries that have been most recently updated.
            *   **Explicit Tagging:** Recognizing sections marked with specific tags (e.g., `#critical`, `#active-focus`) as highly relevant.
            *   **Sub-Task Alignment:** Prioritizing information that directly relates to the currently active sub-task.
            *   **Search Proximity:** Giving higher weight to information found in proximity to keywords or concepts relevant to the current objective.
            This conceptual mechanism ensures the agent focuses on the most pertinent details within potentially large context files.
3.  **Decision & Outcome Logging (using `0_Config/scripts/log_action.py`):**
    *   **Purpose:** This logging mechanism is specifically for high-level **Architectural Decisions**, **Workflow Changes**, **Significant Non-Code Events**, and **Strategic Project State Changes**. It records *why* and *what* major project-level movements occurred, providing a human-readable narrative of project evolution.
    *   **Refined Usage for Internal Documentation:** Minor clarifications, typo fixes, or small adjustments to my internal workflow documentation (e.g., `WORKFLOW.md`, `CLI_TOOLS.md`) that do not alter the fundamental strategic or architectural direction of the project **MUST NOT** be logged via `0_Config/scripts/log_action.py`. These smaller changes are sufficiently tracked by `git commit`.
    *   **Distinction from `git commit`:** While `git commit` is used for versioning **code-level changes** with messages focused on technical modifications, this action log focuses on the broader *project context and decisions*. Do not use this for granular code modifications that are better suited for `git commit` messages.
    *   **Tool Usage:** I **MUST ALWAYS** use the `python 0_Config/main_cli.py log "<message>"` tool to log these significant events.
    *   **Log Destinations:** `GEMINI.md` (Action History) and `0_Config/Context/action_log.md` (Master Log).
    *   **Logging Trigger:**
        *   **Automatic:** `task` CLI commands (e.g., creating a new Task Context File).
        *   **Explicit:** Completion of logical steps or strategic decisions.
    *   **Description Style:** Concise natural language (Why & What).
4.  **Structure & Insight Documentation:** I update `GEMINI.md` as soon as new project structures are introduced or significantly modified.
5.  **Modularization Implementation:** My codebase is modularized. CLI command handling is available for task and file management.

### Step 2: Pre-Flight Checks (Contingency & Contradiction)

#### Robustness & Recovery

To ensure the integrity of work and facilitate recovery from unforeseen issues, the following directives are paramount:

1.  **Proactive Git Commits for State Management:**
    *   **Directive:** Before initiating any significant change (e.g., refactoring, implementing a new complex feature, or performing operations with potential side effects), and upon the successful completion of a major task, I **MUST** create a descriptive `git commit`.
    *   **Purpose:** This establishes a clean, recoverable state. In case of errors, unexpected behavior, or a need to backtrack, the project can be reliably reverted to a known good state using standard Git commands. Commit messages should clearly articulate the *purpose* and *scope* of the changes.

2.  **Error Detection and "Unlooping" Protocol:**
    *   **Directive:** If, after executing a command or a sequence of commands, the system encounters an error, enters an apparent loop (repeated similar outputs without progress), or produces unexpected/undesired results, I **MUST** trigger an internal "Unlooping" protocol.
    *   **Protocol Steps:**
        1.  **Immediate Re-evaluation:** Halt further execution of the problematic sequence.
        2.  **Contextual Review:** Re-read the relevant Task Context File and `GEMINI.md` to re-align with the original objective and any constraints.
        3.  **Problem Identification:** Analyze the last few command outputs and any error messages to identify the root cause of the issue or the looping condition.
        4.  **Alternative Strategy:** Formulate an alternative approach or modify the current strategy based on the re-evaluation and context.
        5.  **User Clarification:** If an alternative strategy is not immediately clear, or if the issue is severe (e.g., data loss, persistent error), I **MUST** pause and request clarification or explicit guidance from the user before proceeding.
        6.  **Git Revert Suggestion (Last Resort):** If the situation is irrecoverable or a clean restart is necessary, I **MUST** propose to the user a `git revert` to the last known good commit, explaining the potential loss of recent changes.

#### Personalization & Feedback

To align agent behavior with user preferences and continuously improve interactions:

1.  **Consult `Preference_Index_MOC.md`:**
    *   **Directive:** When making decisions that could be influenced by user preferences (e.g., coding style, preferred tools, output formats, level of verbosity), I **MUST** actively consult the `0_Config/Context/Preference_Index.md` file.
    *   **Purpose:** This ensures that my actions and outputs are tailored to the user's explicit configurations, providing a more personalized and efficient experience. Any relevant preference found in this MOC should guide my approach.

#### Task Relevancy & Efficiency Metrics

To enhance task prioritization, objective performance analysis, and continuous improvement:

1.  **Relevancy Score:**
    *   **Purpose:** A numerical score reflecting the pertinence of a specific task to the agent's current focus or overall project goals. This guides task prioritization.
    *   **Determination (Conceptual):** Can be user-assigned (manual priority), derived from contextual keyword matching, or dynamically adjusted based on recent activity.
    *   **Integration:** Stored as `relevancy_score` within the `Task` object.

2.  **Efficiency Metrics:**
    *   **Purpose:** Objective measurements of resources (time, interactions) used to complete a task, aiding retrospective analysis and process optimization.
    *   **Metrics Tracked (within `Task` object):**
        *   `time_started`: Timestamp when task status changes to `in_progress`.
        *   `time_completed`: Timestamp when task status changes to `completed` or `cancelled`.
        *   `turn_count`: (Deferred) Number of agent-user conversational turns while task is active.
        *   `command_count`: (Deferred) Number of tool/shell commands executed while task is active.
        *   `error_count`: (Deferred) Number of errors encountered while task is active.
    *   **Collection:** `time_started` and `time_completed` are automatically recorded by the `set-status` command. Other counts require further integration into the agent's core loop.
    *   **Display:** Visible via the `task list` command.

1.  **Contradiction Check:** I assess the new request and updated plan against the existing project context.
2.  **Contingency Assessment:** I analyze the entire updated plan for new risks and dependencies.

### Step 3: History Management (Automated)

**Critical Directive: NO MANUAL EDITS TO GEMINI.MD**
I **MUST NEVER** manually edit `GEMINI.md` using the `write_file` or `replace` tools for managing the `### Action History`, `### Session Handoff`, or the `Persistent To-Do List`. Manual edits are prone to error, break the internal state tracking, and violate the principle of **Maximum Consistency**. All updates to these sections **MUST** be performed exclusively through the designated CLI commands or scripts:
-   **Action History:** Managed exclusively via `python 0_Config/main_cli.py log "<message>"`. This is my **primary and only** way to update project history. I **MUST** prioritize this tool over manual edits.
-   **Session Handoff:** Managed exclusively via `python 0_Config/main_cli.py save handoff "<summary>"`.
-   **To-Do List:** Managed exclusively via `python 0_Config/main_cli.py task ...` commands.

### Step 4: File Generation

I generate the entire, complete, and finalized Markdown content for `GEMINI.md` only when updating its core structure or system directives (Step 5). For all other state tracking, I use the tools mentioned in Step 3.

### Step 5: Execution

I call the built-in file writing tool with the path `GEMINI.md` and the complete, new content as the argument.

### Step 6: Session Wrap-Up Protocol (The "Handoff")
**Critical Directive: END OF SESSION ONLY**
The following protocol and the `save handoff` command **MUST ONLY** be executed when the session is explicitly concluding (e.g., user says "goodbye", "end session", or I have completed all requested tasks and am ready to sign off). I **MUST NOT** run this protocol during active development or between individual task steps within a session.

**Triggers:** Explicit user request to end, or my own intent to conclude the session after all goals are met.

1.  **Review Previous Handoff:** I review the existing `### Session Handoff` content in `GEMINI.md`. I **MUST** carry forward any unresolved context, strategic goals, or long-term state descriptions that are still relevant, ensuring they are not lost if the current session was brief.
2.  **Generate Summary:** I generate a concise, high-density summary that synthesizes the previous context with the new session's "headspace," decisions, and next steps.
3.  **Execute Command:** The agent executes the `save handoff "<generated summary>"` CLI command.
4.  **Purpose:** This ensures that the next instantiation of the agent starts with the immediate conversational context, bridging the gap between sessions.

## II. Knowledge Synthesis Workflow

When you request to "synthesize" information, I follow one of two paths based on the complexity and volume of the input:

### A. The Full Orchestration Path (`synthesis init`)
**Use Case:** Large files, complex multi-turn chat histories, or significant new topics that require a formal historical record (`SYNTH-` note).
**Command:** `python 0_Config/main_cli.py synthesis init --source "<source>"`
1.  **Preliminary Extraction:** Generates a 2-stream summary (User vs. Literature).
2.  **RAG Contextualization:** (Internal) I extract keywords from the preliminary note, and the CLI retrieves relevant vault context.
3.  **Final Synthesis:** Creates a permanent literature note (`SYNTH-[YYYYMMDD]-[Title].md`) in `3_Permanent_Notes/`.
4.  **Safe Integration:** Generates a JSON plan and executes vault updates (new notes/edits).
5.  **Interactive Resolution:** For any contradictions found, I enter an **Interactive Loop** using `manual_review` items to discuss resolutions with you.
6.  **Cleanup:** Removes temporary artifacts.

### B. The Minimal Input Path (`synthesis integrate`)
**Use Case:** "Short shit," single-turn insights, raw ideas, or pre-summarized chat context that doesn't need a standalone `SYNTH-` note.
**Command:** `python 0_Config/main_cli.py synthesis integrate "<content_or_path>"`

**Input Processing Guidelines:**
1.  **Request Interpretation & Input Extraction:**
    *   **Prioritize Your Wording in Chat History (with Inference):** If the input appears to be a chat history, I will first attempt to infer speaker turns based on contextual and stylistic cues. My primary goal is to extract and prioritize your presumed contributions.
    *   **Affirmed AI Content in Chat History:** I will include content from my (AI's) presumed turns ONLY if your subsequent presumed messages explicitly affirm, refer to, or build upon that specific AI content. I will use clear textual markers to identify affirmations.
    *   **General Delimitation for Ambiguous/Mixed Inputs:** If speaker turns cannot be reliably inferred, or for mixed inputs, only your clearly identified direct wording will be prioritized as "user language" for initial interpretation.
2.  **Bias Exclusion:** This integration must rely EXCLUSIVELY on the provided input. Do NOT allow internal session history to influence this content.

**Process:**
1.  **Stage 1 (Keywords):** I extract keywords from the raw input to retrieve context.
2.  **Stage 2 (Integration):** 
    *   The CLI prepares the RAG Context internally.
    *   I generate a JSON plan for immediate integration.
    *   **Interactive Pivot:** I present any contradictions or high-risk edits via "Integrity Consultation" blocks for discussion.
3.  **Execution:** Automated items are committed; resolved items are handled via the Interactive Loop.

### C. External Synthesis Path (High-IQ Milestone)
**Use Case:** Capturing massive architectural shifts, complex multi-session refactors, or "cleaning the headspace" while preserving deep context.
**Process:**
1.  **Generate Session Log:** Use `write_file` to create a `Session_Log_[YYYYMMDD].md` file summarizing all major decisions, structural changes, and "working headspace."
2.  **Clean Start:** Terminate the current session.
3.  **Synthesize Log:** Start a fresh session and call `python 0_Config/main_cli.py synthesis init --source "Session_Log_[YYYYMMDD].md"`.
4.  **Benefits:** Prevents context window bias and forces me to follow the written record strictly, ensuring all new logic is officially integrated into the vault without "assuming" previous conversation states.

**Critical Directive:** Always prioritize your voice. In all paths, I must strictly adhere to the "Input Processing Guidelines" to ensure your intent and motivations are captured accurately while ignoring AI noise unless explicitly affirmed.

## III. Proactive & Output Directives

### A. Proactive Task Suggestion (Anti-Stall Rule)

- If the "Persistent To-Do List" in `GEMINI.md` is empty, AND your latest request does not express intent to pause or end the session, I read the `[[ 3 Permanent Notes/My To-Do List ]]` file and suggest an item as our next task in my final conversational response.

### B. Output & Verbosity

- **Action Logging Style:** Concise natural language, focusing on outcome.
- **Terminal Verbosity:** Minimal output, preferring code blocks or simple results.

### C. File Handling

- **Overwrite by Default:** When a command generates a file, it overwrites any existing file of the same name.
- **Deletion Policy:** Instead of direct deletion, move files to the `=1_Bin` directory. This allows for manual review and cleanup.

### D. Conversational Interaction & Safety Catch

For conversational requests that do not involve explicit tool calls or project state changes, I prioritize maintaining a natural dialogue while adhering to a **Read-Only Default** to ensure vault integrity.

1.  **Read-Only Default:** During standard conversation, I am prohibited from using `write_file`, `replace`, or `task` commands unless you provide an **Action Trigger** (e.g., "save that," "update the note," "add this to my list").
2.  **The "Soft Suggestion" Rule:** If you share an insight, task, or preference, I may conversationally suggest a capture (e.g., "Should I add that to your Fleeting Notes?"). 
    *   **Ignore = Drop:** If you ignore the suggestion or continue the conversation, I will immediately drop the suggestion and move on without nagging or persistent prompts.
3.  **Vibe & Flow:** I aim to be a creative partner and sounding board. I can explore ideas and offer opinions without those thoughts automatically becoming "permanent" in the vault until you explicitly authorize the transition from "vibe" to "file."


