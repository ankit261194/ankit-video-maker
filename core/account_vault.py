import os
import json
import base64

VAULT_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "AnkitVideoMaker")
VAULT_FILE = os.path.join(VAULT_DIR, "accounts_vault.json")

def _obfuscate(text):
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")

def _deobfuscate(encoded):
    try:
        return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
    except Exception:
        return encoded

class AccountVault:
    def __init__(self):
        os.makedirs(VAULT_DIR, exist_ok=True)
        self.accounts = self.load_accounts()
        self.current_index = 0

    def load_accounts(self):
        if not os.path.exists(VAULT_FILE):
            return []
        try:
            with open(VAULT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    item["key"] = _deobfuscate(item.get("key", ""))
                return data
        except Exception:
            return []

    def save_accounts(self):
        os.makedirs(VAULT_DIR, exist_ok=True)
        export_data = []
        for item in self.accounts:
            copy_item = dict(item)
            copy_item["key"] = _obfuscate(copy_item["key"])
            export_data.append(copy_item)
        with open(VAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

    def add_account(self, name, key, tier="Premium"):
        if len(self.accounts) >= 20:
            raise ValueError("Maximum 20 accounts limit reached!")
        
        account_id = f"acc_{len(self.accounts) + 1}"
        new_acc = {
            "id": account_id,
            "name": name,
            "key": key.strip(),
            "tier": tier,
            "status": "READY", # READY, ACTIVE, EXHAUSTED
            "usage_count": 0
        }
        if len(self.accounts) == 0:
            new_acc["status"] = "ACTIVE"

        self.accounts.append(new_acc)
        self.save_accounts()
        return new_acc

    def remove_account(self, account_id):
        self.accounts = [a for a in self.accounts if a["id"] != account_id]
        if self.accounts and not any(a["status"] == "ACTIVE" for a in self.accounts):
            self.accounts[0]["status"] = "ACTIVE"
        self.save_accounts()

    def get_active_account(self):
        for acc in self.accounts:
            if acc["status"] == "ACTIVE":
                return acc
        if self.accounts:
            self.accounts[0]["status"] = "ACTIVE"
            self.save_accounts()
            return self.accounts[0]
        return None

    def trigger_failover(self, reason="Data Low / Quota Limit"):
        """
        Switches to the next available account automatically when quota is low or 1% remains.
        """
        if len(self.accounts) <= 1:
            return None, "Only 1 account configured. Add more accounts (up to 20) for automated failover."

        active_idx = -1
        for i, acc in enumerate(self.accounts):
            if acc["status"] == "ACTIVE":
                active_idx = i
                acc["status"] = "EXHAUSTED"
                break

        # Search for next ready account
        next_idx = (active_idx + 1) % len(self.accounts)
        attempts = 0
        while attempts < len(self.accounts):
            if self.accounts[next_idx]["status"] != "EXHAUSTED":
                self.accounts[next_idx]["status"] = "ACTIVE"
                self.save_accounts()
                return self.accounts[next_idx], f"Switched to {self.accounts[next_idx]['name']} due to: {reason}"
            next_idx = (next_idx + 1) % len(self.accounts)
            attempts += 1

        # If all were exhausted, reset all to READY and activate first
        for acc in self.accounts:
            acc["status"] = "READY"
        self.accounts[0]["status"] = "ACTIVE"
        self.save_accounts()
        return self.accounts[0], "All account cycles completed. Resetting pool and switching to Account 1."
