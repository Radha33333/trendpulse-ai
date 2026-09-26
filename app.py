import io
import json
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from groq import Groq
import pandas as pd
import plotly.express as px
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
import streamlit as st

# ==========================================
# 1. PAGE CONFIG & GLOBALS
# ==========================================
st.set_page_config(
    page_title="TrendPulse AI - Commercial Signal Intelligence",
    page_icon="⚡",
    layout="wide",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# ==========================================
# 2. CATEGORY ARCHITECTURE & MAPPINGS
# ==========================================
UPDATED_NICHE_CATEGORIES = {
    "🛒 E-Commerce & Viral Shopping": [
        "Predicted Bestsellers",
        "TikTok Shop Products",
        "Upcoming High-Demand Drops",
        "Amazon Hot Movers",
        "D2C Breakout Brands",
        "Problem-Solver Gadgets",
    ],
    "🏛️ Politics, News & Civic Events": [
        "Elections & Rallies",
        "Legislative Assembly & Sabha Debates",
        "Protests & Policy Changes",
        "Politician Speeches",
        "Geopolitical Updates",
        "Public Schemes & Subsidies",
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "Famous Temples",
        "Hidden & Ancient Temples",
        "Religious Festivals",
        "Pilgrimage Circuits",
        "Festive Gifting Trends",
        "Spiritual Wellness Drops",
    ],
    "✈️ Travel, Hotels & Food": [
        "Trending Destinations",
        "Hidden Tourist Places",
        "Restaurants & Stays",
        "Veg & Non-Veg Gourmet",
        "Street Food Surges",
        "Budget & Backpacker Escapes",
    ],
    "🌟 Celebrities & Sports Stars": [
        "Cricket & Sports Idols",
        "Movie & OTT Stars",
        "Viral Influencers",
        "Tournament Buzz",
        "Celebrity Fashion Outfits",
        "Pop Culture Controversies",
    ],
    "🏢 Real Estate & High-Ticket Props": [
        "Rental Yield Hotspots",
        "PropTech & Smart Homes",
        "Luxury Estates",
        "Commercial Spaces",
        "Vacation Homes & Villas",
        "Upcoming Transit Hubs",
    ],
    "💄 Beauty, Skincare & Lifestyle": [
        "UGC Skincare Hacks",
        "Clean Beauty Products",
        "Anti-Aging Devices",
        "Sustainable Fashion",
        "Haircare Treatment Trends",
        "Minimalist Capsule Wardrobes",
    ],
    "💻 Digital Products & AI Tools": [
        "Generative AI Software",
        "SaaS & Workflows",
        "Ebooks & Courses",
        "Templates & Prompts",
        "Automation Micro-Tools",
        "No-Code App Builders",
    ],
}

SUBNICHE_SIGNALS_FALLBACK = {
    "Predicted Bestsellers": ["Ergonomic Desk Accessories", "Self-Cleaning Water Bottles", "MagSafe Powerbanks", "Aesthetic Desk Lamp"],
    "TikTok Shop Products": ["Viral Sunset Lamp", "Micro-Needling Patch", "Aesthetic Ice Roller", "Heatless Hair Curler"],
    "Upcoming High-Demand Drops": ["Limited Edition Sneakers", "Modular Travel Backpacks", "Smart Ring Fitness Tracker"],
    "Amazon Hot Movers": ["Portable Espresso Maker", "Smart Cable Organizer", "Mini Thermal Label Printer"],
    "D2C Breakout Brands": ["Organic Matcha Blends", "Zero-Waste Toothpaste Bits", "Bamboo Fiber Apparel"],
    "Problem-Solver Gadgets": ["Anti-Spill Pet Bowl", "Sonic Jewelry Cleaner", "Electric Jar Opener"],

    "Elections & Rallies": ["Assembly Election Turnout", "Campaign Speech Highlights", "Voter Registration Drives"],
    "Legislative Assembly & Sabha Debates": ["Digital Privacy Bill Debates", "Tax Reform Proposals", "Public Infrastructure Budget"],
    "Protests & Policy Changes": ["Labor Law Policy Adjustments", "Agrarian Policy Protests", "Urban Transport Reform"],
    "Politician Speeches": ["Keynote Economy Address", "Townhall Press Briefing", "National Security Statement"],
    "Geopolitical Updates": ["Cross-Border Trade Treaties", "Global Summit Agreements", "Maritime Corridor Deals"],
    "Public Schemes & Subsidies": ["Green Energy Subsidies", "Small Business Housing Grants", "Student Loan Waiver Policy"],

    "Famous Temples": ["VIP Darshan Slot Booking", "Temple Corridor Expansion", "Heritage Sanctum Restoration"],
    "Hidden & Ancient Temples": ["Unexplored Cave Temple Circuit", "10th Century Rock Sculptures", "Secret Forest Shrines"],
    "Religious Festivals": ["Festive Eco-Diya Handicrafts", "Procession Route Guidelines", "Seasonal Ritual Offerings"],
    "Pilgrimage Circuits": ["Char Dham Yatra Bus Pass", "High-Altitude Trek Passes", "Spiritual River Trail Stays"],
    "Festive Gifting Trends": ["Handcrafted Brass Puja Thalis", "Organic Sweet Hampers", "Silver Idol Gift Sets"],
    "Spiritual Wellness Drops": ["Aromatherapy Incense Blends", "Sandalwood Mala Beads", "Copper Water Vessels"],

    "Trending Destinations": ["Offbeat Hill Stations", "Coastal Secret Escapes", "High-Altitude Glamping"],
    "Hidden Tourist Places": ["Unmapped Waterfall Hikes", "Heritage Fort Villages", "Secluded Island Stays"],
    "Restaurants & Stays": ["Boutique Eco-Resorts", "Rooftop Experiential Dining", "Farm-to-Table Homestays"],
    "Veg & Non-Veg Gourmet": ["Regional Smoked Meat Fusion", "Artisanal Sourdough Outlets", "Traditional Clay-Pot Curries"],
    "Street Food Surges": ["Night Market Food Trails", "Fusion Cheese Street Snacks", "Authentic Local Breakfast Stalls"],
    "Budget & Backpacker Escapes": ["Hostel Co-Working Spaces", "Budget Overnight Trains", "Free Walking Tour Trails"],

    "Cricket & Sports Idols": ["World Cup Squad Announcements", "Player Fitness Routines", "Franchise Auction Buzz"],
    "Movie & OTT Stars": ["Blockbuster Teaser Drop", "Celebrity Red Carpet Outfits", "Exclusive OTT Series Leaks"],
    "Viral Influencers": ["Trend Challenge Breakouts", "Podcast Interview Clips", "Creator Brand Collabs"],
    "Tournament Buzz": ["Playoff Final Tickets", "Underdog Team Comebacks", "Stadium Fan Zone Activations"],
    "Celebrity Fashion Outfits": ["Airport Style Lookbooks", "Vintage Met Gala Recreations", "Streetwear Capsule Drops"],
    "Pop Culture Controversies": ["Award Show Feuds", "Viral Interview Debates", "Social Media Account Audits"],

    "Rental Yield Hotspots": ["IT Hub Studio Apartments", "University Corridor Housing", "Tier-2 Metro Outskirts"],
    "PropTech & Smart Homes": ["Automated Keyless Locks", "AI Energy Efficiency Systems", "Smart Solar Roofing"],
    "Luxury Estates": ["Oceanfront Gated Villas", "Penthouse Sky Mansions", "Private Golf Course Residences"],
    "Commercial Spaces": ["Co-Working Plug & Play Hubs", "High-Street Retail Outlets", "Logistics Micro-Warehouses"],
    "Vacation Homes & Villas": ["Hill Station Wooden Chalets", "Poolside Countryside Homestays", "Off-Grid Eco Cabins"],
    "Upcoming Transit Hubs": ["Metro Extension Corridor Plots", "Expressway Junction Warehouses", "Airport Adjacent Townships"],

    "UGC Skincare Hacks": ["Korean Glass Skin Routine", "Ice Facial Sculpting", "Rice Water Hair Rinses"],
    "Clean Beauty Products": ["Sulfate-Free Botanical Serums", "Refillable Lip Tints", "Vegan Sunscreen Sticks"],
    "Anti-Aging Devices": ["LED Light Therapy Masks", "Micro-Current Facial Toners", "Thermal Eye Wand Sculptors"],
    "Sustainable Fashion": ["Upcycled Denim Jackets", "Organic Linen Shirts", "Thrifted Vintage Outfits"],
    "Haircare Treatment Trends": ["Scalp Exfoliation Scrubs", "Rosemary Hair Growth Oils", "Bond Repairing Masks"],
    "Minimalist Capsule Wardrobes": ["Neutral Blazer Essentials", "Tailored Wide-Leg Trousers", "Monochrome Streetwear"],

    "Generative AI Software": ["Text-to-Video Generators", "AI Voice Cloning Plugins", "Code Refactoring Copilots"],
    "SaaS & Workflows": ["Automated Invoicing Plugins", "Micro-SaaS CRM Dashboards", "All-in-One Booking Engines"],
    "Ebooks & Courses": ["Solopreneur Playbook Guides", "No-Code Masterclasses", "Algorithmic Trading Guides"],
    "Templates & Prompts": ["Notion Finance Trackers", "Midjourney Architecture Prompts", "Figma UI Design Kits"],
    "Automation Micro-Tools": ["Zapier Email Webhooks", "Social Media Auto-Responders", "Web Scraping Extensions"],
    "No-Code App Builders": ["Drag-and-Drop Marketplace Builders", "PWA Web App Frameworks", "Database Portals"],
}

# ==========================================
# 3. TRANSLATIONS
# ==========================================
TEXTS = {
    "English": {
        "title": "⚡ TrendPulse AI: Commercial Signal Intelligence",
        "subtitle": "Predictive Trend Intelligence | Automated Creator & Merchant Signal Engine",
        "terminal": "🔑 Enterprise Access Terminal",
        "simulate_pro": "Simulate Pro Subscription Access",
        "config_title": "⚙️ Signal Intelligence Configuration",
        "region": "🌐 Target Region:",
        "platform": "🎛️ Platform Source:",
        "category": "📁 Niche Category:",
        "sub_category": "🔍 Sub-Niche Focus (Optional):",
        "velocity": "⏱️ Signal Velocity:",
        "apply_btn": "🚀 Apply Configuration & Update Radar",
        "telemetry_title": "📊 Live Telemetry & Growth Forecast",
        "custom_search": "🔍 Custom Asset Search (Optional):",
        "active_signals_for": "Active Signals for:",
        "filtered_asset": "Trending Signal",
        "search_volume": "Search Volume",
        "future_forecast": "Future Trend Forecast",
        "chart_title": "📈 Dynamic Velocity & Demand Forecast Curve",
        "matrix_title": "💡 Actionable Intelligence & Strategy Matrix",
        "locked_title": "🔒 MULTI-CHANNEL BLUEPRINT IS LOCKED",
        "locked_info": "Unlock high-converting scripts, viral hooks, ad copy, and step-by-step execution plan.",
        "upgrade_btn": "🔥 Upgrade to Pro & Unlock Full Engine",
        "select_asset": "🎯 Select Filtered Asset:",
        "operating_role": "👤 Operating Role:",
        "gen_blueprint": "⚡ Generate Master Strategy Blueprint",
        "monetization": "💰 Direct High-ROI Monetization Model",
        "content_directives": "🎬 Role-Specific Content Directives & Story Blueprint",
        "hook": "⚡ Visual Hook & Pattern Interrupt Script (0-3s)",
        "audio": "🎵 Recommended Audio / Tone Directives",
        "caption": "📢 Caption, Call to Action & Copy Framework",
        "plan": "⏱️ Time-Chunked Action Roadmap (0-1h, 6h, 48h)",
        "score_label": "Predictive Viral Score",
        "export_pdf_btn": "📄 Download Blueprint PDF",
        "share_wa_btn": "💬 Share to WhatsApp",
        "competitor_insight": "🕵️ Live Competitor Ad Intelligence & Benchmarks",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: कमर्शियल सिग्नल इंटेलिजेंस",
        "subtitle": "प्रेडिक्टिव ट्रेंड इंटेलिजेंस | ऑटोमेटेड क्रिएटर और मर्चेंट सिग्नल इंजन",
        "terminal": "🔑 एंटरप्राइज एक्सेस टर्मिनल",
        "simulate_pro": "प्रो सब्सक्रिप्शन एक्सेस सिमुलेट करें",
        "config_title": "⚙️ सिग्नल इंटेलिजेंस कॉन्फ़िगरेशन",
        "region": "🌐 टारगेट रीजन (क्षेत्र):",
        "platform": "🎛️ प्लेटफॉर्म सोर्स:",
        "category": "📁 नीश कैटेगरी:",
        "sub_category": "🔍 सब-नीश फ़ोकस (वैकल्पिक):",
        "velocity": "⏱️ सिग्नल वेलोसिटी:",
        "apply_btn": "🚀 कॉन्फ़िगरेशन लागू करें और रडार अपडेट करें",
        "telemetry_title": "📊 लाइव टेलीमेट्री और ग्रोथ पूर्वानुमान",
        "custom_search": "🔍 कस्टम एसेट सर्च (वैकल्पिक):",
        "active_signals_for": "सक्रिय सिग्नल:",
        "filtered_asset": "ट्रेंडिंग सिग्नल",
        "search_volume": "सर्च वॉल्यूम",
        "future_forecast": "फ्यूचर ट्रेंड फोरकास्ट",
        "chart_title": "📈 डायनेमिक वेलोसिटी और डिमांड फ़ोरकास्ट कर्व",
        "matrix_title": "💡 एक्शनएबल इंटेलिजेंस और स्ट्रैटेजी मैट्रिक्स",
        "locked_title": "🔒 मल्टी-चैनल ब्लूप्रिंट लॉक है",
        "locked_info": "हाई-कन्वर्टिंग स्क्रिप्ट, वायरल हुक, एड कॉपी और एग्जीक्यूशन प्लान अनलॉक करें।",
        "upgrade_btn": "🔥 प्रो में अपग्रेड करें और पूरा इंजन अनलॉक करें",
        "select_asset": "🎯 फ़िल्टर किया गया एसेट चुनें:",
        "operating_role": "👤 आपकी भूमिका (Role):",
        "gen_blueprint": "⚡ मास्टर स्ट्रैटेजी ब्लूप्रिंट जनरेट करें",
        "monetization": "💰 डायरेक्ट हाई-ROI मोनेटाइजेशन मॉडल",
        "content_directives": "🎬 रोल-स्पेसिफिक कंटेंट डायरेक्टिव्स और स्टोरी ब्लूप्रिंट",
        "hook": "⚡ विजुअल हुक और पैटर्न इंटरप्ट स्क्रिप्ट (0-3s)",
        "audio": "🎵 अनुशंसित ऑडियो / टोन डायरेक्टिव्स",
        "caption": "📢 कैप्शन, कॉल टू एक्शन और कॉपी फ्रेमवर्क",
        "plan": "⏱️ टाइम-चंक्ड एक्शन रोडमैप (0-1h, 6h, 48h)",
        "score_label": "अनुमानित वायरल स्कोर",
        "export_pdf_btn": "📄 ब्लूप्रिंट PDF डाउनलोड करें",
        "share_wa_btn": "💬 व्हाट्सएप पर शेयर करें",
        "competitor_insight": "🕵️ लाइव कॉम्पिटिटर एड इंटेलिजेंस",
    },
}

# ==========================================
# 4. HELPER FUNCTIONS & PDF ENGINE
# ==========================================
def safe_xml_text(text: str) -> str:
    if not text:
        return ""
    clean = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean)
    return clean

