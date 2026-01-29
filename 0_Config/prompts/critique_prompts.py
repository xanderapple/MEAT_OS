from . import mandates

def get_critique_prompt(source_filename, draft_filename):
    """
    Generates a prompt for the Sub-Agent to critique a preliminary synthesis.
    """
    return f"""
Your task is to perform a strict quality audit of a Preliminary Synthesis draft. You must compare it against the original source and the "Architect of Trust" mandates.

### INPUTS
1. **Original Source:** `{source_filename}`
2. **Preliminary Draft:** `{draft_filename}`

**Action Required:** You MUST use `read_file` to read BOTH files before starting your analysis.

### AUDIT CRITERIA

#### 1. THE HIGH-FIDELITY MANDATE (Completeness)
*   **Mandate:** "{mandates.HIGH_FIDELITY_MANDATE}"
*   **Audit Task:** Did the draft collapse or summarize distinct technical details? 
*   **EVIDENCE REQUIRED:** Identify any significant details/metaphors from the Source that are missing or overly generalized in the Draft. Quote the Source text vs. the Draft text. If the draft is comprehensive, state "High Fidelity Maintained".

#### 2. THE VOICE & NUANCE MANDATE
*   **Mandate:** "{mandates.VOICE_MANDATE}"
*   **Audit Task:** 
    *   **First Person Check:** Scan Stream A. Does it use "I" consistently? If it uses "The user...", it FAILS.
    *   **Emotional Intensity:** Did the draft sanitize strong feelings? Quote an example of "Sanitized" vs "Raw".

#### 3. THE TAGGING MANDATE
*   **Mandate:** "{mandates.TAGGING_MANDATE}"
*   **Audit Task:** Does Stream A contain specific hashtags like `#value/` or `#preference/`? If NO tags are present, it FAILS.

#### 4. THE LANGUAGE & IDIOM MANDATE
*   **Mandate:** "{mandates.LANGUAGE_MANDATE}"
*   **Audit Task:** 
    *   **Translation Check:** Did the draft translate specific Chinese idioms, metaphors, or "spirit" phrases into English? FAILS if yes.
    *   **Parenthesis Check:** Did it use "(Translation)" or "(Original)"? FAILS if yes.
    *   **Pinyin Check:** Did it use Pinyin instead of characters? FAILS if yes.

#### 5. AFFIRMATION RIGOR
*   Did the draft include AI-generated ideas that the user did NOT explicitly affirm?
*   Is the separation between Stream A (User) and Stream B (LLM) crystal clear?

### OUTPUT STRUCTURE (Critique Report)

# Synthesis Critique Report

## VERDICT: [PASS / FAIL]
(A PASS means the draft is ready for finalization. A FAIL means it requires a rewrite. Be STRICT.)

## Evidence of Violations
*   **Missing Details (Quote Comparison):**
    *   *Source:* "..."
    *   *Draft:* "..." (or "Missing")
*   **Voice Violation:**
    *   *Example:* (e.g., "The user thinks..." instead of "I think...")
*   **Tagging Violation:**
    *   *Observation:* (e.g., "No #value/ tags found.")

## Feedback for Refinement
(Provide direct instructions on what to fix if the verdict is FAIL.)

**Action Required:** Write your report.
"""

def get_refinement_prompt(source_filename, draft_filename, feedback_filename):
    """
    Generates a prompt for the Sub-Agent to refine a draft based on critique.
    """
    return f"""
You are refining a Preliminary Synthesis draft based on a Critique Report.

### INPUTS
1. **Original Source:** `{source_filename}`
2. **Previous Draft:** `{draft_filename}`
3. **Critique Report:** `{feedback_filename}`

**Action Required:** You MUST read all three files.

### TASK
Rewrite the Preliminary Synthesis. You MUST address every violation and piece of feedback listed in the Critique Report while maintaining the original mandates.
"""