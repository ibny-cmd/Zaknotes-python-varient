# Specification: Reliability, UI, and Local Media Refinements

## Overview
This track addresses three key areas:
1. **Reliability:** Enhance the Gemini transcription process to retry indefinitely with exponential backoff when a chunk returns empty or whitespace-only content.
2. **Backoff Expansion:** Apply exponential backoff to all current delays (post-chunk, retry, post-generation) starting from their current defaults (e.g., 10s for empty chunks, 30s for 429 errors).
3. **UI/UX:** Integrate local file handling into the interactive menu under the "start note generation" section.
4. **Configuration:** Revert to the existing time-based audio chunking logic (default 30 mins) and ensure it's editable via the "configure audio chunks" menu option.

## Functional Requirements
- **Gemini Empty Chunk Retry:**
    - Detect "empty" transcription chunks (whitespace/minimal noise).
    - Implement indefinite retry with exponential backoff for these cases.
    - Ensure strict sequence resumption: a chunk is only "done" when it contains non-empty text.
- **Global Exponential Backoff:**
    - Replace static delays (e.g., 30s for 429 errors, post-chunk pauses) with exponential backoff logic.
    - Start backoff from current project default delays.
- **Interactive Local Media Handling:**
    - Add a "Process Local Media" option under the "start note generation" menu.
    - Maintain existing logic for file naming, chronology, and `uploads/` folder scanning.
- **Time-Based Chunking Restoration:**
    - Remove the file-based chunking logic.
    - Ensure the existing time-based chunking logic (default 30 mins) works correctly.
    - Verify it's editable via the "configure audio chunks" menu option.

## Acceptance Criteria
- [ ] Simulated empty Gemini response triggers an indefinite retry with backoff.
- [ ] All API-related delays (retries, post-chunk) use exponential backoff.
- [ ] "Process Local Media" is available under "start note generation" and functions correctly.
- [ ] Audio is chunked based on a configurable time interval (default 30 mins).
- [ ] Job resumption correctly restarts from an incomplete/empty chunk.

## Out of Scope
- Major architectural changes to the `gemini_api_wrapper.py` beyond retry/backoff logic.
- Changes to the Notion integration or PDF conversion.
