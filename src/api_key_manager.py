import os
import json
import requests
from datetime import datetime, timezone, timedelta

class APIKeyManager:
    DEFAULT_KEYS_FILE = "keys/api_keys.json"
    QUOTA_LIMIT = 20
    # Models as specified in spec
    MODELS = ["gemini-2.5-flash", "gemini-3-flash-preview"]

    def __init__(self, keys_file=None):
        self.keys_file = keys_file or self.DEFAULT_KEYS_FILE
        self.data = self._load_data()
        self.last_key_index = -1

    def _load_data(self):
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "keys": [],
            "last_reset_date": ""
        }

    def _save_data(self):
        os.makedirs(os.path.dirname(self.keys_file), exist_ok=True)
        with open(self.keys_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_key(self, key):
        if any(k["key"] == key for k in self.data["keys"]):
            return False
        
        self.data["keys"].append({
            "key": key,
            "usage": {model: 0 for model in self.MODELS},
            "exhausted": {model: False for model in self.MODELS}
        })
        self._save_data()
        return True

    def remove_key(self, key):
        original_count = len(self.data["keys"])
        self.data["keys"] = [k for k in self.data["keys"] if k["key"] != key]
        if len(self.data["keys"]) != original_count:
            self._save_data()
            return True
        return False

    def list_keys(self):
        return self.data["keys"]

    def record_usage(self, key, model):
        for k in self.data["keys"]:
            if k["key"] == key:
                if model not in k["usage"]:
                    k["usage"][model] = 0
                k["usage"][model] += 1
                self._save_data()
                return True
        return False

    def mark_exhausted(self, key, model):
        """Mark a key as exhausted for a specific model (usually after 429)."""
        for k in self.data["keys"]:
            if k["key"] == key:
                if "exhausted" not in k:
                    k["exhausted"] = {m: False for m in self.MODELS}
                k["exhausted"][model] = True
                self._save_data()
                return True
        return False

    def get_available_key(self, model):
        self.reset_quotas_if_needed()
        
        num_keys = len(self.data["keys"])
        if num_keys == 0:
            return None

        # Start searching from the next key after last_key_index
        for i in range(1, num_keys + 1):
            idx = (self.last_key_index + i) % num_keys
            k = self.data["keys"][idx]
            
            usage = k["usage"].get(model, 0)
            exhausted = k.get("exhausted", {}).get(model, False)
            
            if not exhausted and usage < self.QUOTA_LIMIT:
                self.last_key_index = idx
                return k["key"]
        
        return None

    def get_status_report(self):
        """Returns a list of status strings for all keys."""
        report = []
        for k in self.data["keys"]:
            masked = k['key'][:4] + "..." + k['key'][-4:] if len(k['key']) > 8 else "****"
            status_line = f"Key: {masked}"
            for model in self.MODELS:
                usage = k["usage"].get(model, 0)
                exh = k.get("exhausted", {}).get(model, False)
                marker = " [EXHAUSTED]" if exh or usage >= self.QUOTA_LIMIT else ""
                status_line += f"\n  - {model}: {usage}/{self.QUOTA_LIMIT}{marker}"
            report.append(status_line)
        return report

    def _get_current_time_pt(self):
        """Get current time in Pacific Time."""
        try:
            # Try WorldTimeAPI
            response = requests.get("http://worldtimeapi.org/api/timezone/America/Los_Angeles", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return datetime.fromisoformat(data["datetime"])
        except Exception:
            pass
            
        # Fallback to local system time converted to PT
        utc_now = datetime.now(timezone.utc)
        # Pacific Standard Time is UTC-8.
        return utc_now - timedelta(hours=8)

    def reset_quotas_if_needed(self):
        now_pt = self._get_current_time_pt()
        today_str = now_pt.strftime("%Y-%m-%d")
        
        if not self.data["last_reset_date"]:
            self.data["last_reset_date"] = today_str
            self._save_data()
            return False

        if self.data["last_reset_date"] != today_str:
            for k in self.data["keys"]:
                k["usage"] = {model: 0 for model in self.MODELS}
                k["exhausted"] = {model: False for model in self.MODELS}
            self.data["last_reset_date"] = today_str
            self._save_data()
            return True
        return False
