import subprocess
import json
from typing import List, Dict, Any

def run_gemini_process(audio_file_path: str) -> str:
    """
    Runs the gemini CLI command and returns the raw output string.
    """
    # Build the command as a list to avoid shell syntax errors
    command_list: List[str] = [
        "gemini",
        "-m", "gemini-2.5-flash",
        "--output-format", "json",
        f"Transcribe this audio @{audio_file_path} exactly as spoken. Output *only* the transcript text, no explanation, no translation."
    ]

    try:
        # Execute the command
        result: subprocess.CompletedProcess = subprocess.run(
            command_list,
            capture_output=True, # Capture stdout and stderr
            text=True,           # Return as string, not bytes
            check=True           # Raise error if command fails
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        # e.stderr contains the error message from the Linux command
        print(f"Error output from tool: {e.stderr}")
        return ""

def append_response_to_file(json_output: str, target_file: str) -> None:
    """
    Parses the JSON string, extracts 'response', and appends it to target_file.
    """
    if not json_output:
        print("No output to process.")
        return

    try:
        # Convert string to Python Dictionary
        data: Dict[str, Any] = json.loads(json_output)
        
        # Extract the specific key requested
        transcript_text: str = data.get("response", "")
        
        if not transcript_text:
            print("Warning: Key 'response' was empty or not found.")
            return

        # Open file in 'a' (append) mode to preserve existing content
        with open(target_file, "a", encoding="utf-8") as file:
            file.write(transcript_text)
            
        print(f"Success: Appended data to {target_file}")

    except json.JSONDecodeError:
        print("Error: The output was not valid JSON.")
        print(f"Raw output received: {json_output}")

if __name__ == "__main__":
    # CONFIGURATION
    # Change these paths to match your actual file locations
    INPUT_AUDIO: str = "/home/shoyeb/Music/test.mp3"
    OUTPUT_TEXT: str = "my_transcriptions.txt"

    print("--- Script Starting ---")
    
    # Run the logic
    cmd_output: str = run_gemini_process(INPUT_AUDIO)
    append_response_to_file(cmd_output, OUTPUT_TEXT)
    
    print("--- Script Finished ---")