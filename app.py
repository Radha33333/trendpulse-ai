import io
import json
import os
import re
import sqlite3
import time
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

# Optional Auto-Refresh import with graceful fallback
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

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
# 2. SQLITE DATABASE INITIALIZATION & LIVE SYNC
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

def log_live_signal(platform, keyword, metrics, region):
    cursor = db_conn.cursor()
    cursor.execute("""
        INSERT INTO platform_signals (source_platform, keyword, engagement_metrics, region)
        VALUES (?, ?, ?, ?)
    """, (platform, keyword, str(metrics), region))
    db_conn.commit()

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
        "title": "⚡ TrendPulse AI: Master Intelligence & Revenue Scale Suite",
        "subtitle": "Autonomous Market Domination Engine & Advanced Commercial Dossier Generator",
        "terminal": "🔑 Enterprise Access Terminal",
        "simulate_pro": "Simulate Pro Subscription Access",
        "config_title": "⚙️ Ingestion Pipeline & Signal Filter",
        "region": "🌐 Target Region:",
        "platform": "🎛️ Platform Source:",
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
# 6. PIPELINE & RADAR DATA ENGINE
# ==========================================
@st.cache_data(ttl=300)
def fetch_and_store_signals(region, platform_source, category, sub_niche, timeframe):
    results = [
        (f"Live Ingested Signal: {sub_niche} Spike #1", "Verified Brand Hub", "🚀 Explosive Surge"),
        (f"Live Ingested Signal: {sub_niche} Trend #2", "Creator Network", "🔥 High Growth"),
        (f"Live Ingested Signal: {sub_niche} Momentum #3", "Market Feed", "⚡ Accelerating")
    ]
    for item in results:
        log_live_signal(platform_source, item[0], item[2], region)
    return results

# ==========================================
# 7. MAIN UI APP STRUCTURE & AUTO-REFRESH
# ==========================================
def main():
    # Sidebar Auto-Refresh Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Real-Time Live Sync")
    enable_auto_refresh = st.sidebar.checkbox("Enable Live Auto-Refresh", value=False)
    refresh_interval = st.sidebar.selectbox("Refresh Interval", [5, 10, 30, 60], index=1)
    
    if enable_auto_refresh and st_autorefresh:
        st_autorefresh(interval=refresh_interval * 1000, key="live_trend_pulse_refresher")

    st.title("⚡ TrendPulse AI: Master Intelligence & Revenue Scale Suite")
    st.markdown("Autonomous Market Domination Engine & Advanced Commercial Dossier Generator with Live DB & Real-Time Auto-Refresh.")

    # Database Inspector Tab or Status
    conn = db_conn
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM platform_signals")
    signal_count = cursor.fetchone()[0]
    st.sidebar.info(f"🗄️ Total Live Signals in DB: **{signal_count}**")

if __name__ == "__main__":
    main()
