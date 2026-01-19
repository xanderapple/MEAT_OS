# Obsidian Vault Structure & Best Practices

This document outlines our collaborative workflow for managing our second brain. It's designed to be efficient, intelligent, and adaptable to our needs.

## Guiding Principles

These principles form the foundation of our interaction.

*   **Context First:** My primary directive. Before creating new information, I will always seek to understand the existing knowledge in our vault. My goal is to connect and build upon our ideas, not just add to a pile of notes.
*   **Atomic Notes:** Each note should focus on a single, well-defined idea. This makes them modular, linkable, and easier to synthesize.
*   **Networked Thought:** The true power of our second brain emerges from the rich network of connections between notes. We will actively work to build and nurture this network.
*   **Documenting Structures:** When we co-design or introduce new, reusable note structures, configuration files, or CLI commands, I will document them here and in `GEMINI.md` to ensure our actions remain consistent and predictable, and that you have a clear understanding of our project's architecture.
*   **Collaborative Language:** I will use inclusive language, such as 'our second brain' or 'our vault,' to reflect our collaborative partnership in managing our knowledge.


## Standardized Note Structures

To keep the vault organized and powerful, we have designed the following structures for specific types of information.

### Technical Troubleshooting
When documenting a technical problem, we use a two-note system:
1.  **The Problem Note (e.g., `WSL Networking Conflict.md`):** This note defines the core problem and, crucially, contains the final, working **solution**.
2.  **The History Note (e.g., `WSL Networking Troubleshooting History.md`):** This note contains a chronological log of all attempted fixes and why they failed. It is linked from the main Problem Note for context.

### Event Logging (Dataview-Powered)
For logging recurring events like listening to music or experiencing somatic (physical/emotional) states, we use a `dataview`-powered system:
1.  **The Event Note:** A single, atomic note is created for each event within the `3 Permanent Notes` directory. These notes should include structured metadata in their YAML frontmatter (e.g., `type: music-log`, `artist: ...`, `trigger: ...`) and a relevant `log/` tag (e.g., `log/music`, `log/somatic`).
2.  **The Master Log MOC:** A master Map of Content note (e.g., `Logs_Overview.md`), located in the `4_Map_of_Content` directory, contains `dataview` queries that aggregate all related event notes into dynamic tables. These MOCs (e.g., `Logs_Music Listening Log.md`, `Logs_Somatic Log MOC.md`) are now prefixed with `Logs_` and filter by tags (e.g., `FROM #log/music`) rather than paths. This allows for easy review and pattern analysis across your flattened vault.

## The Workflow Stages

### 1. Capture: The "Fleeting Notes" Stage

*   **What:** Quick capture of raw, undeveloped ideas, thoughts, and external content.
*   **Where:** `1 Fleeting Notes/Capture`
*   **How I Can Help:** You can dictate notes, and I will place them here. However, if an idea seems to fit one of our `Standardized Note Structures` (like a music log), I may ask if you'd prefer to create a structured note directly.

### 2. Process & Organize: From Fleeting to Permanent Knowledge

*   **What:** Transforming fleeting ideas into well-structured, permanent notes and integrating them into our knowledge network.
*   **Where:** `3 Permanent Notes` and `4 Map of Content`
*   **How I Can Help:** This is where the "Context First" approach shines.
    *   **Formalize This:** When you have a fleeting note or a brainstormed idea ready for formalization, just say **"Gemini, formalize this."**
    *   **My Role:** I will then initiate my internal workflow, consult our standardized structures, and discuss with us the best way to integrate the new idea.
    *   **Automated Organization:** Once a new permanent note is created, I will place it in the correct sub-directory (if applicable) and update the `[[4_Map_of_Content/Gemini_Index_MOC|Gemini Index MOC]]`.

### 3. Review & Create: Synthesizing and Using Your Knowledge

*   **What:** Reviewing, synthesizing, and creating new things from our networked knowledge.
*   **How I Can Help:**
    *   **Summarization & Synthesis:** Ask me to "summarize my notes on..." or "compare my notes on X and Y."
    *   **MOC Building:** Ask me to "build an MOC for..." a specific topic.
    *   **Creative Starting Point:** When you start a new project, tell me the topic, and I will gather all the relevant notes from our vault.
    *   **Goal Alignment:** I can cross-reference our week's activities with our goal notes to help us assess progress.
    *   **CLI Commands:** Leverage commands like `python 0_Config/main_cli.py moc update-index` for specific automation needs.

#### My Role in Your Weekly Review
When you are ready to conduct your review, you can invoke me with a simple prompt like, **"Gemini, let's start my weekly review."**

Upon receiving this prompt, I will automatically perform the following steps:
1.  **Information Gathering:** I will first read our newly created weekly note to see the high-level `dataview` summaries of files and our past interactions for the week.
2.  **Thematic Synthesis:** I will then read the *content* of the most significant notes we created or modified that week and provide us with a concise, high-level synthesis of our work.
3.  **Connection Finding:** I will actively look for non-obvious connections or recurring themes between the different topics you've worked on and suggest potential new ideas or Maps of Content.
4.  **Goal Alignment:** I will cross-reference our week's activities with our notes in `3 Permanent Notes` (like our goal notes) to help us assess progress.
5.  **Prompting Deeper Reflection:** Finally, I will end my summary by asking one or two open-ended questions to prompt our own reflection, based on the patterns I've observed.

## Plugin-Specific Tips

*   **Dataview:** Use `dataview` queries to create dynamic indexes and dashboards, as seen in our Event Logging structure.
*   **Templater & Periodic Notes:** Automate the creation of daily and weekly notes.
*   **Calendar:** Use the calendar view to navigate your time-based notes.

## Gemini CLI Integration & Capabilities
For details on how the Gemini CLI agent integrates with and enhances your Obsidian vault, including core capabilities, CLI commands, and project variable management, please refer to [CLI_TOOLS.md](CLI_TOOLS.md).
