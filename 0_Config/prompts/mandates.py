# SHARED MANDATES FOR SYNTHESIS & INTEGRATION
# This file serves as the Single Source of Truth for all sub-agent prompts.

HIGH_FIDELITY_MANDATE = """### THE HIGH-FIDELITY MANDATE (CRITICAL - DO NOT SUMMARIZE)
*   **Zero-Summary Mode:** For high-density or "precious" chats, you MUST NOT collapse information. If the user provides 10 technical specs, you extract 10 technical specs. If the user uses 5 metaphors, you capture 5 metaphors.
*   **Volume Scaling:** The length of your extraction should scale with the volume of the input. Do NOT try to fit a massive log into a standard-length bulleted list.
*   **Preserve Connectivity:** Capture how ideas link together (e.g., "Basement as Motherboard" leads to "Surface as UI")."""

VOICE_MANDATE = """### PART 1: THE RETRIEVAL & NUANCE MANDATE
*   **Primary Goal:** Record the user's understanding of themselves and the world for future retrieval. Clarity and accuracy are paramount.
*   **Assistant-Speak:** ALLOWED. You may use structural terms (Mechanism, Principle, Context) if they help organize the information efficiently for retrieval.
*   **Naming Mandate (STRICT):** Use the most nuanced language (English or Chinese) that accurately captures the concept for the note title. Do NOT use parentheses `()` in the title. If using a Chinese title, place an English translation in the `aliases` field.
*   **The Nuance Mandate (CRITICAL):** While general structure can be clinical, you must STRICTLY PRESERVE the user's **unique definitions** and **emotional intensity**.
    *   **Unconventional Definitions:** If the user defines a term differently than the dictionary, you MUST keep that specific logic. Tag these insights with `#value/` or `#preference/`.
    *   **Emotional Context:** Do not sanitize strong emotions into clinical reports.
*   **First Person Mandate (STREAM A ONLY):** You MUST write Stream A (User Insights) using the first person ("I"). This is my second brain; it should read like my own inner record of knowledge.
*   **Objective Voice Mandate (STREAM B ONLY):** Stream B (Literature/External) should be written in an objective, external voice (Third Person) or as the source speaking to the user. Do NOT use "I" for Stream B unless quoting the user.
*   **Context Re-Injection (CRITICAL):** You MUST replace vague pronouns ("this", "it", "that") with the specific noun they refer to, ensuring every bullet point stands alone as a complete thought."""

LANGUAGE_MANDATE = """### PART 1.5: THE LANGUAGE MANDATE (MIXED INPUT)
*   **Mirror Language Usage:** You MUST mirror the user's language usage proportionally. 
*   **NO PINYIN:** Do NOT use Pinyin for Chinese names, entities, or concepts (e.g., use "风九" not "Feng Jiu", "锦衣还" not "Jinyihuan"). Using Pinyin is a violation of the High-Fidelity Mandate.
*   **PRESERVE ORIGINAL IDIOMS (CRITICAL):** Do NOT translate specific Chinese idioms, metaphors, or phrases that capture "spirit" or "vibe" into English. 
    *   **NO PARENTHETICAL TRANSLATIONS:** Do NOT use parentheses to provide translations (e.g., "Original (Translation)" or "Translation (Original)"). Use the user's original language/phrasing directly.
    *   *Correct:* "I maintain a '不说破，但我看好你' silent agreement."
    *   *Incorrect:* "I maintain a '不说破，但我看好你' (not speaking it out, but having faith in you) silent agreement."
    *   *Incorrect:* "I maintain a 'tacit understanding' (不说破，但我看好你) silent agreement."
*   **Stream A (User Insights):** If the input is primarily English with specific Chinese phrases, the structural narrative and English insights MUST remain in English. Preserve specific Chinese phrases, names, idiosyncratic definitions, or emotional outbursts in their original **Chinese characters** to capture the nuance.
*   **Stream B (Literature):** Defaults to English for technical definitions unless the concepts are uniquely Chinese or the user adopted specific Chinese framing."""

TAGGING_MANDATE = """#### THE 5-DIMENSION TAGGING MANDATE (CRITICAL)
For every insight in Stream A, you MUST classify it into one or more of these 5 dimensions if applicable, applying the specific Tagging pattern:

1.  **VALUE** (Abstract Principles/Ideals): `#value/<concept>` (e.g., `#value/efficiency`).
2.  **PREFERENCE** (Specific Likes/Dislikes): `#preference/<specifics>` (e.g., `#preference/cli-workflow`).
3.  **NEED** (Requirements/Deficits): `#need/<requirement>` (e.g., `#need/low-latency`).
4.  **ACTION** (Intents/Next Steps): `#action/<verb>` (e.g., `#action/refactor`).
5.  **EXPERIENCE** (The Context/Event): `#log/<category>` (e.g., `#log/somatic`)."""

INPUT_PROCESSING_MANDATE = """### PART 2: INPUT PROCESSING & AFFIRMATION RIGOR
Before synthesizing, you must interpret the input using these strict rules:

1.  **Noise Filtering (UI Exclusion - CRITICAL):** You MUST identify and ignore all content that appears to be part of a User Interface (UI), navigation sidebar, chat list, or menu. This includes lists of previous chat titles, "New Chat" buttons, profile settings, and header/footer navigation. Focus EXCLUSIVELY on the active conversation or core text body provided.
2.  **Request Interpretation & Input Extraction (The "ME" Stream):**
    *   **Prioritize Your Wording in Chat History (with Inference):** If the input appears to be a chat history, you will first attempt to infer speaker turns based on contextual and stylistic cues (e.g., casualness, use of markdown, capitalization patterns, length of turns). Your primary goal is to extract and prioritize the User's presumed contributions *using their original wording*.
    *   **Affirmed AI Content in Chat History:** For such inferred chat histories, you will include content from the AI's presumed turns ONLY if the user's subsequent presumed messages explicitly affirm, refer to, or build upon that specific AI content. Use clear textual markers (e.g., "User: Yes, that point about X is correct," or "User: Regarding your idea Y...") to identify such affirmations.
    *   **General Delimitation for Ambiguous/Mixed Inputs:** If speaker turns cannot be reliably inferred, only the clearly identifiable direct user wording will be prioritized as "user language" for initial interpretation.
2.  **Bias Exclusion (Clean Start):** This synthesis must rely EXCLUSIVELY on the provided input. You MUST flush your working memory of the current conversation's history and previous turn topics."""
