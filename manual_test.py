from job_manager import JobManager
import sys

def main_menu():
    jm = JobManager()

    print("==========================================")
    print("   PHASE 1: LOGIC & HISTORY TESTER")
    print("==========================================\n")

    # --- STEP 1: CHECK PENDING JOBS ---
    pending_jobs = jm.get_pending_from_last_150()
    
    if pending_jobs:
        print(f"⚠️  Found {len(pending_jobs)} incomplete jobs in history.")
        print("1. Cancel them (Start fresh)")
        print("2. Resume them")
        print("3. Resume + Add more jobs")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            jm.cancel_pending()
            print("❌ Previous jobs cancelled.")
            pending_jobs = [] # Clear local list
        elif choice == '2':
            print("🔄 Resuming previous jobs...")
            # In a real app, we would jump straight to processing here
            # But for testing, we just print them
        elif choice == '3':
            print("➕ Keeping previous jobs and asking for new ones...")
            # We keep pending_jobs list as is
        else:
            print("Invalid choice. Defaulting to Resume (2).")

    # --- STEP 2: GET NEW INPUT (If needed) ---
    # We ask for input if:
    # A) There were no pending jobs
    # B) User chose Option 1 (Cancel) -> so we need new jobs
    # C) User chose Option 3 (Resume + Add)
    
    need_input = False
    if not pending_jobs: need_input = True
    if pending_jobs and choice == '3': need_input = True
    if pending_jobs and choice == '1': need_input = True

    if need_input:
        print("\n--- NEW JOB INPUT ---")
        names = input("Enter NAMES: ")
        urls = input("Enter URLs:  ")
        
        if names and urls:
            new_added = jm.add_jobs(names, urls)
            print(f"\n✅ Added {len(new_added)} new jobs.")
            # Merge lists for display
            pending_jobs.extend(new_added)

    # --- STEP 3: SHOW FINAL QUEUE ---
    print("\n" + "="*30)
    print("   CURRENT PROCESSING QUEUE")
    print("="*30)
    
    # Reload from file to be sure we see what is actually saved
    jm.load_history() 
    final_queue = [j for j in jm.history if j['status'] == 'queue']
    
    if not final_queue:
        print("(Empty)")
    else:
        for j in final_queue:
            print(f"[{j['status'].upper()}] {j['name']} -> {j['url']}")

if __name__ == "__main__":
    main_menu()