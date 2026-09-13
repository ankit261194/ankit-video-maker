import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def create_circular_avatar(image_path, size=(450, 450), glow_color=(0, 230, 255)):
    """
    Crops user photo into a circular avatar with glowing cyber HUD border.
    """
    img = Image.open(image_path).convert("RGBA")
    
    # Square crop center
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize(size, Image.Resampling.LANCZOS)
    
    # Circular mask
    mask = Image.new("L", size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, size[0], size[1]), fill=255)
    
    # Output avatar with transparency
    avatar = Image.new("RGBA", size, (0, 0, 0, 0))
    avatar.paste(img, (0, 0), mask=mask)
    
    # Add glowing border rings
    border_img = Image.new("RGBA", (size[0] + 40, size[1] + 40), (0, 0, 0, 0))
    draw_border = ImageDraw.Draw(border_img)
    
    # Outer glow
    glow_box = (10, 10, size[0] + 30, size[1] + 30)
    draw_border.ellipse(glow_box, outline=(*glow_color, 120), width=6)
    
    # Inner sharp neon ring
    inner_box = (18, 18, size[0] + 22, size[1] + 22)
    draw_border.ellipse(inner_box, outline=(*glow_color, 255), width=4)
    
    border_img.paste(avatar, (20, 20), mask=avatar)
    return border_img

def generate_avatar_badge(avatar_path, output_path, size=(450, 450), glow_color=(0, 230, 255)):
    """
    Saves a circular cyber HUD avatar badge directly to a file.
    If avatar_path is None or doesn't exist, creates an official AVM holographic presenter badge.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if avatar_path and os.path.exists(avatar_path):
        badge = create_circular_avatar(avatar_path, size=size, glow_color=glow_color)
    else:
        # Create neon holographic presenter badge
        total_size = (size[0] + 40, size[1] + 40)
        badge = Image.new("RGBA", total_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge)
        glow_box = (10, 10, size[0] + 30, size[1] + 30)
        draw.ellipse(glow_box, fill=(12, 20, 36, 220), outline=(*glow_color, 150), width=6)
        inner_box = (20, 20, size[0] + 20, size[1] + 20)
        draw.ellipse(inner_box, outline=(*glow_color, 255), width=3)
        draw.text((size[0]//2 - 40, size[1]//2), "AVM PRESENTER", fill=(0, 230, 255))
    badge.save(output_path, format="PNG")
    return output_path

def generate_avatar_frame(base_visual_path, avatar_path, output_path, scale_pulse=1.0):
    """
    Composes the user's avatar onto the scene background with dynamic pulse framing.
    """
    base = Image.open(base_visual_path).convert("RGBA").resize((1920, 1080), Image.Resampling.LANCZOS)
    
    if avatar_path and os.path.exists(avatar_path):
        avatar = create_circular_avatar(avatar_path, size=(420, 420))
        if scale_pulse != 1.0:
            new_w = int(avatar.width * scale_pulse)
            new_h = int(avatar.height * scale_pulse)
            avatar = avatar.resize((new_w, new_h), Image.Resampling.BILINEAR)
            
        # Place in bottom-right anchor position (Broadcast style)
        pos_x = 1920 - avatar.width - 60
        pos_y = 1080 - avatar.height - 110 # Above subtitle zone
        base.paste(avatar, (pos_x, pos_y), mask=avatar)
        
    base.convert("RGB").save(output_path, quality=95)
    return output_path

def generate_procedural_cyber_canvas(title, subtitle, output_path, theme="blue"):
    """
    Generates a 1080p high-tech cyber background if user doesn't have custom images.
    """
    w, h = 1920, 1080
    canvas = Image.new("RGB", (w, h), (8, 12, 22))
    draw = ImageDraw.Draw(canvas)
    
    accent = (0, 220, 255) if theme == "blue" else (0, 255, 160)
    
    # Draw high tech grid
    for x in range(0, w, 80):
        draw.line([(x, 0), (x, h)], fill=(16, 25, 45), width=1)
    for y in range(0, h, 80):
        draw.line([(0, y), (w, y)], fill=(16, 25, 45), width=1)
        
    # Cyber HUD borders
    draw.rectangle([40, 40, w - 40, h - 40], outline=accent, width=2)
    draw.rectangle([35, 35, 75, 75], outline=(255, 255, 255), width=3)
    draw.rectangle([w - 75, 35, w - 35, 75], outline=(255, 255, 255), width=3)
    
    # Title badge
    draw.rectangle([100, 100, 700, 170], fill=(15, 25, 50))
    draw.rectangle([100, 100, 700, 170], outline=accent, width=2)
    draw.text((120, 115), title[:40].upper(), fill=(255, 255, 255))
    draw.text((120, 142), subtitle[:60], fill=accent)
    
    canvas.save(output_path, quality=95)
    return output_path

def fetch_ai_visual_frame(prompt_text, output_path, fallback_title="SCENE", fallback_subtitle=""):
    """
    Generates an ultra-crisp 1080p AI cinematic visual using Pollinations Flux engine.
    If offline or network times out, seamlessly falls back to procedural cyber canvas.
    """
    import urllib.request
    import urllib.parse
    clean_prompt = prompt_text.strip() if prompt_text else ""
    if not clean_prompt:
        clean_prompt = f"cinematic documentary visualization, {fallback_title}, 8k high quality dark tech aesthetic"
    
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt[:300])}?width=1920&height=1080&model=flux&nologo=true"
    req = urllib.request.Request(url, headers={"User-Agent": "AVM-Flux-Cinematic/2.5"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = response.read()
                if len(data) > 5000:
                    import io
                    img = Image.open(io.BytesIO(data)).convert("RGB")
                    img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                    img.save(output_path, quality=95)
                    return True
    except Exception:
        pass
    
    # Fallback to procedural cyber canvas
    generate_procedural_cyber_canvas(fallback_title, fallback_subtitle, output_path)
    return False

def create_thumbnail(image_path, thumb_path, size=(160, 90)):
    """
    Creates a high-quality 16:9 thumbnail for GUI scene preview.
    """
    try:
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        img = Image.open(image_path).convert("RGB")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        thumb = Image.new("RGB", size, (10, 15, 25))
        pos_x = (size[0] - img.width) // 2
        pos_y = (size[1] - img.height) // 2
        thumb.paste(img, (pos_x, pos_y))
        thumb.save(thumb_path, "JPEG", quality=85)
        return thumb_path
    except Exception:
        return None
