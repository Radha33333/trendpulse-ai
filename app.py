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

# API Key fallback check (Supports Streamlit secrets or OS Environment Variable)
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

CATEGORY_SIGNALS_FALLBACK = {
    "🛒 E-Commerce & Viral Shopping": [
        "Next-Gen Ergonomic Desk Accessories",
        "Smart Pet Grooming Hardware",
        "Self-Cleaning Water Bottles",
        "Aesthetic MagSafe Powerbanks",
    ],
    "🏛️ Politics, News & Civic Events": [
        "Assembly Election Rallies & Turnout",
        "Parliament Digital Economy Policy Debates",
        "State Infrastructure Bill & Public Protests",
        "Civic Reform & Election Key Speeches",
    ],
    "🛕 Faith, Festivals & Sacred Travel": [
        "Unexplored Ancient Temples Circuit Travel",
        "Upcoming Festival Handicrafts & Festive Decor",
        "Pilgrimage Eco-Resorts & VIP Pass Trends",
        "Historic Temple Heritage Restoration",
    ],
    "✈️ Travel, Hotels & Food": [
        "Hidden Hill Station Stays & Eco-Resorts",
        "Regional Non-Veg Fusion Food Spots",
        "Fine Dining Cloud Kitchen Collaborations",
        "Offbeat Coastal Escapes & Stays",
    ],
    "🌟 Celebrities & Sports Stars": [
        "World Cup Squad Announcements & Fan Buzz",
        "OTT Blockbuster Movie Trailer Drops",
        "Athlete Fitness Routines & Brand Endorsements",
        "Viral Pop Culture Influencer Moments",
    ],
    "🏢 Real Estate & High-Ticket Props": [
        "High Yield Tier-2 City Commercial Hubs",
        "AI-Integrated PropTech Smart Homes",
        "Luxury Gated Communities & Villas",
        "Co-Living & Flexible Work Spaces",
    ],
    "💄 Beauty, Skincare & Lifestyle": [
        "Micro-Needling & Anti-Aging At-Home Devices",
        "Korean Glass-Skin Serum UGC Campaigns",
        "Sustainable Organic Linen Capsule Wardrobe",
        "Clean Eco-Friendly Cosmetics",
    ],
    "💻 Digital Products & AI Tools": [
        "Automated AI Workflow & Prompt Libraries",
        "Micro-SaaS Invoicing & Booking Plugins",
        "Digital Notion Planners & Finance Dashboards",
        "Generative Video Editing Extensions",
    ],
}

