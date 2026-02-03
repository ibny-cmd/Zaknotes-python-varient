# Specification: Replace AI Studio with Gemini CLI for Audio Processing

## 1. Overview
The goal of this track is to replace the existing AI Studio web automation logic with a direct integration using the `gemini` CLI tool. This change streamlines the audio-to-note pipeline by processing downloaded audio files locally, chunking them, transcribing them via Gemini, and then generating study notes. The final output will be a PDF, saved in a designated directory.

## 2. Functional Requirements

### 2.1 Audio Processing
- **Validation Logic:**
  - **Check Size First:** Check the file size of the downloaded audio.
  - **Case A (< 20MB):** If the file is less than 20MB, skip chunking and proceed directly to transcription.
  - **Case B (>= 20MB):**
    - Split the audio into 30-minute chunks using `ffmpeg`.
    - **Re-Validation:** Check the size of each resulting chunk.
    - If any chunk is still >= 20MB, re-process it (e.g., lower bitrate or shorter duration) until it is < 20MB.
- **Tool:** Use `ffmpeg` for splitting and resizing/re-encoding.
- **Cleanup:** Original audio chunks MUST be deleted after successful transcription.
- **Manual Cleanup:** Provide a utility/option to manually clean up stranded audio chunks (e.g., from previous failed runs).

### 2.2 Transcription (Step 1)
- **Tool:** Execute the `gemini` CLI for each audio file (or chunk).
- **Model:** Use `gemini-2.5-flash` (or user-configured model).
- **Prompt:** Use the prompt structure defined in `@demo/transcription.py`.
- **Output:** Save the raw JSON response from the CLI.
- **Parsing:** Extract the transcript text from the JSON response and append it to a single `.txt` file for the entire job.
- **Cleanup:** Delete the temporary JSON response files after parsing.

### 2.3 Note Generation (Step 2)
- **Input:** The consolidated transcript `.txt` file from Step 2.2.
- **Tool:** Execute the `gemini` CLI.
- **Model:** Use `gemini-3-pro-preview` by default (configurable).
- **Prompt:** Use the content from `@demo/note generation prompt.txt`.
- **Output:** Save the generated notes to a Markdown (`.md`) file.
- **Cleanup:** Delete the transcript `.txt` file after successful note generation.

### 2.4 PDF Generation (Step 3)
- **Input:** The generated Markdown (`.md`) notes.
- **Logic:** Use the existing PDF generation logic (ref. `src/pdf_converter_py.py` or similar).
- **Output:** Save the final PDF to the `./pdfs/` directory (create if it doesn't exist).
- **Cleanup:** Delete the Markdown `.md` file after successful PDF generation.
- **Final State:** The only remaining artifact for the job should be the `.pdf` file in `./pdfs/`.

### 2.5 Job Management & Error Handling
- **Job Status:**
  - If ANY step (transcription, note gen, etc.) fails, the job status MUST be updated to `failed`.
  - **Critical:** If a job fails, ALL currently running jobs (in the current batch/session) MUST also be marked as `failed` to prevent cascading issues or wasted resources.
  - Use the format in `@demo/example error.json` to detect errors if applicable, or standard CLI exit codes/stderr.
- **Error Strategy:** Fail-Fast for the entire batch.
- **Configuration:**
  - Update `@zaknotes.py` menu.
  - Remove "Refresh Browser Profile".
  - Add "Configure Models" option to allow users to specify which Gemini model to use for Transcription vs. Note Generation.

## 3. Non-Functional Requirements
- **Performance:** Chunking should be efficient. Large files should not crash the script.
- **Reliability:** The system should handle network errors from the CLI gracefully by marking the job as failed rather than crashing the entire application.
- **Dependencies:** Ensure `ffmpeg` is checked/available or warn the user.

## 4. Acceptance Criteria
1.  **Audio Processing:** Files < 20MB are processed directly. Files >= 20MB are chunked (30m) and validated to be < 20MB.
2.  **Transcription:** `gemini` CLI is called correctly; transcripts are merged.
3.  **Notes:** `gemini` CLI is called with the specific prompt; notes are saved as MD.
4.  **PDF:** MD is converted to PDF; PDF is saved in `./pdfs/`.
5.  **Cleanup:** Intermediate files (audio chunks, .txt, .md) are removed automatically.
6.  **Manual Cleanup:** User can trigger a cleanup of leftover chunks.
7.  **Configuration:** User can change models via the CLI menu.
8.  **Error Handling:** If one job fails, all running jobs in the batch are marked as failed.

## 5. Out of Scope
-   Browser automation (Puppeteer/Selenium) - strictly removing this.
-   Complex retry mechanisms (simple failure marking only).
