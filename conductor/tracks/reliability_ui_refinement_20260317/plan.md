# Implementation Plan: Reliability, UI, and Local Media Refinements

## Phase 1: Reliability - Exponential Backoff and Empty Chunk Retry

- [ ] Task 1: Implement Exponential Backoff Logic.
    - [ ] Create a utility for exponential backoff in `src/gemini_api_wrapper.py` or a dedicated module.
    - [ ] Update all static delays (retry, post-chunk, post-generation) to use the new backoff utility.
    - [ ] Add unit tests for the backoff utility.
- [ ] Task 2: Implement Empty Transcription Chunk Detection.
    - [ ] Update `src/gemini_api_wrapper.py` (or the relevant service) to identify empty/whitespace responses.
    - [ ] Implement an indefinite retry loop for empty chunks using the new exponential backoff.
    - [ ] Ensure that a chunk is only marked as "completed" in the state file if it contains non-empty text.
    - [ ] Add unit tests to simulate empty Gemini responses and verify the retry behavior.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: UI/UX - Interactive Local Media and Time-Based Chunking

- [ ] Task 1: Restore Time-Based Chunking.
    - [ ] Remove the file-based chunking logic from `src/audio_processor.py`.
    - [ ] Ensure the existing time-based chunking logic (default 30 mins) is functional.
    - [ ] Verify that the "configure audio chunks" menu option correctly updates this setting.
    - [ ] Add unit tests for time-based chunking.
- [ ] Task 2: Integrate Local Media into the Interactive Menu.
    - [ ] Modify the main entry point (e.g., `zaknotes.py`) to add a "Process Local Media" option under "start note generation".
    - [ ] Update the menu logic to handle the new option, ensuring it triggers the existing local media processing flow.
    - [ ] Maintain consistent file naming and chronology logic for local media.
    - [ ] Add a basic integration test for the new menu option.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)