# DYNAMIC SUB-NICHE SIGNAL MAPPER
SUBNICHE_SIGNALS_FALLBACK = {
    # 🛒 E-Commerce & Viral Shopping
    "Predicted Bestsellers": ["Ergonomic Desk Accessories", "Self-Cleaning Water Bottles", "MagSafe Powerbanks", "Aesthetic Desk Lamp"],
    "TikTok Shop Products": ["Viral Sunset Lamp", "Micro-Needling Patch", "Aesthetic Ice Roller", "Heatless Hair Curler"],
    "Upcoming High-Demand Drops": ["Limited Edition Sneakers", "Modular Travel Backpacks", "Smart Ring Fitness Tracker"],
    "Amazon Hot Movers": ["Portable Espresso Maker", "Smart Cable Organizer", "Mini Thermal Label Printer"],
    "D2C Breakout Brands": ["Organic Matcha Blends", "Zero-Waste Toothpaste Bits", "Bamboo Fiber Apparel"],
    "Problem-Solver Gadgets": ["Anti-Spill Pet Bowl", "Sonic Jewelry Cleaner", "Electric Jar Opener"],

    # 🏛️ Politics, News & Civic Events
    "Elections & Rallies": ["Assembly Election Turnout", "Campaign Speech Highlights", "Voter Registration Drives"],
    "Legislative Assembly & Sabha Debates": ["Digital Privacy Bill Debates", "Tax Reform Proposals", "Public Infrastructure Budget"],
    "Protests & Policy Changes": ["Labor Law Policy Adjustments", "Agrarian Policy Protests", "Urban Transport Reform"],
    "Politician Speeches": ["Keynote Economy Address", "Townhall Press Briefing", "National Security Statement"],
    "Geopolitical Updates": ["Cross-Border Trade Treaties", "Global Summit Agreements", "Maritime Corridor Deals"],
    "Public Schemes & Subsidies": ["Green Energy Subsidies", "Small Business Housing Grants", "Student Loan Waiver Policy"],

    # 🛕 Faith, Festivals & Sacred Travel
    "Famous Temples": ["VIP Darshan Slot Booking", "Temple Corridor Expansion", "Heritage Sanctum Restoration"],
    "Hidden & Ancient Temples": ["Unexplored Cave Temple Circuit", "10th Century Rock Sculptures", "Secret Forest Shrines"],
    "Religious Festivals": ["Festive Eco-Diya Handicrafts", "Procession Route Guidelines", "Seasonal Ritual Offerings"],
    "Pilgrimage Circuits": ["Char Dham Yatra Bus Pass", "High-Altitude Trek Passes", "Spiritual River Trail Stays"],
    "Festive Gifting Trends": ["Handcrafted Brass Puja Thalis", "Organic Sweet Hampers", "Silver Idol Gift Sets"],
    "Spiritual Wellness Drops": ["Aromatherapy Incense Blends", "Sandalwood Mala Beads", "Copper Water Vessels"],

    # ✈️ Travel, Hotels & Food
    "Trending Destinations": ["Offbeat Hill Stations", "Coastal Secret Escapes", "High-Altitude Glamping"],
    "Hidden Tourist Places": ["Unmapped Waterfall Hikes", "Heritage Fort Villages", "Secluded Island Stays"],
    "Restaurants & Stays": ["Boutique Eco-Resorts", "Rooftop Experiential Dining", "Farm-to-Table Homestays"],
    "Veg & Non-Veg Gourmet": ["Regional Smoked Meat Fusion", "Artisanal Sourdough Outlets", "Traditional Clay-Pot Curries"],
    "Street Food Surges": ["Night Market Food Trails", "Fusion Cheese Street Snacks", "Authentic Local Breakfast Stalls"],
    "Budget & Backpacker Escapes": ["Hostel Co-Working Spaces", "Budget Overnight Trains", "Free Walking Tour Trails"],

    # 🌟 Celebrities & Sports Stars
    "Cricket & Sports Idols": ["World Cup Squad Announcements", "Player Fitness Routines", "Franchise Auction Buzz"],
    "Movie & OTT Stars": ["Blockbuster Teaser Drop", "Celebrity Red Carpet Outfits", "Exclusive OTT Series Leaks"],
    "Viral Influencers": ["Trend Challenge Breakouts", "Podcast Interview Clips", "Creator Brand Collabs"],
    "Tournament Buzz": ["Playoff Final Tickets", "Underdog Team Comebacks", "Stadium Fan Zone Activations"],
    "Celebrity Fashion Outfits": ["Airport Style Lookbooks", "Vintage Met Gala Recreations", "Streetwear Capsule Drops"],
    "Pop Culture Controversies": ["Award Show Feuds", "Viral Interview Debates", "Social Media Account Audits"],

    # 🏢 Real Estate & High-Ticket Props
    "Rental Yield Hotspots": ["IT Hub Studio Apartments", "University Corridor Housing", "Tier-2 Metro Outskirts"],
    "PropTech & Smart Homes": ["Automated Keyless Locks", "AI Energy Efficiency Systems", "Smart Solar Roofing"],
    "Luxury Estates": ["Oceanfront Gated Villas", "Penthouse Sky Mansions", "Private Golf Course Residences"],
    "Commercial Spaces": ["Co-Working Plug & Play Hubs", "High-Street Retail Outlets", "Logistics Micro-Warehouses"],
    "Vacation Homes & Villas": ["Hill Station Wooden Chalets", "Poolside Countryside Homestays", "Off-Grid Eco Cabins"],
    "Upcoming Transit Hubs": ["Metro Extension Corridor Plots", "Expressway Junction Warehouses", "Airport Adjacent Townships"],

    # 💄 Beauty, Skincare & Lifestyle
    "UGC Skincare Hacks": ["Korean Glass Skin Routine", "Ice Facial Sculpting", "Rice Water Hair Rinses"],
    "Clean Beauty Products": ["Sulfate-Free Botanical Serums", "Refillable Lip Tints", "Vegan Sunscreen Sticks"],
    "Anti-Aging Devices": ["LED Light Therapy Masks", "Micro-Current Facial Toners", "Thermal Eye Wand Sculptors"],
    "Sustainable Fashion": ["Upcycled Denim Jackets", "Organic Linen Shirts", "Thrifted Vintage Outfits"],
    "Haircare Treatment Trends": ["Scalp Exfoliation Scrubs", "Rosemary Hair Growth Oils", "Bond Repairing Masks"],
    "Minimalist Capsule Wardrobes": ["Neutral Blazer Essentials", "Tailored Wide-Leg Trousers", "Monochrome Streetwear"],

    # 💻 Digital Products & AI Tools
    "Generative AI Software": ["Text-to-Video Generators", "AI Voice Cloning Plugins", "Code Refactoring Copilots"],
    "SaaS & Workflows": ["Automated Invoicing Plugins", "Micro-SaaS CRM Dashboards", "All-in-One Booking Engines"],
    "Ebooks & Courses": ["Solopreneur Playbook Guides", "No-Code Masterclasses", "Algorithmic Trading Guides"],
    "Templates & Prompts": ["Notion Finance Trackers", "Midjourney Architecture Prompts", "Figma UI Design Kits"],
    "Automation Micro-Tools": ["Zapier Email Webhooks", "Social Media Auto-Responders", "Web Scraping Extensions"],
    "No-Code App Builders": ["Drag-and-Drop Marketplace Builders", "PWA Web App Frameworks", "Database Portals"],
}

