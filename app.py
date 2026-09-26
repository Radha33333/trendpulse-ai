import html
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
    initial_sidebar_state="expanded",
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

# Authentication Credentials
USER_CREDENTIALS = {
    "admin": "trendpulse2026",
    "creator": "viral123"
}

# Language Dictionaries
TRANSLATIONS = {
    "English": {
        "title": "TRENDPULSE",
        "subtitle": "Commercial Signal Intelligence | Automated Creator & Merchant Strategy Engine",
        "pro_badge": "🟢 PRO TERMINAL ACTIVE",
        "login_header": "🔐 User Authentication",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "auth_failed": "Invalid Username or Password",
        "region": "🌍 Region:",
        "source": "📱 Source:",
        "niche_cat": "📁 Niche Category:",
        "sub_niche": "🔍 Sub-Niche:",
        "velocity_win": "⏱️ Velocity Window:",
        "telemetry_title": "📊 Signal Telemetry",
        "active_sub_filter": "Active Sub-Niche Filter:",
        "custom_search_label": "🔍 Custom Asset Search:",
        "custom_search_placeholder": "Enter keyword to override...",
        "predictive_title": "📈 Predictive Trajectory",
        "signal_cfg": "🎯 Signal Configuration",
        "target_signal": "Target Signal:",
        "operating_role": "Operating Role:",
        "gen_btn": "⚡ Generate Strategy Blueprint",
        "blueprint_title": "💡 Master Strategy Blueprint",
        "monetization": "💰 Monetization Model",
        "role_directives": "🎬 Role Directives",
        "hook_script": "⚡ 0-3s Visual Hook Script",
        "ad_copy": "📢 Caption & Ad Copy",
        "roadmap": "⏱️ 48-Hour Action Roadmap",
        "competitor": "🕵️ Competitor Benchmarks",
        "prompt_title": "🚀 Ready-to-Use AI Video & Content Production Prompt",
        "download_pdf": "📄 Download Complete PDF Blueprint",
        "select_prompt": "👈 Select a target signal and click 'Generate Strategy Blueprint' to view actionable tactics.",
        "lang_label": "🌐 Language / भाषा:"
    },
    "हिन्दी": {
        "title": "ट्रेंडपल्स",
        "subtitle": "कमर्शियल सिग्नल इंटेलिजेंस | स्वचालित क्रिएटर और मर्चेंट रणनीति इंजन",
        "pro_badge": "🟢 प्रो टर्मिनल सक्रिय",
        "login_header": "🔐 उपयोगकर्ता प्रमाणीकरण",
        "login_btn": "लॉग इन करें",
        "logout_btn": "लॉग आउट करें",
        "auth_failed": "अमान्य उपयोगकर्ता नाम या पासवर्ड",
        "region": "🌍 क्षेत्र:",
        "source": "📱 स्रोत:",
        "niche_cat": "📁 नीश श्रेणी:",
        "sub_niche": "🔍 उप-नीश (Sub-Niche):",
        "velocity_win": "⏱️ गति विंडो (Velocity Window):",
        "telemetry_title": "📊 सिग्नल टेलीमेट्री",
        "active_sub_filter": "सक्रिय उप-नीश फ़िल्टर:",
        "custom_search_label": "🔍 कस्टम एसेट खोज:",
        "custom_search_placeholder": "ओवरराइड करने के लिए कीवर्ड दर्ज करें...",
        "predictive_title": "📈 प्रेडिक्टिव प्रक्षेपवक्र (Trajectory)",
        "signal_cfg": "🎯 सिग्नल कॉन्फ़िगरेशन",
        "target_signal": "लक्ष्य सिग्नल:",
        "operating_role": "ऑपरेटिंग भूमिका:",
        "gen_btn": "⚡ रणनीति खाका तैयार करें",
        "blueprint_title": "💡 मास्टर रणनीति खाका (Strategy Blueprint)",
        "monetization": "💰 मुद्रीकरण मॉडल (Monetization)",
        "role_directives": "🎬 भूमिका निर्देश",
        "hook_script": "⚡ 0-3s विज़ुअल हुक स्क्रिप्ट",
        "ad_copy": "📢 कैप्शन्स और विज्ञापन कॉपी",
        "roadmap": "⏱️ 48-घंटे का एक्शन रोडमैप",
        "competitor": "🕵️ प्रतियोगी बेंचमार्क",
        "prompt_title": "🚀 उपयोग के लिए तैयार AI वीडियो और सामग्री प्रॉम्प्ट",
        "download_pdf": "📄 संपूर्ण PDF ब्लूप्रिंट डाउनलोड करें",
        "select_prompt": "👈 कार्रवाई योग्य रणनीति देखने के लिए एक लक्ष्य सिग्नल चुनें और 'रणनीति खाका तैयार करें' पर क्लिक करें।",
        "lang_label": "🌐 Language / भाषा:"
    }
}

