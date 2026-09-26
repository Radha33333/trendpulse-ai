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
    page_title="TrendPulse AI - Enterprise Intelligence & Execution Suite",
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

TEXTS = {
    "English": {
        "title": "⚡ TrendPulse AI: Enterprise Intelligence & Execution Suite",
        "subtitle": "Autonomous Market Domination Engine & Advanced Dossier Generator",
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
        "tab_blueprint": "🚀 Enterprise Dossier & 3-Tab Execution",
        "tab_db": "🗄️ Database Inspector & Logs",
    },
    "Hindi": {
        "title": "⚡ TrendPulse AI: एंटरप्राइज इंटेलिजेंस और एग्जीक्यूशन सुइट",
        "subtitle": "ऑटोनॉमस मार्केट डोमिनेशन इंजन और एडवांस डॉसियर जेनरेटर",
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
        "tab_blueprint": "🚀 एंटरप्राइज डॉसियर और 3-टैब एग्जीक्यूशन",
        "tab_db": "🗄️ डेटाबेस इंस्पेक्टर और लॉग्स",
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

def create_pdf_dossier(asset_name, category, role, viral_score, window, result):
    clean_asset = sanitize_trend_input(asset_name)
    clean_cat = sanitize_trend_input(category)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=16, textColor="#ff4b4b", spaceAfter=10)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=11, textColor="#1a1a1a", spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=8.5, leading=12, textColor="#333333", spaceAfter=6)

    story = [
        Paragraph("TrendPulse AI - Enterprise Commercial Intelligence Dossier", title_style),
        Paragraph(f"<b>Asset:</b> {safe_xml_text(clean_asset)} | <b>Category:</b> {safe_xml_text(clean_cat)} | <b>Role:</b> {safe_xml_text(role)}", body_style),
        Paragraph(f"<b>Predictive Viral Score:</b> {safe_xml_text(str(viral_score))} | <b>Window:</b> {safe_xml_text(str(window))}", body_style),
        Spacer(1, 8)
    ]

    sections = [
        ("Financial Unit Economics", result.get("unit_economics", "")),
        ("Omnichannel Direct Execution Assets", result.get("tab1_direct", "")),
        ("Advanced Creator & Engineer Prompts", result.get("tab2_prompts", "")),
        ("Competitor Intelligence & Benchmarks", result.get("tab3_competitor", "")),
        ("Automated 7-Day Action Roadmap", result.get("action_roadmap", "")),
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(safe_xml_text(text), body_style))
        story.append(Spacer(1, 3))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 5. PIPELINE & RADAR DATA ENGINE
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
# 6. ENTERPRISE LLM INTELLIGENCE GENERATOR
# ==========================================
def generate_enterprise_dossier(keyword_asset, category, sub_niche, target_role, platform, timeframe, velocity_score, lang):
    clean_asset = sanitize_trend_input(keyword_asset)
    clean_cat = sanitize_trend_input(category)
    clean_sub = sanitize_trend_input(sub_niche)
    sub_ctx = f" focusing on '{clean_sub}'" if clean_sub and clean_sub != "All Sub-Niches" else ""

    default_response = {
        "viral_score": f"{velocity_score}%",
        "prediction_window": f"Active Timing Window ({timeframe})",
        "unit_economics": "• **Estimated Sourcing Cost:** $4.50 per unit\n• **Suggested Retail Price (SRP):** $29.99\n• **Gross Profit Margin:** 85.0%\n• **Break-Even ROAS Threshold:** 1.5x (Profitable scale starts above 2.2x ROAS)",
        "tab1_direct": f"• **Visual Hook (0-3s):** Dynamic split-screen introducing {clean_asset} with rapid pattern-interrupt motion.\n• **Script Voiceover:** \"Stop using outdated solutions in 2026. Here is why top operators in {clean_cat} are scaling {clean_asset[:25]} instantly...\"\n• **Hashtags:** #{clean_asset.replace(' ', '')} #ViralDrop2026 #D2CScaling #TrendPulse\n• **Ad Copy (Meta):** \"The ultimate secret behind {clean_asset} is finally accessible. High performance, premium quality. Tap below to claim inventory!\"",
        "tab2_prompts": f"• **Midjourney v6.0 Prompt:** Hyper-realistic studio product photography of {clean_asset}, minimalist luxury packaging, clean ambient lighting, cinematic 8k resolution, commercial advertising style --ar 16:9 --v 6.0\n• **Claude / Cursor Prompt:** Act as a Senior E-Commerce Growth Engineer. Write a Python script using async requests to monitor daily stock velocity and price shifts for {clean_cat}.",
        "tab3_competitor": "• **Competitor Ad Spend Tier:** Medium-High ($1,500 - $4,000/day active spend).\n• **Estimated CPA:** $12.50\n• **Performance Benchmark:** Top 5% CTR via UGC-style unboxing hooks.",
        "action_roadmap": "1. HOUR 1-6: Sourcing setup, private-label packaging confirmation, & landing page optimization.\n2. HOUR 24: Launch micro-testing cross-channel ad campaign with $50/day budget.\n3. DAY 3: Scale winning ad sets by 50% & kill underperforming creatives.\n4. DAY 7: Deploy retargeting upsell funnel to boost Average Order Value (AOV)."
    }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Return ONLY a raw valid JSON object (no markdown, no backticks).
