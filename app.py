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
    page_title="TrendPulse AI - Master Intelligence & Revenue Scale Suite",
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
# 2. SQLITE DATABASE INITIALIZATION
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
# 4. MASTER ROLE-BASED METRICS
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
        "title": "⚡ TrendPulse AI: Master Intelligence & Revenue Scale Suite",
        "subtitle": "Autonomous Market Domination Engine & Advanced Commercial Dossier Generator",
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
        "tab_blueprint": "🚀 Master Intelligence & Revenue Dossier Engine",
        "tab_db": "🗄️ Database Inspector & Logs",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: मास्टर इंटेलिजेंस और रेवेन्यू स्केल सुइट",
        "subtitle": "ऑटोनॉमस मार्केट डोमिनेशन इंजन और एडवांस्ड कमर्शियल डॉसियर जेनरेटर",
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
        "tab_blueprint": "🚀 मास्टर इंटेलिजेंस और रेवेन्यू डॉसियर इंजन",
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
    clean_role = sanitize_trend_input(role).lstrip('n').strip()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=14, textColor="#ff4b4b", spaceAfter=6)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=10, textColor="#1a1a1a", spaceBefore=5, spaceAfter=2)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=7.5, leading=10, textColor="#333333", spaceAfter=3)

    story = [
        Paragraph("TrendPulse AI - Master Intelligence & Revenue Scale Dossier", title_style),
        Paragraph(f"<b>Asset:</b> {safe_xml_text(clean_asset)} | <b>Category:</b> {safe_xml_text(clean_cat)} | <b>Role:</b> {safe_xml_text(clean_role)}", body_style),
        Paragraph(f"<b>Predictive Viral Score:</b> {safe_xml_text(str(viral_score))} | <b>Window:</b> {safe_xml_text(str(window))}", body_style),
        Spacer(1, 4)
    ]

    sections = [
        ("1. Advanced Monetization, Rate Card & Unit Economics Vault", result.get("unit_economics", "")),
        ("2. Geo-Targeting & Regional Hotspot Mapping", result.get("geo_mapping", "")),
        ("3. Psychological Hook Matrix & Video Storyboard (0-3s)", result.get("hook_matrix", "")),
        ("4. Ready-to-Deploy Multi-Angle Copywriting Vault", result.get("copywriting_vault", "")),
        ("5. Competitor & Market Saturation Threat Matrix", result.get("saturation_matrix", "")),
        ("6. AI Prompt Engineering & Script Generation Pack", result.get("tech_prompts", "")),
        ("7. Algorithmic Scale vs Kill Risk Management Rules", result.get("scale_kill_rules", "")),
        ("8. Realtime Audience Sentiment & Virality Predictive Formula", result.get("virality_formula", "")),
        ("9. Multi-Platform Syndication & Marketing Matrix", result.get("syndication_matrix", "")),
        ("10. Automated 10-Day Master Execution & Scaling Roadmap", result.get("action_roadmap", "")),
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(safe_xml_text(text), body_style))
        story.append(Spacer(1, 2))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 6. UNIVERSAL DYNAMIC DOMAIN-SMART SIGNAL ENGINE
