import os
import json
import re

def generate_viral_script_ai(
    topic, 
    custom_prompt="", 
    category="Mystery", 
    tone="High-Retention Mystery", 
    language="English", 
    scene_count=5, 
    gemini_api_key=None
):
    """
    Generates a full structured video script.
    Allows custom prompts, user-defined styles, dynamic scene counts (3 to 10), and language selection.
    Uses Google Gemini API if key is present, otherwise falls back to the algorithmic prompt engine.
    """
    # Cryptographic License Guard (Anti-Bypass Protection)
    from .license_engine import load_active_license
    is_active, _ = load_active_license()
    if not is_active:
        raise PermissionError("AVM Security Violation: An active cryptographically signed license or Super Admin authorization is required to generate scripts.")

    count = max(3, min(10, int(scene_count)))

    if gemini_api_key:
        models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-pro-latest"]
        last_err = None
        for mod in models_to_try:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=gemini_api_key)

                system_instruction = (
                    f"You are the world's premier viral video scriptwriter and documentary director. "
                    f"Write a high-retention, engaging {count}-scene video script on the topic: '{topic}'. "
                    f"Tone: {tone}. Language: {language}. Format: {category}.\n"
                )

                if custom_prompt and custom_prompt.strip():
                    system_instruction += (
                        f"\nUSER CUSTOM INSTRUCTIONS & SPECIFIC PROMPT:\n"
                        f"\"\"\"\n{custom_prompt.strip()}\n\"\"\"\n"
                        f"You MUST strictly fulfill the user's specific instructions, narrative direction, and custom details.\n"
                    )

                system_instruction += (
                    f"\nGenerate exactly {count} scenes. Output ONLY a valid JSON list of {count} scene objects:\n"
                    f"[\n"
                    f"  {{\n"
                    f"    \"title\": \"Short punchy scene heading\",\n"
                    f"    \"text\": \"Narration script in {language} (natural spoken voiceover, 60-90 words, ultra engaging)\",\n"
                    f"    \"visual_prompt\": \"Cinematic visual description for 1080p AI image generation (lighting, subject, 8k dark aesthetic)\"\n"
                    f"  }},\n"
                    f"  ...\n"
                    f"]"
                )

                try:
                    cfg = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7
                    )
                    response = client.models.generate_content(
                        model=mod,
                        contents=system_instruction,
                        config=cfg
                    )
                except Exception:
                    response = client.models.generate_content(
                        model=mod,
                        contents=system_instruction
                    )

                text_res = response.text.strip()
                m = re.search(r'\[\s*\{.*\}\s*\]', text_res, re.DOTALL)
                raw_json = m.group(0) if m else text_res.replace("```json", "").replace("```", "").strip()
                scenes = json.loads(raw_json, strict=False)
                if isinstance(scenes, list) and len(scenes) > 0:
                    return scenes, f"Generated via Google Gemini AI Engine ({mod})"
            except Exception as e:
                last_err = e
                continue
        if last_err:
            print("Gemini API call failed, falling back to algorithmic engine:", last_err)

    # Built-in High-Retention Algorithmic Engine (Dynamic Scene Count Fallback)
    scenes = []
    if language == "Hindi":
        hindi_templates = [
            ("1. रहस्यमयी शुरुआत // हुक", f"क्या आप जानते हैं कि {topic} के पीछे एक ऐसा सच छिपा है जो आम तौर पर लोगों से छिपाया जाता है? आज हम कोई साधारण बातें नहीं करेंगे। इस वीडियो में हम जानेंगे वो बातें जो आपका नजरिया बदल देंगी।", f"Cinematic dark room, glowing holographic data HUD analyzing {topic}"),
            ("2. छुपा हुआ सच // पहला रहस्य", f"पहली नज़र में {topic} बहुत सामान्य लगता है, लेकिन इसके डेटा और सिस्टम को खंगालने पर पता चलता है कि बड़े एल्गोरिदम कैसे पर्दे के पीछे काम करते हैं। इसका सीधा असर आपकी ज़िंदगी पर पड़ता है।", "Digital flowchart showing data flow between high-tech servers"),
            ("3. अनसुलझा पहलू // दूसरा पहलू", f"वैज्ञानिकों और जानकारों की कई रिपोर्टों में यह साबित हुआ है कि {topic} के नियमों को जानबूझकर जटिल बनाया जाता है। लेकिन सही जानकारी होने पर आप इसे आसानी से समझ सकते हैं।", "High-tech research laboratory, cyber inspect interface glowing green"),
            ("4. गहरा विश्लेषण // कोर मैकेनिज़्म", f"अगर आप इसके अंदरूनी स्ट्रक्चर को देखें, तो समझ आएगा कि कैसे एक छोटी सी तकनीक पूरे सिस्टम को बदल सकती है। {topic} को गहराई से समझना ही आपको दूसरों से आगे रखता है।", "Futuristic mechanical motherboard with glowing neural connections"),
            ("5. सुरक्षा और समाधान", f"इस परिस्थिति में अपने आप को जागरूक रखना ही सबसे बड़ा हथियार है। आपको अपनी सेटिंग्स, प्राइवेसी और बुनियादी नियमों का पालन करना चाहिए ताकि आप पूरी तरह सुरक्षित रहें।", "Futuristic security shield with holographic padlock interface"),
            ("6. एक्सपर्ट इनसाइट", f"इंडस्ट्री के टॉप एक्सपर्ट्स हमेशा यह सलाह देते हैं कि किसी भी ट्रेंड पर आंख बंद करके भरोसा न करें। {topic} के इस पहलू को समझना हर डिजिटल यूजर के लिए अनिवार्य है।", "Sophisticated glass office overlooking cyberpunk futuristic cityscape"),
            ("7. भविष्य की दिशा", f"आने वाले कुछ सालों में यह टेक्नोलॉजी और भी तेज़ी से बदलने वाली है। अगर आप आज तैयार नहीं हैं, तो आने वाले समय में बड़ा नुकसान हो सकता है।", "Futuristic artificial intelligence core pulsing with blue light 8k"),
            ("8. निष्कर्ष और कॉल टू एक्शन", f"इस पूरे रहस्य में से किस बात ने आपको सबसे ज़्यादा हैरान किया? अपने विचार नीचे कमेंट्स में ज़रूर बताएं। ऐसे ही उच्च-मूल्य वाले वीडियो के लिए लाइक और सब्सक्राइब करें। मिलते हैं अगले वीडियो में!", "Minimalist sleek outro screen with holographic subscribe bell")
        ]
        for i in range(min(count, len(hindi_templates))):
            t, b, vp = hindi_templates[i]
            scenes.append({"title": t, "text": b, "visual_prompt": vp})
    else:
        eng_templates = [
            ("1. The Unspoken Reality // Hook", f"There is an uncomfortable truth about {topic} that most people encounter every single day without ever realizing it. Today, we are skipping the fluff to uncover the high-level secrets that will completely change how you navigate this space.", f"Cinematic dark room, glowing holographic data HUD analyzing {topic}"),
            ("2. The Hidden Pipeline // Secret 1", f"What seems like a coincidence on the surface is actually a carefully engineered mechanism. Behind {topic}, massive data networks and algorithms operate quietly to monitor behavioral patterns and guide decisions without your explicit awareness.", "High-tech digital flowchart showing data flow between servers"),
            ("3. The Architectural Flaw // Secret 2", f"Most industry documentation buries these critical details in fine print. When you examine the underlying structure of {topic}, you realize that simple, zero-cost adjustments can instantly tilt the advantage back into your hands.", "Developer tools inspecting blurred interface elements, code highlight"),
            ("4. Deep Investigation // Inside Look", f"When you trace the original blueprints, the motive becomes crystal clear. Every layer of {topic} was constructed to reward early adopters who understand the math and penalize those who rely on outdated assumptions.", "Cybernetic control room with glowing matrix monitors and data analytics"),
            ("5. The Countermeasure // Action Plan", f"To protect your autonomy, all you need is a practical, repeatable workflow. By auditing your system configurations and understanding these key technical boundaries, you regain complete control in under five minutes.", "Clean cyber dashboard with green verified security badges"),
            ("6. The Industry Blindspot", f"Why hasn't the mainstream covered this? Because legacy platforms profit from user friction. Once you bypass the gatekeepers, you unlock capabilities that were previously reserved for high-budget enterprises.", "Futuristic glass skyscraper overlooking high-tech city skyline 8k"),
            ("7. Long-term Trajectory", f"Over the next 18 months, these dynamics will accelerate exponentially. Positioning yourself on the right side of this curve is no longer optional—it is the single highest-ROI move you can make today.", "Abstract neural network lattice pulsing with cyan and violet light"),
            ("8. Conclusion & Viral CTA", f"Which of these insights surprised you the most? Drop your perspective in the comments below. Smash that like button and subscribe for more zero-fluff, high-value breakdowns. See you in the next investigation!", "Sleek minimalist dark outro with holographic subscribe bell")
        ]
        for i in range(min(count, len(eng_templates))):
            t, b, vp = eng_templates[i]
            scenes.append({"title": t, "text": b, "visual_prompt": vp})

    note = (
        "Generated via Built-in Algorithmic Engine. "
        "(Tip: Connect your Google Gemini API key in the Vault tab for customized AI script generation!)"
    )
    return scenes, note
