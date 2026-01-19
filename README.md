# MEAT_OS

This repository contains the logic and automation scripts for the MEAT system (a personal knowledge management system/vault).

## Dependencies

- **Gemini CLI:** This system is built to run as a toolset within the [Gemini CLI](https://github.com/google/gemini-cli) environment.
- **Python 3.10+**
- **Required Packages:**
  - `gemini` (Internal/Sub-agent dependency)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:xanderapple/MEAT_OS.git
    ```
2.  **Configure your environment:**
    - Navigate to `0_Config/`.
    - Copy `PROJECT_VARIABLE.template.md` to `PROJECT_VARIABLE.md`.
    - Edit `PROJECT_VARIABLE.md` and update the paths and settings for your local machine (Vault paths, API keys, etc.).

## Structure

- `0_Config/`: Core configuration, scripts, and logic.

## Usage

The primary entry point is `0_Config/main_cli.py`. It is designed to be invoked by the Gemini CLI to automate vault operations like synthesis, RAG extraction, and note management.
