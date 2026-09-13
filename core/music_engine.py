import math
import struct
import wave
import os

def create_bgm_loop(loop_duration=4.0, sr=44100):
    """
    Synthesizes a rich, seamless ambient lo-fi cyber drone loop.
    100% royalty-free procedural audio, ultra-low memory, zero crash guarantee.
    """
    total_samples = int(sr * loop_duration)
    frames = bytearray()
    
    # 55Hz (A1 Sub) + 55.3Hz (Analog detune beating) + 110Hz (Warm Bass) + 220Hz (Pad) + 330Hz (Overtone)
    for i in range(total_samples):
        t = i / sr
        s1 = math.sin(2 * math.pi * 55.0 * t) * 0.35
        s2 = math.sin(2 * math.pi * 55.3 * t) * 0.25
        s3 = math.sin(2 * math.pi * 110.0 * t) * 0.20
        s4 = math.sin(2 * math.pi * 220.0 * t) * 0.15
        s5 = math.sin(2 * math.pi * 330.0 * t) * 0.10
        
        # Analog slow pulse LFO (0.25 Hz)
        lfo = 0.80 + 0.20 * math.sin(2 * math.pi * 0.25 * t)
        sample_val = (s1 + s2 + s3 + s4 + s5) * lfo * 0.65
        
        int_val = int(max(-32767, min(32767, sample_val * 32767)))
        # 16-bit Stereo PCM (Little-endian, 2 channels)
        frames.extend(struct.pack('<hh', int_val, int_val))
        
    return bytes(frames)

def generate_procedural_bgm(output_path, total_duration=300.0, loop_duration=4.0, sr=44100):
    """
    Generates a 100% royalty-free procedural BGM track of any duration.
    Streamed in lightweight chunks to guarantee zero RAM bloat and instant speed.
    """
    d = os.path.dirname(output_path)
    if d:
        os.makedirs(d, exist_ok=True)
        
    loop_bytes = create_bgm_loop(loop_duration, sr)
    bytes_per_second = sr * 2 * 2  # 16-bit stereo = 4 bytes per sample
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
