# Specification: Comprehensive Project Documentation (Arch Linux Focus)

## Overview
This track involves rewriting the project's `README.md` into a comprehensive, user-friendly guide tailored for Arch Linux users. It will cover everything from initial system setup to advanced feature usage, ensuring new users can easily navigate and harness the full potential of Zaknotes.

## Target Audience
- **Primary:** New users running Arch Linux.
- **Tone:** Helpful, step-by-step, and instructional.

## Functional Requirements
- **Complete README.md Overhaul:** The existing `README.md` will be replaced with an all-in-one guide.
- **Section: Introduction:** Explain the project's purpose: converting class URLs (YouTube, Facebook, etc.) into high-quality Markdown study notes using the Gemini API.
- **Section: Arch Linux Installation & Prerequisites:**
    - Detailed system-level prerequisites: `ffmpeg`, `nodejs` (for EJS), and `uv`.
    - Specific Arch Linux commands (e.g., `sudo pacman -S ffmpeg nodejs`).
- **Section: Quick Start Guide:** A 3-step "Happy Path" (Install -> Add API Key -> Generate Notes).
- **Section: Full Feature Deep-Dive:**
    - **Note Generation:** Detailed explanation of the sub-menu (Start New, Add to Queue, Process Old).
    - **API Key Management:** How to add/remove keys and interpret the "View Quota Status" report.
    - **Audio Chunking:** Guidance on when and how to configure chunking time.
    - **Cleanup:** Explaining the utility of cleaning stranded chunks.
- **Section: Troubleshooting:** 
    - Handling "429 Quota Exceeded" (Key rotation logic).
    - YouTube "n challenge" issues (Ensuring Node.js is in PATH).
    - Media download failures.

## Content & Formatting
- **Visual Aids:** Extensive use of code blocks for commands and bulleted/numbered lists for steps.
- **Arch-Centric:** Use Arch-specific package names and conventions.
- **Clarity:** Ensure every menu option in `zaknotes.py` is explained.

## Acceptance Criteria
- [ ] `README.md` contains all defined sections.
- [ ] Installation instructions are verified for Arch Linux.
- [ ] Every feature in the current `zaknotes.py` menu is documented.
- [ ] The tone remains helpful and accessible for beginners.
