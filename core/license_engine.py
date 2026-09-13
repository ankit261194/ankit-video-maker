import os
import sys
import subprocess
import hashlib
import hmac
import json
import base64
import datetime

# Master Secret Salt Mask (De-obfuscated dynamically at runtime)
_SALT_MASK = b'\x1b\x0c\x17\x05\x1b\x14\x11\x13\x0e\x05\n\x08\x15\x05\t\x1f\x19\x0f\x08\x1f\x05\x11\x1f\x03\x05hjhl\x05"bc<\x05\x0cc'
_MASTER_SALT = bytes([b ^ 0x5A for b in _SALT_MASK])
_MASTER_ADMIN_HASH = "be9a70c9c2397384f542670d01abd65cb4597ea03634d408ac8f57f9a1c13ab0"

LICENSE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "AnkitVideoMaker")
LICENSE_FILE = os.path.join(LICENSE_DIR, "avm_license.dat")

PRICING_PLANS = {
    "1_machine_1yr": {"name": "1 Machine License (1 Year)", "price": "₹3,300", "days": 365, "code": "1Y"},
    "2_years_pack": {"name": "2 Years Studio Pack (2 Years)", "price": "₹6,000", "days": 730, "code": "2Y"},
    "5_years_pack": {"name": "5 Years Enterprise Pack (5 Years)", "price": "₹10,000", "days": 1825, "code": "5Y"},
    "lifetime_vip": {"name": "Lifetime VIP Access (Permanent)", "price": "₹24,999", "days": 36500, "code": "LIFE"}
}

