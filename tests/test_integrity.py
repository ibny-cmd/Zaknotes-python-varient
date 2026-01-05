import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

def test_imports():
    from src import job_manager
    from src import bot_engine
    from src import downloader
    from src import cookie_manager
    
    assert job_manager
    assert bot_engine
    assert downloader
    assert cookie_manager
