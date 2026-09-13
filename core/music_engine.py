import numpy as np
import wave
import os

def create_bgm_loop(loop_duration=32.0, sr=44100):
    samples = int(sr * loop_duration)
    t = np.linspace(0, loop_duration, samples, endpoint=False, dtype=np.float32)
    
    # 1. Analog Sub-bass Drone (55 Hz A1) with slow detune beating
    bass = 0.30 * np.sin(2 * np.pi * 55.0 * t, dtype=np.float32) + \
           0.22 * np.sin(2 * np.pi * 55.25 * t, dtype=np.float32) + \
           0.10 * np.sin(2 * np.pi * 110.0 * t, dtype=np.float32)
           
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (1.0 / loop_duration * 2) * t, dtype=np.float32)
    bass *= lfo
    
    # 2. Ambient Lo-Fi Chords (Am7 -> Fmaj7 -> Dm9 -> Em7)
    pad_l = np.zeros(samples, dtype=np.float32)
    pad_r = np.zeros(samples, dtype=np.float32)
    
    chords = [
        [220.0, 261.63, 329.63, 392.0],   # Am7
        [174.61, 220.0, 261.63, 329.63],  # Fmaj7
        [146.83, 220.0, 261.63, 349.23],  # Dm7
        [164.81, 196.0, 246.94, 329.63]   # Em7
    ]
    
    seg_len = int(samples // 4)
    fade_len = int(sr * 1.0)
    for c_idx, freqs in enumerate(chords):
        s_idx = c_idx * seg_len
        e_idx = s_idx + seg_len
        c_t = np.linspace(0, seg_len / sr, seg_len, endpoint=False, dtype=np.float32)
        
        env = np.ones(seg_len, dtype=np.float32)
        env[:fade_len] = np.linspace(0, 1, fade_len, dtype=np.float32)
        env[-fade_len:] = np.linspace(1, 0, fade_len, dtype=np.float32)
        
        sig_l = np.zeros(seg_len, dtype=np.float32)
        sig_r = np.zeros(seg_len, dtype=np.float32)
        for f_idx, f in enumerate(freqs):
            phase_l = f_idx * 0.4
            phase_r = f_idx * 0.4 + 0.3
            sig_l += 0.04 * np.sin(2 * np.pi * f * c_t + phase_l, dtype=np.float32)
            sig_r += 0.04 * np.sin(2 * np.pi * (f * 1.002) * c_t + phase_r, dtype=np.float32)
            
        pad_l[s_idx:e_idx] += sig_l * env
        pad_r[s_idx:e_idx] += sig_r * env
        
    # 3. Lo-Fi Texture Noise
    np.random.seed(42)
    noise = np.random.normal(0, 0.010, samples).astype(np.float32)
    
    # 4. Soft Cyber Pulse Beat
    beat_step = int(sr * 2.0)
    kick_len = int(sr * 0.12)
    k_t = np.linspace(0, 0.12, kick_len, endpoint=False, dtype=np.float32)
    kick = (0.18 * np.sin(2 * np.pi * (65 - 25 * k_t / 0.12) * k_t, dtype=np.float32) * np.exp(-20 * k_t)).astype(np.float32)
    
    beats = np.zeros(samples, dtype=np.float32)
    for b in range(0, samples, beat_step):
        if b + kick_len <= samples:
            beats[b:b+kick_len] += kick
            
    mix_l = bass + pad_l + noise + beats
    mix_r = bass + pad_r + noise + beats
    
    peak = max(np.max(np.abs(mix_l)), np.max(np.abs(mix_r)))
    if peak > 0:
        mix_l = (mix_l / peak) * 0.70
        mix_r = (mix_r / peak) * 0.70
        
    left_i16 = (mix_l * 32767).astype(np.int16)
    right_i16 = (mix_r * 32767).astype(np.int16)
    
    stereo_interleaved = np.empty((samples * 2,), dtype=np.int16)
    stereo_interleaved[0::2] = left_i16
    stereo_interleaved[1::2] = right_i16
    
    return stereo_interleaved.tobytes()

def generate_procedural_bgm(output_path, total_duration=300.0, loop_duration=32.0, sr=44100):
    """
    Generates a 100% royalty-free procedural BGM track of any duration.
    Streamed in small memory chunks to prevent RAM bloat.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    loop_bytes = create_bgm_loop(loop_duration, sr)
    bytes_per_second = sr * 2 * 2
    target_bytes = int(total_duration * bytes_per_second)
    
    with wave.open(output_path, 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        
        written = 0
        while written < target_bytes:
            to_write = min(len(loop_bytes), target_bytes - written)
            wav.writeframes(loop_bytes[:to_write])
            written += to_write
            
    return output_path