def get_machine_id():
    """
    Generates a unique, non-spoofable Machine ID from motherboard UUID / Registry MachineGuid.
    Format: AVM-XXXX-XXXX-XXXX
    """
    raw_id = ""
    # Try Windows Registry MachineGuid first
    try:
        import winreg
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
        raw_id, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
    except Exception:
        pass

    # Fallback to WMI UUID if needed
    if not raw_id:
        try:
            cmd = ["wmic", "csproduct", "get", "uuid"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            lines = [l.strip() for l in res.stdout.split("\n") if l.strip() and "UUID" not in l]
            if lines:
                raw_id = lines[0]
        except Exception:
            pass

    if not raw_id:
        raw_id = os.environ.get("COMPUTERNAME", "UNKNOWN_PC") + os.environ.get("USERNAME", "USER")

    # Hash to clean 12-char hex string
    digest = hashlib.sha256(raw_id.encode("utf-8")).hexdigest().upper()
    return f"AVM-{digest[:4]}-{digest[4:8]}-{digest[8:12]}"

def sign_license_payload(machine_id, plan_code, expiry_str):
    """
    Cryptographic HMAC-SHA256 signature generator.
    Used by Ankit Admin Key Generator.
    """
    payload = f"{machine_id}::{plan_code}::{expiry_str}"
    sig = hmac.new(_MASTER_SALT, payload.encode("utf-8"), hashlib.sha256).hexdigest().upper()
    token = f"{plan_code}-{expiry_str}-{sig[:16]}"
    return token

def generate_license_key(machine_id, plan_code_or_key):
    """
    Convenience helper to generate official activation key for a Machine ID and Plan.
    Returns (key, display_expiry)
    """
    plan_info = None
    if plan_code_or_key in PRICING_PLANS:
        plan_info = PRICING_PLANS[plan_code_or_key]
    else:
        for k, v in PRICING_PLANS.items():
            if v["code"] == plan_code_or_key or (plan_code_or_key == "2M" and v["code"] == "2Y") or (plan_code_or_key == "5M" and v["code"] == "5Y"):
                plan_info = v
                break
    if not plan_info:
        plan_info = PRICING_PLANS["1_machine_1yr"]

    today = datetime.date.today()
    if plan_info["code"] == "LIFE":
        exp_date_str = "99991231"
        display_exp = "Permanent (Never Expires)"
    else:
        exp_date = today + datetime.timedelta(days=plan_info["days"])
        exp_date_str = exp_date.strftime("%Y%m%d")
        display_exp = exp_date.strftime("%d-%b-%Y")

    token = sign_license_payload(machine_id, plan_info["code"], exp_date_str)
    return token, display_exp

def verify_license_key(machine_id, key_str):
    """
    Verifies a license key against this machine ID and expiration date.
    Returns (is_valid, plan_name, expiry_date_str, error_message)
    """
    key_clean = key_str.strip().upper()
    parts = key_clean.split("-")
    if len(parts) < 3:
        return False, None, None, "Invalid key format! Please check and try again."

    plan_code = parts[0]
    expiry_str = parts[1]
    sig_provided = parts[2]

    # Recompute signature
    payload = f"{machine_id}::{plan_code}::{expiry_str}"
    sig_expected = hmac.new(_MASTER_SALT, payload.encode("utf-8"), hashlib.sha256).hexdigest().upper()[:16]

    if not hmac.compare_digest(sig_provided, sig_expected):
        return False, None, None, "License key signature mismatch! This key is not valid for this Machine ID."

    # Check expiration date
    if plan_code == "LIFE":
        plan_name = "Lifetime VIP Access (Permanent)"
        expiry_display = "Permanent (Never Expires)"
    else:
        try:
            exp_date = datetime.datetime.strptime(expiry_str, "%Y%m%d").date()
            if datetime.date.today() > exp_date:
                return False, None, None, f"License has expired on {exp_date.strftime('%d-%b-%Y')}. Please renew."
            
            plan_name = "1 Machine License (1 Year)"
            for p_key, p_info in PRICING_PLANS.items():
                if p_info["code"] == plan_code or (plan_code == "2M" and p_info["code"] == "2Y") or (plan_code == "5M" and p_info["code"] == "5Y"):
                    plan_name = p_info["name"]
                    break
            expiry_display = exp_date.strftime("%d-%b-%Y")
        except Exception:
            return False, None, None, "Invalid expiration date encoded in license key."

    return True, plan_name, expiry_display, None

def verify_admin_password(password_entered):
    """
    Verifies if entered password is the Master Admin Password.
    If true, activates Super Admin access for any PC without machine ID check.
    """
    pwd_clean = str(password_entered).strip()
    if hashlib.sha256(pwd_clean.encode("utf-8")).hexdigest() == _MASTER_ADMIN_HASH:
        os.makedirs(LICENSE_DIR, exist_ok=True)
        admin_data = {
            "is_admin": True,
            "machine_id": "MASTER_ADMIN_BYPASS",
            "license_key": "ADMIN-SUPER-ACCESS-UNLIMITED",
            "plan_name": "SUPER ADMIN / DEVELOPER ACCESS",
            "expiry_display": "Permanent (Master Admin Access)",
            "activated_on": datetime.date.today().strftime("%Y-%m-%d")
        }
        encoded = base64.b64encode(json.dumps(admin_data).encode("utf-8")).decode("utf-8")
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            f.write(encoded)
        return True, "SUPER ADMIN / DEVELOPER ACCESS", "Permanent (Master Admin Access)"
    return False, None, None

def logout_admin():
    """
    Removes admin session and reverts PC to normal unactivated state.
    """
    if os.path.exists(LICENSE_FILE):
        try:
            os.remove(LICENSE_FILE)
            return True
        except Exception:
            pass
    return False

def save_license(machine_id, key_str, plan_name, expiry_display):
    os.makedirs(LICENSE_DIR, exist_ok=True)
    data = {
        "is_admin": False,
        "machine_id": machine_id,
        "license_key": key_str,
        "plan_name": plan_name,
        "expiry_display": expiry_display,
        "activated_on": datetime.date.today().strftime("%Y-%m-%d")
    }
    encoded = base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(encoded)

def load_active_license():
    """
    Loads and checks current machine's license or admin session.
    Returns (is_active, license_data)
    """
    if not os.path.exists(LICENSE_FILE):
        return False, None
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            encoded = f.read().strip()
        data = json.loads(base64.b64decode(encoded.encode("utf-8")).decode("utf-8"))
        
        # Check if Super Admin session
        if data.get("is_admin") is True:
            return True, data

        current_mid = get_machine_id()
        if data.get("machine_id") != current_mid:
            return False, None
            
        is_valid, plan_name, expiry_display, _ = verify_license_key(current_mid, data.get("license_key", ""))
        if is_valid:
            data["plan_name"] = plan_name
            data["expiry_display"] = expiry_display
            return True, data
    except Exception:
        pass
    return False, None
