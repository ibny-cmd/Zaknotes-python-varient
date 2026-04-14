import os
import sys
import shutil
import logging
from unittest.mock import MagicMock, patch
from src.pipeline import ProcessingPipeline
from src.config_manager import ConfigManager
from src.job_manager import JobManager

# Configure logging to see the pipeline progress
logging.basicConfig(level=logging.INFO, format='%(message)s')

def verify_full_flow():
    print("🚀 Verifying Phase 5: Final End-to-End Flow (Simulated)...")
    
    # 1. Setup mock config for both integrations enabled
    config = ConfigManager(config_file="final_test_config.json")
    config.set("notion_integration_enabled", True)
    config.set("rclone_integration_enabled", True)
    config.save()
    
    # 2. Setup Job Manager
    with patch('src.job_manager.HISTORY_FILE', 'final_test_history.json'):
        manager = JobManager()
    
    # 3. Setup Pipeline with mocks for API and Services
    with patch('src.pipeline.GeminiAPIWrapper') as MockAPI, \
         patch('src.pipeline.NotionService') as MockNotion, \
         patch('src.pipeline.RcloneService') as MockRclone, \
         patch('src.pipeline.NoteGenerationService') as MockNoteGen, \
         patch('src.pipeline.AudioProcessor') as MockAudioProc, \
         patch('src.pipeline.download_audio') as MockDownload, \
         patch('src.pipeline.get_expected_audio_path') as MockGetPath, \
         patch('src.pipeline.FileCleanupService') as MockCleanup, \
         patch('src.pipeline.RcloneConfigManager') as MockRcloneConfig, \
         patch('src.pipeline.NotionConfigManager') as MockNotionConfig:
        
        # Setup mock behavior
        mock_api = MockAPI.return_value
        mock_api.generate_content_with_file.return_value = "Simulated Transcript"
        mock_api.backoff_manager = MagicMock()
        
        mock_notion = MockNotion.return_value
        mock_notion.create_page.return_value = "https://notion.so/test_page"
        
        mock_rclone = MockRclone.return_value
        mock_rclone.push_note.return_value = (True, "Successfully pushed to rclone")
        
        mock_rclone_config = MockRcloneConfig.return_value
        mock_rclone_config.get_credentials.return_value = ("test_remote", "test/path")
        
        mock_notion_config = MockNotionConfig.return_value
        mock_notion_config.get_credentials.return_value = ("test_secret", "test_db")
        
        MockNoteGen.generate.return_value = True
        MockAudioProc.optimize_audio.return_value = True
        MockAudioProc.process_for_transcription.return_value = ["temp/test_chunk.mp3"]
        MockDownload.return_value = "downloads/test.mp3"
        MockGetPath.return_value = "downloads/test.mp3"
        
        # Pipeline init
        pipeline = ProcessingPipeline(config, api_wrapper=mock_api, job_manager=manager)
        
        # 4. Execute a simulated job
        job = {"id": "final_test_1", "name": "E2E Test Note", "status": "queue"}
        manager.history.append(job)
        manager.save_history()
        
        # Create dummy files that the pipeline expects
        os.makedirs("temp", exist_ok=True)
        os.makedirs("downloads", exist_ok=True)
        os.makedirs("notes", exist_ok=True)
        
        with open("downloads/test.mp3", "w") as f: f.write("dummy")
        with open("temp/test_chunk.mp3", "w") as f: f.write("dummy")
        with open("notes/E2E_Test_Note.md", "w") as f: f.write("dummy notes")
        
        print("\n--- Running pipeline.execute_job ---")
        success = pipeline.execute_job(job)
        print("--- Pipeline execution finished ---\n")
        
        # 5. Verify outcomes
        print(f"Pipeline Success: {success}")
        
        notion_called = mock_notion.create_page.called
        rclone_called = mock_rclone.push_note.called
        print(f"Notion Push Called: {notion_called}")
        print(f"Rclone Push Called: {rclone_called}")
        
        job_in_hist = manager.get_job("final_test_1")
        final_job_status = job_in_hist['status'] if job_in_hist else "NOT_FOUND"
        print(f"Final Job Status: {final_job_status}")
        
        # Cleanup dummy files
        for d in ["temp", "downloads", "notes"]:
            if os.path.exists(d):
                shutil.rmtree(d)
        if os.path.exists("final_test_config.json"): os.remove("final_test_config.json")
        if os.path.exists("final_test_history.json"): os.remove("final_test_history.json")
        
        if success and notion_called and rclone_called and final_job_status == 'completed':
            print("\n✅ PASSED: Full End-to-End Flow verification successful")
            return True
        else:
            print("\n❌ FAILED: Full End-to-End Flow verification failed")
            return False

if __name__ == "__main__":
    if not verify_full_flow():
        sys.exit(1)
