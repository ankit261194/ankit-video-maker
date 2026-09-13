import os
import sys
import json
import zipfile
import tempfile
import urllib.request

CURRENT_VERSION = "2.6.0"
CONFIG_PATH = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "AnkitVideoMaker", "cloud_config.json")

DEFAULT_CLOUD_REPO = "ankit261194/ankit-video-maker" # Default cloud repository channel

def get_cloud_repo():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("repo", DEFAULT_CLOUD_REPO)
        except Exception:
            pass
    return DEFAULT_CLOUD_REPO

def set_cloud_repo(repo_name):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"repo": repo_name}, f, indent=2)
        return True
    except Exception:
        return False

def get_git_remote_url(app_dir=None):
    if not app_dir:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    try:
        import subprocess
        res = subprocess.run(["git", "config", "--get", "remote.origin.url"], cwd=app_dir, capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return ""

def set_git_remote_url(remote_url, app_dir=None):
    if not app_dir:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    try:
        import subprocess
        res = subprocess.run(["git", "remote"], cwd=app_dir, capture_output=True, text=True)
        if "origin" in res.stdout:
            subprocess.run(["git", "remote", "set-url", "origin", remote_url.strip()], cwd=app_dir, check=True)
        else:
            subprocess.run(["git", "remote", "add", "origin", remote_url.strip()], cwd=app_dir, check=True)
        
        if "github.com/" in remote_url:
            clean_repo = remote_url.split("github.com/")[-1].replace(".git", "").strip("/")
            set_cloud_repo(clean_repo)
            
        return True, f"Remote origin connected to: {remote_url}"
    except Exception as e:
        return False, str(e)

def push_git_to_remote(app_dir=None):
    if not app_dir:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    try:
        import subprocess
        subprocess.run(["git", "branch", "-M", "main"], cwd=app_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=app_dir, check=True)
        st = subprocess.run(["git", "status", "--porcelain"], cwd=app_dir, capture_output=True, text=True)
        if st.stdout.strip():
            subprocess.run(["git", "commit", "-m", "Synchronize official updates to repository"], cwd=app_dir, check=True)
        res = subprocess.run(["git", "push", "-u", "origin", "main", "--tags"], cwd=app_dir, capture_output=True, text=True)
        if res.returncode == 0:
            return True, "Successfully pushed all updates to GitHub repository!"
        else:
            return False, res.stderr or res.stdout
    except Exception as e:
        return False, str(e)

def check_cloud_update(repo_name=None):
    """
    Checks AVM Official Cloud Release Network for latest version.
    Returns: (update_available, latest_version, download_url, notes)
    """
    if not repo_name:
        repo_name = get_cloud_repo()

    api_url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    req = urllib.request.Request(api_url, headers={"User-Agent": "AVM-Official-Cloud-Sync/2.5"})

    def parse_v(v):
        return [int(x) for x in v.split(".") if x.isdigit()]

    candidates = []

    # 1. Check formal GitHub Releases
    try:
        api_url = f"https://api.github.com/repos/{repo_name}/releases/latest"
        req = urllib.request.Request(api_url, headers={"User-Agent": "AVM-Official-Cloud-Sync/2.6"})
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                rel_tag = data.get("tag_name", "").replace("v", "").strip()
                rel_notes = data.get("body", "Official performance improvements and enhancements.")
                download_url = None
                assets = data.get("assets", [])
                if assets:
                    for a in assets:
                        if a.get("name", "").endswith(".zip"):
                            download_url = a.get("browser_download_url")
                            break
                    if not download_url:
                        download_url = assets[0].get("browser_download_url")
                if not download_url:
                    download_url = data.get("zipball_url")
                if rel_tag and download_url:
                    candidates.append((rel_tag, download_url, rel_notes))
    except Exception:
        pass

    # 2. Check Git Tags (immediately picks up published tags)
    try:
        tags_url = f"https://api.github.com/repos/{repo_name}/tags"
        tags_req = urllib.request.Request(tags_url, headers={"User-Agent": "AVM-Official-Cloud-Sync/2.6"})
        with urllib.request.urlopen(tags_req, timeout=8) as t_res:
            if t_res.status == 200:
                tags_data = json.loads(t_res.read().decode("utf-8"))
                if tags_data and len(tags_data) > 0:
                    top_tag = tags_data[0].get("name", "").replace("v", "").strip()
                    zip_url = tags_data[0].get("zipball_url")
                    if top_tag and zip_url:
                        candidates.append((top_tag, zip_url, "Official AVM Cloud Network Update - Core Enhancements & Optimization"))
    except Exception:
        pass

    if candidates:
        def v_key(item):
            return [int(x) for x in item[0].split(".") if x.isdigit()]
        best_ver, best_url, best_notes = max(candidates, key=v_key)
        try:
            is_newer = parse_v(best_ver) > parse_v(CURRENT_VERSION)
        except Exception:
            is_newer = best_ver > CURRENT_VERSION
        return is_newer, best_ver, best_url, best_notes

    return False, CURRENT_VERSION, None, "Up to date"

def apply_cloud_update(download_url, progress_callback=None, app_dir=None):
    """
    Downloads and applies the latest AVM update archive seamlessly.
    Preserves user license and account vault.
    """
    if not app_dir:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if not download_url:
        return False, "No update package URL provided."

    try:
        if progress_callback:
            progress_callback("Connecting to AVM Official Cloud Network...")

        temp_dir = tempfile.mkdtemp(prefix="avm_update_")
        zip_path = os.path.join(temp_dir, "update_pkg.zip")

        # Download with progress
        def _reporthook(block_num, block_size, total_size):
            if total_size > 0 and progress_callback:
                percent = min(100, int(block_num * block_size * 100 / total_size))
                progress_callback(f"Downloading AVM update package: {percent}%")

        urllib.request.urlretrieve(download_url, zip_path, reporthook=_reporthook)

        if progress_callback:
            progress_callback("Extracting and applying cloud components...")

        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find the root folder inside zip (GitHub zips have repo-tag/ as top directory)
        extracted_items = os.listdir(extract_dir)
        source_root = extract_dir
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_dir, extracted_items[0])):
            source_root = os.path.join(extract_dir, extracted_items[0])

        # Copy files over app_dir
        for root, dirs, files in os.walk(source_root):
            rel_path = os.path.relpath(root, source_root)
            target_root = os.path.join(app_dir, rel_path)
            os.makedirs(target_root, exist_ok=True)
            for f in files:
                # Don't overwrite local user caches or logs
                if f.endswith(".dat") or f.endswith(".json") and "vault" in f:
                    continue
                src_file = os.path.join(root, f)
                dst_file = os.path.join(target_root, f)
                try:
                    import shutil
                    shutil.copy2(src_file, dst_file)
                except Exception:
                    pass

        if progress_callback:
            progress_callback("Cloud update installed successfully!")

        return True, "Update applied successfully!"
    except Exception as e:
        return False, f"Update installation failed: {str(e)}"