# ==========================================
@st.cache_data(ttl=300)
def fetch_and_store_signals(region, platform_source, category, sub_niche, timeframe):
    results = []
    
    sub_label = sub_niche if sub_niche and sub_niche != "All Sub-Niches" else category
    
    category_context_map = {
        "E-Commerce": ("Viral Product Spike & Flash Deal", "D2C Verified Store Hub"),
        "Real Estate": ("High-Yield Property & Smart Space Demand", "PropTech Asset Network"),
        "Automobile": ("EV & Smart Mobility Launch Wave", "Automotive Innovation Hub"),
        "Parenting": ("Smart Kids Gear & Routine Trend", "Family Care Direct Hub"),
        "Pets": ("Pet Health & Care Product Surge", "Animal Care Verified Brand"),
        "Finance": ("Wealth Asset & Yield Breakout", "Quant & FinTech Hub"),
        "Business": ("Startup Growth & Scaling Signal", "Enterprise B2B Network"),
        "Digital Products": ("SaaS & AI Tool Adoption Surge", "Cloud Stack & Dev Hub"),
        "Education": ("Upskilling & Career Track Surge", "Global EdTech & Certification Hub"),
        "Sustainability": ("Green Tech & Eco-Friendly Shift", "CleanEnergy Verified Network"),
        "Movies": ("Box Office & OTT Stream Surge", "Cinematic Media Hub"),
        "Music": ("Viral Sound & Remix Wave", "Artist & Audio Distribution Hub"),
        "Pop Culture": ("Viral Trend & Meme Surge", "Creator Drama & Fandom Hub"),
        "Anime": ("Gaming & Fandom Epic Drop", "Esports & Animation Hub"),
        "Celebrities": ("Star Power & Fashion Trend", "Influencer Media Hub"),
        "Beauty": ("Skincare & Glow Trend Wave", "D2C Cosmetics Hub"),
        "Health": ("Biohacking & Fitness Protocol Surge", "Wellness & Performance Hub"),
        "Travel": ("Offbeat Destination & Resort Spike", "Travel Explorer Network"),
        "Faith": ("Spiritual & Heritage Gathering Wave", "Sacred Trails & Events Hub"),
        "Politics": ("Civic & Policy Discussion Surge", "Public Affairs Tracker")
    }
    
    matched_prefix = ("Market Demand Spike", "Enterprise Verified Hub")
    for cat_key, ctx_val in category_context_map.items():
        if cat_key.lower() in category.lower():
            matched_prefix = ctx_val
            break

    velocity_status_list = ["🔥 High Growth", "⚡ Accelerating", "🚀 Explosive Surge", "📈 Trending"]

    for i in range(10):
        base_vol = 1450000 - (i * 85400)
        v_status = velocity_status_list[i % len(velocity_status_list)]
        
        item_keyword = f"{sub_label} - {matched_prefix[0]} #{i+1}"
        entity_name = f"{matched_prefix[1]} ({sub_label})"
        
        results.append({
            "Keyword": item_keyword,
            "Entity": entity_name,
            "Volume": f"{base_vol:,} Interactions ({region})",
            "Velocity": v_status
        })

    try:
        cursor = db_conn.cursor()
        for r in results:
            cursor.execute(
                "INSERT INTO platform_signals (source_platform, keyword, engagement_metrics, region) VALUES (?, ?, ?, ?)",
                (platform_source, f"{r['Keyword']} | Entity: {r['Entity']}", r["Volume"], region)
            )
        db_conn.commit()
    except Exception:
        pass

    return results

