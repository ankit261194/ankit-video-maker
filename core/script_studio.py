import os
import json

def generate_viral_script_ai(topic, category="Mystery", tone="High-Retention Mystery", language="English", gemini_api_key=None):
    """
    Generates a full structured video script.
    Uses Google Gemini API if key is present, otherwise falls back to the algorithmic prompt engine.
    """
    # Cryptographic License Guard (Anti-Bypass Protection)
    from .license_engine import load_active_license
    is_active, _ = load_active_license()
    if not is_active:
        raise PermissionError("AVM Security Violation: An active cryptographically signed license or Super Admin authorization is required to generate scripts.")

    if gemini_api_key:
        import re
        models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_err = None
        for mod in models_to_try:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_api_key)
                prompt = (
                    f"You are a viral YouTube documentary scriptwriter. "
                    f"Write a high-retention, engaging 5-scene video script on the topic: '{topic}'. "
                    f"Category: {category}. Tone: {tone}. Language: {language}. "
                    f"Output ONLY a raw valid JSON list of 5 scenes where each scene has: "
                    f"'title': (short punchy title), 'text': (engaging voiceover narration 60-90 words), 'visual_prompt': (visual description). "
                )
                response = client.models.generate_content(
                    model=mod,
                    contents=prompt
                )
                text_res = response.text.strip()
                m = re.search(r'\[\s*\{.*\}\s*\]', text_res, re.DOTALL)
                raw_json = m.group(0) if m else text_res.replace("```json", "").replace("```", "").strip()
                scenes = json.loads(raw_json)
                if isinstance(scenes, list) and len(scenes) > 0:
                    return scenes, f"Generated via Google Gemini AI Engine ({mod})"
            except Exception as e:
                last_err = e
                continue
        if last_err:
            print("Gemini API call failed, falling back to algorithmic engine:", last_err)

    # Built-in High-Retention Algorithmic Engine (Zero-Key Fallback)
    if language == "Hindi":
        scenes = [
            {
                "title": f"1. रहस्यमयी शुरुआत // {topic}",
                "text": f"क्या आप जानते हैं कि {topic} के पीछे एक ऐसा सच छिपा है जो आम तौर पर लोगों से छिपाया जाता है? आज हम कोई साधारण बातें नहीं करेंगे। इस वीडियो में हम जानेंगे वो चार बातें जो आपका नजरिया हमेशा के लिए बदल देंगी।",
                "visual_prompt": f"Cinematic dark room, holographic data HUD about {topic}"
            },
            {
                "title": f"2. छुपा हुआ सच // पहला रहस्य",
                "text": f"पहली नज़र में {topic} बहुत सामान्य लगता है, लेकिन इसके डेटा और इतिहास को खंगालने पर पता चलता है कि बड़े उद्योग और एल्गोरिदम कैसे पर्दे के पीछे काम करते हैं। इसका सीधा असर हमारी रोज़मर्रा की ज़िंदगी पर पड़ता है।",
                "visual_prompt": "Digital flowchart, server racks and data telemetry"
            },
            {
                "title": f"3. अनसुलझा पहलू // दूसरा रहस्य",
                "text": f"वैज्ञानिकों और शोधकर्ताओं की कई रिपोर्टों में यह साबित हुआ है कि {topic} के कई नियमों को जानबूझकर जटिल बनाया जाता है ताकि आम लोग सवाल न पूछ सकें। लेकिन आज के डिजिटल युग में यह समझना सबसे ज़रूरी है।",
                "visual_prompt": "High-tech research laboratory, blurred documents becoming clear"
            },
            {
                "title": f"4. सुरक्षा और समाधान",
                "text": f"इस परिस्थिति में अपने आप को जागरूक रखना ही सबसे बड़ा हथियार है। आपको अपनी सेटिंग्स, प्राइवेसी और डिजिटल सुरक्षा के कुछ बुनियादी नियमों का पालन करना चाहिए जिससे कोई भी आपके डेटा या ध्यान का दुरुपयोग न कर सके।",
                "visual_prompt": "Futuristic security shield, encrypted padlock interface"
            },
            {
                "title": "5. निष्कर्ष और कॉल टू एक्शन",
                "text": f"इस रहस्य में से किस बात ने आपको सबसे ज़्यादा हैरान किया? अपने विचार नीचे कमेंट्स में ज़रूर बताएं। ऐसे ही उच्च-मूल्य वाले वीडियो के लिए लाइक और सब्सक्राइब करें। मिलते हैं अगले वीडियो में!",
                "visual_prompt": "Minimalist sleek outro screen with subscribe bell"
            }
        ]
    else:
        scenes = [
            {
                "title": f"1. The Unspoken Reality // {topic}",
                "text": f"There is an uncomfortable truth about {topic} that most people encounter every single day without ever realizing it. Today, we are skipping the fluff to uncover the high-level secrets that will completely change how you navigate this space.",
                "visual_prompt": f"Cinematic dark room, glowing holographic data HUD analyzing {topic}"
            },
            {
                "title": f"2. The Hidden Pipeline // Secret 1",
                "text": f"What seems like a coincidence on the surface is actually a carefully engineered mechanism. Behind {topic}, massive data networks and algorithms operate quietly to monitor behavioral patterns and guide decisions without your explicit awareness.",
                "visual_prompt": "High-tech digital flowchart showing data flow between servers"
            },
            {
                "title": f"3. The Architectural Flaw // Secret 2",
                "text": f"Most industry documentation buries these critical details in fine print. When you examine the underlying structure of {topic}, you realize that simple, zero-cost adjustments can instantly tilt the advantage back into your hands.",
                "visual_prompt": "Developer tools inspecting blurred interface elements, code highlight"
            },
            {
                "title": f"4. The Modern Solution // Action Plan",
                "text": f"To protect your autonomy, all you need is a practical, repeatable workflow. By auditing your system configurations and understanding these key technical boundaries, you regain complete control in under five minutes.",
                "visual_prompt": "Clean cyber dashboard with green verified security badges"
            },
            {
                "title": "5. Conclusion & Viral CTA",
                "text": f"Which of these insights surprised you the most? Drop your perspective in the comments below. Smash that like button and subscribe for more zero-fluff, high-value breakdowns. See you in the next investigation!",
                "visual_prompt": "Sleek minimalist dark outro with holographic subscribe bell"
            }
        ]

    note = (
        "Generated via Built-in Algorithmic Engine. "
        "(Tip: Connect your Google Gemini API key in the Vault tab for customized AI script generation!)"
    )
    return scenes, note
