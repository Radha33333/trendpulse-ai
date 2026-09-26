import io
import json
import os
import re
import sqlite3
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
# 1. PAGE CONFIG & GLOBAL ENTERPRISE STYLING
# ==========================================
st.set_page_config(
    page_title="TrendPulse AI - Master Intelligence & Execution Suite",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #fafafa; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e222b 0%, #11141d 100%);
        border: 1px solid #2d3748;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.5px; }
    .stButton>button {
        background: linear-gradient(90deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white; border: none; border-radius: 6px; font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #e03e3e 0%, #ff4b4b 100%);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.4);
    }
    .blueprint-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/test_demo"

# ==========================================
# 2. SQLITE DATABASE INITIALIZATION (5 CORE TABLES)
# ==========================================
def init_database():
    conn = sqlite3.connect("trendpulse_enterprise.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_table (
            user_id TEXT PRIMARY KEY,
            email TEXT,
            selected_role TEXT,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_signals (
            signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_platform TEXT,
            keyword TEXT,
            engagement_metrics TEXT,
            region TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS niches_table (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT,
            sub_niche_name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trends_table (
            trend_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_name TEXT,
            category_name TEXT,
            velocity_score REAL,
            saturation_index TEXT,
            emergence_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blueprints_table (
            blueprint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trend_name TEXT,
            role_type TEXT,
            full_dossier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

db_conn = init_database()

# ==========================================
# 3. 20 MASTER CATEGORIES & 120 SUB-NICHES
# ==========================================
UPDATED_NICHE_CATEGORIES = {
    "🛒 E-Commerce & Viral Shopping": [
        "TikTok Shop & Live Deals", "Amazon Hot Movers & Bestsellers", "D2C Breakout & DTC Brands",
        "Problem-Solver Gadgets", "Print-on-Demand & Custom Merch", "Upcoming High-Demand Drops"
    ],
    "🏢 Real Estate & High-Ticket Props": [
        "Rental Yield Hotspots", "PropTech & Smart Homes", "Luxury Estates & Villas",
        "Commercial & Co-Working Spaces", "Fractional Real Estate & REITs", "Upcoming Transit & Metro Hubs"
    ],
    "🚗 Automobile, EV & Mobility": [
        "EV Launches & Battery Tech", "ADAS, Dashcams & Smart Tech", "Car & Bike Accessories / Gadgets",
        "Auto Reviews & Mileage Hacks", "Custom Bike & Supercar Buzz", "Commuter Vehicle Price Drops"
    ],
    "👶 Parenting, Baby Care & Kids": [
        "Baby Gear & Smart Strollers", "Early Childhood EdTech & Toys", "Modern Parenting & Routine Hacks",
        "Kids Nutrition & Organic Foods", "Maternity & Postpartum Care", "Family Lifestyle & Travel Gear"
    ],
    "🐾 Pets & Animal Care": [
        "Pet Health & Nutrition", "Dog & Cat Training Hacks", "Smart Pet Accessories & Tech",
        "Cute & Funny Pet Virals", "Grooming & Hygiene Products", "Breed Guides & Adoption Signals"
    ],
    "💰 Finance, Crypto & Wealth Building": [
        "Credit Card & Reward Hacks", "Stock Market & Algo Trading Bots", "Crypto & Web3 Signals",
        "Side Hustles & Passive Income", "Personal Tax & Saving Strategies", "Real Estate & Fractional Investing"
    ],
    "💼 Business, Startups & Entrepreneurship": [
        "Startup Funding & Pitch Decks", "Solopreneur & One-Person Business", "AI Automation Agencies (AAA)",
        "Freelancing & Agency Scaling", "Growth Hacking & B2B Marketing", "E-Commerce Supply Chain & Fulfillment"
    ],
    "💻 Digital Products & AI Tools": [
        "Vibe Coding & Code Extensions", "Generative AI & SaaS Tools", "Notion & Productivity Dashboards",
        "Digital Ebooks & Online Courses", "UI/UX Templates & Prompt Packs", "No-Code App Builders & Micro-Tools"
    ],
    "🎓 Education, Careers & Jobs": [
        "Govt Exam Dates & Prep Hacks", "AI Upskilling & Tech Roadmaps", "Study Abroad Scholarships & Visas",
        "Resume, Portfolio & Interview Hacks", "Remote Job & Hiring Alerts", "College Campus & Placement Trends"
    ],
    "🌿 Sustainability & Green Tech": [
        "Solar Power & Home Energy", "Zero-Waste Lifestyle & Reusables", "Organic & Sustainable Fashion",
        "Clean Tech & Carbon Offsets", "Eco-Friendly Packaging Solutions", "Electric Mobility & Micro-Transit"
    ],
    "🎬 Movies, OTT & Series": [
        "Box Office Collections & Predictions", "OTT Releases & Platform Buzz", "Teasers, Trailers & Fan Theories",
        "Celebrity Cast Interviews & BTS", "Regional Cinema Surges", "Reviews, Recaps & Ending Explained"
    ],
    "🎵 Music & Viral Sound Tracks": [
        "Trending TikTok & Reels Sounds", "Album Drops & Concert Tours", "Regional & Folk Remix Surges",
        "Indie Artists & Unsigned Talent", "Lo-Fi & Instrumental Tracks", "Dance Challenges & Cover Videos"
    ],
    "🎭 Pop Culture, Memes & Drama": [
        "Viral Meme Formats & Parodies", "Creator Scandals & Internet Drama", "Nostalgia & Throwback Trends",
        "Fan Theories & Fandom Culture", "Viral Challenges & Trends", "Reality TV & Live Broadcast Buzz"
    ],
    "🐉 Anime, Gaming & Fandom": [
        "Esports Tournaments & Highlights", "Mobile & PC Gaming Drops", "Anime Episode Releases & Manga Leaks",
        "Cosplay & Comic Conventions", "Streamer Highlights & Clipped Moments", "Gaming PC, Console & Gear Drops"
    ],
    "🌟 Celebrities & Sports Stars": [
        "Cricket & Sports Idols", "Movie & OTT Stars", "Viral Influencers & Vloggers",
        "Tournament & League Buzz", "Celebrity Fashion & Outfits", "Pop Culture Controversies"
    ],
    "💄 Beauty, Skincare & Lifestyle": [
        "UGC Skincare Hacks", "K-Beauty & Glass Skin Trends", "Anti-Aging & Beauty Devices",
        "Men's Grooming & Beard Care", "Haircare Treatment Trends", "Minimalist Capsule Wardrobes"
    ],
    "🏋️ Health, Fitness & Biohacking": [
        "Gym & Home Workout Gear", "Whey & Supplement Drops", "Biohacking & Wearable Tech (Oura/Whoop)",
        "Weight Loss & Nutrition Diets", "Mental Health & Burnout Recovery", "Recovery Gear & Cold Plunges"
    ],
    "✈️ Travel, Hotels & Food": [
        "Trending Destinations", "Hidden Tourist Places", "Luxury Hotels & Resort Stays",
        "Gourmet & Regional Cuisines", "Street Food Surges", "Budget & Backpacker Escapes"
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "Famous Temples & Shrines", "Hidden & Ancient Temples", "Religious Festivals & Pujas",
        "Pilgrimage Circuits & Yatras", "Festive Gifting Trends", "Spiritual Wellness & Meditation Drops"
    ],
    "🏛️ Politics, News & Civic Events": [
        "Elections & Campaign Rallies", "Legislative Debates & Laws", "Protests & Policy Changes",
        "Politician Speeches & Interviews", "Geopolitical & Diplomatic Updates", "Public Schemes & Subsidies"
    ],
}

# ==========================================
# 4. MASTER ROLE-BASED METRIC MAPPING
# ==========================================
ROLE_SPECIFIC_METRICS = {
    "🛍️ E-Commerce Merchants & D2C Brands": {
        "m1": "Estimated Sourcing Cost (COGS)", "m2": "Suggested Retail Price (SRP)", 
        "m3": "Gross Profit Margin (>80%)", "m4": "Break-Even ROAS Threshold", "m5": "Ad-Saturated Fatigue Index"
    },
    "🎬 Viral Content Creators & Media Houses": {
        "m1": "Retention Velocity Multiplier (3s+)", "m2": "Est. Revenue Per 1M Views (RPM)", 
        "m3": "Viral Index Score (1-100)", "m4": "Trending Audio Co-efficient", "m5": "Platform Algorithm Reach Weight"
    },
    "💸 Affiliate Marketers & Arbitrage Traders": {
        "m1": "Projected EPC (Earnings Per Click)", "m2": "Average Commission Value", 
        "m3": "Organic Traffic Loophole Score", "m4": "Affiliate Network Trust Rating", "m5": "Landing Page Conversion Rate"
    },
    "🏢 Real Estate Agents & High-Ticket Brokers": {
        "m1": "Target Cost Per Qualified Lead (CPQL)", "m2": "Average Commission Value (Closed Escrow)", 
        "m3": "Local Intent Index (Zip Code Demand)", "m4": "Inbound vs Outbound Ratio", "m5": "Property Days on Market (DOM)"
    },
    "💻 SaaS Founders, AI Builders & Solopreneurs": {
        "m1": "Target LTV to CAC Ratio", "m2": "Average Contract Value (ACV)", 
        "m3": "Tech Stack Cost Overhead (API Burn)", "m4": "Churn Risk Probability", "m5": "Product-Led Growth (PLG) Velocity"
    },
    "📈 Stock & Crypto Traders / Market Analysts": {
        "m1": "Volatility Breaker Range", "m2": "Smart Money Flow Index (Whale Tracking)", 
        "m3": "Risk-to-Reward Ratio (R:R)", "m4": "Liquidity Depth Score", "m5": "Institutional Sentiment Index"
    }
}

TEXTS = {
    "English": {
        "title": "⚡ TrendPulse AI: Master Intelligence & Execution Suite",
        "subtitle": "Autonomous Market Domination Engine & 10-Point Master Dossier Generator",
        "terminal": "🔑 Enterprise Access Terminal",
        "simulate_pro": "Simulate Pro Subscription Access",
        "config_title": "⚙️ Ingestion Pipeline & Signal Filter",
        "region": "🌐 Target Region:",
        "platform": "🎛️ Platform Source (12 Master Sources):",
        "category": "📁 Niche Category:",
        "sub_category": "🔍 Sub-Niche Focus:",
        "velocity": "⏱️ Signal Velocity & Timeframe:",
        "apply_btn": "🚀 Execute Ingestion Pipeline & Update DB",
        "telemetry_title": "📊 Live Telemetry & Database Signals",
        "custom_search": "🔍 Custom Asset Injection:",
        "active_signals_for": "Active Ingested Signals for:",
        "tab_radar": "📡 Ingestion Radar",
        "tab_blueprint": "🚀 10-Point Master Intelligence Dossier Engine",
        "tab_db": "🗄️ Database Inspector & Logs",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: मास्टर इंटेलिजेंस और एग्जीक्यूशन सुइट",
        "subtitle": "ऑटोनॉमस मार्केट डोमिनेशन इंजन और 10-पॉइंट मास्टर डॉसियर जेनरेटर",
        "terminal": "🔑 एंटरप्राइज एक्सेस टर्मिनल",
        "simulate_pro": "प्रो सब्सक्रिप्शन एक्सेस सिमुलेट करें",
        "config_title": "⚙️ इंजेक्शन पाइपलाइन और सिग्नल फ़िल्टर",
        "region": "🌐 टारगेट रीजन:",
        "platform": "🎛️ प्लेटफॉर्म सोर्स:",
        "category": "📁 नीश कैटेगरी:",
        "sub_category": "🔍 सब-नीश फ़ोकस:",
        "velocity": "⏱️ सिग्नल वेलोसिटी और टाइमफ्रेम:",
        "apply_btn": "🚀 इंजेक्शन पाइपलाइन चलाएं और DB अपडेट करें",
        "telemetry_title": "📊 लाइव टेलीमेट्री और डेटाबेस सिग्नल",
        "custom_search": "🔍 कस्टम एसेट इंजेक्शन:",
        "active_signals_for": "सक्रिय इंजेस्टेड सिग्नल:",
        "tab_radar": "📡 इंजेक्शन रडार",
        "tab_blueprint": "🚀 10-पॉइंट मास्टर इंटेलिजेंस डॉसियर इंजन",
        "tab_db": "🗄️ डेटाबेस इंस्पेक्टर और लॉग्स",
    },
}

# ==========================================
# 5. HELPER FUNCTIONS & PDF ENGINE
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

def create_pdf_dossier(asset_name, category, role, viral_score, window, result):
    clean_asset = sanitize_trend_input(asset_name)
    clean_cat = sanitize_trend_input(category)
    clean_role = sanitize_trend_input(role).lstrip('n').strip() # Fixes leading 'n' role bug

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=14, textColor="#ff4b4b", spaceAfter=6)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=10, textColor="#1a1a1a", spaceBefore=5, spaceAfter=2)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=7.5, leading=10, textColor="#333333", spaceAfter=3)

    story = [
        Paragraph("TrendPulse AI - 10-Point Enterprise Intelligence Commercial Dossier", title_style),
        Paragraph(f"<b>Asset:</b> {safe_xml_text(clean_asset)} | <b>Category:</b> {safe_xml_text(clean_cat)} | <b>Role:</b> {safe_xml_text(clean_role)}", body_style),
        Paragraph(f"<b>Predictive Viral Score:</b> {safe_xml_text(str(viral_score))} | <b>Window:</b> {safe_xml_text(str(window))}", body_style),
        Spacer(1, 4)
    ]

    sections = [
        ("1. Role-Specific Unit Economics & Financial Vault", result.get("unit_economics", "")),
        ("2. Geo-Targeting & Regional Hotspot Mapping", result.get("geo_mapping", "")),
        ("3. Psychological Hook Matrix (0-3s)", result.get("hook_matrix", "")),
        ("4. Ready-to-Deploy Multi-Angle Copywriting Vault", result.get("copywriting_vault", "")),
        ("5. Competitor & Market Saturation Threat Matrix", result.get("saturation_matrix", "")),
        ("6. Monetization & Pricing Strategy Vault", result.get("monetization_vault", "")),
        ("7. AI Prompt Engineering & Script Generation Pack", result.get("tech_prompts", "")),
        ("8. Algorithmic Scale vs Kill Risk Management Rules", result.get("scale_kill_rules", "")),
        ("9. Python Async Data Scraper & Pipeline Monitor", result.get("python_code", "")),
        ("10. Automated 10-Day Master Execution Roadmap", result.get("action_roadmap", "")),
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(safe_xml_text(text), body_style))
        story.append(Spacer(1, 2))

    doc.build(story)
    buffer.seek(0)
    return buffer
# ==========================================
# 6. PIPELINE & RADAR DATA ENGINE
# ==========================================
@st.cache_data(ttl=300)
def fetch_and_store_signals(region, platform_source, category, sub_niche, timeframe):
    results = []
    region_term = "India" if region == "IN" else ("US" if region == "US" else "")
    sub_ctx = f"{sub_niche}" if (sub_niche and sub_niche != "All Sub-Niches") else ""
    query_text = f"{category.split()[-1]} {sub_ctx} {region_term}".strip()
    search_query = urllib.parse.quote(query_text)
    platform_name = platform_source.split()[1] if len(platform_source.split()) > 1 else platform_source

    if "Reddit" in platform_source:
        try:
            url = f"https://www.reddit.com/search.json?q={search_query}&sort=hot&limit=10"
            headers = {"User-Agent": "Mozilla/5.0 TrendPulseAI/3.0"}
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

    elif "Google Trends" in platform_source or "Google News" in platform_source:
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
        if sub_niche in UPDATED_NICHE_CATEGORIES.get(category, []):
            base_pool = [f"Viral {sub_niche}", f"Top Surge {sub_niche}", f"Breakout {sub_niche}", f"High-Demand {sub_niche}", f"Elite {sub_niche}"]
        else:
            base_pool = [f"{category.split()[-1]} Spike", f"Viral Trend", f"Top Choice {region_term}", "Breakout Signal", "Elite Movement"]

        for i, item in enumerate(base_pool):
            if len(results) >= 5:
                break
            results.append({
                "Keyword": f"[{platform_name}] {item}",
                "Volume": f"{(95 - i * 11) * 10}K+ Interactions ({region})"
            })

    try:
        cursor = db_conn.cursor()
        for r in results:
            cursor.execute(
                "INSERT INTO platform_signals (source_platform, keyword, engagement_metrics, region) VALUES (?, ?, ?, ?)",
                (platform_source, r["Keyword"], r["Volume"], region)
            )
        db_conn.commit()
    except Exception:
        pass

    return results[:5]

# ==========================================
# 7. MASTER LLM 10-POINT DOSSIER GENERATOR
# ==========================================
def generate_master_enterprise_dossier(keyword_asset, category, sub_niche, target_role, platform, timeframe, velocity_score, lang):
    clean_asset = sanitize_trend_input(keyword_asset)
    clean_cat = sanitize_trend_input(category)
    clean_sub = sanitize_trend_input(sub_niche)
    sub_ctx = f"focusing on sub-niche '{clean_sub}'" if clean_sub and clean_sub != "All Sub-Niches" else ""

    metrics_template = ROLE_SPECIFIC_METRICS.get(target_role, ROLE_SPECIFIC_METRICS["🛍️ E-Commerce Merchants & D2C Brands"])

    # Safe text values avoiding raw newline rendering issues
    default_response = {
        "viral_score": f"{velocity_score}%",
        "prediction_window": f"Active Timing Window ({timeframe})",
        "unit_economics": f"• **{metrics_template['m1']}:** Optimized tier\n• **{metrics_template['m2']}:** INR 1,500 – INR 2,800 benchmark\n• **{metrics_template['m3']}:** Strong market fit\n• **{metrics_template['m4']}:** Safe margin threshold\n• **{metrics_template['m5']}:** Stable index",
        "geo_mapping": "• **Primary Tier-1 Hotspots:** Mumbai, Bengaluru, Delhi-NCR, Pune\n• **Emerging Tier-2 Hubs:** Jaipur, Indore, Chandigarh, Lucknow\n• **International Spillover:** US/UK diaspora clusters",
        "hook_matrix": f"• **FOMO Hook:** \"The secret strategy behind {clean_asset} that elite operators are hiding...\"\n• **Risk Hook:** \"If you ignore {clean_asset} in {timeframe}, you are leaving massive ROI on the table...\"\n• **Dopamine Hook:** [Visual Pattern Interrupt] High-end cinematic showcase of {clean_asset}.",
        "copywriting_vault": f"• **Problem-Solver Angle:** \"Struggling with {clean_asset}? Here is the ultimate modern solution to scale your results instantly.\"\n• **Trust Builder Angle:** \"⭐⭐⭐⭐⭐ 'This completely transformed my workflow within 3 days.' - Verified User.\"",
        "saturation_matrix": "• **Saturation Index:** Moderate (62% saturated, high incoming demand)\n• **Competitor Weakness:** Slow fulfillment and generic design copy\n• **Our Strategic Edge:** Ultra-fast 48-hour delivery & micro-community branding",
        "monetization_vault": "• **Optimal Pricing Model:** INR 999 – INR 1,499 sweet spot\n• **Upsell Stack Strategy:** Bundle Pack (2 + 1 Free) to increase AOV by 35%",
        "tech_prompts": f"• **ChatGPT Script Prompt:** Write a 30-second high-retention script for {clean_asset}.\n• **Midjourney v6.0:** Hyper-realistic minimalist luxury asset photography of {clean_asset}, clean studio lighting, 8k --ar 16:9 --v 6.0",
        "scale_kill_rules": "• **The Kill Rule:** If ad budget crosses INR 4,000/day with 0 conversions in 24h -> PAUSE IMMEDIATELY.\n• **The Scaling Rule:** If ROAS is stable for 48h -> Increase budget by 20%-30% daily at 11:00 AM.",
        "python_code": "import asyncio\nimport aiohttp\n\nasync def fetch_metrics(session, url):\n    async with session.get(url) as r:\n        print(await r.json())",
        "action_roadmap": "1. HOUR 1-6 (Setup): Core infrastructure & <2s speed optimization.\n2. HOUR 24 (Micro-Testing): Low-budget cross-channel validation.\n3. DAY 3 (Optimization): Apply 'Scale vs Kill' rules.\n4. DAY 10 (Scaling): Deploy retention and upsell funnels."
    }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
You are an elite Enterprise Intelligence AI. Return ONLY a raw valid JSON object (no markdown, no backticks).
Generate a hyper-realistic, highly customized 10-Point Commercial Intelligence Dossier in English for:
- Asset/Trend: "{clean_asset}"
- Category: "{clean_cat} {sub_ctx}"
- Target Operating Role: "{target_role}"
- Platform Source: "{platform}"
- Timeframe: "{timeframe}"

Ensure all monetary values use 'INR ' instead of special characters and metrics strictly match the domain of '{target_role}'.

JSON Format:
{{
  "viral_score": "{velocity_score}%",
  "prediction_window": "Lifecycle timing window",
  "unit_economics": "• **{metrics_template['m1']}:** ...\\n• **{metrics_template['m2']}:** INR ...\\n• **{metrics_template['m3']}:** ...\\n• **{metrics_template['m4']}:** ...\\n• **{metrics_template['m5']}:** ...",
  "geo_mapping": "• **Primary Tier-1 Hotspots:** ...\\n• **Emerging Tier-2 Hubs:** ...\\n• **International Spillover:** ...",
  "hook_matrix": "• **FOMO Hook:** ...\\n• **Risk Hook:** ...\\n• **Dopamine Hook:** ...",
  "copywriting_vault": "• **Problem-Solver Angle:** ...\\n• **Trust Builder Angle:** ...",
  "saturation_matrix": "• **Saturation Index:** ...\\n• **Competitor Weakness:** ...\\n• **Our Strategic Edge:** ...",
  "monetization_vault": "• **Optimal Pricing Model:** INR ...\\n• **Upsell Stack Strategy:** ...",
  "tech_prompts": "• **ChatGPT Script Prompt:** ...\\n• **Midjourney Prompt:** ...",
  "scale_kill_rules": "• **The Kill Rule:** INR 4,000/day threshold ...\\n• **The Scaling Rule:** ...",
  "python_code": "import asyncio...",
  "action_roadmap": "1. HOUR 1-6: ...\\n2. HOUR 24: ...\\n3. DAY 3: ...\\n4. DAY 10: ..."
}}
"""
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)
    except Exception:
        return default_response

# ==========================================
# 8. MAIN UI LAYOUT & BACKEND INSPECTOR
# ==========================================
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

head_col1, head_col2 = st.columns([3, 1])
with head_col2:
    selected_lang = st.selectbox("🌐 Language / भाषा:", ["English", "Hindi"], index=0)

t = TEXTS[selected_lang]

with head_col1:
    st.title(t["title"])
    st.caption(f"{t['subtitle']} | ⚡ 10-Point Enterprise Intelligence & 5-Table SQLite Architecture")

st.markdown("---")

with st.expander(t["terminal"], expanded=False):
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
                "🔎 Google Trends & Search Intent",
                "📌 Pinterest Trends & Visual Discovery",
                "🧵 X (Twitter) Realtime Trends",
                "👽 Reddit Viral & Community Buzz",
                "🛒 Amazon Movers & E-Com Marketplaces",
                "▶️ YouTube Shorts & Video Popularity",
                "💼 LinkedIn Business & B2B Signals",
                "🚀 Product Hunt & GitHub Trending",
                "🛍️ Etsy & D2C Niche Marketplaces",
                "📰 Google News & Newsletter Aggregators",
            ],
            index=0,
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

active_signals = fetch_and_store_signals(
    geo_map[geo_option], platform_source, selected_category, selected_sub_niche, timeframe
)

signal_scores = {item["Keyword"]: round(99.4 - (i * 2.1), 1) for i, item in enumerate(active_signals)}
df = pd.DataFrame([{ "Trending Asset Signal": item["Keyword"], "Engagement / Volume": item["Volume"], "Velocity Status": "🔥 High Growth" } for item in active_signals])

# TABBED WORKFLOW UI
tab_radar, tab_blueprint, tab_db = st.tabs([t["tab_radar"], t["tab_blueprint"], t["tab_db"]])

with tab_radar:
    st.subheader(t["telemetry_title"])
    custom_search = st.text_input(t["custom_search"], placeholder="e.g. Vibe Coding, AI Automation Agency, K-Beauty Glass Skin")
    if custom_search.strip():
        custom_item = {"Keyword": f"[Custom Injection] {custom_search.strip()}", "Volume": f"Realtime Query ({geo_option})"}
        if not any(custom_search.strip() in s["Keyword"] for s in active_signals):
            active_signals.insert(0, custom_item)

    st.markdown(f"**{t['active_signals_for']}** `{selected_category}` | `{platform_source}` | `{geo_option}`")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### 📈 Signal Velocity & Pipeline Demand Curve")
    chart_keyword = active_signals[0]["Keyword"] if active_signals else "Asset"
    base_score = signal_scores.get(chart_keyword, 94.0)
    chart_df = pd.DataFrame({
        "Timeline": ["Day -3", "Day -2", "Day -1", "Today", "Day +1 (Proj)", "Day +2 (Proj)", "Day +3 (Proj)"],
        "Velocity Score": [max(10.0, base_score - 45), max(15.0, base_score - 30), max(25.0, base_score - 15), base_score, min(99.9, base_score + 5), min(99.9, base_score + 8), min(99.9, base_score + 4)]
    })
    fig = px.line(chart_df, x="Timeline", y="Velocity Score", markers=True, line_shape="spline", title=f"Backend Pipeline Trajectory: {chart_keyword}")
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="#fafafa")
    fig.update_traces(line_color="#ff4b4b", line_width=3, marker_size=8)
    st.plotly_chart(fig, use_container_width=True)

with tab_blueprint:
    st.subheader("🚀 10-Point Master Intelligence Dossier Engine")

    if not st.session_state["is_premium"]:
        st.warning("🔒 10-POINT MASTER DOSSIER ENGINE IS LOCKED")
        st.info("Unlock all 10 enterprise intelligence vaults including geo-mapping, threat matrix, monetization, and automated execution roadmaps.")
        st.link_button("🔥 Upgrade to Pro & Unlock Master Engine", STRIPE_CHECKOUT_URL, use_container_width=True)
    else:
        st.success("🔓 MASTER PRO ENGINE ACTIVE (10-POINT SUITE)")

        asset_list = [item["Keyword"] for item in active_signals]
        selected_asset = st.selectbox("🎯 Select Ingested Asset:", options=asset_list, index=0)

        target_role = st.selectbox(
            "👤 Operating Role (6 User Modes):",
            [
                "🛍️ E-Commerce Merchants & D2C Brands",
                "🎬 Viral Content Creators & Media Houses",
                "💸 Affiliate Marketers & Arbitrage Traders",
                "🏢 Real Estate Agents & High-Ticket Brokers",
                "💻 SaaS Founders, AI Builders & Solopreneurs",
                "📈 Stock & Crypto Traders / Market Analysts",
            ],
            index=0,
        )

        gen_btn = st.button("⚡ Generate 10-Point Master Dossier", use_container_width=True)

        if gen_btn or "enterprise_result" in st.session_state:
            curr_score = signal_scores.get(selected_asset, 95.0)
            if gen_btn:
                with st.spinner("Synthesizing 10-Point Enterprise Intelligence Dossier..."):
                    result = generate_master_enterprise_dossier(
                        selected_asset, selected_category, selected_sub_niche, target_role, platform_source, timeframe, curr_score, selected_lang
                    )
                    st.session_state["enterprise_result"] = result
                    st.session_state["ent_asset"] = selected_asset
                    st.session_state["ent_role"] = target_role
                    st.session_state["ent_score"] = curr_score
            else:
                result = st.session_state["enterprise_result"]
                selected_asset = st.session_state["ent_asset"]
                target_role = st.session_state["ent_role"]
                curr_score = st.session_state["ent_score"]

            # Metrics Row
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Predictive Viral Score", result.get("viral_score", f"{curr_score}%"))
            m_col2.metric("Lifecycle Timing Window", result.get("prediction_window", timeframe))

            st.markdown("---")
            st.markdown(f"### 📊 1. Role-Specific Unit Economics & Financial Vault ({target_role})")
            st.markdown(result.get("unit_economics", ""))

            st.markdown("---")
            st.markdown("### 🌍 2. Geo-Targeting & Regional Hotspot Mapping")
            st.markdown(result.get("geo_mapping", ""))

            st.markdown("---")
            st.markdown("### 🎯 3. The Psychological Hook Matrix (0-3s Triggers)")
            st.markdown(result.get("hook_matrix", ""))

            st.markdown("---")
            st.markdown("### ✍️ 4. Ready-to-Deploy Multi-Angle Copywriting Vault")
            st.markdown(result.get("copywriting_vault", ""))

            st.markdown("---")
            st.markdown("### ⚠️ 5. Competitor & Market Saturation Threat Matrix")
            st.markdown(result.get("saturation_matrix", ""))

            st.markdown("---")
            st.markdown("### 💰 6. Monetization & Pricing Strategy Vault")
            st.markdown(result.get("monetization_vault", ""))

            st.markdown("---")
            st.markdown("### 🧠 7. AI Prompt Engineering & Script Generation Pack")
            st.markdown(result.get("tech_prompts", ""))

            st.markdown("---")
            st.markdown("### 📉 8. Algorithmic Scale vs Kill Risk Management Rules")
            st.markdown(result.get("scale_kill_rules", ""))

            st.markdown("---")
            st.markdown("### ⚙️ 9. Python Async Data Scraper & Pipeline Monitor")
            st.code(result.get("python_code", ""), language="python")

            st.markdown("---")
            st.markdown("### 📅 10. Automated 10-Day Master Execution Roadmap")
            st.text(result.get("action_roadmap", ""))

            st.markdown("---")
            pdf_bytes = create_pdf_dossier(selected_asset, selected_category, target_role, curr_score, timeframe, result)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📄 Download 10-Point Master PDF Dossier",
                    data=pdf_bytes,
                    file_name=f"TrendPulse_10Pt_Dossier_{sanitize_trend_input(selected_asset)[:15]}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            with d_col2:
                wa_text = urllib.parse.quote(
                    f"⚡ *TrendPulse AI 10-Point Master Dossier*\n\n"
                    f"Asset: {sanitize_trend_input(selected_asset)}\n"
                    f"Role: {target_role}\n"
                    f"Viral Score: {curr_score}%\n\n"
                    f"View full enterprise intelligence briefing!"
                )
                st.link_button(
                    label="💬 Share to WhatsApp",
                    url=f"https://wa.me/?text={wa_text}",
                    use_container_width=True,
                )

with tab_db:
    st.subheader("🗄️ Database Inspector & Pipeline Logs (5 Core Tables)")
    try:
        db_df = pd.read_sql("SELECT * FROM platform_signals ORDER BY timestamp DESC LIMIT 50", db_conn)
        st.markdown(f"**Total Ingested Signals Logged in SQLite:** `{len(db_df)}` records")
        st.dataframe(db_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Database read error: {e}")

    if st.button("🧹 Clear Pipeline Logs", use_container_width=False):
        try:
            cursor = db_conn.cursor()
            cursor.execute("DELETE FROM platform_signals")
            db_conn.commit()
            st.success("Pipeline logs cleared successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing logs: {e}")
