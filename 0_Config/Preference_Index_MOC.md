---
Tags: moc, preference, config
Edited: '2025-12-22'
---

# Preference Index MOC

This MOC serves as the active configuration file for guiding the RAG synthesis process. It defines various preferences, constraints, and instructions that influence the tone, priority, and structure of the generated synthesis outputs.

- [[Unscripted Reality]] (#preference/unscripted-reality): Rejection of surveillance-based matchmaking.
- [[Voluntary Broadcast]] (#preference/voluntary-broadcast): Sovereignty over discovery intent.
## Behavioral Constraints
- These constraints define the desired behavior and style of the Gemini CLI during synthesis.
    - **Tone:** Neutral, Objective
    - **Verbosity:** Detailed
    - **Audience:** Technical
    - **Perspective:** Third-person
    - **Communication Style:** Direct, concise, and focused on actionable information.

## Content Prioritization
- These preferences guide the prioritization of information during synthesis.
    - **Keywords to emphasize:** RAG, Synthesis, Obsidian, PKM, AI Integration, Knowledge Management, Workflow Automation
    - **Topics to prioritize:** AI Integration, Knowledge Management, Workflow Automation, Data Sovereignty, Security, Budget, Ethics, Bias Mitigation

## Output Structure Preferences
- These preferences dictate the desired structure and format of the synthesis outputs.
    - **Include Summary:** Yes
    - **Include Key Takeaways:** Yes
    - **Include Ambiguities/Contradictions:** Yes
    - **Reference Style:** Wikilinks
    - **Conciseness:** Prioritize brief, direct statements, especially in tables and lists.
    - **Table Formatting:** Ensure clean Markdown table syntax with direct content in cells; avoid extraneous formatting or repetition of column headers within content.

## Core Mandates & Priorities (Static List)
These are fundamental, non-negotiable principles and high-priority tasks that the Gemini CLI MUST adhere to and factor into all syntheses and recommendations.

### Data Governance & Security
- **Data Sovereignty:** Local data storage prioritized; avoid cloud services without E2E encryption for sensitive knowledge.
- **Security Protocol:** Integrate robust security measures at every stage; always choose the more secure option.
- **Data Sensitivity Tiers:** Establish clear guidelines for processing sensitive data (local-only vs. external LLM).

### Resource & Project Constraints
- **Budget Constraints:** New software components must be free tier or under $10/month; prioritize open-source solutions.
- **Time Constraint:** Project phases not to exceed 4 hours of focused work per week; prioritize quick wins.
- **Manage Project Time Allocation:** Implement modular, quickly implementable components.

### Workflow Automation & Efficiency
- **Automate Metadata Addition:** Standard YAML frontmatter for raw Markdown chat exports upon ingestion.
- **Automate Preference Bank Population:** Design/implement mechanism for automatically populating the Preference Bank.
- **Establish CLI-Based Integration Pipeline:** Integrate browser-based Gemini chat exports directly into Obsidian.
- **Refine RAG Workflow Integration:** Enhance RAG system using `rag_cli_utils.py` functions, MOCs, and tags for context/efficiency.
- **Staged Export Review:** Local staging area with explicit user review for automated Gemini CLI exports.

### Synthesis Quality & AI Principles
- **Establish Quality Control for Synthesis:** Balance automation efficiency with manual curation for factual accuracy and preference alignment.
- **Mitigate LLM Bias:** Develop/implement protocols for mitigating personal and inherent biases in LLM-driven synthesis.
- **Implement Multi-Perspective Synthesis:** Develop RAG workflow capabilities for generating actionable knowledge from integrated chat content.
- **Preference Weighting:** Implement system for user-defined influence of "Preference Bank" on RAG synthesis, including 'neutral' option.
- **Local LLM Integration:** Research/integrate open-source, local-first LLM as alternative RAG backend for sensitive data.
- **Incremental RAG Rollout:** Adopt a modular, phased approach to RAG enhancements.

This structured format should provide clear and consistent guidance to the AI.

## Value-Driven Priorities (Dynamic List)

<!-- GEMINI_AUTO_GENERATED_PREFERENCES_START -->
| Preference | Action | Value | Effort |
|:---|:---|:---|:---|
<!-- GEMINI_AUTO_GENERATED_PREFERENCES_END -->

---
## References
- [[Log - The Uncanny Valley of Scripted Reality.md]]
