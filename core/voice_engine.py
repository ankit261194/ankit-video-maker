import asyncio
import os
import winsound
import edge_tts
import imageio_ffmpeg
import subprocess

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

AVAILABLE_VOICES = {
    "English - Christopher (Deep Tech Male)": "en-US-ChristopherNeural",
    "English - Guy (Natural American Male)": "en-US-GuyNeural",
    "English - Aria (Professional Female)": "en-US-AriaNeural",
    "English - Jenny (Conversational Female)": "en-US-JennyNeural",
    "English - Ryan (British Tech Male)": "en-GB-RyanNeural",
    "Hindi - Madhur (Natural Hindi Male Narrator)": "hi-IN-MadhurNeural",
    "Hindi - Swara (Natural Hindi Female Narrator)": "hi-IN-SwaraNeural"
}

def play_audio_async(wav_path):
    try:
        winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print("Audio play error:", e)

async def _gen_sample_and_play(voice_id, temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    mp3_path = os.path.join(temp_dir, "sample_preview.mp3")
    wav_path = os.path.join(temp_dir, "sample_preview.wav")

    sample_text = (
        "नमस्ते, यह अंकित वीडियो मेकर की नेचुरल हिंदी आवाज़ है।"
        if "hi-IN" in voice_id else
        "Hello! This is an authentic voice sample from Ankit Video Maker."
    )

    for attempt in range(3):
        try:
            comm = edge_tts.Communicate(sample_text, voice_id, rate="-2%")
            await comm.save(mp3_path)
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 500:
                break
        except Exception:
            await asyncio.sleep(0.8 * (attempt + 1))

    # Convert to WAV for instant winsound playback
    cmd = [FFMPEG, "-y", "-i", mp3_path, "-ac", "2", "-ar", "44100", wav_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(wav_path):
        play_audio_async(wav_path)

def preview_voice(voice_id, temp_dir):
    """
    Called from UI thread to generate and play instant voice preview.
    """
    asyncio.run(_gen_sample_and_play(voice_id, temp_dir))

async def _generate_audio_and_subs(text, voice_id, rate_str, audio_out, srt_out):
    ad = os.path.dirname(audio_out)
    if ad:
        os.makedirs(ad, exist_ok=True)
    sd = os.path.dirname(srt_out)
    if sd:
        os.makedirs(sd, exist_ok=True)
    
    last_err = None
    for attempt in range(4):
        try:
            submaker = edge_tts.SubMaker()
            comm = edge_tts.Communicate(text, voice_id, rate=rate_str)
            
            with open(audio_out, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                        submaker.feed(chunk)
                        
            srt_content = submaker.get_srt()
            if not srt_content.strip():
                srt_content = f"1\n00:00:00,000 --> 00:00:05,000\n{text[:80]}\n\n"
                
            with open(srt_out, "w", encoding="utf-8") as f:
                f.write(srt_content)
                
            if os.path.exists(audio_out) and os.path.getsize(audio_out) > 500:
                return
        except Exception as e:
            last_err = e
            await asyncio.sleep(1.0 * (attempt + 1))
            
    if last_err:
        raise last_err

def generate_scene_audio(text, voice_id, rate_str, audio_out, srt_out):
    rate_clean = str(rate_str).strip() if rate_str else "+0%"
    if not rate_clean.startswith(("+", "-")):
        rate_clean = "+" + rate_clean
    if not rate_clean.endswith("%"):
        rate_clean = rate_clean + "%"
    asyncio.run(_generate_audio_and_subs(text, voice_id, rate_clean, audio_out, srt_out))
