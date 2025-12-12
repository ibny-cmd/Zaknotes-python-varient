from downloader import download_audio

# Test Job
job = {
    "name": "Test_Audio",
    # REPLACE THIS URL WITH A REAL ONE FOR TESTING
    "url": "https://edgecoursebd.com/mycourses/346?lesson=89740" 
}

try:
    download_audio(job)
except Exception as e:
    print(f"Test Failed: {e}")