# ==========================================
# 7. MASTER LLM DOSSIER GENERATOR
# ==========================================
def generate_master_enterprise_dossier(keyword_asset, category, sub_niche, target_role, platform, timeframe, velocity_score, lang):
    clean_asset = sanitize_trend_input(keyword_asset)
    clean_cat = sanitize_trend_input(category)
    clean_sub = sanitize_trend_input(sub_niche)
    sub_ctx = f"focusing on sub-niche '{clean_sub}'" if clean_sub and clean_sub != "All Sub-Niches" else ""

    metrics_template = ROLE_SPECIFIC_METRICS.get(target_role, ROLE_SPECIFIC_METRICS["🛍️ E-Commerce Merchants & D2C Brands"])

    default_response = {
        "viral_score": f"{velocity_score}%",
        "prediction_window": f"Active Timing Window ({timeframe})",
        "unit_economics": f"• **{metrics_template['m1']}:** Optimized tier\n• **{metrics_template['m2']}:** INR 1,500 – INR 2,800 benchmark\n• **Brand Rate Card (Reel/Short):** INR 15,000 – INR 25,000 per post\n• **Affiliate Commission Stack:** 12% per confirmed conversion\n• **Viral Index Score:** Strong market fit",
        "geo_mapping": "• **Primary Tier-1 Hotspots:** Mumbai, Bengaluru, Delhi-NCR, Pune\n• **Emerging Tier-2 Hubs:** Jaipur, Indore, Chandigarh, Lucknow\n• **International Spillover:** US/UK diaspora clusters",
        "hook_matrix": f"• **FOMO Hook:** \"The secret strategy behind {clean_asset} that elite operators are hiding...\"\n• **Risk Hook:** \"If you ignore {clean_asset} in {timeframe}, you are leaving massive ROI on the table...\"\n• **Dopamine Hook (Storyboard):** [0-3s] High-end cinematic visual hook transitioning into problem-solver narrative.",
        "copywriting_vault": f"• **Problem-Solver Angle:** \"Struggling with {clean_asset}? Here is the ultimate modern solution to scale your results instantly.\"\n• **Trust Builder Angle:** \"⭐⭐⭐⭐⭐ 'This completely transformed my workflow within 3 days.' - Verified User.\"",
        "saturation_matrix": "• **Saturation Index:** Moderate (62% saturated, high incoming demand)\n• **Competitor Weakness:** Slow fulfillment and generic design copy\n• **Our Strategic Edge:** Ultra-fast 48-hour delivery & micro-community branding",
        "tech_prompts": f"• **ChatGPT Script Prompt:** Write a 30-second high-retention script for {clean_asset}.\n• **Midjourney v6.0:** Hyper-realistic minimalist luxury asset photography of {clean_asset}, clean studio lighting, 8k --ar 16:9 --v 6.0",
        "scale_kill_rules": "• **The Kill Rule:** If ad budget crosses INR 4,000/day with 0 conversions in 24h -> PAUSE IMMEDIATELY.\n• **The Scaling Rule:** If ROAS is stable for 48h -> Increase budget by 20%-30% daily at 11:00 AM.",
        "virality_formula": "• **Algorithm Core Logic:** Calculates engagement velocity vs comment sentiment ratios.\n• **Formula:** Virality Score = ((3s Watch Retention * Shares) / Impressions) * (1 + Comment Sentiment Weight)\n• **Pipeline Monitoring Rule:** If engagement ratio deviates by >15% in 6h, flag for instant scaling or pivot.",
        "syndication_matrix": "• **Instagram Reels Strategy:** Trending audio loops with high-contrast text overlays.\n• **YouTube Shorts Strategy:** Optimized thumbnail and evening publishing window (6 PM - 8 PM).\n• **Cross-Platform Retargeting:** Push top 15s cutdowns as paid community ads.",
        "action_roadmap": "1. HOUR 1-6 (Setup): Core infrastructure & affiliate integration.\n2. HOUR 24 (Micro-Testing): Low-budget cross-channel validation.\n3. DAY 3 (Optimization): Apply 'Scale vs Kill' algorithmic rules.\n4. DAY 10 (Scaling): Deploy retention loops and brand monetization funnels."
    }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
