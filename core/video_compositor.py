import os
import time
import subprocess
import imageio_ffmpeg
from .voice_engine import generate_scene_audio
from .music_engine import generate_procedural_bgm
from .avatar_engine import generate_avatar_frame, generate_procedural_cyber_canvas, fetch_ai_visual_frame
from .seo_engine import generate_viral_seo_kit

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30

def render_full_project(project_data, progress_callback=None, log_callback=None):
    """
    Renders the complete video project:
    1. Generates neural speech + SRT subtitles for each scene
    2. Composes avatar / procedural visuals
    3. Generates procedural 100% royalty-free BGM
    4. Renders scene MP4s via FFmpeg (ultrafast, Ken Burns, 85/15 audio mix)
    5. Concat all scenes losslessly into Downloads folder
    6. Generates Viral SEO Kit text file in Downloads folder
    """
    def log(msg):
        clean_msg = "".join(c for c in str(msg) if ord(c) <= 0xFFFF)
        if log_callback:
            try:
                log_callback(clean_msg)
            except Exception:
                pass
        try:
            print(clean_msg, flush=True)
        except Exception:
            pass
        
    def set_progress(pct):
        if progress_callback:
            progress_callback(pct)

    # Cryptographic License Guard (Anti-Bypass Protection)
    from .license_engine import load_active_license
    is_active, _ = load_active_license()
    if not is_active:
        raise PermissionError("AVM Security Violation: An active cryptographically signed license or Super Admin authorization is required to render videos.")

    title = project_data.get("title", "My_Video")
    voice_id = project_data.get("voice_id", "en-US-ChristopherNeural")
    speech_rate = project_data.get("speech_rate", "-2%")
    avatar_image = project_data.get("avatar_image", None)
    output_dir = project_data.get("output_dir", os.path.join(os.path.expanduser("~"), "Downloads"))
    keywords = project_data.get("keywords", "tech, cybersecurity, privacy")
    scenes = project_data.get("scenes", [])
    
    clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    final_video_path = os.path.join(output_dir, f"{clean_title}_1080p.mp4")
    temp_dir = os.path.join(output_dir, "_temp_avm")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    log(f"==================================================")
    log(f"ANKIT VIDEO MAKER - RENDERING: {title}")
    log(f"Target Export: {final_video_path}")
    log(f"Voice: {voice_id} | Scenes: {len(scenes)}")
    log(f"==================================================")
    
    set_progress(0.05)
    
    # 1. Generate Voice & Subtitles for all scenes
    total_duration = 0.0
    processed_scenes = []
    
    for idx, sc in enumerate(scenes):
        sc_num = idx + 1
        log(f"-> Generating Voiceover for Scene {sc_num}/{len(scenes)}...")
        sc_audio = os.path.join(temp_dir, f"scene{sc_num}.mp3")
        sc_srt = os.path.join(temp_dir, f"scene{sc_num}.srt")
        
        generate_scene_audio(sc["text"], voice_id, speech_rate, sc_audio, sc_srt)
        
        # Get duration
        cmd = [FFMPEG, "-i", sc_audio]
        res = subprocess.run(cmd, capture_output=True, text=True)
        dur = 10.0
        for line in res.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.strip().split(",")[0].replace("Duration:", "").strip().split(":")
                dur = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
                break
                
        sc_info = dict(sc)
        sc_info["audio_path"] = sc_audio
        sc_info["srt_path"] = sc_srt
        sc_info["duration"] = dur
        sc_info["bgm_offset"] = total_duration
        total_duration += dur
        processed_scenes.append(sc_info)
        set_progress(0.05 + 0.25 * (idx + 1) / len(scenes))
        
    log(f"Total Video Narration Duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
    
    # 2. Generate Procedural Royalty-Free BGM
    log("-> Generating 100% Royalty-Free Procedural BGM...")
    bgm_path = os.path.join(temp_dir, "procedural_bgm.wav")
    generate_procedural_bgm(bgm_path, total_duration=total_duration + 5.0)
    set_progress(0.35)
    
    # 3. Render Each Scene
    scene_mp4s = []
    for idx, sc in enumerate(processed_scenes):
        sc_num = idx + 1
        dur = sc["duration"]
        log(f"\n-> Rendering Scene {sc_num}: {sc.get('title', 'Chapter')} ({dur:.2f}s)...")
        
        # Setup visual frame
        visual_base = os.path.join(temp_dir, f"visual_{sc_num}.jpg")
        custom_img = sc.get("image_path")
        
        if custom_img and os.path.exists(custom_img):
            base_to_use = custom_img
        else:
            base_to_use = os.path.join(temp_dir, f"cyber_{sc_num}.jpg")
            log(f"   [AI Visual] Generating 1080p cinematic visual for Scene {sc_num}...")
            ai_prompt = sc.get("visual_prompt", "") or f"cinematic high budget documentary shot, {sc.get('title', '')}, {keywords}, dark atmospheric 8k wallpaper"
            fetch_ai_visual_frame(ai_prompt, base_to_use, fallback_title=sc.get("title", f"Scene {sc_num}"), fallback_subtitle=sc.get("text", "")[:60])
            
        if avatar_image and os.path.exists(avatar_image):
            generate_avatar_frame(base_to_use, avatar_image, visual_base)
        else:
            from PIL import Image
            Image.open(base_to_use).convert("RGB").resize((1920, 1080)).save(visual_base)
            
        # Ken Burns Shot
        shot_mp4 = os.path.join(temp_dir, f"sc{sc_num}_shot.mp4")
        d_frames = int(dur * FPS)
        vf_shot = f"zoompan=z='min(zoom+0.00015,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d_frames}:s=1920x1080:fps={FPS}"
        cmd_shot = [
            FFMPEG, "-y",
            "-i", visual_base,
            "-vf", vf_shot,
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            shot_mp4
        ]
        subprocess.run(cmd_shot, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Merge Audio (85% VO / 15% BGM) & Burn Subtitles
        sc_final = os.path.join(temp_dir, f"sc{sc_num}_final.mp4")
        escaped_srt = os.path.abspath(sc["srt_path"]).replace('\\', '/').replace(':', r'\:')
        filter_graph = (
            f"subtitles='{escaped_srt}':force_style='FontName=Segoe UI,FontSize=28,Bold=1,"
            f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,"
            f"BorderStyle=3,MarginV=50'[v];"
            f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.85[vo];"
            f"[2:a]volume=0.15[bgm];"
            f"[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )
        cmd_merge = [
            FFMPEG, "-y",
            "-i", shot_mp4,
            "-i", sc["audio_path"],
            "-ss", str(sc["bgm_offset"]), "-t", str(dur), "-i", bgm_path,
            "-filter_complex", filter_graph,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            sc_final
        ]
        subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        scene_mp4s.append(sc_final)
        
        set_progress(0.35 + 0.50 * (sc_num / len(processed_scenes)))
        log(f"   Scene {sc_num} complete! ({os.path.getsize(sc_final):,} bytes)")
        
    # 4. Master Lossless Concat
    log("\n-> Assembling all scenes into Master Full HD 1080p Video...")
    concat_list = os.path.join(temp_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for sf in scene_mp4s:
            f.write(f"file '{sf.replace(chr(92), '/')}'\n")
            
    cmd_concat = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy",
        final_video_path
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    set_progress(0.92)
    
    # 5. Generate Viral SEO Kit Text File
    log("-> Generating Viral SEO Kit (Titles, Description, Tags, Thumbnail Framework)...")
    seo_file = generate_viral_seo_kit(title, keywords, processed_scenes, output_dir)
    set_progress(1.0)
    
    log(f"\n==================================================")
    log(f"EXPORT COMPLETE!")
    log(f"[VIDEO] Path: {final_video_path} ({os.path.getsize(final_video_path)/(1024*1024):.2f} MB)")
    log(f"[SEO KIT] Path: {seo_file}")
    log(f"==================================================")
    
    return final_video_path, seo_file