# ==========================================
# 3. TRANSLATIONS / LOCALIZATION
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
        "analyzing_custom": "Analyzing Signal Potential for:",
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
        "analyzing_custom": "सिग्नल क्षमता का विश्लेषण:",
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
    """Escapes XML elements and converts basic Markdown bold into ReportLab tags."""
    if not text:
        return ""
    clean = (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean)
    return clean

def sanitize_trend_input(text: str) -> str:
    """Strips system tags, bracketed metadata, and formatting artifacts."""
    if not text:
        return ""
    cleaned = re.sub(r'\[.*?\]', '', text)
    cleaned = re.sub(r'^\s*n\s+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def create_pdf_blueprint(asset_name, category, role, viral_score, window, result):
    clean_asset = sanitize_trend_input(asset_name)
    clean_cat = sanitize_trend_input(category)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor="#ff4b4b",
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor="#1a1a1a",
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor="#333333",
        spaceAfter=8,
    )

    story = []
    story.append(Paragraph("TrendPulse AI - Master Strategy Blueprint", title_style))
    story.append(
        Paragraph(
            f"<b>Asset:</b> {safe_xml_text(clean_asset)} | <b>Category:</b> {safe_xml_text(clean_cat)} | <b>Role:</b> {safe_xml_text(role)}",
            body_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Predictive Viral Score:</b> {safe_xml_text(str(viral_score))} | <b>Monetization Window:</b> {safe_xml_text(str(window))}",
            body_style,
        )
    )
    story.append(Spacer(1, 10))

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
# 5. DATA FETCHING & RSS RADAR PIPELINE
# ==========================================
@st.cache_data(ttl=300)
def fetch_filtered_radar_signals(region, platform_source, category, sub_niche, timeframe):
    url = f"https://trends.google.com/trending/rss?geo={region}"
    raw_signals = []

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {"ht": "https://trends.google.com/trending/rss"}
            for item in root.findall(".//item"):
                title = item.find("title")
                traffic = item.find("ht:approx_traffic", ns)
                if title is not None and title.text:
                    raw_signals.append({
                        "Keyword": f"{title.text} ({platform_source})",
                        "Volume": (
                            traffic.text
                            if (traffic is not None and traffic.text)
                            else "100K+ Queries"
                        ),
                    })
    except Exception:
        pass

    # Sub-Niche Specific RSS Filtering
    if sub_niche and sub_niche != "All Sub-Niches":
        sub_words = [w.lower() for w in sub_niche.split() if len(w) > 2]
        matched_rss = [
            item for item in raw_signals 
            if any(word in item["Keyword"].lower() for word in sub_words)
        ]
        if matched_rss:
            raw_signals = matched_rss

    # Target Sub-Niche Keyword Resolution
    if sub_niche in SUBNICHE_SIGNALS_FALLBACK:
        default_keywords = SUBNICHE_SIGNALS_FALLBACK[sub_niche]
    else:
        default_keywords = CATEGORY_SIGNALS_FALLBACK.get(category, ["Trending Breakout Asset"])

    if sub_niche and sub_niche != "All Sub-Niches":
        combined = [
            {"Keyword": f"[{sub_niche}] {kw} [{platform_source}]", "Volume": f"180K+ ({timeframe})"}
            for kw in default_keywords
        ]
    else:
        combined = [
            {"Keyword": f"{kw} [{platform_source}]", "Volume": f"150K+ ({timeframe})"}
            for kw in default_keywords
        ]

    for item in raw_signals[:2]:
        combined.append(
            {"Keyword": item["Keyword"], "Volume": item["Volume"]}
        )

    return combined[:5]