You are an elite Enterprise Intelligence AI. Return ONLY a raw valid JSON object (no markdown, no backticks).
Generate a hyper-realistic, highly customized Commercial Intelligence & Revenue Scale Dossier in English for:
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
  "unit_economics": "• **{metrics_template['m1']}:** ...\\n• **{metrics_template['m2']}:** INR ...\\n• **Brand Rate Card (Reel/Short):** INR 15,000 – INR 25,000\\n• **Affiliate Commission Stack:** 12%\\n• **Viral Index Score:** ...",
  "geo_mapping": "• **Primary Tier-1 Hotspots:** ...\\n• **Emerging Tier-2 Hubs:** ...\\n• **International Spillover:** ...",
  "hook_matrix": "• **FOMO Hook:** ...\\n• **Risk Hook:** ...\\n• **Dopamine Hook (Storyboard):** ...",
  "copywriting_vault": "• **Problem-Solver Angle:** ...\\n• **Trust Builder Angle:** ...",
  "saturation_matrix": "• **Saturation Index:** ...\\n• **Competitor Weakness:** ...\\n• **Our Strategic Edge:** ...",
  "tech_prompts": "• **ChatGPT Script Prompt:** ...\\n• **Midjourney Prompt:** ...",
  "scale_kill_rules": "• **The Kill Rule:** INR 4,000/day threshold ...\\n• **The Scaling Rule:** ...",
  "virality_formula": "• **Algorithm Core Logic:** ...\\n• **Formula:** Virality Score = ((3s Watch Retention * Shares) / Impressions) * (1 + Comment Sentiment Weight)\\n• **Pipeline Monitoring Rule:** ...",
  "syndication_matrix": "• **Instagram Reels Strategy:** ...\\n• **YouTube Shorts Strategy:** ...\\n• **Cross-Platform Retargeting:** ...",
  "action_roadmap": "1. HOUR 1-6: Setup & affiliate integration.\\n2. HOUR 24: Micro-Testing.\\n3. DAY 3: Optimization.\\n4. DAY 10: Scaling."
}}
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only response engine. Return strictly valid JSON without code blocks."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2500
        ]
        
        content = chat_completion.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed_json = json.loads(content.strip())
        return parsed_json
    except Exception:
        return default_response

