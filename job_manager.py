import re
import json
import os
from datetime import datetime

QUEUE_FILE = "queue.json"
HISTORY_FILE = "history.json"

class JobManager:
    def __init__(self):
        self.queue = []
        self.load_queue()

    def smart_split(self, text):
        """
        Splits text by comma, semicolon, pipe, or newline,
        BUT ignores delimiters inside parentheses ( ).
        """
        if not text:
            return []
        
        # This regex looks for delimiters but skips content inside (...)
        # It matches a delimiter only if it's followed by an even number of closing parens (or 0)
        # This is a simplified approach. For strictly nested stuff, we'd need a parser, 
        # but this works for standard (a,b) lists.
        pattern = r'[|;,\n](?![^(]*\))'
        parts = re.split(pattern, text)
        return [p.strip() for p in parts if p.strip()]

    def parse_group(self, text):
        """
        If text looks like "(a, b)", remove parens and split by comma.
        Else return [text].
        """
        text = text.strip()
        if text.startswith("(") and text.endswith(")"):
            content = text[1:-1]
            return [x.strip() for x in content.split(",") if x.strip()]
        return [text]

    def create_jobs(self, name_input, url_input):
        name_slots = self.smart_split(name_input)
        url_slots = self.smart_split(url_input)
        
        new_jobs = []

        # We loop through the URL slots as the anchor
        for i, url_slot in enumerate(url_slots):
            # Get corresponding name, or use "Untitled X" if run out
            if i < len(name_slots):
                base_name = name_slots[i]
            else:
                base_name = f"Untitled {i+1}"

            # Expand the URL slot (check for groups)
            expanded_urls = self.parse_group(url_slot)
            
            # Logic Rule 3: Numbering
            if len(expanded_urls) > 1:
                # If slot has multiple URLs, number the name: Name 1, Name 2
                for j, url in enumerate(expanded_urls):
                    job_name = f"{base_name} {j+1}"
                    new_jobs.append({
                        "id": f"{datetime.now().timestamp()}_{i}_{j}",
                        "name": job_name,
                        "url": url,
                        "status": "pending"
                    })
            else:
                # If slot has 1 URL, keep name as is
                new_jobs.append({
                    "id": f"{datetime.now().timestamp()}_{i}",
                    "name": base_name,
                    "url": expanded_urls[0],
                    "status": "pending"
                })
        
        self.queue.extend(new_jobs)
        self.save_queue()
        return new_jobs

    def save_queue(self):
        with open(QUEUE_FILE, 'w') as f:
            json.dump(self.queue, f, indent=4)

    def load_queue(self):
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                self.queue = json.load(f)

    def get_next_job(self):
        pending = [j for j in self.queue if j['status'] == 'pending']
        return pending[0] if pending else None

    def mark_done(self, job_id):
        # Move from queue to history
        for job in self.queue:
            if job['id'] == job_id:
                job['status'] = 'completed'
                job['completed_at'] = str(datetime.now())
                
                # Append to history file
                self._append_history(job)
                
        # Remove completed from queue (optional: or keep them as 'done')
        self.queue = [j for j in self.queue if j['id'] != job_id]
        self.save_queue()

    def _append_history(self, job):
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                try: history = json.load(f)
                except: pass
        history.append(job)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)