def sanitize_trend_input(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'\[.*?\]', '', text)
    cleaned = re.sub(r'[^\w\s\-\.\,\/\&\(\)]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def create_pdf_blueprint(asset_name, category, role, viral_score, window, result):
    clean_asset = sanitize_trend_input(asset_name)
    clean_cat = sanitize_trend_input(category)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=18, textColor="#ff4b4b", spaceAfter=12)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=12, textColor="#1a1a1a", spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=9, leading=13, textColor="#333333", spaceAfter=8)

    story = [
        Paragraph("TrendPulse AI - Master Strategy Blueprint (Phase 1 Finalized)", title_style),
        Paragraph(f"<b>Asset:</b> {safe_xml_text(clean_asset)} | <b>Category:</b> {safe_xml_text(clean_cat)} | <b>Role:</b> {safe_xml_text(role)}", body_style),
        Paragraph(f"<b>Predictive Viral Score:</b> {safe_xml_text(str(viral_score))} | <b>Window:</b> {safe_xml_text(str(window))}", body_style),
        Spacer(1, 10)
    ]

    sections = [
        ("Monetization Model", result.get("profit_model", "")),
        ("Role-Specific Content Directives", result.get("content_directives", "")),
        ("Execution Hook & Visual Script", result.get("execution_hook", "")),
        ("Recommended Audio / Tone Vibe", result.get("audio_suggestion", "")),
        ("Caption, CTA & Ad Copy", result.get("ad_copy", "")),
        ("Action Roadmap", result.get("action_blueprint", "")),
        ("Competitor Ad Intelligence", result.get("competitor_intelligence", "")),
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(safe_xml_text(text), body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 5. FULLY SYNCED PIPELINE WITH PHASE 1 ENHANCEMENTS
# ==========================================
@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category, sub_niche, timeframe):
    results = []
    
    region_term = "India" if region == "IN" else ("US" if region == "US" else "")
    sub_ctx = f"{sub_niche}" if (sub_niche and sub_niche != "All Sub-Niches") else ""
    query_text = f"{category.split()[-1]} {sub_ctx} {region_term}".strip()
    search_query = urllib.parse.quote(query_text)
    
    platform_name = platform_source.split()[1] if len(platform_source.split()) > 1 else platform_source

    if "Reddit" in platform_source:
        try:
            url = f"https://www.reddit.com/search.json?q={search_query}&sort=hot&limit=10"
            headers = {"User-Agent": "Mozilla/5.0 TrendPulseAI/2.0"}
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                for post in data.get("data", {}).get("children", []):
                    title = post["data"].get("title", "")
                    score = post["data"].get("score", 0)
                    if title:
                        results.append({"Keyword": f"[Reddit] {title[:70]}...", "Volume": f"{score:,} Upvotes"})
        except Exception:
            pass

    elif "YouTube" in platform_source:
        try:
            url = f"https://www.youtube.com/feeds/videos.xml?search_query={search_query}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=4)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("atom:entry", ns):
                    title_elem = entry.find("atom:title", ns)
                    if title_elem is not None and title_elem.text:
                        results.append({"Keyword": f"[YouTube] {title_elem.text[:70]}", "Volume": f"High Demand ({timeframe})"})
        except Exception:
            pass

    elif "Google Trends" in platform_source:
        try:
            geo_code = region if region != "ALL" else ""
            url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo_code}"
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item"):
                    title = item.find("title")
                    traffic = item.find("{https://trends.google.com/trends/trendingsearches/daily}approx_traffic")
                    if title is not None and title.text:
                        results.append({"Keyword": f"[Google] {title.text}", "Volume": f"{traffic.text if traffic is not None else '100K+'} Searches"})
        except Exception:
            pass

    if len(results) < 5:
        if sub_niche in SUBNICHE_SIGNALS_FALLBACK:
            base_pool = SUBNICHE_SIGNALS_FALLBACK[sub_niche]
        else:
            base_pool = [f"{category.split()[-1]} Surge", f"Viral {sub_niche}", f"Top Choice {region_term}", "Breakout Signal"]

        platform_mods = {
            "TikTok": ["Viral Hook", "Shop Hot Seller", "POV Trend"],
            "Instagram": ["Reels Audio Surge", "Ad Spurt", "Carousel Trend"],
            "Google": ["High Intent Query", "Breakout Search", "Volume Surge"],
            "X (Twitter)": ["Realtime Hashtag", "Trending Thread"],
            "Reddit": ["Community Spike", "AMA Viral Post"],
            "Amazon": ["Movers & Shakers", "Bestsellers Category"],
            "YouTube": ["Shorts Viral Clip", "High CTR Topic"]
        }
        
        current_mod = ["Trending Signal"]
        for p_key, mods in platform_mods.items():
            if p_key in platform_source:
                current_mod = mods
                break

        for i, item in enumerate(base_pool):
            if len(results) >= 5:
                break
            mod = current_mod[i % len(current_mod)]
            results.append({
                "Keyword": f"[{platform_name}] {item} ({mod})",
                "Volume": f"{(95 - i * 11) * 10}K+ Interactions ({region})"
            })

    return results[:5]