# ==========================================
# 2. INJECT DARK GLASSMORPHISM BENTO CSS
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f17;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(17, 24, 39, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: border-color 0.2s ease;
    }

    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        border-color: rgba(255, 75, 75, 0.3) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #ff4b4b 0%, #d32f2f 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 25px rgba(255, 75, 75, 0.8) !important;
        transform: translateY(-1px);
    }

    .metric-badge {
        background: rgba(255, 75, 75, 0.1);
        border: 1px solid rgba(255, 75, 75, 0.3);
        color: #ff4b4b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. COMPLETE RESTORED CATEGORY ARCHITECTURE
# ==========================================
ALL_NICHE_CATEGORIES = {
    "🛒 E-Commerce & Viral Shopping": [
        "Predicted Bestsellers", "TikTok Shop Products", "Upcoming High-Demand Drops", "Amazon Hot Movers"
    ],
    "💻 Digital Products & AI Tools": [
        "Generative AI Software", "SaaS & Workflows", "Ebooks & Courses", "Templates & Prompts"
    ],
    "✈️ Travel, Hotels & Food": [
        "Trending Destinations", "Hidden Tourist Places", "Restaurants & Stays", "Gourmet Food Shifts"
    ],
    "🏛️ Politics, News & Civic Events": [
        "Elections & Rallies", "Legislative Assembly Debates", "Protests & Policy Changes"
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "Famous Temples", "Hidden & Ancient Temples", "Religious Festivals"
    ],
    "🏋️ Fitness, Health & Wellness": [
        "Home Gym Equipment", "Supplements & Biohacking", "Workout Routines & Apps"
    ],
    "🎮 Gaming & Esports": [
        "Viral Indie Games", "Esports Tournaments", "Gaming Hardware & Gear"
    ],
    "👗 Fashion & Personal Style": [
        "Streetwear Drops", "Sustainable Fashion", "Luxury & Dupes"
    ],
    "💵 Personal Finance & Crypto": [
        "Crypto Trends & Altcoins", "Budgeting Tools", "Investment Strategies"
    ],
    "🚗 Automotive & Mobility": [
        "Electric Vehicles (EVs)", "Car Accessories & Mods", "Commuter Hardware"
    ]
}

SUB_NICHE_SIGNALS_FALLBACK = {
    # E-Commerce
    "Predicted Bestsellers": ["Ergonomic Mechanical Keyboards", "Smart LED Desk Mat", "Self-Cleaning Water Bottles"],
    "TikTok Shop Products": ["Sunset Projection Lamp", "MagSafe Pocket Powerbank", "Viral Lip Oils"],
    "Upcoming High-Demand Drops": ["Thermal Label Printers", "Modular Travel Backpacks", "Portable Mini Espresso Makers"],
    "Amazon Hot Movers": ["Posture Corrector Wearables", "Foldable Electric Scooters", "Air Purifier Desk Fans"],

    # Digital Products
    "Generative AI Software": ["AI Video Rendering Plugins", "Generative Voice Cloning SaaS", "AI Presentation Builders"],
    "SaaS & Workflows": ["Automated Invoicing Integrations", "Micro-SaaS CRM Dashboards", "No-Code Database Sync"],
    "Ebooks & Courses": ["Solopreneur Agency Playbooks", "Prompt Engineering Guides", "Algorithmic Trading Guides"],
    "Templates & Prompts": ["Notion Finance Trackers", "Figma UI Component Systems", "Midjourney Prompt Vaults"],

    # Travel & Food
    "Trending Destinations": ["Varkala Cliff Beach Stays", "Spiti Valley Roadtrip Circuit", "Coorg Eco-Resorts"],
    "Hidden Tourist Places": ["Gokarna Secret Beaches", "Tirthan Valley River Cabins", "Mawlynnong Clean Village"],
    "Restaurants & Stays": ["Cloud Kitchen Burger Collabs", "Heritage Fort Boutique Stays", "Artisanal Coffee Roasteries"],
    "Gourmet Food Shifts": ["Matcha Specialty Cafes", "Korean Street Food Popups", "Plant-Based Protein Snacks"],

    # Politics & News
    "Elections & Rallies": ["Assembly Election Campaigns", "Youth Voter Registration Drives", "Political Rally Live-Streams"],
    "Legislative Assembly Debates": ["Digital Economy Regulation Bills", "Tech Infrastructure Budgets", "Civic Land Usage Acts"],
    "Protests & Policy Changes": ["Gig Worker Welfare Directives", "Environmental Zoning Laws", "Tax Policy Adjustments"],

    # Faith & Sacred Travel
    "Famous Temples": ["Kashi Vishwanath Corridor Travel", "Tirupati Balaji VIP Pilgrimage", "Kedarnath Yatra Packages"],
    "Hidden & Ancient Temples": ["Bhimashankar Forest Temple Trail", "Khajuraho Ancient Architecture", "Lepakshi Hanging Pillar Temple"],
    "Religious Festivals": ["Eco-Friendly Festival Decor", "Handloom Festival Wear", "Spiritual Retreat Bundles"],

    # Fitness
    "Home Gym Equipment": ["Adjustable Smart Dumbbells", "Foldable Walking Pads", "Resistance Band Bar Sets"],
    "Supplements & Biohacking": ["Cold Plunge Tubs", "NMN Longevity Boosters", "Electrolyte Hydration Mixes"],
    "Workout Routines & Apps": ["HYROX Training Manuals", "Calisthenics Skill Trees", "AI Form Correction Apps"],

    # Gaming
    "Viral Indie Games": ["Co-Op Horror Games", "Pixel Art Deckbuilders", "Procedural Survival Simulators"],
    "Esports Tournaments": ["Valorant Regional Finals", "Mobile Legends League", "Counter-Strike Major Qualifiers"],
    "Gaming Hardware & Gear": ["Rapid Trigger Keyboards", "Ultralight Wireless Mice", "OLED Gaming Monitors"],

    # Fashion
    "Streetwear Drops": ["Heavyweight Boxy Tees", "Gorpcore Cargo Pants", "Retro Runner Sneakers"],
    "Sustainable Fashion": ["Thrifted Vintage Jackets", "Bamboo Fiber Wear", "Upcycled Denim Bags"],
    "Luxury & Dupes": ["Minimalist Leather Totes", "Designer Sunglasses Alternatives", "Scent Dupes & Perfume Oils"],

    # Finance
    "Crypto Trends & Altcoins": ["Layer 2 Scaling Networks", "AI Agent Crypto Tokens", "Real World Asset Tokenization"],
    "Budgeting Tools": ["Zero-Based Budget Sheets", "Automated Micro-Investing Apps", "Debt Payoff Trackers"],
    "Investment Strategies": ["High-Yield Savings Hacks", "Index Fund Starter Kits", "Dividend Growth Portfolios"],

    # Automotive
    "Electric Vehicles (EVs)": ["Compact City EVs", "Bidirectional Charging Units", "LFP Battery Retrofits"],
    "Car Accessories & Mods": ["Dashcams with 4K AI Vision", "Custom Ambient LED Lighting", "Wireless CarPlay Adapters"],
    "Commuter Hardware": ["Electric Skateboard Hubs", "E-Bike Cargo Racks", "Smart Helmet Headsets"]
}

CATEGORY_FALLBACK = [
    "Ergonomic Desk Accessories", "Smart Pet Hardware", "Generative AI Workflows", "Micro-SaaS Software"
]

# ==========================================
# 4. AUTHENTICATION SIDEBAR
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    selected_lang = st.selectbox("🌐 Language / भाषा:", ["English", "हिन्दी"])
    t = TRANSLATIONS[selected_lang]

    st.markdown("---")
    if not st.session_state["authenticated"]:
        st.markdown(f"### {t['login_header']}")
        username_input = st.text_input("Username / उपयोगकर्ता नाम")
        password_input = st.text_input("Password / पासवर्ड", type="password")
        if st.button(t["login_btn"], use_container_width=True):
            if USER_CREDENTIALS.get(username_input) == password_input:
                st.session_state["authenticated"] = True
                st.session_state["user"] = username_input
                st.rerun()
            else:
                st.error(t["auth_failed"])
    else:
        st.success(f"Logged in as: **{st.session_state.get('user', 'User')}**")
        if st.button(t["logout_btn"], use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

if not st.session_state["authenticated"]:
    st.title("🔒 TrendPulse AI - Locked Terminal")
    st.info("Please enter your Username and Password in the sidebar to access the terminal.")
    st.stop()

# ==========================================
# 5. HELPER FUNCTIONS & EXPORTER ENGINE
# ==========================================
def sanitize_trend_input(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'\[.*?\]', '', text)
    cleaned = re.sub(r'^\s*n\s+', '', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip()

def create_pdf_blueprint(asset_name, category, sub_niche, role, viral_score, window, result):
    clean_asset = sanitize_trend_input(asset_name)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=18, textColor="#ff4b4b", spaceAfter=12)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=12, textColor="#1a1a1a", spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=9, leading=13, textColor="#333333", spaceAfter=6)
    code_style = ParagraphStyle("CodeStyle", parent=styles["Code"], fontSize=8, leading=11, textColor="#111827", spaceAfter=6)

    def safe_html(text: str) -> str:
        escaped = html.escape(str(text or ""))
        return escaped.replace("\n", "<br/>")

    story = [
        Paragraph("TrendPulse AI - Master Strategy Blueprint", title_style),
        Paragraph(f"<b>Asset:</b> {safe_html(clean_asset)} | <b>Category:</b> {safe_html(category)} | <b>Sub-Niche:</b> {safe_html(sub_niche)}", body_style),
        Paragraph(f"<b>Role:</b> {safe_html(role)} | <b>Predictive Score:</b> {safe_html(viral_score)} | <b>Window:</b> {safe_html(window)}", body_style),
        Spacer(1, 10)
    ]

    sections = [
        ("Monetization Model", result.get("profit_model", "")),
        ("Role Directives", result.get("content_directives", "")),
        ("Execution Hook & Visual Script", result.get("execution_hook", "")),
        ("Caption, CTA & Ad Copy", result.get("ad_copy", "")),
        ("Action Roadmap", result.get("action_blueprint", "")),
        ("Competitor Benchmarks", result.get("competitor_intelligence", "")),
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(safe_html(text), body_style))
        story.append(Spacer(1, 4))

    if result.get("production_prompt"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("AI Video & Content Production Prompt", heading_style))
        story.append(Paragraph(safe_html(result.get("production_prompt")), code_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category, sub_niche, timeframe):
    if sub_niche in SUB_NICHE_SIGNALS_FALLBACK:
        default_keywords = SUB_NICHE_SIGNALS_FALLBACK[sub_niche]
    else:
        default_keywords = CATEGORY_FALLBACK

    raw_signals = []
    url = f"https://trends.google.com/trending/rss?geo={region}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {"ht": "https://trends.google.com/trending/rss"}
            for item in root.findall(".//item")[:2]:
                title = item.find("title")
                traffic = item.find("ht:approx_traffic", ns)
                if title is not None and title.text:
                    raw_signals.append({
                        "Keyword": f"{title.text} [{platform_source}]",
                        "Volume": traffic.text if (traffic is not None and traffic.text) else "100K+ Queries",
                    })
    except Exception:
        pass

    combined = [
        {"Keyword": f"{kw} [{platform_source}]", "Volume": f"150K+ ({timeframe})"}
        for kw in default_keywords
    ]
    for item in raw_signals:
        combined.append({"Keyword": item["Keyword"], "Volume": item["Volume"]})

    return combined[:5]

def generate_master_intelligence(keyword_asset, category, sub_niche, target_role, platform, timeframe, velocity_score, lang="English"):
    clean_asset = sanitize_trend_input(keyword_asset)
    effective_sub_niche = sub_niche if sub_niche != "All Sub-Niches" else category
    tag_keyword = effective_sub_niche.split()[0].upper() if effective_sub_niche else "TREND"

    if lang == "हिन्दी":
        default_response = {
            "viral_score": f"{velocity_score}%",
            "prediction_window": f"सक्रिय जीवनचक्र ({timeframe})",
            "profit_model": f"• **मुख्य मॉडल:** {effective_sub_niche} में {target_role} के लिए रणनीति।\n• **फनल:** लक्षित रूपांतरण फ़नल के माध्यम से '{clean_asset}' के लिए ट्रैफ़िक बदलें।",
            "content_directives": f"• **कोण (Angle):** {target_role} के लिए विशेष {effective_sub_niche} स्थिति।\n• **मुख्य बिंदु:** 1. मांग वृद्धि 2. नीश प्रमाण 3. केंद्रित CTA।",
            "execution_hook": f"• **0-3s संकेत:** विज़ुअल प्रमाण जो '{clean_asset}' को समस्या हल करते हुए दिखाता है।\n• **टेक्स्ट ओवरले:** \"ध्यान दें {effective_sub_niche} खरीदार! इसे देखें...\"",
            "ad_copy": f"{clean_asset} के साथ अपने {effective_sub_niche} सेटअप में क्रांति लाएं! 🚀\n\nविवरण के लिए '{tag_keyword}' कमेंट करें।",
            "action_blueprint": f"1. घंटा 1: मुख्य कोण पहचानें।\n2. घंटा 6: टेस्ट क्रिएटिव लॉन्च करें।\n3. घंटा 48: जुड़ाव के आधार पर अनुकूलित करें।",
            "competitor_intelligence": f"• **फोकस:** शॉर्ट-फॉर्म वीडियो ट्रेंड्स।\n• **अवधि:** 12-20 सेकंड।",
            "production_prompt": f"[सिस्टम भूमिका: वायरल शॉर्ट-फॉर्म वीडियो निदेशक]\n\nउत्पाद: {clean_asset}\nश्रेणी: {category}\nउप-नीश: {effective_sub_niche}\nभूमिका: {target_role}"
        }
    else:
        default_response = {
            "viral_score": f"{velocity_score}%",
            "prediction_window": f"Active Lifecycle ({timeframe})",
            "profit_model": f"• **Primary Model:** Monetization strategy tailored for {target_role} in {effective_sub_niche}.\n• **Funnel:** Convert traffic for '{clean_asset}' via targeted {effective_sub_niche} conversion funnels.",
            "content_directives": f"• **Angle:** Specialized {effective_sub_niche} positioning for {target_role}.\n• **Key Points:** 1. {effective_sub_niche} demand spike 2. Niche proof 3. Focused CTA.\n• **Visuals:** Fast cuts tailored to {effective_sub_niche} audiences.",
            "execution_hook": f"• **0-3s Cue:** Visual proof showing '{clean_asset}' solving a key {effective_sub_niche} problem.\n• **Text Overlay:** \"Attention {effective_sub_niche} buyers! Check this out...\"\n• **Script:** \"If you're into {effective_sub_niche}, here is why {clean_asset} is currently exploding...\"",
            "ad_copy": f"Revolutionize your {effective_sub_niche} setup with {clean_asset}! 🚀\n\nComment '{tag_keyword}' for details.\n\n#{clean_asset.replace(' ', '')} #{effective_sub_niche.replace(' ', '')}",
            "action_blueprint": f"1. HOUR 1: Identify core {effective_sub_niche} angle.\n2. HOUR 6: Launch test creative.\n3. HOUR 48: Optimize based on engagement.",
            "competitor_intelligence": f"• **Focus:** Short-form video trends within {effective_sub_niche}.\n• **Duration:** 12-20 seconds.\n• **Benchmark:** High share-to-view ratio in {category}.",
            "production_prompt": f"""[SYSTEM ROLE: VIRAL SHORT-FORM VIDEO DIRECTOR & UGC AD STRATEGIST]

PRODUCT/ASSET: {clean_asset}
CATEGORY: {category}
SUB-NICHE FOCUS: {effective_sub_niche}
TARGET ROLE: {target_role}
PLATFORM: {platform}

1. VISUAL STORYBOARD & SCRIPT (15s Vertical 9:16)
• 00-03s (Hook): Close-up of {clean_asset} solving a major issue in {effective_sub_niche}. Text Overlay: "Attention {effective_sub_niche}!" | Audio: "If you care about {effective_sub_niche}, stop scrolling."
• 03-08s (Proof): Rapid demonstration of key features for {target_role}. Text Overlay: "Essential for {effective_sub_niche} ✨" | Audio: "This completely transforms how you handle {clean_asset}."
• 08-15s (CTA): Point to screen with call-to-action overlay. Text Overlay: "Comment '{tag_keyword}' for 15% OFF 👇" | Audio: "Comment below or tap the link to claim your access!"

2. AI TEXT-TO-VIDEO GENERATOR PROMPT (Runway / CapCut / Sora)
"A fast-paced 9:16 vertical video featuring {clean_asset} focused on {effective_sub_niche}. Ultra-clean modern setup, 4K resolution, realistic UGC feel, high-contrast visual focus."

3. CAPTION & HASHTAGS
"Level up your {effective_sub_niche} game with {clean_asset}! 🚀 Comment '{tag_keyword}' for instant direct link.\n#{clean_asset.replace(' ', '')} #{effective_sub_niche.replace(' ', '')} #ViralFinds"
"""
        }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Generate a complete JSON strategy blueprint and video production prompt in Language '{lang}' specifically tailored for:
- Asset: "{clean_asset}"
- Category: "{category}"
- Sub-Niche Focus: "{effective_sub_niche}"
- Target Role: "{target_role}"
- Platform: "{platform}"
- Velocity Score: {velocity_score}%

Required JSON Structure:
{{
  "viral_score": "{velocity_score}%",
  "prediction_window": "Active lifecycle",
  "profit_model": "Monetization model explicitly tailored to {effective_sub_niche}",
  "content_directives": "• **Angle:** Specific positioning...\\n• **Key Points:** 1...",
  "execution_hook": "• **0-3s Cue:** ...\\n• **Text:** ...",
  "ad_copy": "Caption and Call to Action",
  "action_blueprint": "1. HOUR 1...\\n2. HOUR 6...",
  "competitor_intelligence": "• **Focus:** ...",
  "production_prompt": "Production prompt text"
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
# 6. HEADER & TOP CONTROL BAR
# ==========================================
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown(f"<h1>⚡ {t['title']} <span style='color:#ff4b4b;'>AI</span></h1>", unsafe_allow_html=True)
    st.caption(t["subtitle"])
with h_col2:
    st.markdown(f"<br><span class='metric-badge'>{t['pro_badge']}</span>", unsafe_allow_html=True)

st.markdown("---")

# Global Filter Bar
with st.container(border=True):
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        geo_option = st.selectbox(t["region"], ["India (IN)", "United States (US)", "United Kingdom (GB)"])
        geo_map = {"India (IN)": "IN", "United States (US)": "US", "United Kingdom (GB)": "GB"}
    with f2:
        platform_source = st.selectbox(t["source"], ["Social Video & Reels", "TikTok Shop", "Search Intent"])
    with f3:
        selected_category = st.selectbox(t["niche_cat"], list(ALL_NICHE_CATEGORIES.keys()))
    with f4:
        sub_options = ALL_NICHE_CATEGORIES.get(selected_category, [])
        selected_sub_niche = st.selectbox(t["sub_niche"], ["All Sub-Niches"] + sub_options)
    with f5:
        timeframe = st.selectbox(t["velocity_win"], ["Realtime Spike (24h)", "Short-Term (7 Days)", "Macro (30 Days)"])

# ==========================================
# 7. HYBRID BENTO DASHBOARD LAYOUT
# ==========================================
left_col, right_col = st.columns([0.42, 0.58], gap="medium")

active_signals = fetch_filtered_radar_signals(geo_map[geo_option], platform_source, selected_category, selected_sub_niche, timeframe)
signal_scores = {item["Keyword"]: round(98.8 - (i * 3.2), 1) for i, item in enumerate(active_signals)}

# --- LEFT COLUMN: TELEMETRY & TRAJECTORY ---
with left_col:
    with st.container(border=True):
        st.markdown(f"### {t['telemetry_title']}")
        st.caption(f"{t['active_sub_filter']} **{selected_sub_niche}**")
        custom_search = st.text_input(t["custom_search_label"], placeholder=t["custom_search_placeholder"])
        
        table_data = [
            {"Signal": item["Keyword"], "Volume": item["Volume"], "Velocity": f"{signal_scores[item['Keyword']]}%"}
            for item in active_signals
        ]
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.markdown(f"### {t['predictive_title']}")
        chart_keyword = custom_search.strip() if custom_search.strip() else (active_signals[0]["Keyword"] if active_signals else "Asset")
        base_score = signal_scores.get(chart_keyword, 92.0)

        days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        velocity_curve = [round(base_score * p, 1) for p in [0.6, 0.72, 0.85, 0.94, 1.0, 1.08, 1.15]]

        fig = px.line(
            pd.DataFrame({"Timeline": days, "Velocity Score": velocity_curve}),
            x="Timeline", y="Velocity Score",
            markers=True, line_shape="spline"
        )
        fig.update_traces(line_color="#ff4b4b", line_width=3, marker_size=7, marker_color="#ffffff")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", height=220, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

# --- RIGHT COLUMN: BENTO STRATEGY ENGINE ---
with right_col:
    with st.container(border=True):
        st.markdown(f"### {t['signal_cfg']}")
        available_keywords = [item["Keyword"] for item in active_signals]
        if custom_search.strip():
            available_keywords.insert(0, custom_search.strip())

        cfg_c1, cfg_c2 = st.columns(2)
        with cfg_c1:
            selected_asset = st.selectbox(t["target_signal"], options=available_keywords, index=0)
        with cfg_c2:
            target_role = st.selectbox(t["operating_role"], ["E-Commerce Merchant / Dropshipper", "Content Creator / Influencer", "Agency Owner / Freelancer"])

        if st.button(t["gen_btn"], use_container_width=True):
            with st.spinner("Analyzing telemetry & generating blueprint..."):
                st.session_state["active_blueprint"] = generate_master_intelligence(
                    selected_asset, selected_category, selected_sub_niche, target_role,
                    platform_source, timeframe, signal_scores.get(selected_asset, 90.0),
                    lang=selected_lang
                )
                st.session_state["active_asset"] = selected_asset
                st.session_state["active_sub_niche"] = selected_sub_niche
                st.session_state["active_role"] = target_role

    bp = st.session_state.get("active_blueprint", {})
    
    with st.container(border=True):
        st.markdown(f"### {t['blueprint_title']}")
        if not bp:
            st.info(t["select_prompt"])
        else:
            b1, b2 = st.columns(2)
            with b1:
                st.markdown(f"#### {t['monetization']}")
                st.markdown(bp.get("profit_model", ""))
            with b2:
                st.markdown(f"#### {t['role_directives']}")
                st.markdown(bp.get("content_directives", ""))

            st.markdown("---")

            b3, b4 = st.columns(2)
            with b3:
                st.markdown(f"#### {t['hook_script']}")
                st.markdown(bp.get("execution_hook", ""))
            with b4:
                st.markdown(f"#### {t['ad_copy']}")
                st.code(bp.get("ad_copy", ""), language="markdown")

            st.markdown("---")

            b5, b6 = st.columns(2)
            with b5:
                st.markdown(f"#### {t['roadmap']}")
                st.markdown(bp.get("action_blueprint", ""))
            with b6:
                st.markdown(f"#### {t['competitor']}")
                st.markdown(bp.get("competitor_intelligence", ""))

            st.markdown("---")

            st.markdown(f"#### {t['prompt_title']}")
            st.code(bp.get("production_prompt", ""), language="text")

            st.markdown("---")

            pdf_buf = create_pdf_blueprint(
                st.session_state.get("active_asset", selected_asset),
                selected_category, st.session_state.get("active_sub_niche", selected_sub_niche),
                st.session_state.get("active_role", target_role),
                bp.get("viral_score", "90%"), bp.get("prediction_window", timeframe), bp
            )
            st.download_button(t["download_pdf"], data=pdf_buf, file_name="TrendPulse_Blueprint.pdf", mime="application/pdf", use_container_width=True)
