import os
import datetime

def generate_viral_seo_kit(project_title, topic_keywords, scenes=None, output_dir=None):
    """
    Generates a complete YouTube / Instagram / Facebook Viral SEO Kit:
    - 5 High-CTR Curiosity-Gap Titles
    - Full Search-Optimized Description with Timestamps & Chapters
    - 30 High-Velocity Tags (comma-separated copy-paste ready)
    - High-CTR Thumbnail Design Framework & Visual Prompts
    """
    # Support both (title, kw, scenes, output_dir) and (title, kw, output_path)
    if isinstance(scenes, str) and output_dir is None:
        target_path = scenes
        scenes = []
        if os.path.isdir(target_path):
            output_dir = target_path
            filename = f"{''.join(c for c in project_title if c.isalnum() or c in (' ', '_')).rstrip()}_VIRAL_SEO_KIT.txt"
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = target_path
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
    else:
        if scenes is None:
            scenes = []
        if output_dir is None:
            output_dir = os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{''.join(c for c in project_title if c.isalnum() or c in (' ', '_')).rstrip()}_VIRAL_SEO_KIT.txt"
        filepath = os.path.join(output_dir, filename)

    # 1. Calculate Timestamps
    timestamps = []
    current_time = 0.0
    for idx, scene in enumerate(scenes):
        m = int(current_time // 60)
        s = int(current_time % 60)
        timestamps.append(f"{m:02d}:{s:02d} - {scene.get('title', f'Chapter {idx+1}')}")
        current_time += scene.get("duration", 30.0)

    # 2. Extract Keywords
    raw_kw = [k.strip() for k in topic_keywords.split(",") if k.strip()]
    if not raw_kw:
        raw_kw = ["technology", "cybersecurity", "digital privacy", "internet secrets", "tech guide"]

    kw_primary = raw_kw[0].capitalize()
    kw_secondary = raw_kw[1] if len(raw_kw) > 1 else "Tech Secrets"

    # 3. High-CTR Viral Titles
    viral_titles = [
        f"4 {kw_primary} Secrets That Feel ALMOST ILLEGAL To Know (Don't Ignore This!)",
        f"Stop Doing This! The Hidden {kw_primary} Truth Most People Never Realize",
        f"How To Protect Yourself From {kw_primary} in 2026 (Zero Cost Tutorial)",
        f"The {kw_primary} Mystery Nobody Talks About... Until Now! [Full Guide]",
        f"Why Everyone Is Wrong About {kw_primary} (What Tech Companies Won't Tell You)"
    ]

    # 4. Tags Compilation (30 high-ranking SEO tags)
    base_tags = [
        kw_primary.lower(),
        f"{kw_primary.lower()} 2026",
        f"{kw_primary.lower()} guide",
        f"{kw_primary.lower()} tutorial",
        "tech hacks",
        "digital privacy",
        "cybersecurity",
        "internet mystery",
        "how to protect your data",
        "privacy settings",
        "data broker opt out",
        "cross device tracking",
        "inspect element tricks",
        "dead internet theory",
        "viral tech breakdown",
        "zero cost tools",
        "online security",
        "trending tech",
        "tech explainer",
        "algorithm secrets"
    ]
    # Add custom user keywords
    for k in raw_kw:
        if k.lower() not in base_tags:
            base_tags.append(k.lower())

    tags_formatted = ", ".join(base_tags[:30])

    # 5. Build Comprehensive SEO Document
    content = f"""================================================================================
           ANKIT VIDEO MAKER - VIRAL SEO & ALGORITHM BOOST KIT
================================================================================
Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Target Video: {project_title}
Status: 100% Algorithmic Optimization (YouTube, Instagram, Facebook, TikTok)
================================================================================

1. TOP 5 HIGH-CTR VIRAL TITLES (Choose the one with highest curiosity gap):
--------------------------------------------------------------------------------
Option 1 (Highest CTR):
  {viral_titles[0]}

Option 2 (Urgency & Warning):
  {viral_titles[1]}

Option 3 (Actionable Tutorial):
  {viral_titles[2]}

Option 4 (Deep Mystery Hook):
  {viral_titles[3]}

Option 5 (Contrarian / Debate Starter):
  {viral_titles[4]}

--------------------------------------------------------------------------------
2. FULL OPTIMIZED VIDEO DESCRIPTION (Copy & paste directly into YouTube):
--------------------------------------------------------------------------------
In this video, we break down high-level {kw_primary} secrets, zero-cost privacy tools, 
and practical steps you can take right now to protect your digital footprint. 
No generic fluff—only high-value, actionable technical insights that most platforms won't reveal.

Make sure to watch until the end to understand the full mechanism!

 TIMESTAMPS & CHAPTERS:
"""
    for ts in timestamps:
        content += f"{ts}\n"

    content += f"""
 KEY TAKEAWAYS:
• How modern data aggregation networks quietly build profiles.
• The exact settings to toggle on your mobile devices to break cross-device ad graphs.
• How to bypass client-side paywalls using native browser Developer Tools.
• Recognizing synthetic AI accounts and bot swarms on social feeds.

 LINKS & TOOLS MENTIONED:
• JustDelete.me (Data Broker Directory)
• Privacy Rights Clearinghouse
• Official Opt-Out Repositories

If you found this breakdown valuable, smash that LIKE button and SUBSCRIBE for more zero-fluff tech guides!
Drop your thoughts in the comments below: Which secret surprised you the most?

#CyberSecurity #{kw_primary.replace(' ', '')} #TechTips #DigitalPrivacy #OnlineSecurity #TrendingTech #LifeHacks

--------------------------------------------------------------------------------
3. HIGH-VELOCITY SEARCH TAGS (Copy & paste directly into Tags field):
--------------------------------------------------------------------------------
{tags_formatted}

--------------------------------------------------------------------------------
4. HIGH-CTR THUMBNAIL DESIGN BLUEPRINT (Proven to exceed 10% CTR):
--------------------------------------------------------------------------------
• Primary Focal Point: High-contrast close-up of a dark cyber room or human portrait 
  with glowing neon warning badges (red or electric cyan).
• Text Overlay (Max 3-4 Words): "DELETE THIS NOW!" or "STOP DOING THIS!" or "THEY KNOW EVERYTHING"
• Typography: Ultra-bold sans-serif font (Impact, Bebas Neue, Montserrat ExtraBold) 
  with yellow or neon green fill and deep black drop-shadow.
• Psychological Trigger: Curiosity & urgent warning (avoid crowded imagery; 
  use rule of thirds with clear subject on right and bold text on left).

================================================================================
END OF VIRAL SEO KIT - ANKIT VIDEO MAKER
================================================================================
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath

# Backward compatibility alias
generate_seo_kit = generate_viral_seo_kit

