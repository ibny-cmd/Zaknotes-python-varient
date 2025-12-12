from job_manager import JobManager
import os

def test_logic():
    # Clear old files for testing
    if os.path.exists("queue.json"): os.remove("queue.json")
    
    jm = JobManager()
    
    print("--- TEST CASE 1: Your Complex Example ---")
    names = "chemistry, biology"
    urls = "(urla, urlb) , (urlc, urld)"
    
    print(f"Names: {names}")
    print(f"URLs:  {urls}")
    
    jobs = jm.create_jobs(names, urls)
    
    print("\nGenerated Jobs:")
    for j in jobs:
        print(f"[{j['name']}] -> {j['url']}")

    # Verification Logic
    expected = [
        ("chemistry 1", "urla"),
        ("chemistry 2", "urlb"),
        ("biology 1", "urlc"),
        ("biology 2", "urld")
    ]
    
    passed = True
    if len(jobs) != 4:
        passed = False
    for i, (exp_name, exp_url) in enumerate(expected):
        if jobs[i]['name'] != exp_name or jobs[i]['url'] != exp_url:
            passed = False
            
    print(f"\nTest 1 Result: {'PASSED ✅' if passed else 'FAILED ❌'}")

    print("\n--- TEST CASE 2: Single URL (No numbering) ---")
    names = "Math"
    urls = "http://math.com"
    jobs = jm.create_jobs(names, urls)
    print(f"Job: [{jobs[-1]['name']}] -> {jobs[-1]['url']}")
    
    if jobs[-1]['name'] == "Math":
        print("Test 2 Result: PASSED ✅")
    else:
        print("Test 2 Result: FAILED ❌ (Name should not have number)")

if __name__ == "__main__":
    test_logic()