Analyze:
Asset: "{clean_asset}"
Category: "{clean_cat}"
Sub-Niche: "{clean_sub}"
Role: "{target_role}"
Platform: "{platform}"
Language: {lang}

JSON Format:
{{
  "viral_score": "{velocity_score}%",
  "prediction_window": "Lifecycle timing window",
  "unit_economics": "• **Sourcing Cost:** ...\\n• **SRP:** ...\\n• **Margin:** ...\\n• **Break-even ROAS:** ...",
  "tab1_direct": "• **Visual Hook:** ...\\n• **Script:** ...\\n• **Hashtags:** ...\\n• **Ad Copy:** ...",
  "tab2_prompts": "• **Midjourney Prompt:** ...\\n• **Cursor Prompt:** ...",
  "tab3_competitor": "• **Ad Spend Tier:** ...\\n• **CPA:** ...\\n• **Benchmark:** ...",
  "action_roadmap": "1. HOUR 1-6: ...\\n2. HOUR 24: ...\\n3. DAY 3: ...\\n4. DAY 7: ..."
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
# 7. MAIN UI LAYOUT & BACKEND INSPECTOR
# ==========================================
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

head_col1, head_col2 = st.columns([3, 1])
with head_col2:
    selected_lang = st.selectbox("🌐 Language / भाषा:", ["English", "Hindi"], index=0)

t = TEXTS[selected_lang]

with head_col1:
    st.title(t["title"])
    st.caption(f"{t['subtitle']} | ⚡ Autonomous Pipeline & Enterprise DB Architecture")

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
    st.subheader("💡 Enterprise Commercial Intelligence Dossier")

    if not st.session_state["is_premium"]:
        st.warning("🔒 MULTI-CHANNEL ENTERPRISE DOSSIER IS LOCKED")
        st.info("Unlock financial unit economics, omnichannel ad suites, competitor ad intelligence, and automated action roadmaps.")
        st.link_button("🔥 Upgrade to Pro & Unlock Full Enterprise Engine", STRIPE_CHECKOUT_URL, use_container_width=True)
    else:
        st.success("🔓 ENTERPRISE PRO ENGINE ACTIVE")

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

        gen_btn = st.button("⚡ Generate Enterprise Dossier", use_container_width=True)

        if gen_btn or "enterprise_result" in st.session_state:
            curr_score = signal_scores.get(selected_asset, 95.0)
            if gen_btn:
                with st.spinner("Synthesizing Cross-Platform Intelligence & Financial Unit Economics..."):
                    result = generate_enterprise_dossier(
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
            st.markdown("### 💰 Financial Unit Economics & Profitability Calculator")
            st.markdown(result.get("unit_economics", ""))

            st.markdown("---")
            st.markdown("### 🚀 Omnichannel 3-Tab Execution Engine")
            
            tab1_d, tab2_p, tab3_c = st.tabs([
                "📌 TAB 1: DIRECT EXECUTION",
                "💡 TAB 2: AI PROMPTS",
                "🕵️ TAB 3: COMPETITOR INTEL"
            ])

            with tab1_d:
                st.markdown("#### Ready-to-Use Assets & Ad Copy")
                st.markdown(result.get("tab1_direct", ""))

            with tab2_p:
                st.markdown("#### Advanced Creator & Engineer Prompt Packs")
                st.markdown(result.get("tab2_prompts", ""))

            with tab3_c:
                st.markdown("#### Competitor Ad Intelligence & Benchmarks")
                st.markdown(result.get("tab3_competitor", ""))

            st.markdown("---")
            st.markdown("### ⏱️ Automated 7-Day Action Roadmap")
            st.text(result.get("action_roadmap", ""))

            st.markdown("---")
            pdf_bytes = create_pdf_dossier(selected_asset, selected_category, target_role, curr_score, timeframe, result)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📄 Download Enterprise PDF Dossier",
                    data=pdf_bytes,
                    file_name=f"TrendPulse_Enterprise_Dossier_{sanitize_trend_input(selected_asset)[:15]}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            with d_col2:
                wa_text = urllib.parse.quote(
                    f"⚡ *TrendPulse AI Enterprise Dossier*\n\n"
                    f"Asset: {sanitize_trend_input(selected_asset)}\n"
                    f"Category: {sanitize_trend_input(selected_category)}\n"
                    f"Viral Score: {curr_score}%\n\n"
                    f"View full intelligence report!"
                )
                st.link_button(
                    label="💬 Share to WhatsApp",
                    url=f"https://wa.me/?text={wa_text}",
                    use_container_width=True,
                )

with tab_db:
    st.subheader("🗄️ Database Inspector & Pipeline Logs")
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
