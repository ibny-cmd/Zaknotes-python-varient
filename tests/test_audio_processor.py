import os
import sys
import pytest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio_processor import AudioProcessor

@pytest.fixture
def dummy_file(tmp_path):
    """Creates a 1KB dummy file."""
    p = tmp_path / "test.mp3"
    p.write_bytes(b"\0" * 1024)
    return str(p)

def test_get_file_size(dummy_file):
    """Test retrieving file size in bytes."""
    size = AudioProcessor.get_file_size(dummy_file)
    assert size == 1024

def test_is_under_limit(dummy_file):
    """Test file size limit validation."""
    # 1KB is under 1MB limit
    assert AudioProcessor.is_under_limit(dummy_file, limit_mb=1) is True
    
    # Create a 2MB file
    large_file = os.path.join(os.path.dirname(dummy_file), "large.mp3")
    with open(large_file, "wb") as f:
        f.write(b"\0" * (2 * 1024 * 1024))
    
    # 2MB is NOT under 1MB limit
    assert AudioProcessor.is_under_limit(large_file, limit_mb=1) is False
