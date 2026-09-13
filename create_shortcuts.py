import os
import sys
import subprocess

app_dir = r"C:\Users\hp\Desktop\Ankit Video Maker"
app_exe = os.path.join(app_dir, "Ankit Video Maker.exe")
icon_path = os.path.join(app_dir, "assets", "ankit_icon.ico")
desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
start_menu_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")

def create_windows_shortcut(target_path, arguments, shortcut_path, icon, working_dir, description):
    ps_script = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{target_path}'
    $Shortcut.Arguments = '{arguments}'
    $Shortcut.WorkingDirectory = '{working_dir}'
    $Shortcut.IconLocation = '{icon}'
    $Shortcut.Description = '{description}'
    $Shortcut.Save()
    """
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
    print(f"Created shortcut: {shortcut_path}")

def setup_all_shortcuts():
    # 1. Desktop Shortcut
    desktop_lnk = os.path.join(desktop_dir, "Ankit Video Maker.lnk")
    create_windows_shortcut(
        target_path=app_exe,
        arguments="",
        shortcut_path=desktop_lnk,
        icon=app_exe,
        working_dir=app_dir,
        description="Ankit Video Maker - Full HD Video & Viral SEO Studio"
    )

    # 2. Windows Start Menu Shortcut (Searchable in Windows Search)
    start_menu_lnk = os.path.join(start_menu_dir, "Ankit Video Maker.lnk")
    create_windows_shortcut(
        target_path=app_exe,
        arguments="",
        shortcut_path=start_menu_lnk,
        icon=app_exe,
        working_dir=app_dir,
        description="Ankit Video Maker - Full HD Video & Viral SEO Studio"
    )

    print("\nAll Windows Shortcuts successfully registered to Ankit Video Maker.exe!")

if __name__ == "__main__":
    setup_all_shortcuts()