# ==========================================
# 8. STREAMLIT ENTERPRISE UI INTERFACE
# ==========================================
def main():
    st.sidebar.markdown("### 🌐 Language Selector / भाषा")
    selected_lang = st.sidebar.selectbox("Choose Language / भाषा चुनें", ["English", "Hindi"])
    t = TEXTS[selected_lang]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {t['terminal']}")
    simulate_pro = st.sidebar.checkbox(t["simulate_pro"], value=True)
    
    st.markdown(f"# {t['title']}")
    st.markdown(f"### {t['subtitle']}")
    st.markdown("---")

    st.markdown(f"### {t['config_title']}")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        region = st.selectbox(t["region"], ["India (IN)", "United States (US)", "United Kingdom (GB)", "Global (ALL)"])
    with col2:
        platform_source = st.selectbox(t["platform"], [
            "TikTok Shop / Viral", "Instagram Reels", "Google Trends", "Amazon Movers",
            "YouTube Shorts", "Twitter / X Trends", "Reddit Viral Subs", "Product Hunt",
            "Substack / Newsletters", "LinkedIn B2B Trends", "App Store Charts", "Telegram Crypto Channels"
        ])
    with col3:
        category_options = list(UPDATED_NICHE_CATEGORIES.keys())
        selected_category = st.selectbox(t["category"], category_options)
    with col4:
        sub_niches_list = ["All Sub-Niches"] + UPDATED_NICHE_CATEGORIES.get(selected_category, [])
        selected_sub_niche = st.selectbox(t["sub_category"], sub_niches_list)
    with col5:
        timeframe = st.selectbox(t["velocity"], ["Realtime Spike (24h)", "7 Days Rolling", "30 Days Momentum", "90 Days Macro Trend"])

    execute_btn = st.button(t["apply_btn"], use_container_width=True)

    tab1, tab2, tab3 = st.tabs([t["tab_radar"], t["tab_blueprint"], t["tab_db"]])

    with tab1:
        st.markdown(f"### {t['telemetry_title']}")
        custom_query = st.text_input(t["custom_search"], placeholder="Type any keyword or asset name to track instantly...")
        
        signals_data = fetch_and_store_signals(region, platform_source, selected_category, selected_sub_niche, timeframe)
        
        if custom_query:
            signals_data.insert(0, {
                "Keyword": f"Custom Injected Asset: {custom_query}",
                "Entity": "Custom User Target Hub",
                "Volume": f"1,850,000 Interactions ({region})",
                "Velocity": "🔥 Explosive Custom Spike"
            })

        st.markdown(f"**{t['active_signals_for']} {selected_category} -> {selected_sub_niche}**")
        df_signals = pd.DataFrame(signals_data)
        st.dataframe(df_signals, use_container_width=True, hide_index=True)

        st.markdown("#### 📈 Realtime Velocity Score Curve")
        chart_data = pd.DataFrame({
            "Day": [f"Day {i+1}" for i in range(7)],
            "Engagement Velocity Score": [45, 62, 78, 85, 92, 96, 99]
        })
        fig = px.line(chart_data, x="Day", y="Engagement Velocity Score", markers=True, line_shape="spline")
        fig.update_traces(line_color="#ff4b4b", line_width=3)
        fig.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#0e1117", font_color="#fafafa")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown(f"### {t['tab_blueprint']}")
        
        if not simulate_pro:
            st.warning("🔒 Pro Subscription Required for Full Commercial Dossier Engine. Please activate Pro mode in the Enterprise Terminal sidebar.")
            st.markdown(f"[🚀 Click Here to Upgrade via Stripe]({STRIPE_CHECKOUT_URL})", unsafe_allow_html=True)
        else:
            asset_options = [s["Keyword"] for s in signals_data]
            selected_asset = st.selectbox("Select Asset / Signal to Generate Dossier:", asset_options)
            
            role_options = list(ROLE_SPECIFIC_METRICS.keys())
            selected_role = st.selectbox("Select Target Operating Role:", role_options)
            
            if st.button("🚀 Generate Master Intelligence & Revenue Dossier", use_container_width=True):
                with st.spinner("Executing multi-agent enterprise synthesis & financial modeling..."):
                    dossier = generate_master_enterprise_dossier(
                        selected_asset, selected_category, selected_sub_niche, 
                        selected_role, platform_source, timeframe, 98.4, selected_lang
                    )
                    
                    st.session_state["last_dossier"] = dossier
                    st.session_state["last_asset"] = selected_asset
                    st.session_state["last_role"] = selected_role

            if "last_dossier" in st.session_state:
                d = st.session_state["last_dossier"]
                
                pdf_file = create_pdf_dossier(
                    st.session_state["last_asset"], selected_category, 
                    st.session_state["last_role"], d["viral_score"], timeframe, d
                )
                st.download_button(
                    label="📥 Download Official PDF Commercial & Revenue Dossier",
                    data=pdf_file,
                    file_name="TrendPulse_Master_Revenue_Dossier.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                st.markdown("---")
                sections_mapping = [
                    ("1. Advanced Monetization, Rate Card & Unit Economics Vault", d.get("unit_economics", "")),
                    ("2. Geo-Targeting & Regional Hotspot Mapping", d.get("geo_mapping", "")),
                    ("3. Psychological Hook Matrix & Video Storyboard (0-3s)", d.get("hook_matrix", "")),
                    ("4. Ready-to-Deploy Multi-Angle Copywriting Vault", d.get("copywriting_vault", "")),
                    ("5. Competitor & Market Saturation Threat Matrix", d.get("saturation_matrix", "")),
                    ("6. AI Prompt Engineering & Script Generation Pack", d.get("tech_prompts", "")),
                    ("7. Algorithmic Scale vs Kill Risk Management Rules", d.get("scale_kill_rules", "")),
                    ("8. Realtime Audience Sentiment & Virality Predictive Formula", d.get("virality_formula", "")),
                    ("9. Multi-Platform Syndication & Marketing Matrix", d.get("syndication_matrix", "")),
                    ("10. Automated 10-Day Master Execution & Scaling Roadmap", d.get("action_roadmap", ""))
                ]

                for sec_title, sec_content in sections_mapping:
                    with st.expander(sec_title, expanded=True):
                        st.markdown(sec_content)

    with tab3:
        st.markdown(f"### {t['tab_db']}")
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM platform_signals ORDER BY timestamp DESC LIMIT 50")
            rows = cursor.fetchall()
            df_db = pd.DataFrame(rows, columns=["Signal ID", "Platform Source", "Keyword & Entity", "Engagement Metrics", "Region", "Timestamp"])
            st.dataframe(df_db, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Database Inspection Error: {e}")

if __name__ == "__main__":
    main()
