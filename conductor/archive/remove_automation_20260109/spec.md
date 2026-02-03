# Specification: Remove Browser Automation and UI Elements

## Overview
This track focuses on removing the dependency on browser automation (specifically AI Studio automation) and the user interface elements from the Zaknotes project. The goal is to strip down the codebase to its core video downloading and PDF conversion capabilities, replacing automated browser interactions with placeholders. **Additionally, the remaining browser automation tasks (Vimeo URL extraction) will be migrated from Selenium to Playwright to consolidate dependencies.**

## Functional Requirements
- **Code Removal:**
    - Delete `src/browser_driver.py`.
    - Delete `src/bot_engine.py`.
    - Delete the entire `src/ui_elements/` directory.
    - Delete the entire `tests/` directory (as they largely depend on the removed components).
- **Placeholder Implementation:**
    - Identify all references to the removed modules/classes in remaining files (e.g., `zaknotes.py`, `src/job_manager.py`).
    - Replace calls to these modules with simple log messages (e.g., `print("Browser automation placeholder triggered")`).
    - Ensure the application remains runnable (no import errors or crashes).
- **Dependency Consolidation (Selenium -> Playwright):**
    - Refactor `src/find_vimeo_url.py` to use `playwright` instead of `selenium`.
    - Ensure the Vimeo URL extraction logic remains functional (including cookie handling if applicable).
    - Remove `selenium` from `requirements.txt` after migration.
- **Preservation:**
    - Keep `src/find_vimeo_url.py` (refactored) and all cookie-related files/logic as they are required for video downloading.

## Non-Functional Requirements
- **Git Hygiene:** Every commit must be followed by a push to the remote repository.
- **Maintainability:** Placeholders should be clearly marked so they can be easily replaced or removed in the future.

## Acceptance Criteria
1. The specified files and directories are deleted.
2. The application (specifically `zaknotes.py` or other entry points) can be executed without import errors.
3. Triggering functionality that previously used browser automation results in a log message instead of a crash.
4. `src/find_vimeo_url.py` functions correctly using Playwright.
5. `selenium` is removed from `requirements.txt`.
6. All changes are pushed to the remote repository.

## Out of Scope
- Implementing a new UI.
- Rewriting the core video download or PDF conversion logic (beyond the Selenium -> Playwright migration).
