import os
import sys
import json
import pytest
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.note_generation_service import NoteGenerationService

@pytest.fixture
def transcript_file(tmp_path):
    p = tmp_path / "transcript.txt"
    p.write_text("This is the transcript.")
    return str(p)

@pytest.fixture
def output_md(tmp_path):
    return str(tmp_path / "notes.md")

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_generate_success(mock_run, transcript_file, output_md):
    """Test successful note generation with default prompt."""
    mock_run.return_value = {
        "success": True, 
        "stdout": json.dumps({"response": "# Notes\nContent"})
    }
    
    success = NoteGenerationService.generate(
        transcript_path=transcript_file,
        model="model-y",
        output_path=output_md
    )
    
    assert success is True
    
    # Verify prompt construction (placeholder replaced)
    args = mock_run.call_args[0][0]
    assert f"@{transcript_file}" in args[len(args)-1]
    
    with open(output_md, 'r') as f:
        assert f.read() == "# Notes\nContent"

@patch('src.gemini_wrapper.GeminiCLIWrapper.run_command')
def test_generate_custom_prompt(mock_run, transcript_file, output_md):
    """Test note generation with custom prompt text."""
    mock_run.return_value = {
        "success": True, 
        "stdout": json.dumps({"response": "Custom output"})
    }
    
    custom_prompt = "Custom prompt for @transcription/file/location"
    success = NoteGenerationService.generate(
        transcript_path=transcript_file,
        model="model-y",
        output_path=output_md,
        prompt_text=custom_prompt
    )
    
    assert success is True
    args = mock_run.call_args[0][0]
    assert f"Custom prompt for @{transcript_file}" in args