# ==========================================
# 6. GROQ LLM BLUEPRINT GENERATOR (SECURE)
# ==========================================
def generate_master_intelligence(keyword_asset, category, sub_niche, target_role, platform, timeframe, velocity_score, lang):
    clean_asset = sanitize_trend_input(keyword_asset)
    clean_cat = sanitize_trend_input(category)
    clean_sub = sanitize_trend_input(sub_niche)

    sub_ctx = f" focusing on '{clean_sub}'" if clean_sub and clean_sub != "All Sub-Niches" else ""

    default_response = {
        "viral_score": f"{velocity_score}%",
        "prediction_window": f"Active Timing Window ({timeframe})",
        "profit_model": f"• **Primary Funnel:** Phase 1 Optimized Direct High-ROI Strategy for {target_role} in {clean_cat}{sub_ctx}.\n• **Execution Path:** Monetize '{clean_asset}' through targeted localized ad funnels.",
        "content_directives": f"• **Narrative Angle:** Capturing institutional momentum of '{clean_asset}'.\n• **Core Message:** High-converting solution-focused value proposition.",
        "execution_hook": f"• **0-3s Cue:** Dynamic visual introducing {clean_asset}.\n• **Text Overlay:** \"Why top operators are scaling {clean_asset[:20]} right now...\"\n• **Script:** \"Here is the exact framework to capitalize on {clean_asset}...\"",
        "audio_suggestion": "Upbeat Commercial Audio / High-Energy Vibe",
        "ad_copy": f"Discover how {clean_asset} is breaking records in {clean_cat}. Tap link to access Phase 1 intelligence! #{clean_asset.replace(' ', '')}",
        "action_blueprint": "1. HOUR 1: Deploy target tracking & asset setup.\n2. HOUR 6: Launch cross-channel ad & content campaigns.\n3. DAY 2: Scale top-performing variations using real-time telemetry.",
        "competitor_intelligence": "• **Phase 1 Benchmark:** Top 10% market retention and CTR performance tier.",
    }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Return ONLY a raw valid JSON object (no markdown, no backticks).
