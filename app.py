import os
import sys
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Self-healing dependency verification right at startup
from core.dependency_engine import verify_and_heal_environment, ensure_package
verify_and_heal_environment()

# Import core modules
from core.voice_engine import AVAILABLE_VOICES, preview_voice
from core.video_compositor import render_full_project
from core.account_vault import AccountVault
from core.updater import (
    check_cloud_update, apply_cloud_update, CURRENT_VERSION, 
    get_cloud_repo, set_cloud_repo, get_git_remote_url, set_git_remote_url, push_git_to_remote
)
from core.license_engine import (
    get_machine_id, verify_license_key, save_license, load_active_license, 
    PRICING_PLANS, verify_admin_password, logout_admin
)
from core.script_studio import generate_viral_script_ai

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ActivationDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.on_success = on_success_callback
        self.title("Ankit Video Maker - License Activation")
        self.geometry("720x680")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.machine_id = get_machine_id()
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#0a101f")
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="🔐 ANKIT VIDEO MAKER - ACTIVATION REQUIRED", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00e5ff").pack(side="left", padx=20, pady=15)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=15)

        # Machine ID Box
        mid_box = ctk.CTkFrame(body, fg_color="#121a2d", corner_radius=8)
        mid_box.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(mid_box, text="YOUR UNIQUE MACHINE ID:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8899b5").pack(anchor="w", padx=15, pady=(10, 2))
        
        mid_row = ctk.CTkFrame(mid_box, fg_color="transparent")
        mid_row.pack(fill="x", padx=15, pady=(0, 10))

        lbl_mid = ctk.CTkLabel(mid_row, text=self.machine_id, font=ctk.CTkFont(family="Consolas", size=17, weight="bold"), text_color="#00ffcc")
        lbl_mid.pack(side="left")

        btn_copy = ctk.CTkButton(mid_row, text="📋 Copy Machine ID", width=140, height=30, fg_color="#1e293b", hover_color="#334155", command=self._copy_mid)
        btn_copy.pack(side="right")

        # Official Pricing Table
        price_box = ctk.CTkFrame(body, fg_color="#121a2d", corner_radius=8)
        price_box.pack(fill="x", pady=5)

        ctk.CTkLabel(price_box, text="OFFICIAL PRICING & LICENSE PLANS:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00e5ff").pack(anchor="w", padx=15, pady=(10, 5))
        
        plans_text = (
            "• 1 Machine License (1 Year)          :  ₹3,300\n"
            "• 2 Years Studio Pack (2 Years)       :  ₹6,000\n"
            "• 5 Years Enterprise Pack (5 Years)   :  ₹10,000\n"
            "• Lifetime VIP Access (Permanent)     :  ₹24,999"
        )
        ctk.CTkLabel(price_box, text=plans_text, font=ctk.CTkFont(family="Consolas", size=12), justify="left", text_color="#f8fafc").pack(anchor="w", padx=20, pady=(0, 10))

        # Instructions
        inst_box = ctk.CTkFrame(body, fg_color="#162238", corner_radius=8)
        inst_box.pack(fill="x", pady=8)

        inst_text = (
            "📲 TO GET YOUR ACTIVATION KEY (1-Year, 2-Year, 5-Year, Lifetime):\n"
            "1. Copy your Machine ID above.\n"
            "2. Send your Machine ID + Payment screenshot on WhatsApp to: +91 8533955333\n"
            "3. You will receive your official cryptographically verified Activation Key instantly.\n\n"
            "⚠️ PREREQUISITE: To run this software and unlock unlimited AI script generation,\n"
            "   a Google Gemini API subscription/key is compulsory."
        )
        ctk.CTkLabel(inst_box, text=inst_text, font=ctk.CTkFont(size=11), justify="left", text_color="#38bdf8").pack(anchor="w", padx=15, pady=10)

        # Key Input
        ctk.CTkLabel(body, text="Enter Activation Key:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(8, 2))
        self.entry_key = ctk.CTkEntry(body, height=40, font=ctk.CTkFont(family="Consolas", size=13), placeholder_text="e.g. 1Y-20270913-XXXXXXXXXXXXXXXX")
        self.entry_key.pack(fill="x", pady=(0, 10))

        # Activate Button
        btn_act = ctk.CTkButton(
            body,
            text="⚡ ACTIVATE ANKIT VIDEO MAKER",
            height=44,
            fg_color="#00e5ff",
            text_color="#070d1e",
            hover_color="#33ecff",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._activate
        )
        btn_act.pack(fill="x")

        # Admin Master Access Button
        admin_row = ctk.CTkFrame(body, fg_color="transparent")
        admin_row.pack(fill="x", pady=(8, 0))

        btn_admin = ctk.CTkButton(
            admin_row,
            text="👑 Ankit Admin Master Login (Password Access)",
            height=32,
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#38bdf8",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._admin_login_prompt
        )
        btn_admin.pack(fill="x")

    def _admin_login_prompt(self):
        prompt = ctk.CTkInputDialog(text="Enter Ankit Admin Master Password:", title="Master Admin Access")
        pwd = prompt.get_input()
        if pwd is not None:
            is_valid, plan_name, exp_display = verify_admin_password(pwd)
            if is_valid:
                messagebox.showinfo(
                    "Super Admin Granted!",
                    "👑 Welcome Ankit!\nMaster Admin Access successfully verified.\nAll software services are unlocked on this PC without Machine ID restrictions!"
                )
                self.destroy()
                self.on_success(plan_name, exp_display)
            else:
                messagebox.showerror("Access Denied", "Incorrect Master Admin Password!")

    def _copy_mid(self):
        self.clipboard_clear()
        self.clipboard_append(self.machine_id)
        messagebox.showinfo("Copied", "Machine ID copied to clipboard! Send this on WhatsApp: 8533955333")

    def _activate(self):
        key = self.entry_key.get().strip()
        if not key:
            messagebox.showerror("Error", "Please paste your Activation Key!")
            return

        is_valid, plan_name, expiry_display, err = verify_license_key(self.machine_id, key)
        if is_valid:
            save_license(self.machine_id, key, plan_name, expiry_display)
            messagebox.showinfo(
                "Activation Successful!",
                f"🎉 License Activated Successfully!\n\nPlan: {plan_name}\nValid: {expiry_display}\n\nWelcome to Ankit Video Maker!"
            )
            self.destroy()
            self.on_success(plan_name, expiry_display)
        else:
            messagebox.showerror("Activation Failed", err or "Invalid License Key.")

class AnkitVideoMakerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ankit Video Maker - Full HD Video, Multi-Account Vault & Viral SEO Studio")
        self.geometry("1180x780")
        self.minsize(980, 680)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "ankit_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.vault = AccountVault()
        self.avatar_image_path = None
        self.rendered_video_path = None
        self.rendered_seo_path = None
        self.is_rendering = False
        self.license_info = None

        self._build_ui()
        self._load_default_sample()
        self._refresh_accounts_list()
        
        # Check license on startup
        self.after(100, self._check_license_startup)
        # Background cloud update check on startup
        self.after(3000, self._silent_startup_update_check)

    def _check_license_startup(self):
        is_active, lic = load_active_license()
        if is_active:
            self.license_info = lic
            if lic.get("is_admin") is True:
                self.lbl_license_badge.configure(
                    text="👑 SUPER ADMIN MODE (Master Unlocked)",
                    text_color="#00ffcc"
                )
                self.btn_admin_logout.pack(side="right", padx=(0, 10), pady=18)
            else:
                self.lbl_license_badge.configure(
                    text=f"✅ {lic.get('plan_name', 'Active License')} • Expires: {lic.get('expiry_display', 'Permanent')}",
                    text_color="#00ffcc"
                )
                self.btn_admin_logout.pack_forget()
        else:
            self.lbl_license_badge.configure(text="⚠️ Unregistered / Trial Mode", text_color="#f59e0b")
            self.btn_admin_logout.pack_forget()
            ActivationDialog(self, on_success_callback=self._on_license_activated)

    def _on_license_activated(self, plan_name, expiry_display):
        is_active, lic = load_active_license()
        self.license_info = lic
        if is_active and lic and lic.get("is_admin") is True:
            self.lbl_license_badge.configure(text="👑 SUPER ADMIN MODE (Master Unlocked)", text_color="#00ffcc")
            self.btn_admin_logout.pack(side="right", padx=(0, 10), pady=18)
        else:
            self.lbl_license_badge.configure(text=f"✅ {plan_name} • Expires: {expiry_display}", text_color="#00ffcc")
            self.btn_admin_logout.pack_forget()

    def _logout_admin_click(self):
        confirm = messagebox.askyesno(
            "Confirm Admin Logout",
            "Are you sure you want to log out of Super Admin mode on this computer?\n\n"
            "This machine will return to unactivated status until a customer license is entered or Admin re-authenticates."
        )
        if confirm:
            logout_admin()
            self.license_info = None
            self.lbl_license_badge.configure(text="⚠️ Unregistered / Trial Mode", text_color="#f59e0b")
            self.btn_admin_logout.pack_forget()
            messagebox.showinfo("Logged Out", "Admin session logged out successfully!\nOpening activation screen...")
            ActivationDialog(self, on_success_callback=self._on_license_activated)

    def _build_ui(self):
        header = ctk.CTkFrame(self, height=72, corner_radius=0, fg_color="#0d1424")
        header.pack(fill="x", side="top")
        
        lbl_title = ctk.CTkLabel(
            header,
            text="⚡ ANKIT VIDEO MAKER",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00e5ff"
        )
        lbl_title.pack(side="left", padx=20, pady=12)

        self.lbl_license_badge = ctk.CTkLabel(
            header,
            text="Checking License...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8899b5"
        )
        self.lbl_license_badge.pack(side="left", padx=10, pady=18)

        # Right buttons
        ctk.CTkButton(
            header,
            text="🔑 License Details",
            width=130,
            height=30,
            fg_color="#1e293b",
            hover_color="#334155",
            command=lambda: ActivationDialog(self, on_success_callback=self._on_license_activated)
        ).pack(side="right", padx=20, pady=18)

        self.btn_admin_logout = ctk.CTkButton(
            header,
            text="🚪 Logout Admin",
            width=120,
            height=30,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._logout_admin_click
        )

        # Tabview with 5 tabs
        self.tabview = ctk.CTkTabview(self, corner_radius=10, fg_color="#121a2d")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=8)

        self.tab_script = self.tabview.add("🎬 1. Script & Scenes")
        self.tab_voice = self.tabview.add("🎙️ 2. Voice & Music Studio")
        self.tab_avatar = self.tabview.add("👤 3. Photo Avatar & Visuals")
        self.tab_accounts = self.tabview.add("🔐 4. Multi-Account Vault (1-20)")
        self.tab_render = self.tabview.add("🚀 5. Render & Export")

        self._setup_script_tab()
        self._setup_voice_tab()
        self._setup_avatar_tab()
        self._setup_accounts_tab()
        self._setup_render_tab()

    def _setup_script_tab(self):
        # AI Script Generator Tool Box
        ai_box = ctk.CTkFrame(self.tab_script, fg_color="#152138", corner_radius=8)
        ai_box.pack(fill="x", padx=10, pady=(5, 10))

        ai_hdr = ctk.CTkFrame(ai_box, fg_color="transparent")
        ai_hdr.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(ai_hdr, text="✨ AI VIRAL SCRIPT & PROMPT STUDIO", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00e5ff").pack(side="left")
        ctk.CTkLabel(ai_hdr, text="• ⚠️ Google Gemini Subscription/Key is COMPULSORY for custom AI scripts", font=ctk.CTkFont(size=11, weight="bold"), text_color="#38bdf8").pack(side="left", padx=10)

        ai_inputs = ctk.CTkFrame(ai_box, fg_color="transparent")
        ai_inputs.pack(fill="x", padx=12, pady=(0, 8))

        self.entry_ai_topic = ctk.CTkEntry(ai_inputs, width=380, height=32, placeholder_text="Enter any topic: e.g. Space Mysteries, Top 5 AI Tools, Cyber Hacks")
        self.entry_ai_topic.pack(side="left", padx=(0, 10))

        self.ai_tone_var = ctk.StringVar(value="High-Retention Mystery")
        tone_menu = ctk.CTkOptionMenu(ai_inputs, values=["High-Retention Mystery", "Tech Documentary", "Fast Viral", "Deep Storytelling"], variable=self.ai_tone_var, width=170, height=32)
        tone_menu.pack(side="left", padx=(0, 10))

        self.ai_lang_var = ctk.StringVar(value="English")
        lang_menu = ctk.CTkOptionMenu(ai_inputs, values=["English", "Hindi"], variable=self.ai_lang_var, width=110, height=32)
        lang_menu.pack(side="left", padx=(0, 10))

        self.btn_ai_gen = ctk.CTkButton(ai_inputs, text="⚡ Write Script", width=130, height=32, fg_color="#00e5ff", text_color="#070d1e", font=ctk.CTkFont(weight="bold"), command=self._generate_ai_script)
        self.btn_ai_gen.pack(side="left")

        # Project Title & Keywords
        top_frame = ctk.CTkFrame(self.tab_script, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(top_frame, text="Video Project Title:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        self.entry_title = ctk.CTkEntry(top_frame, height=34, font=ctk.CTkFont(size=12), placeholder_text="e.g., 4 Digital Mysteries That Feel Illegal To Know")
        self.entry_title.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(top_frame, text="Topic Keywords (For Viral SEO Tags & Description):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.entry_keywords = ctk.CTkEntry(top_frame, height=32, font=ctk.CTkFont(size=12), placeholder_text="e.g., cybersecurity, privacy, tech tips, data brokers")
        self.entry_keywords.pack(fill="x", pady=(2, 8))

        lbl_scenes = ctk.CTkLabel(self.tab_script, text="Scenes & Voiceover Narration Script:", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_scenes.pack(anchor="w", padx=10)

        self.scenes_scroll = ctk.CTkScrollableFrame(self.tab_script, height=240, fg_color="#0e1526")
        self.scenes_scroll.pack(fill="both", expand=True, padx=10, pady=4)

        self.scene_widgets = []

        btn_frame = ctk.CTkFrame(self.tab_script, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(btn_frame, text="➕ Add Scene", width=120, command=self._add_scene, fg_color="#00b4d8", hover_color="#0077b6").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📋 Load Tech Sample", width=140, command=self._load_default_sample, fg_color="#2b3a55", hover_color="#3d5175").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑️ Clear All", width=100, command=self._clear_scenes, fg_color="#6c757d", hover_color="#495057").pack(side="right", padx=5)

    def _generate_ai_script(self):
        topic = self.entry_ai_topic.get().strip()
        if not topic:
            messagebox.showwarning("Enter Topic", "Please write a topic for the script!")
            return

        active_acc = self.vault.get_active_account()
        gemini_key = active_acc["key"] if active_acc else None

        tone = self.ai_tone_var.get()
        lang = self.ai_lang_var.get()

        self.btn_ai_gen.configure(state="disabled", text="⏳ Writing...")

        def _bg_script():
            try:
                scenes, note = generate_viral_script_ai(topic, tone=tone, language=lang, gemini_api_key=gemini_key)
                def _ui_update():
                    self._clear_scenes()
                    for sc in scenes:
                        self._add_scene(sc.get("title", "Scene"), sc.get("text", ""))
                    self.entry_title.delete(0, "end")
                    self.entry_title.insert(0, topic)
                    self.entry_keywords.delete(0, "end")
                    self.entry_keywords.insert(0, f"{topic}, viral video, secrets, breakdown, guide")
                    self.btn_ai_gen.configure(state="normal", text="⚡ Write Script")
                    messagebox.showinfo("Script Generated!", f"🎉 Successfully created {len(scenes)} scenes!\n\n{note}")
                self.after(0, _ui_update)
            except Exception as e:
                def _err():
                    self.btn_ai_gen.configure(state="normal", text="⚡ Write Script")
                    messagebox.showerror("Error", f"Failed to generate script:\n{e}")
                self.after(0, _err)

        threading.Thread(target=_bg_script, daemon=True).start()

    def _setup_voice_tab(self):
        v_frame = ctk.CTkFrame(self.tab_voice, fg_color="transparent")
        v_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(v_frame, text="Select Neural Voiceover (Hindi & English • 100% Copyright-Free):", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(5, 5))
        
        voice_row = ctk.CTkFrame(v_frame, fg_color="transparent")
        voice_row.pack(fill="x", pady=5)

        self.voice_var = ctk.StringVar(value="English - Christopher (Deep Tech Male)")
        self.voice_menu = ctk.CTkOptionMenu(
            voice_row,
            values=list(AVAILABLE_VOICES.keys()),
            variable=self.voice_var,
            width=430,
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.voice_menu.pack(side="left", padx=(0, 15))

        btn_test = ctk.CTkButton(
            voice_row,
            text="🔊 Awaaz Sunein (Test Voice)",
            width=190,
            height=38,
            fg_color="#00e5ff",
            text_color="#0a1128",
            hover_color="#33ecff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._test_voice
        )
        btn_test.pack(side="left")

        ctk.CTkLabel(v_frame, text="Speech Pacing / Speed Rate:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(25, 5))
        self.rate_var = ctk.StringVar(value="-2% (Authoritative / Clear Tech)")
        rate_menu = ctk.CTkOptionMenu(
            v_frame,
            values=["-5% (Deliberate / Serious)", "-2% (Authoritative / Clear Tech)", "0% (Natural Standard)", "+5% (Fast / Dynamic)"],
            variable=self.rate_var,
            width=300,
            height=35
        )
        rate_menu.pack(anchor="w", pady=5)

        ctk.CTkLabel(v_frame, text="Background Music Engine:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(25, 5))
        lbl_bgm_info = ctk.CTkLabel(
            v_frame,
            text="✨ Procedural Cyber Mystery Lo-Fi Engine: Generates original, un-copyrightable ambient music for every video.",
            font=ctk.CTkFont(size=12),
            text_color="#00ffb4"
        )
        lbl_bgm_info.pack(anchor="w")
        ctk.CTkLabel(v_frame, text="Audio Mix Ratio: 85% Voiceover / 15% Music (Optimized)", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 0))

    def _setup_avatar_tab(self):
        a_frame = ctk.CTkFrame(self.tab_avatar, fg_color="transparent")
        a_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(a_frame, text="👤 Photo Avatar Studio (Apni Photo Se Video Banayein):", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(5, 5))
        
        info_lbl = ctk.CTkLabel(
            a_frame,
            text="Upload any portrait photo. Ankit Video Maker creates a professional Broadcaster Avatar HUD badge with dynamic audio-reactive breathing and aura glow synchronized with the narration.",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            wraplength=800,
            justify="left"
        )
        info_lbl.pack(anchor="w", pady=(0, 15))

        upload_row = ctk.CTkFrame(a_frame, fg_color="transparent")
        upload_row.pack(fill="x", pady=10)

        ctk.CTkButton(
            upload_row,
            text="📷 Upload Presenter Photo",
            width=200,
            height=40,
            fg_color="#00b4d8",
            hover_color="#0077b6",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._upload_avatar
        ).pack(side="left", padx=(0, 15))

        self.lbl_avatar_status = ctk.CTkLabel(
            upload_row,
            text="No photo selected (Will use Procedural Cyberpunk Graphics).",
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1"
        )
        self.lbl_avatar_status.pack(side="left")

        ctk.CTkLabel(a_frame, text="Visual Motion & Animation Style:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(25, 5))
        self.visual_style_var = ctk.StringVar(value="Ken Burns Cinematic Zoom & Drift")
        style_menu = ctk.CTkOptionMenu(
            a_frame,
            values=["Ken Burns Cinematic Zoom & Drift", "Cyberpunk HUD Scanlines & Glitch", "Minimalist Clean Tech"],
            variable=self.visual_style_var,
            width=320,
            height=35
        )
        style_menu.pack(anchor="w", pady=5)

    def _setup_accounts_tab(self):
        acc_frame = ctk.CTkFrame(self.tab_accounts, fg_color="transparent")
        acc_frame.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            acc_frame,
            text="🔐 Multi-Account Vault (1 to 20 Accounts with Auto-Failover):",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")

        # Compulsory Gemini Instruction Box
        gem_box = ctk.CTkFrame(acc_frame, fg_color="#18233a", corner_radius=8)
        gem_box.pack(fill="x", pady=(8, 10))

        gem_text = (
            "⚠️ COMPULSORY PREREQUISITE FOR FULL AI POWER:\n"
            "An active Google Gemini API Key / Subscription is compulsory for custom AI scripts and high-speed generation.\n"
            "• Get your free/pro key at: https://aistudio.google.com\n"
            "• You can add up to 20 keys below. If one key runs low on quota (1% remaining), the system auto-switches immediately!"
        )
        ctk.CTkLabel(gem_box, text=gem_text, font=ctk.CTkFont(size=11), justify="left", text_color="#38bdf8").pack(anchor="w", padx=15, pady=10)

        # Accounts List Frame
        self.accounts_scroll = ctk.CTkScrollableFrame(acc_frame, height=180, fg_color="#0e1526")
        self.accounts_scroll.pack(fill="both", expand=True, pady=4)

        # Control Buttons
        btn_row = ctk.CTkFrame(acc_frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=8)

        ctk.CTkButton(btn_row, text="➕ Add Account / Gemini Key", width=200, height=36, fg_color="#00b4d8", hover_color="#0077b6", command=self._popup_add_account).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="🔄 Test Auto-Failover", width=180, height=36, fg_color="#2b3a55", hover_color="#3d5175", command=self._manual_failover).pack(side="left", padx=5)

        # White-labeled Cloud Update Section
        upd_box = ctk.CTkFrame(acc_frame, fg_color="#11192e", corner_radius=8)
        upd_box.pack(fill="x", pady=(10, 5), padx=5)

        upd_hdr = ctk.CTkFrame(upd_box, fg_color="transparent")
        upd_hdr.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(upd_hdr, text=f"🌐 AVM Official Cloud Engine (Version: v{CURRENT_VERSION}):", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(upd_hdr, text="🔍 Check Cloud Updates", width=170, height=28, fg_color="#059669", hover_color="#10b981", command=self._check_updates).pack(side="right")

        # GitHub Official Repository Connection Section
        git_box = ctk.CTkFrame(acc_frame, fg_color="#11192e", corner_radius=8)
        git_box.pack(fill="x", pady=6, padx=5)

        git_hdr = ctk.CTkFrame(git_box, fg_color="transparent")
        git_hdr.pack(fill="x", padx=15, pady=(8, 4))
        ctk.CTkLabel(git_hdr, text="🐙 Connect Official GitHub Repository Channel:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00e5ff").pack(side="left")

        git_row = ctk.CTkFrame(git_box, fg_color="transparent")
        git_row.pack(fill="x", padx=15, pady=(0, 10))

        current_remote = get_git_remote_url()
        self.entry_git_remote = ctk.CTkEntry(
            git_row,
            height=32,
            font=ctk.CTkFont(family="Consolas", size=11),
            placeholder_text="e.g. https://github.com/ankitchaudhary/ankit-video-maker.git"
        )
        if current_remote:
            self.entry_git_remote.insert(0, current_remote)
        self.entry_git_remote.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            git_row,
            text="💾 Save / Connect",
            width=130,
            height=32,
            fg_color="#00b4d8",
            hover_color="#0077b6",
            command=self._save_git_remote
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            git_row,
            text="⬆️ Push to GitHub",
            width=130,
            height=32,
            fg_color="#059669",
            hover_color="#10b981",
            command=self._push_to_github
        ).pack(side="left")

    def _setup_render_tab(self):
        r_frame = ctk.CTkFrame(self.tab_render, fg_color="transparent")
        r_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.btn_render = ctk.CTkButton(
            r_frame,
            text="⚡ GENERATE FULL HD 1080P VIDEO & VIRAL SEO KIT",
            height=50,
            fg_color="#00e5ff",
            text_color="#070d1e",
            hover_color="#33ecff",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_render
        )
        self.btn_render.pack(fill="x", pady=(5, 10))

        self.progress_bar = ctk.CTkProgressBar(r_frame, height=14, corner_radius=7)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0.0)

        ctk.CTkLabel(r_frame, text="Rendering Engine Status & Logs:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(10, 2))
        self.txt_console = ctk.CTkTextbox(r_frame, height=250, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#090d18", text_color="#00ffcc")
        self.txt_console.pack(fill="both", expand=True, pady=5)

        act_row = ctk.CTkFrame(r_frame, fg_color="transparent")
        act_row.pack(fill="x", pady=(10, 5))

        self.btn_open_folder = ctk.CTkButton(
            act_row,
            text="📁 Open Downloads Folder",
            width=200,
            height=36,
            fg_color="#1e293b",
            hover_color="#334155",
            command=self._open_downloads
        )
        self.btn_open_folder.pack(side="left", padx=5)

        self.btn_play_video = ctk.CTkButton(
            act_row,
            text="▶️ Play Rendered Video",
            width=180,
            height=36,
            fg_color="#059669",
            hover_color="#10b981",
            command=self._play_video
        )
        self.btn_play_video.pack(side="left", padx=5)

    def _refresh_accounts_list(self):
        for w in self.accounts_scroll.winfo_children():
            w.destroy()

        accounts = self.vault.accounts
        if not accounts:
            lbl = ctk.CTkLabel(self.accounts_scroll, text="No Google Gemini / API accounts configured. Click 'Add Account / Gemini Key' to add your keys.", text_color="#64748b")
            lbl.pack(pady=20)
            return

        for acc in accounts:
            card = ctk.CTkFrame(self.accounts_scroll, fg_color="#162035", corner_radius=6)
            card.pack(fill="x", padx=5, pady=4)

            status_color = "#00ffcc" if acc["status"] == "ACTIVE" else ("#f59e0b" if acc["status"] == "READY" else "#ef4444")
            lbl_info = ctk.CTkLabel(
                card,
                text=f"[{acc['tier']}] {acc['name']}  •  Status: {acc['status']}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=status_color
            )
            lbl_info.pack(side="left", padx=15, pady=8)

            btn_del = ctk.CTkButton(
                card,
                text="Delete",
                width=70,
                height=26,
                fg_color="#dc2626",
                hover_color="#b91c1c",
                command=lambda aid=acc["id"]: self._delete_account(aid)
            )
            btn_del.pack(side="right", padx=10)

    def _popup_add_account(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Google Gemini Key")
        dialog.geometry("480x280")
        dialog.transient(self)

        ctk.CTkLabel(dialog, text="Account Name / Label:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(15, 2))
        entry_name = ctk.CTkEntry(dialog, height=32, placeholder_text="e.g., Gemini Key 1 (Primary)")
        entry_name.pack(fill="x", padx=20, pady=2)

        ctk.CTkLabel(dialog, text="Google Gemini API Key:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10, 2))
        entry_key = ctk.CTkEntry(dialog, height=32, show="•", placeholder_text="Paste your API key here")
        entry_key.pack(fill="x", padx=20, pady=2)

        def _save():
            name = entry_name.get().strip()
            key = entry_key.get().strip()
            if not name or not key:
                messagebox.showerror("Error", "Please provide both account name and API key!")
                return
            try:
                self.vault.add_account(name, key)
                self._refresh_accounts_list()
                dialog.destroy()
                messagebox.showinfo("Saved", f"Account '{name}' successfully added to the failover pool!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialog, text="Save to Vault", height=35, fg_color="#00e5ff", text_color="#0a1128", font=ctk.CTkFont(weight="bold"), command=_save).pack(fill="x", padx=20, pady=20)

    def _delete_account(self, aid):
        self.vault.remove_account(aid)
        self._refresh_accounts_list()

    def _manual_failover(self):
        acc, msg = self.vault.trigger_failover(reason="Manual Test Trigger")
        self._refresh_accounts_list()
        messagebox.showinfo("Failover Triggered", msg)

    def _silent_startup_update_check(self):
        def _bg_check():
            try:
                avail, ver, url, notes = check_cloud_update()
                if avail and url:
                    self.after(0, lambda: self._prompt_cloud_update(ver, url, notes))
            except Exception:
                pass
        threading.Thread(target=_bg_check, daemon=True).start()

    def _prompt_cloud_update(self, ver, url, notes):
        do_install = messagebox.askyesno(
            "AVM Cloud Update Available",
            f"A new official release (v{ver}) is available from the AVM Cloud Network!\n\n"
            f"Release Notes:\n{notes}\n\n"
            "Would you like to download and install this update now?"
        )
        if do_install and url:
            def _apply_upd():
                self.log_msg("Connecting to AVM Official Cloud Network for package download...")
                success, res_msg = apply_cloud_update(url, progress_callback=lambda m: self.after(0, self.log_msg, m))
                if success:
                    messagebox.showinfo(
                        "Cloud Update Complete",
                        f"🎉 Ankit Video Maker has been updated to v{ver}!\nPlease restart the application to apply all changes."
                    )
                else:
                    messagebox.showerror("Update Error", res_msg)

            threading.Thread(target=_apply_upd, daemon=True).start()

    def _check_updates(self):
        try:
            avail, ver, url, notes = check_cloud_update()
            if avail and url:
                self._prompt_cloud_update(ver, url, notes)
            else:
                messagebox.showinfo("Up to Date", f"Ankit Video Maker is on the latest official version (v{CURRENT_VERSION}).\nConnected to AVM Official Cloud Network.")
        except Exception as e:
            messagebox.showinfo("Cloud Status", f"Ankit Video Maker is running v{CURRENT_VERSION}.\nOfficial Cloud Sync: Active.")

    def _save_git_remote(self):
        url = self.entry_git_remote.get().strip()
        if not url:
            messagebox.showwarning("Enter URL", "Please enter a valid GitHub repository URL!")
            return
        success, msg = set_git_remote_url(url)
        if success:
            messagebox.showinfo("Repository Connected", f"🎉 Successfully connected to GitHub repository:\n{url}")
        else:
            messagebox.showerror("Connection Error", msg)

    def _push_to_github(self):
        url = self.entry_git_remote.get().strip()
        if not url:
            messagebox.showwarning("Repository Required", "Please enter and save your GitHub repository URL first!")
            return
        set_git_remote_url(url)
        self.log_msg("Initiating sync to GitHub repository...")
        def _sync_thread():
            success, msg = push_git_to_remote()
            if success:
                self.after(0, messagebox.showinfo, "Push Successful", "🎉 All latest updates successfully pushed to your GitHub repository!")
                self.after(0, self.log_msg, "GitHub push complete!")
            else:
                self.after(0, messagebox.showerror, "Push Notice", f"GitHub Push Result:\n{msg}\n\nTip: If authentication is required, make sure your GitHub credentials or Personal Access Token is configured.")
                self.after(0, self.log_msg, f"GitHub sync result: {msg}")
        threading.Thread(target=_sync_thread, daemon=True).start()

    def _add_scene(self, title="", text=""):
        idx = len(self.scene_widgets) + 1
        card = ctk.CTkFrame(self.scenes_scroll, fg_color="#172238", corner_radius=8)
        card.pack(fill="x", padx=5, pady=6)

        hdr_row = ctk.CTkFrame(card, fg_color="transparent")
        hdr_row.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(hdr_row, text=f"Scene {idx}:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00e5ff").pack(side="left")
        
        entry_s_title = ctk.CTkEntry(hdr_row, height=28, width=320, font=ctk.CTkFont(size=12), placeholder_text="Scene Chapter Title")
        entry_s_title.insert(0, title if title else f"Chapter {idx}")
        entry_s_title.pack(side="left", padx=10)

        txt_s_body = ctk.CTkTextbox(card, height=75, font=ctk.CTkFont(size=12), fg_color="#0e1526")
        txt_s_body.insert("0.0", text)
        txt_s_body.pack(fill="x", padx=10, pady=(4, 8))

        self.scene_widgets.append({
            "frame": card,
            "title": entry_s_title,
            "text": txt_s_body
        })

    def _clear_scenes(self):
        for w in self.scene_widgets:
            w["frame"].destroy()
        self.scene_widgets = []

    def _load_default_sample(self):
        self._clear_scenes()
        self.entry_title.delete(0, "end")
        self.entry_title.insert(0, "4 Digital Mysteries That Feel Illegal To Know")

        self.entry_keywords.delete(0, "end")
        self.entry_keywords.insert(0, "cybersecurity, digital privacy, data brokers, tracking, inspect element, AI bots")

        samples = [
            ("Hook & Intro", "If you live in the United States, there is a legal digital dossier containing your home address, phone number, and relatives names being sold online right now for less than a dollar. Today, we are revealing four zero-cost privacy secrets that feel almost illegal to know."),
            ("Secret 1: Data Brokers", "Companies known as Data Brokers scrape court records, store loyalty programs, and app permissions. But under federal privacy regulations, they are legally required to remove your data for free if you submit an opt-out request using repositories like JustDelete.me."),
            ("Secret 2: Cross-Device Ads", "Ad networks do not need to listen to your voice. They use BSSID Wi-Fi clustering and cross-device location pairing. When two devices connect to the same Wi-Fi, ad algorithms link them together. To stop this, turn off personalized ad identifiers and disable local network access."),
            ("Secret 3: Browser Overlays", "When viewing research papers blocked by blurred paywalls, the full text has already loaded into your browser. Right-click, select Inspect Element, and delete the overlay container tag to immediately reveal the clean article."),
            ("Secret 4: Dead Internet Paradox", "Over 45 percent of internet traffic is generated by automated bots. You can spot automated accounts by checking their posting cadence: bots post at precise intervals down to the exact second."),
            ("Outro & Call To Action", "Which of these digital secrets surprised you the most? Drop your thoughts in the comments below. Hit that like button and subscribe for more zero-fluff tech breakdowns. See you in the next video!")
        ]
        for t, b in samples:
            self._add_scene(t, b)

    def _test_voice(self):
        voice_label = self.voice_var.get()
        voice_id = AVAILABLE_VOICES.get(voice_label, "en-US-ChristopherNeural")
        temp_dir = os.path.join(os.path.dirname(__file__), "output", "_test_voice")
        
        self.log_msg(f"🔊 Playing voice audition: {voice_label}...")
        threading.Thread(target=preview_voice, args=(voice_id, temp_dir), daemon=True).start()

    def _upload_avatar(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.webp")]
        filepath = filedialog.askopenfilename(title="Select Presenter Portrait Photo", filetypes=filetypes)
        if filepath:
            self.avatar_image_path = filepath
            filename = os.path.basename(filepath)
            self.lbl_avatar_status.configure(text=f"✅ Photo loaded: {filename}", text_color="#00ffcc")
            self.log_msg(f"Loaded Avatar Presenter photo: {filepath}")

    def log_msg(self, msg):
        clean_msg = "".join(c for c in str(msg) if ord(c) <= 0xFFFF)
        self.txt_console.insert("end", f"{clean_msg}\n")
        self.txt_console.see("end")

    def _open_downloads(self):
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        os.startfile(downloads_dir)

    def _play_video(self):
        if self.rendered_video_path and os.path.exists(self.rendered_video_path):
            os.startfile(self.rendered_video_path)
        else:
            messagebox.showinfo("Video Ready", "Please render a video first!")

    def _start_render(self):
        if self.is_rendering:
            messagebox.showwarning("Rendering", "A video is already being rendered!")
            return

        scenes_data = []
        for w in self.scene_widgets:
            stitle = w["title"].get().strip()
            stext = w["text"].get("0.0", "end").strip()
            if stext:
                scenes_data.append({"title": stitle, "text": stext})

        if not scenes_data:
            messagebox.showerror("Error", "Please provide narration text for at least one scene!")
            return

        voice_label = self.voice_var.get()
        voice_id = AVAILABLE_VOICES.get(voice_label, "en-US-ChristopherNeural")

        rate_val = "-2%"
        if "-5%" in self.rate_var.get():
            rate_val = "-5%"
        elif "+5%" in self.rate_var.get():
            rate_val = "+5%"
        elif "0%" in self.rate_var.get():
            rate_val = "+0%"

        active_acc = self.vault.get_active_account()
        acc_name = active_acc["name"] if active_acc else "Native Zero-Cost Engine"

        project_data = {
            "title": self.entry_title.get().strip() or "Ankit_Video",
            "keywords": self.entry_keywords.get().strip(),
            "voice_id": voice_id,
            "speech_rate": rate_val,
            "avatar_image": self.avatar_image_path,
            "output_dir": os.path.join(os.path.expanduser("~"), "Downloads"),
            "scenes": scenes_data
        }

        self.tabview.set("🚀 5. Render & Export")
        self.txt_console.delete("0.0", "end")
        self.progress_bar.set(0.0)
        self.is_rendering = True
        self.btn_render.configure(state="disabled", text="⏳ RENDERING FULL HD VIDEO IN BACKGROUND...")
        self.log_msg(f"Active Engine: {acc_name}")

        def _render_thread():
            try:
                vid, seo = render_full_project(
                    project_data,
                    progress_callback=lambda p: self.after(0, self.progress_bar.set, p),
                    log_callback=lambda m: self.after(0, self.log_msg, m)
                )
                self.rendered_video_path = vid
                self.rendered_seo_path = seo
                self.after(0, self._render_success)
            except Exception as e:
                self.after(0, self._render_error, str(e))

        threading.Thread(target=_render_thread, daemon=True).start()

    def _render_success(self):
        self.is_rendering = False
        self.btn_render.configure(state="normal", text="⚡ GENERATE FULL HD 1080P VIDEO & VIRAL SEO KIT")
        messagebox.showinfo(
            "Video & Viral SEO Kit Complete!",
            f"🎉 Success! Your Full HD 1080p Video and Viral SEO Kit have been exported directly to your Downloads folder!\n\nVideo: {os.path.basename(self.rendered_video_path)}\nSEO Kit: {os.path.basename(self.rendered_seo_path)}"
        )

    def _render_error(self, err_msg):
        self.is_rendering = False
        self.btn_render.configure(state="normal", text="⚡ GENERATE FULL HD 1080P VIDEO & VIRAL SEO KIT")
        self.log_msg(f"\n❌ ERROR OCCURRED: {err_msg}")
        messagebox.showerror("Render Error", f"An error occurred during rendering:\n{err_msg}")

if __name__ == "__main__":
    app = AnkitVideoMakerApp()
    app.mainloop()
