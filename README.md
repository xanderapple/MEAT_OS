# MEAT_OS (The Logic Core)

MEAT_OS is the automation engine for the **Mind's External Archive & Toolkit**. It is a standalone, public logic repository designed to be integrated into a private Obsidian vault.

## Architecture

*   **MEAT_OS:** The public repository (this one) containing Python scripts, templates, and agent mandates.
*   **MEAT (Vault):** Your private vault where data resides. MEAT_OS is typically linked as a submodule or cloned alongside the vault.

## Setup & Installation

### 1. Prerequisites
- **Python 3.10+**
- **pip install -r requirements.txt**

### 2. Deployment to Vault
MEAT_OS uses an `install.py` script to safely deploy logic updates to your target vault while preserving your private configurations and logs.

```bash
# Clone the OS
git clone --recursive git@github.com:xanderapple/MEAT_OS.git

# Install/Update logic in your vault
python install.py --target /path/to/your/vault
```

### 3. Configure the Vault
After the first installation, go to your vault's `0_Config/Context/` directory:
1.  Copy `PROJECT_VARIABLE.template.md` to `PROJECT_VARIABLE.md`.
2.  Update the paths and API keys in `PROJECT_VARIABLE.md`.

## User-Specific Files (Protected)
The following files in your vault are **never** overwritten by `install.py` updates:
- `0_Config/Context/PROJECT_VARIABLE.md`
- `0_Config/Context/action_log.md`
- `0_Config/Context/GEMINI_INDEX.md`
- `0_Config/Context/Preference_Index.md`
- `GEMINI.md`

## Structure
- `0_Config/logic/`: Core Python modules for note management and synthesis.
- `0_Config/commands/`: CLI command definitions.
- `0_Config/prompts/`: Agent mandates and LLM instructions.
- `gemini_subagent/`: (Submodule) The underlying LLM interaction engine.