# ==========================================
# 6. GROQ LLM BLUEPRINT GENERATOR
# ==========================================
def generate_master_intelligence(
    keyword_asset,
    category,
    sub_niche,
    target_role,
    platform,
    timeframe,
    velocity_score,
    lang,
):
    clean_asset = sanitize_trend_input(keyword_asset)
    clean_cat = sanitize_trend_input(category)
    clean_sub = sanitize_trend_input(sub_niche)

    sub_context_str = f" strictly targeting the '{clean_sub}' sub-niche under '{clean_cat}'" if clean_sub and clean_sub != "All Sub-Niches" else f" in '{clean_cat}'"

    # Dynamic Fallback Templates
    if target_role == "Agency Owner / Freelancer":
        default_response = {
            "viral_score": f"{velocity_score}%",
            "prediction_window": f"Active Viral Lifecycle Window ({timeframe})",
            "profit_model": (
                f"• **Primary Funnel:** B2B High-Ticket Client Acquisition & White-Label Audits{sub_context_str}.\n"
                f"• **Execution Path:** Package '{clean_asset}' insights into a $2,500/mo trend-jacking retainer deck for brands operating in '{clean_sub if clean_sub else clean_cat}'."
            ),
            "content_directives": (
                f"• **Narrative Angle / Thesis:** Explaining how businesses in '{clean_sub if clean_sub else clean_cat}' can turn demand around '{clean_asset}' into predictable revenue.\n"
                f"• **Key Talking Points:**\n"
                f"  1. The missed ROI opportunity most brands ignore regarding {clean_asset}.\n"
                f"  2. Step-by-step breakdown of the sub-niche client campaign workflow.\n"
                f"  3. Expected CAC reduction and conversion metrics.\n"
                f"• **Visual & B-Roll Assets:** LinkedIn PDF slide overlays, ROI spreadsheets, screen recordings of campaign setups.\n"
                f"• **Category Guardrails:** Keep communication professional, metric-driven, and focused on business bottom-line growth."
            ),
            "execution_hook": (
                f"• **0-3s Visual Cue:** Screen recording of client dashboard showing traffic spikes overlaying '{clean_asset}'.\n"
                f"• **Text Overlay:** \"How to turn {clean_asset[:20]} into $10k in client retainers...\"\n"
                f"• **Spoken Script:** \"If you run an agency or consult brands in {clean_sub if clean_sub else clean_cat}, here is the exact framework we're using to turn {clean_asset} into high-converting client campaigns this week...\""
            ),
            "audio_suggestion": "Low-fi Instrumental Chill / Professional Corporate Narrative Background",
            "ad_copy": (
                f"We just published our B2B Strategy Briefing on capitalizing on {clean_asset} ({clean_sub if clean_sub else clean_cat}). 💼\n\n"
                "Comment 'AGENCY' below to get our complete pitch deck and client outreach templates sent directly to your DMs!\n\n"
                f"#{clean_asset.replace(' ', '')} #AgencyGrowth #B2BStrategy #TrendPulse"
            ),
            "action_blueprint": (
                "1. HOUR 1: Turn this trend data into a 5-page PDF Strategy Audit deck.\n"
                "2. HOUR 6: Launch cold email & LinkedIn video pitches targeting brand CMOs using the framework.\n"
                "3. DAY 2: Set up automated discovery call calendars for incoming DM leads."
            ),
            "competitor_intelligence": (
                f"• **Top Competitor Hook Style:** *'How agencies are scaling with {clean_asset}...'*\n"
                "• **Optimal Video Duration:** 45 - 60 seconds (LinkedIn/YouTube Shorts)\n"
                "• **Estimated Engagement Benchmark:** 8.4% Lead Conversion Rate on DMs"
            ),
        }
    elif target_role == "E-Commerce Merchant / Dropshipper":
        default_response = {
            "viral_score": f"{velocity_score}%",
            "prediction_window": f"Active Viral Lifecycle Window ({timeframe})",
            "profit_model": (
                f"• **Primary Funnel:** Direct-to-Consumer Impulse Sales & Flash Offer Drops{sub_context_str}.\n"
                f"• **Execution Path:** Source or bundle product inventory related to '{clean_asset}' and leverage TikTok Shop / Reels ad spark posts."
            ),
            "content_directives": (
                f"• **Narrative Angle / Thesis:** Highlighting problem-solution angles and immediate transformation tied to {clean_asset} in the {clean_sub if clean_sub else clean_cat} market.\n"
                f"• **Key Talking Points:**\n"
                f"  1. Main buyer pain point before discovering this sub-niche asset.\n"
                f"  2. Live product unboxing / stress-test demonstration.\n"
                f"  3. Scarcity & limited stock warning.\n"
                f"• **Visual & B-Roll Assets:** Close-up macro product shots, rapid 0.5x reaction cuts, fast unboxing, aesthetic lifestyle usage.\n"
                f"• **Category Guardrails:** Emphasize fast shipping, high visual contrast, and immediate impulse buy triggers."
            ),
            "execution_hook": (
                f"• **0-3s Visual Cue:** Rapid hands-on product demonstration with price tag flash overlay for '{clean_asset}'.\n"
                f"• **Text Overlay:** \"Stop scrolling! This {clean_asset[:20]} sold out 3x this week 🚨\"\n"
                f"• **Spoken Script:** \"If you've been looking for {clean_asset}, stop buying cheap knockoffs. Here is why everyone in {clean_sub if clean_sub else clean_cat} is ordering this exact one...\""
            ),
            "audio_suggestion": "Upbeat Phonk / Trending TikTok Sound Effect Accent",
            "ad_copy": (
                f"The demand for {clean_asset} is breaking the internet! 🛒\n\n"
                "Tap the 'Shop Now' button or click the link in bio to claim 20% OFF before our flash stock runs out!\n\n"
                f"#{clean_asset.replace(' ', '')} #TikTokMadeMeBuyIt #EcomTrends #TrendPulse"
            ),
            "action_blueprint": (
                "1. HOUR 1: Create a high-converting single-product landing page or TikTok Shop listing.\n"
                "2. HOUR 6: Launch 3 user-generated video ad variants targeting broad interest stacks.\n"
                "3. DAY 2: Scale ad spend on winning creative and trigger cart abandonment emails."
            ),
            "competitor_intelligence": (
                f"• **Top Competitor Hook Style:** *'Why everyone is obsessed with {clean_asset}...'*\n"
                "• **Optimal Video Duration:** 9 - 15 seconds\n"
                "• **Estimated Engagement Benchmark:** High (4.8% Direct Purchase CTR)"
            ),
        }
    else:  # Content Creator / Influencer
        default_response = {
            "viral_score": f"{velocity_score}%",
            "prediction_window": f"Active Viral Lifecycle Window ({timeframe})",
            "profit_model": (
                f"• **Primary Funnel:** Organic Viral Reach, Follower Growth & ManyChat DM Automation{sub_context_str}.\n"
                f"• **Execution Path:** Use pattern-interrupt commentary on '{clean_asset}' to drive thousands of keyword comments and grow audience loyalty."
            ),
            "content_directives": (
                f"• **Narrative Angle / Thesis:** Delivering a unique hot-take or deep-dive breakdown behind '{clean_asset}' in '{clean_sub if clean_sub else clean_cat}' that nobody else is mentioning.\n"
                f"• **Key Talking Points:**\n"
                f"  1. What everyone gets wrong about this topic.\n"
                f"  2. The hidden detail or story behind the sub-niche trend.\n"
                f"  3. Open-ended controversial question to spark debate.\n"
                f"• **Visual & B-Roll Assets:** Face-cam with green screen background, fast cutaways, dramatic text pop-ups, meme overlays.\n"
                f"• **Category Guardrails:** Maximize retention, avoid corporate jargon, focus on entertainment and curiosity."
            ),
            "execution_hook": (
                f"• **0-3s Visual Cue:** Green-screen reaction in front of a trending headline about '{clean_asset}'.\n"
                f"• **Text Overlay:** \"Nobody is talking about this detail... 😳\"\n"
                f"• **Spoken Script:** \"Everyone is posting about {clean_asset}, but almost nobody in {clean_sub if clean_sub else clean_cat} noticed what actually happened behind the scenes...\""
            ),
            "audio_suggestion": "Viral Rhythmic Beat / Dramatic Tension Sound Effect",
            "ad_copy": (
                f"What's your take on {clean_asset}? 💬\n\n"
                "Comment 'TRUTH' below and I'll send the full breakdown video straight to your DMs!\n\n"
                f"#{clean_asset.replace(' ', '')} #ViralTrends #CreatorEconomy #TrendPulse"
            ),
            "action_blueprint": (
                "1. HOUR 1: Film a 9:16 vertical video using green screen overlay and script above.\n"
                "2. HOUR 6: Activate auto-DM responder for keyword 'TRUTH' to boost post velocity.\n"
                "3. DAY 2: Pin top engaging comments and post a follow-up story poll."
            ),
            "competitor_intelligence": (
                f"• **Top Competitor Hook Style:** *'The secret behind {clean_asset} revealed...'*\n"
                "• **Optimal Video Duration:** 15 - 30 seconds\n"
                "• **Estimated Engagement Benchmark:** Very High (8.5%+ Comment/Share Ratio)"
            ),
        }

    if not GROQ_API_KEY:
        return default_response

    try:
        client = Groq(api_key=GROQ_API_KEY)
        sub_niche_prompt_rule = (
            f"STRICT SUB-NICHE MANDATE: All content hooks, spoken scripts, profit models, and talking points MUST BE EXCLUSIVELY "
            f"tailored to the '{clean_sub}' sub-niche under '{clean_cat}'. DO NOT broaden to general '{clean_cat}'."
            if clean_sub and clean_sub != "All Sub-Niches"
            else f"Focus on the '{clean_cat}' category."
        )

        prompt = f"""
You are TrendPulse AI's Master Strategy Blueprint Generator.
Generate a highly customized, role-specific operational execution blueprint.

=========================================
INPUT DATA & MANDATES:
=========================================
- Asset / Topic: "{clean_asset}"
- Main Category: "{clean_cat}"
- Target Sub-Niche: "{clean_sub if clean_sub else 'General'}"
- Operating Role: "{target_role}"
- Platform Focus: "{platform}"
- Timeframe: "{timeframe}"
- Viral Score: {velocity_score}%
- Target Language: {lang}

{sub_niche_prompt_rule}

=========================================
JSON OUTPUT REQUIREMENTS:
=========================================
Return ONLY a valid JSON object matching this structure EXACTLY (do not wrap in markdown tags):
{{
  "viral_score": "{velocity_score}%",
  "prediction_window": "Active lifecycle timing window details",
  "profit_model": "Role-tailored high-ROI monetization model strategy tailored strictly for {target_role} in {clean_sub if clean_sub else clean_cat}",
  "content_directives": "• **Narrative Angle / Thesis:** [Core story]\n• **Key Talking Points:**\n  1. [Beat 1]\n  2. [Beat 2]\n  3. [Beat 3]\n• **Visual & B-Roll Assets:** [Shot list]\n• **Category Guardrails:** [Do's and Don'ts]",
  "execution_hook": "• **0-3s Visual Cue:** [Cue]\n• **Text Overlay:** \"[Punchy text]\"\n• **Spoken Script:** \"[Script]\"",
  "audio_suggestion": "Specific music genre or sound vibe matching {target_role}",
  "ad_copy": "Complete caption with CTA keyword tailored strictly to {target_role}",
  "action_blueprint": "1. HOUR 1: [Immediate setup]\n2. HOUR 6: [Deployment]\n3. HOUR 48: [Optimization]",
  "competitor_intelligence": "• **Top Competitor Focus:** [Style/Angle]\n• **Optimal Format/Duration:** [Format]\n• **Target Benchmarks:** [Metrics]"
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
# 7. UI LAYOUT & RENDER
# ==========================================
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

head_col1, head_col2 = st.columns([3, 1])

with head_col2:
    selected_lang = st.selectbox(
        "🌐 Language / भाषा:", ["English", "Hindi"], index=0
    )

t = TEXTS[selected_lang]

with head_col1:
    st.title(t["title"])
    st.caption(t["subtitle"])

st.markdown("---")

with st.expander(t["terminal"]):
    st.session_state["is_premium"] = st.checkbox(
        t["simulate_pro"], value=st.session_state["is_premium"]
    )

st.markdown(f"### {t['config_title']}")

# Filter Form Configuration
with st.form(key="filter_form"):
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

    with f_col1:
        geo_option = st.selectbox(
            t["region"],
            [
                "India (IN)",
                "United States (US)",
                "United Kingdom (GB)",
                "Global (ALL)",
            ],
        )
        geo_map = {
            "India (IN)": "IN",
            "United States (US)": "US",
            "United Kingdom (GB)": "GB",
            "Global (ALL)": "US",
        }

    with f_col2:
        platform_source = st.selectbox(
            t["platform"],
            [
                "Social Video & Reels",
                "TikTok & Instagram Reels",
                "Search Engine Intent",
                "E-Commerce Shopping",
            ],
        )

    with f_col3:
        selected_category = st.selectbox(
            t["category"],
            options=list(UPDATED_NICHE_CATEGORIES.keys()),
            index=0
        )

    with f_col4:
        sub_niche_options = UPDATED_NICHE_CATEGORIES.get(selected_category, [])
        selected_sub_niche = st.selectbox(
            t["sub_category"],
            options=["All Sub-Niches"] + sub_niche_options,
            index=0
        )

    with f_col5:
        timeframe = st.selectbox(
            t["velocity"],
            [
                "Realtime Spike (24h)",
                "Short-Term Trend (7 Days)",
                "Viral Surge (3-7 Days)",
                "Macro Trend (30 Days)",
            ],
        )

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
        geo_map[geo_option], 
        platform_source, 
        selected_category, 
        selected_sub_niche, 
        timeframe
    )

    future_forecast_options = [
        "🔥 High Growth (Next 7 Days)",
        "🚀 Viral Peak Expected",
        "📈 Steady Upward Surge",
        "⚡ Breakout Candidate",
        "📊 Emerging Trend",
    ]

    table_data = []
    signal_scores = {}

    for idx, item in enumerate(active_signals):
        score = round(98.8 - (idx * 3.2), 1)
        forecast = future_forecast_options[
            idx % len(future_forecast_options)
        ]

        table_data.append({
            t["filtered_asset"]: item["Keyword"],
            t["search_volume"]: item["Volume"],
            t["future_forecast"]: forecast,
        })
        signal_scores[item["Keyword"]] = score

    df = pd.DataFrame(table_data)
    sub_title_ctx = f" | Sub: `{selected_sub_niche}`" if selected_sub_niche != "All Sub-Niches" else ""
    st.markdown(
        f"**{t['active_signals_for']}** `{selected_category}`{sub_title_ctx} |"
        f" `{platform_source}` | `{geo_option}`"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            t["filtered_asset"]: st.column_config.TextColumn(
                t["filtered_asset"], width="large"
            ),
            t["search_volume"]: st.column_config.TextColumn(
                t["search_volume"], width="small"
            ),
            t["future_forecast"]: st.column_config.TextColumn(
                t["future_forecast"], width="medium"
            ),
        },
    )

    st.markdown(f"#### {t['chart_title']}")

    if custom_search.strip():
        chart_keyword = custom_search.strip()
        base_score = 95.0
    else:
        chart_keyword = (
            active_signals[0]["Keyword"] if active_signals else "Asset"
        )
        base_score = signal_scores.get(chart_keyword, 90.0)

    # Historical & Velocity Forecast Plot
    days = ["Day -3", "Day -2", "Day -1", "Today", "Day +1 (Proj)", "Day +2 (Proj)", "Day +3 (Proj)"]
    scores = [
        max(10.0, base_score - 45),
        max(15.0, base_score - 30),
        max(25.0, base_score - 12),
        base_score,
        min(99.5, base_score + 3.5),
        min(98.0, base_score + 2.0),
        max(40.0, base_score - 10.0)
    ]
    
    chart_df = pd.DataFrame({"Timeline": days, "Signal Velocity Score": scores})
    fig = px.line(
        chart_df,
        x="Timeline",
        y="Signal Velocity Score",
        markers=True,
        title=f"Demand Curve for '{chart_keyword[:30]}...'",
        line_shape="spline",
    )
    fig.update_traces(line_color="#ff4b4b", line_width=3, marker_size=8)
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader(t["matrix_title"])

    if not st.session_state["is_premium"]:
        st.warning(f"**{t['locked_title']}**")
        st.write(t["locked_info"])
        st.markdown(
            f'<a href="{STRIPE_CHECKOUT_URL}" target="_blank">'
            f'<button style="background-color:#ff4b4b;color:white;padding:12px 24px;'
            f'border:none;border-radius:6px;width:100%;font-weight:bold;cursor:pointer;">'
            f'{t["upgrade_btn"]}</button></a>',
            unsafe_allow_html=True,
        )
    else:
        if custom_search.strip():
            selected_asset = custom_search.strip()
            v_score = 95.0
            st.info(f"{t['analyzing_custom']} **{selected_asset}**")
        else:
            asset_options = [item["Keyword"] for item in active_signals]
            selected_asset = st.selectbox(
                t["select_asset"], options=asset_options, index=0
            )
            v_score = signal_scores.get(selected_asset, 92.0)

        selected_role = st.selectbox(
            t["operating_role"],
            [
                "Content Creator / Influencer",
                "E-Commerce Merchant / Dropshipper",
                "Agency Owner / Freelancer",
            ],
            index=0,
        )

        if st.button(t["gen_blueprint"], use_container_width=True):
            with st.spinner("Generating precision intelligence..."):
                intel = generate_master_intelligence(
                    selected_asset,
                    selected_category,
                    selected_sub_niche,
                    selected_role,
                    platform_source,
                    timeframe,
                    v_score,
                    selected_lang,
                )

                st.success("Blueprint Generated Successfully!")

                st.metric(
                    label=t["score_label"],
                    value=intel.get("viral_score", f"{v_score}%"),
                )

                st.markdown(f"#### {t['monetization']}")
                st.markdown(intel.get("profit_model", ""))

                st.markdown(f"#### {t['content_directives']}")
                st.markdown(intel.get("content_directives", ""))

                st.markdown(f"#### {t['hook']}")
                st.markdown(intel.get("execution_hook", ""))

                st.markdown(f"#### {t['audio']}")
                st.markdown(f"• {intel.get('audio_suggestion', '')}")

                st.markdown(f"#### {t['caption']}")
                st.code(intel.get("ad_copy", ""), language="markdown")

                st.markdown(f"#### {t['plan']}")
                st.markdown(intel.get("action_blueprint", ""))

                st.markdown(f"#### {t['competitor_insight']}")
                st.markdown(intel.get("competitor_intelligence", ""))

                # Downloads & Export Section
                st.markdown("---")
                pdf_bytes = create_pdf_blueprint(
                    selected_asset,
                    selected_category,
                    selected_role,
                    v_score,
                    timeframe,
                    intel,
                )

                st.download_button(
                    label=t["export_pdf_btn"],
                    data=pdf_bytes,
                    file_name=f"TrendPulse_Blueprint_{sanitize_trend_input(selected_asset)[:15]}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

                wa_text = urllib.parse.quote(
                    f"🚀 *TrendPulse Intelligence Briefing*\n\n"
                    f"Asset: {selected_asset}\n"
                    f"Role: {selected_role}\n"
                    f"Score: {v_score}%\n\n"
                    f"Monetization Path:\n{intel.get('profit_model', '')[:200]}..."
                )
                wa_url = f"https://api.whatsapp.com/send?text={wa_text}"
                st.markdown(
                    f'<a href="{wa_url}" target="_blank">'
                    f'<button style="background-color:#25D366;color:white;padding:8px 16px;'
                    f'border:none;border-radius:4px;width:100%;font-weight:bold;margin-top:8px;">'
                    f'{t["share_wa_btn"]}</button></a>',
                    unsafe_allow_html=True,
                )
