import os
import pytest
from src.audio_processor import AudioProcessor

def test_time_based_chunking_restoration(tmp_path):
    # This test needs a real (short) mp3 to verify ffprobe/ffmpeg if possible,
    # but we can also mock the subprocess calls.
    # For now, let's just test that process_for_transcription accepts segment_time.
    
    input_file = tmp_path / "test.mp3"
    input_file.write_bytes(b"fake mp3 content")
    
    output_dir = tmp_path / "chunks"
    output_dir.mkdir()
    
    # We expect process_for_transcription to now support segment_time
    # If it still uses max_size_mb as primary, we'll see it in the behavior.
    
    # Let's mock optimize_audio to return True and just copy the file
    with pytest.MonkeyPatch.context() as m:
        m.setattr(AudioProcessor, "optimize_audio", lambda *args, **kwargs: True)
        # Mock get_duration to return 3600s (1h)
        m.setattr(AudioProcessor, "get_duration", lambda *args, **kwargs: 3600.0)
        # Mock is_under_limit to return False so it triggers splitting
        m.setattr(AudioProcessor, "is_under_limit", lambda *args, **kwargs: False)
        
        # Capture the call to split_into_chunks or similar
        split_calls = []
        def mock_split(input_path, output_pattern, segment_time, threads=0):
            split_calls.append(segment_time)
            # Create a fake chunk
            chunk_path = str(tmp_path / "chunks" / "chunk_001.mp3")
            with open(chunk_path, "w") as f: f.write("chunk")
            return [chunk_path]
            
        m.setattr(AudioProcessor, "split_into_chunks", mock_split)
        
        chunks = AudioProcessor.process_for_transcription(
            str(input_file), 
            segment_time=600, # 10 minutes
            output_dir=str(output_dir)
        )
        
        assert len(chunks) == 1
        assert 600 in split_calls