Analyze Phase 1 commercial requirements:
Asset: "{clean_asset}"
Category: "{clean_cat}"
Sub-Niche: "{clean_sub}"
Role: "{target_role}"
Platform: "{platform}"
Language: {lang}

JSON Format:
{{
  "viral_score": "{velocity_score}%",
  "prediction_window": "Lifecycle timing details",
  "profit_model": "Step by step monetization model",
  "content_directives": "• **Narrative Angle:** ...\\n• **Key Points:** ...",
  "execution_hook": "• **0-3s Cue:** ...\\n• **Overlay:** ...\\n• **Script:** ...",
  "audio_suggestion": "Audio vibe",
  "ad_copy": "Ad copy and hashtags",
  "action_blueprint": "1. HOUR 1: ...\\n2. HOUR 6: ...\\n3. DAY 2: ...",
  "competitor_intelligence": "• **Benchmark:** ..."
}}
"""
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)
    except Exception:
        return default_response

# ==========================================
# 7. UI LAYOUT & RENDERING ENGINE
# ==========================================
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

head_col1, head_col2 = st.columns([3, 1])

with head_col2:
    selected_lang = st.selectbox("🌐 Language / भाषा:", ["English", "Hindi"], index=0)

t = TEXTS[selected_lang]

with head_col1:
    st.title(t["title"])
    st.caption(f"{t['subtitle']} | Phase 1 Deployment")

st.markdown("---")

with st.expander(t["terminal"]):
    st.session_state["is_premium"] = st.checkbox(t["simulate_pro"], value=st.session_state["is_premium"])

st.markdown(f"### {t['config_title']}")

with st.form(key="filter_form"):
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

    with f_col1:
        geo_option = st.selectbox(t["region"], ["India (IN)", "United States (US)", "United Kingdom (GB)", "Global (ALL)"])
        geo_map = {"India (IN)": "IN", "United States (US)": "US", "United Kingdom (GB)": "GB", "Global (ALL)": "ALL"}

    with f_col2:
        platform_source = st.selectbox(
            t["platform"],
            [
                "🎵 TikTok Trends & Creative Center",
                "📸 Instagram Reels & Meta Ad Library",
                "🔎 Google Trends & Keyword Search",
                "📌 Pinterest Trends & Visual Discovery",
                "🧵 X (Twitter) Realtime Trends",
                "👽 Reddit Viral & Community Buzz",
                "🛒 Amazon Movers & Shakers",
                "▶️ YouTube Shorts & Video Popularity",
            ],
            index=5,
        )

    with f_col3:
        selected_category = st.selectbox(t["category"], options=list(UPDATED_NICHE_CATEGORIES.keys()), index=0)

    with f_col4:
        sub_niche_options = UPDATED_NICHE_CATEGORIES.get(selected_category, [])
        selected_sub_niche = st.selectbox(t["sub_category"], options=["All Sub-Niches"] + sub_niche_options, index=0)

    with f_col5:
        timeframe = st.selectbox(t["velocity"], ["Realtime Spike (24h)", "Short-Term Trend (7 Days)", "Viral Surge (3-7 Days)", "Macro Trend (30 Days)"])

    apply_filters = st.form_submit_button(t["apply_btn"], use_container_width=True)

st.markdown("---")

left_col, right_col = st.columns([1.3, 0.7], gap="large")

with left_col:
    st.subheader(t["telemetry_title"])
    
    custom_search = st.text_input(
        t["custom_search"],
        placeholder="e.g. Ergonomic Desk, State Infrastructure Bill, Pilgrimage Circuits",
    )

    active_signals = fetch_filtered_radar_signals(
        geo_map[geo_option], platform_source, selected_category, selected_sub_niche, timeframe
    )

    if custom_search.strip():
        custom_item = {"Keyword": f"[Custom Search] {custom_search.strip()}", "Volume": f"Realtime Query ({geo_option})"}
        if not any(custom_search.strip() in s["Keyword"] for s in active_signals):
            active_signals.insert(0, custom_item)

    future_forecast_options = ["🔥 High Growth (7 Days)", "🚀 Viral Peak Expected", "📈 Steady Surge", "⚡ Breakout Candidate", "📊 Emerging Trend"]

    table_data = []
    signal_scores = {}

    for idx, item in enumerate(active_signals):
        score = round(98.8 - (idx * 3.2), 1)
        forecast = future_forecast_options[idx % len(future_forecast_options)]

        table_data.append({
            t["filtered_asset"]: item["Keyword"],
            t["search_volume"]: item["Volume"],
            t["future_forecast"]: forecast,
        })
        signal_scores[item["Keyword"]] = score

    df = pd.DataFrame(table_data)
    sub_title_ctx = f" | Sub: `{selected_sub_niche}`" if selected_sub_niche != "All Sub-Niches" else ""
    st.markdown(f"**{t['active_signals_for']}** `{selected_category}`{sub_title_ctx} | `{platform_source}` | `{geo_option}`")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown(f"#### {t['chart_title']}")

    chart_keyword = active_signals[0]["Keyword"] if active_signals else "Asset"
    base_score = signal_scores.get(chart_keyword, 90.0)

    days = ["Day -3", "Day -2", "Day -1", "Today", "Day +1 (Proj)", "Day +2 (Proj)", "Day +3 (Proj)"]
    scores = [
        max(10.0, base_score - 45),
        max(15.0, base_score - 30),
        max(25.0, base_score - 15),
        base_score,
        min(99.9, base_score + 5),
        min(99.9, base_score + 8),
        min(99.9, base_score + 4),
    ]

    chart_df = pd.DataFrame({"Timeline": days, "Velocity Score": scores})
    fig = px.line(chart_df, x="Timeline", y="Velocity Score", markers=True, line_shape="spline", title=f"Trajectory: {chart_keyword}")
    fig.update_traces(line_color="#ff4b4b", line_width=3, marker_size=8)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader(t["matrix_title"])

    if not st.session_state["is_premium"]:
        st.warning(t["locked_title"])
        st.info(t["locked_info"])
        st.link_button(t["upgrade_btn"], STRIPE_CHECKOUT_URL, use_container_width=True)
    else:
        st.success("🔓 PRO ENGINE ACTIVE (PHASE 1)")

        asset_list = [item["Keyword"] for item in active_signals]
        selected_asset = st.selectbox(t["select_asset"], options=asset_list, index=0)

        target_role = st.selectbox(
            t["operating_role"],
            [
                "🛍️ E-Commerce Seller / Merchant",
                "🎬 Content Creator / Influencer",
                "📢 Affiliate Marketer / Media Buyer",
                "🏢 Local Business / Real Estate Broker",
                "💻 SaaS Founder / Digital Product Creator",
            ],
            index=0,
        )

        gen_btn = st.button(t["gen_blueprint"], use_container_width=True)

        if gen_btn or "last_result" in st.session_state:
            if gen_btn:
                curr_score = signal_scores.get(selected_asset, 94.5)
                with st.spinner("Generating Phase 1 Multi-Channel Commercial Strategy..."):
                    result = generate_master_intelligence(
                        selected_asset,
                        selected_category,
                        selected_sub_niche,
                        target_role,
                        platform_source,
                        timeframe,
                        curr_score,
                        selected_lang,
                    )
                    st.session_state["last_result"] = result
                    st.session_state["last_asset"] = selected_asset
                    st.session_state["last_role"] = target_role
                    st.session_state["last_score"] = curr_score
            else:
                result = st.session_state["last_result"]
                selected_asset = st.session_state["last_asset"]
                target_role = st.session_state["last_role"]
                curr_score = st.session_state["last_score"]

            m_col1, m_col2 = st.columns(2)
            m_col1.metric(t["score_label"], result.get("viral_score", f"{curr_score}%"))
            m_col2.metric("Lifecycle Window", result.get("prediction_window", timeframe))

            st.markdown("---")
            st.markdown(f"#### {t['monetization']}")
            st.markdown(result.get("profit_model", ""))

            st.markdown(f"#### {t['content_directives']}")
            st.markdown(result.get("content_directives", ""))

            st.markdown(f"#### {t['hook']}")
            st.markdown(result.get("execution_hook", ""))

            st.markdown(f"#### {t['audio']}")
            st.caption(result.get("audio_suggestion", ""))

            st.markdown(f"#### {t['caption']}")
            st.code(result.get("ad_copy", ""), language="text")

            st.markdown(f"#### {t['plan']}")
            st.text(result.get("action_blueprint", ""))

            st.markdown(f"#### {t['competitor_insight']}")
            st.markdown(result.get("competitor_intelligence", ""))

            st.markdown("---")

            pdf_bytes = create_pdf_blueprint(
                selected_asset, selected_category, target_role, curr_score, timeframe, result
            )

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label=t["export_pdf_btn"],
                    data=pdf_bytes,
                    file_name=f"TrendPulse_Phase1_Blueprint_{sanitize_trend_input(selected_asset)[:15]}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            with d_col2:
                wa_text = urllib.parse.quote(
                    f"⚡ *TrendPulse AI Phase 1 Blueprint*\n\n"
                    f"Asset: {sanitize_trend_input(selected_asset)}\n"
                    f"Category: {sanitize_trend_input(selected_category)}\n"
                    f"Viral Score: {curr_score}%\n\n"
                    f"Hook: {result.get('execution_hook', '')[:100]}..."
                )
                st.link_button(
                    label=t["share_wa_btn"],
                    url=f"https://wa.me/?text={wa_text}",
                    use_container_width=True,
                )
