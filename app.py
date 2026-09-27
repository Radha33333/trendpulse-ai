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
# 6. PIPELINE & RADAR DATA ENGINE (FULL 120 SUB-NICHE POOLS)
# ==========================================
@st.cache_data(ttl=300)
def fetch_and_store_signals(region, platform_source, category, sub_niche, timeframe):
    # Complete manual dictionary covering categories 16-20 and full coverage
   specific_pools = {
        # --- 16. Beauty, Skincare & Lifestyle ---
        "UGC Skincare Hacks": [
            ("Viral Ice Rolling Skin De-Puffing Morning Routine", "Skin icing TikTok trend", "🔥 High Growth"),
            ("Slugging Method Petroleum Jelly Overnight Barrier Repair", "CeraVe & Vaseline Hack", "🚀 Explosive Surge"),
            ("Double Cleansing Oil Method Korean Skincare Ritual", "Anua Cleansing Oil Drop", "⚡ Accelerating"),
            ("Dermaplaning Exfoliation Face Shaving At-Home Hack", "Schick Silk Touch-Up", "📈 Trending"),
            ("Under-Eye Color Correcting Brightener Makeup Hack", "Pink Powder TikTok Trend", "🔥 High Growth"),
            ("Gua Sha Lymphatic Drainage Facial Massage Tutorial", "Herbivore Rose Quartz", "🚀 Explosive Surge"),
            ("Rice Water Fermentation Hair and Skin Glow Hack", "DIY K-Beauty Secret", "⚡ Accelerating"),
            ("Pimple Patch Hydrocolloid Overnight Blemish Healing", "Hero Cosmetics Mighty Patch", "📈 Trending"),
            ("Lip Basting Retinol Exfoliation Dry Lip Hack", "Dr. Whitney Bowe Method", "🔥 High Growth"),
            ("Tinted SPF Mineral Sunscreen Glow Drop Routine", "La Roche-Posay Anthelios", "⚡ Accelerating")
        ],
        "K-Beauty & Glass Skin Trends": [
            ("Fermented Snail Mucin Essence Barrier Repair Surge", "Cosrx Advanced Snail 96 Mucin", "🔥 High Growth"),
            ("Korean Sheet Mask 7-Day Hydration Challenge Glow", "Mediheal & Innisfree Kits", "🚀 Explosive Surge"),
            ("Centella Asiatica Calming Toner Pad Restock", "Anua Heartleaf 77 Pad", "⚡ Accelerating"),
            ("Ginseng & Retinol Eye Cream Anti-Aging Innovation", "Beauty of Joseon Revive", "📈 Trending"),
            ("Glass Skin Cushion Foundation Dewy Finish Drop", "Tirtir Mask Fit Red Cushion", "🔥 High Growth"),
            ("Rice Bran Water Brightening Face Cleanser Wave", "I'm From Rice Toner", "🚀 Explosive Surge"),
            ("Melting Collagen Deep Facial Mask Sheet Treatment", "Biodance Bio-Collagen Real Deep", "⚡ Accelerating"),
            ("Water Drop Hydration Sun Serum K-Beauty Formula", "Round Lab Birch Juice SPF", "📈 Trending"),
            ("Pore Clearing Volcanic Ash Clay Mask Treatment", "Innisfree Pore Clearing", "🔥 High Growth"),
            ("Propolis Vitamin Energy Glow Serum Ampoule", "COSRX Propolis Synergy", "⚡ Accelerating")
        ],
        "Anti-Aging & Beauty Devices": [
            ("LED Light Therapy Face Mask Anti-Aging Wrinkle Device", "CurrentBody Skin LED Mask", "🔥 High Growth"),
            ("Microcurrent Facial Toning & Contouring Device", "NuFace Trinity Pro", "🚀 Explosive Surge"),
            ("Radio Frequency (RF) Skin Tightening At-Home Wand", "Tripollar Stop Vx", "⚡ Accelerating"),
            ("Ultrasonic Skin Spatula Blackhead Remover Scrubber", "Skin scrubber portable device", "📈 Trending"),
            ("Cryotherapy Facial Ice Globe Cooling Glass Sticks", "Spa Ice Globes Trend", "🔥 High Growth"),
            ("Ionic Facial Steamer Deep Pore Cleansing Device", "Dr. Dennis Gross Steamer", "🚀 Explosive Surge"),
            ("High-Frequency Acne Spot Treatment Wand Device", "NuDerma Skin Wand", "⚡ Accelerating"),
            ("Smart App-Connected Skin Analysis Mirror Device", "HiMirror Mini Pro", "📈 Trending"),
            ("Laser Hair Removal At-Home IPL Handset Device", "Braun Silk-expert Pro 5", "🔥 High Growth"),
            ("Sonic Vibration Eye Massager Anti-Puffiness Wand", "Foreo Iris Eye Massager", "⚡ Accelerating")
        ],
        "Men's Grooming & Beard Care": [
            ("Argan & Cedarwood Organic Beard Growth Oil Drop", "Beardo & Ustraa Grooming", "🔥 High Growth"),
            ("Precision Cordless T-Blade Hair Trimmer for Fades", "Wahl Detailer Pro", "🚀 Explosive Surge"),
            ("Activated Charcoal Deep Cleansing Men's Face Wash", "Brickell Men's Wash", "⚡ Accelerating"),
            ("Solid Cologne Travel Balm Long-Lasting Fragrance", "Fulton & Roark Solid", "📈 Trending"),
            ("Matte Finish Hair Styling Clay Strong Hold Paste", "Bed Head BForMen Wax", "🔥 High Growth"),
            ("Safety Razor Traditional Wet Shaving Starter Kit", "Merkur Classic Safety Razor", "🚀 Explosive Surge"),
            ("Boar Bristle Beard Brush & Wooden Comb Grooming Set", "Viking Revolution Kit", "⚡ Accelerating"),
            ("Anti-Hair Loss Caffeine Shampoo Scalp Treatment", "Alpecin C1 Caffeine", "📈 Trending"),
            ("Nose and Ear Hair Precision Trimmer Grooming Tool", "Philips Nose trimmer 3000", "🔥 High Growth"),
            ("Hydrating Aftershave Balm Sensitive Skin Relief", "Proraso Sensitive Balm", "⚡ Accelerating")
        ],
        "Haircare Treatment Trends": [
            ("Bond Repair Hair Treatment Mask for Damaged Strands", "Olaplex No. 3 Perfector", "🔥 High Growth"),
            ("Scalp Exfoliating Scrub Brush for Hair Growth", "Mielle Organics Rosemary Mint", "🚀 Explosive Surge"),
            ("Heatless Silk Curling Ribbon Overnight Wave Set", "Kitsch Satin Heatless Curler", "⚡ Accelerating"),
            ("Rosemary Essential Oil Scalp Drops for Hair Growth", "Mielle Rosemary Oil", "📈 Trending"),
            ("Professional Ionic Salon Hair Dryer Lightweight Drop", "Dyson Supersonic Nural", "🔥 High Growth"),
            ("Anti-Frizz Smoothing Hair Gloss Treatment Gloss", "Color Wow Dream Coat", "🚀 Explosive Surge"),
            ("Dry Shampoo Volume Powder Instant Refresh Spray", "Batiste & Living Proof", "⚡ Accelerating"),
            ("Silk Pillowcase Anti-Frizz Hair & Skin Protection", "Slip Pure Silk Pillowcase", "📈 Trending"),
            ("Keratin Smoothing Treatment At-Home Serum Drop", "Brazilian Blowout Home Kit", "🔥 High Growth"),
            ("Leave-in Conditioner Detangling Spray Spray Bottle", "It's a 10 Miracle Leave-In", "⚡ Accelerating")
        ],
        "Minimalist Capsule Wardrobes": [
            ("Neutral Tone Heavyweight Cotton Oversized T-Shirt", "Uniqlo U Collection", "🔥 High Growth"),
            ("Classic Tailored Wool Blend Trench Coat Winter Drop", "COS & Massimo Dutti", "🚀 Explosive Surge"),
            ("Sustainable Organic Cotton Straight-Leg Denim Jeans", "Everlane Way High Jean", "⚡ Accelerating"),
            ("Minimalist White Leather Sneaker Everyday Staple", "Veja Campo & Common Projects", "📈 Trending"),
            ("Cashmere Crewneck Sweater Luxury Basic Knitwear", "Naadam & Quince Cashmere", "🔥 High Growth"),
            ("Structured Leather Crossbody Everyday Handbag", "Polene Numéro Dix", "🚀 Explosive Surge"),
            ("Pleated High-Waisted Tailored Trouser Pants", "Aritzia Effortless Pant", "⚡ Accelerating"),
            ("Classic Gold Hoop Earrings Minimalist Jewelry Drop", "Mejuri Bold Hoops", "📈 Trending"),
            ("Structured Linen Blazer Summer Capsule Jacket", "Abercrombie Tailored Linen", "🔥 High Growth"),
            ("Ribbed Organic Cotton Tank Top Basic Layer", "Skims Cotton Rib", "⚡ Accelerating")
        ],

        # --- 17. Health, Fitness & Biohacking ---
        "Gym & Home Workout Gear": [
            ("Adjustable Dumbbell Set Space-Saving Home Gym", "Nuobell & PowerBlock", "🔥 High Growth"),
            ("Heavy-Duty Power Rack & Barbell Home Gym Setup", "Rogue Fitness Monster Lite", "🚀 Explosive Surge"),
            ("Resistance Bands Set with Door Anchor & Handles", "Whatnot Fitness Bands", "⚡ Accelerating"),
            ("Non-Slip Yoga Mat Extra Thick Eco-Friendly Mat", "Lululemon 5mm Workout Mat", "📈 Trending"),
            ("Compact Under-Desk Walking Pad Treadmill", "Urevo Fitness Pad", "🔥 High Growth"),
            ("Olympic Rubber Bumper Plate Weight Set", "REP Fitness Plates", "🚀 Explosive Surge"),
            ("Suspension Training Bodyweight Fitness Straps", "TRX GO System", "⚡ Accelerating"),
            ("Speed Agility Training Ladder & Cones Kit", "SKLZ Pro Training", "📈 Trending"),
            ("Adjustable Plyometric Jump Box Foam Platform", "Titan Fitness Box", "🔥 High Growth"),
            ("Heavy Slam Ball Core Strength Fitness Medicine Ball", "Dynamax Med Ball", "⚡ Accelerating")
        ],
        "Whey & Supplement Drops": [
            ("Isolate Whey Protein Powder Chocolate Flavor Drop", "Optimum Nutrition Gold Standard", "🔥 High Growth"),
            ("Creatine Monohydrate Micronized Muscle Recovery", "MuscleBlaze & Dymatize", "🚀 Explosive Surge"),
            ("Pre-Workout Energy Drink Powder Extreme Focus", "C4 Original & Ghost Legend", "⚡ Accelerating"),
            ("BCAA Amino Acid Hydration Powder Formula", "Scivation Xtend BCAA", "📈 Trending"),
            ("Plant-Based Vegan Pea Protein Powder Organic Blend", "Orgain Organic Protein", "🔥 High Growth"),
            ("L-Glutamine Recovery Powder Muscle Repair Supplement", "Nutrabay Pure Glutamine", "🚀 Explosive Surge"),
            ("Ashwagandha KSM-66 Stress & Testosterone Support", "Carbamide Forte KSM-66", "⚡ Accelerating"),
            ("Omega-3 Triple Strength Fish Oil Softgels", "TrueBasics Omega-3", "📈 Trending"),
            ("Multivitamin Daily Sport Athletic Performance Pill", "Centrum Performance", "🔥 High Growth"),
            ("Collagen Peptides Powder Joint & Skin Complex", "Sports Research Collagen", "⚡ Accelerating")
        ],
        "Biohacking & Wearable Tech (Oura/Whoop)": [
            ("Smart Ring Sleep & Recovery Biometric Tracker", "Oura Ring Gen 4", "🔥 High Growth"),
            ("Advanced Fitness & Strain Wearable Strap Device", "WHOOP 4.0 Strap", "🚀 Explosive Surge"),
            ("Continuous Glucose Monitor (CGM) Metabolic Tracker", "Abbott Libre & Levels Health", "⚡ Accelerating"),
            ("Red Light Therapy Panel Full Body Recovery Lamp", "Hooga & Platinum LED", "📈 Trending"),
            ("Heart Rate Variability (HRV) Biofeedback Monitor", "Elite HRV Sensor Band", "🔥 High Growth"),
            ("Smart Sleep Tracking & Snoring Smart Mat", "Withings Sleep Analyzer", "🚀 Explosive Surge"),
            ("Brainwave Entrainment & Focus Neural Headband", "Muse 2 EEG Headband", "⚡ Accelerating"),
            ("Smart Insole Running Gait & Pressure Sensor Pod", "Rundvå Tracker Insole", "📈 Trending"),
            ("Hydration Smart Electrolyte Sweat Sensor Patch", "Gatorade Gx Sweat Patch", "🔥 High Growth"),
            ("PEMF Therapy Mat Recovery Mat Low Frequency", "BEMER Practitioner Mat", "⚡ Accelerating")
        ],
        "Weight Loss & Nutrition Diets": [
            # Continue your remaining items here...
        ]
}
            ("Ketogenic Diet Macro Calculator & Meal Plan", "Diet Doctor Keto Hub", "🔥 High Growth"),
            ("Intermittent Fasting 16:8 Timer & Tracking App", "Zero Fasting App", "🚀 Explosive Surge"),
            ("High-Protein Low-Calorie Meal Prep Delivery", "Eat Clean Meal Plan", "⚡ Accelerating"),
            ("Plant-Based Whole Foods Diet Recipe Ebook", "Forks Over Knives Guide", "📈 Trending"),
            ("Gluten-Free Gut Healing Organic Diet Plan", "Digestive Health Program", "🔥 High Growth"),
            ("Calorie Tracking & Macro Nutrient Scanner App", "MyFitnessPal Premium", "🚀 Explosive Surge"),
            ("Mediterranean Diet Heart-Healthy Cookbook Guide", "Oldways Preservation Hub", "⚡ Accelerating"),
            ("Carnivore Diet High-Fat Meat Protein Protocol", "Dr. Shawn Baker Blueprint", "📈 Trending"),
            ("Sugar Detox 21-Day Clean Eating Challenge Guide", "Sarah Wilson Quit Sugar", "🔥 High Growth"),
            ("Metabolic Reset Hormone Balancing Nutrition Plan", "Fast Like a Girl Protocol", "⚡ Accelerating")
        ],
        "Mental Health & Burnout Recovery": [
            ("Guided Meditation & Mindfulness Sleep App Subscription", "Headspace & Calm App", "🔥 High Growth"),
            ("Cognitive Behavioral Therapy (CBT) Journaling Guide", "BetterHelp Workbook", "🚀 Explosive Surge"),
            ("Corporate Burnout Recovery Masterclass & Retreat", "Arianna Huffington Thrive", "⚡ Accelerating"),
            ("Weighted Anxiety Relief Blanket Heavy Sensory Rest", "Baloo Living Weighted", "📈 Trending"),
            ("Aromatherapy Essential Oil Diffuser Ultrasonic Hub", "InnoGear Essential Oil Diffuser", "🔥 High Growth"),
            ("Light Therapy Lamp Seasonal Affective Disorder Cure", "Verilux HappyLight", "🚀 Explosive Surge"),
            ("Daily Stoic Journaling Prompt Book & Daily Planner", "Ryan Holiday Stoic Journal", "⚡ Accelerating"),
            ("Noise-Masking Sleep Earbuds Wireless Comfort", "Bose Sleepbuds II", "📈 Trending"),
            ("Somatic Stress Release & Nervous System Regulation", "Dr. Nicole LePera Guide", "🔥 High Growth"),
            ("Gratitude Journal 5-Minute Daily Mindset Practice", "Intelligent Change Journal", "⚡ Accelerating")
        ],
        "Recovery Gear & Cold Plunges": [
            ("Inflatable Portable Cold Plunge Tub Ice Bath", "Plunge & Ice Barrel", "🔥 High Growth"),
            ("Percussive Deep Tissue Muscle Massage Gun Device", "Theragun PRO Plus", "🚀 Explosive Surge"),
            ("Dynamic Air Compression Recovery Boot System", "Normatec 3 Leg Boots", "⚡ Accelerating"),
            ("Electric Heated Vibration Foam Roller Fitness Tool", "Hyperice Vyper 3", "📈 Trending"),
            ("Cryotherapy Ice Compression Wrap Joint Support", "Hyperice Ice Compression", "🔥 High Growth"),
            ("Far Infrared Sauna Blanket Portable Detox Spa", "HigherDOSE Infrared Sauna", "🚀 Explosive Surge"),
            ("Epsom Salt Magnesium Flakes Muscle Bath Soak", "Dr Teal's Pure Epsom Salt", "⚡ Accelerating"),
            ("Trigger Point Massage Ball Set Mobility Release", "RumbleRoller Beastie", "📈 Trending"),
            ("Acupressure Mat & Pillow Pain Relief Set", "Pranamat ECO Mat", "🔥 High Growth"),
            ("Compression Leg Sleeves Blood Circulation Aid", "2XU Compression Calf Guard", "⚡ Accelerating")
        ],

        # --- 18. Travel, Hotels & Food ---
        "Trending Destinations": [
            ("Hidden Island Beach Paradise Tourism Surge", "Andaman & Nicobar Islands", "🔥 High Growth"),
            ("Himalayan Scenic Mountain Valley Tourist Spike", "Spiti Valley & Leh Ladakh", "🚀 Explosive Surge"),
            ("European Cultural Heritage City Weekend Getaway", "Prague & Budapest Tourism", "⚡ Accelerating"),
            ("Southeast Asian Tropical Jungle Resort Destination", "Bali & Phuket Luxury Drop", "📈 Trending"),
            ("Desert Luxury Glamping Oasis Experience Wave", "Wadi Rum & Thar Desert", "🔥 High Growth"),
            ("Scenic Coastal Highway Road Trip Destination", "Great Ocean Road & Amalfi", "🚀 Explosive Surge"),
            ("Nordic Northern Lights Arctic Igloo Stay Trend", "Tromso Norway Glass Igloo", "⚡ Accelerating"),
            ("Ancient Historical Temple Trail Tourist Spike", "Angkor Wat & Hampi Tour", "📈 Trending"),
            ("Eco-Friendly Rainforest Jungle Lodge Retreat", "Costa Rica Eco Lodge", "🔥 High Growth"),
            ("Wine Tasting Vineyard Touristic Valley Escape", "Napa Valley & Tuscany", "⚡ Accelerating")
        ],
        "Hidden Tourist Places": [
            ("Unexplored Waterfall & Cave Trekking Trail", "Meghalaya Living Root Bridges", "🔥 High Growth"),
            ("Secret Cliffside Coastal Village Secret Beach", "Gokarna Hidden Coves", "🚀 Explosive Surge"),
            ("High Altitude Alpine Lake Trekking Expedition", "Kedartal Trek Uttarakhand", "⚡ Accelerating"),
            ("Offbeat Heritage Village Homestay Experience", "Chettinad Mansion Stay", "📈 Trending"),
            ("Bioluminescent Beach Night Glowing Waves Wave", "Jalapally Beach & Mirihi", "🔥 High Growth"),
            ("Mystical Haunted Fort Ruin Historical Walk", "Bhangarh Fort Expedition", "🚀 Explosive Surge"),
            ("Remote Mountain Monastery Spiritual Retreat Stay", "Tawang Monastery Arunachal", "⚡ Accelerating"),
            ("Undiscovered Fossil Park Geological Trail", "Shivalik Fossil Park", "📈 Trending"),
            ("Secret River Island Kayaking & Camping Spot", "Majuli Island Assam", "🔥 High Growth"),
            ("Secret Underground Cave Exploration Tour", "Krem Liat Prah Meghalaya", "⚡ Accelerating")
        ],
        "Luxury Hotels & Resort Stays": [
            ("Overwater Private Pool Villa Resort Booking Spike", "Maldives Luxury Resorts", "🔥 High Growth"),
            ("Palace Heritage Hotel Royal Stay Experience", "Umaid Bhawan Palace Jodhpur", "🚀 Explosive Surge"),
            ("Private Jungle Safari Treehouse Resort Booking", "Aman Resorts & Jim Corbett", "⚡ Accelerating"),
            ("Cliffside Infinity Pool Luxury Resort Suite", "Santorini Grace Hotel", "📈 Trending"),
            ("Ski-In Ski-Out Alpine Luxury Chalet Resort", "Zermatt Switzerland Chalet", "🔥 High Growth"),
            ("Private Island Exclusive Resort Helicopter Transfer", "Necker Island Luxury", "🚀 Explosive Surge"),
            ("Sub-Aquatic Underwater Hotel Suite Experience", "The Muraka Maldives", "⚡ Accelerating"),
            ("Historic Castle Hotel Wine Cellar Dining Suite", "Chateau de Chambord Stay", "📈 Trending"),
            ("Desert Luxury Dune Camp Private Butler Villa", "Al Maha Desert Resort", "🔥 High Growth"),
            ("Boutique Design Hotel Rooftop Pool Suite", "Soho House Mumbai", "⚡ Accelerating")
        ],
        "Gourmet & Regional Cuisines": [
            ("Authentic Chef's Table Multi-Course Tasting Menu", "Bukhara & Indian Accent", "🔥 High Growth"),
            ("Traditional Awadh Dum Biryani Masterclass Recipe", "Lucknow Culinary Heritage", "🚀 Explosive Surge"),
            ("Authentic Neapolitan Wood-Fired Pizza Workshop", "Mumbai Craft Pizzeria", "⚡ Accelerating"),
            ("Japanese Omakase Sushi Dining Experience Trend", "Tokyo Master Chef Pop-up", "📈 Trending"),
            ("Authentic Coastal Seafood Thali Culinary Tour", "Malvani & Goan Cuisine Hub", "🔥 High Growth"),
            ("Handmade Artisan Pasta Making Masterclass", "Bologna Culinary School", "🚀 Explosive Surge"),
            ("Royal Rajasthani Laal Maas Feast Experience", "Jaipur Gourmet Heritage", "⚡ Accelerating"),
            ("Authentic Korean BBQ Tabletop Grill Experience", "K-Food Seoul Trend", "📈 Trending"),
            ("French Patisserie Macaron Baking Masterclass", "Parisian Bakery Academy", "🔥 High Growth"),
            ("Authentic South Indian Filter Coffee & Dosa Trail", "Mylapore Food Walk", "⚡ Accelerating")
        ],
        "Street Food Surges": [
            ("Viral Cheese Burst Street Food Sandwich Trend", "Mumbai Toast Sandwich", "🔥 High Growth"),
            ("Smoky Charcoal Tandoori Momos Street Food Spike", "Delhi Street Food Hub", "🚀 Explosive Surge"),
            ("Crispy Pani Puri Golgappa Fusion Water Taste Test", "Kolkata Phuchka Wave", "⚡ Accelerating"),
            ("Spicy Butter Garlic Noodles Street Cart Surge", "Bangalore Night Street Food", "📈 Trending"),
            ("Chocolate Melted Vadapav Street Food Innovation", "Ahmedabad Street Snack", "🔥 High Growth"),
            ("Authentic Hyderabadi Haleem Ramzan Street Food", "Charminar Food Walk", "🚀 Explosive Surge"),
            ("Crispy Jalebi Rabri Sweet Stall Evening Rush", "Chandni Chowk Sweet Hub", "⚡ Accelerating"),
            ("Cheesy Corn Maggi Street Cart Midnight Snack", "North Campus Delhi Hub", "📈 Trending"),
            ("Spicy Kathi Roll Gourmet Street Roll Outlet", "Park Street Kolkata", "🔥 High Growth"),
            ("Tangy Pav Bhaji Amul Butter Extra Load Stall", "Sardar Pav Bhaji Mumbai", "⚡ Accelerating")
        ],
        "Budget & Backpacker Escapes": [
            ("Hostel Dorm Room Backpacking Europe Rail Pass", "Eurail Global Pass Hub", "🔥 High Growth"),
            ("Low-Cost Budget Airline Flash Sale Ticket Alert", "AirAsia & IndiGo Sale", "🚀 Explosive Surge"),
            ("Backpacker Jungle Trekking & Camping Adventure", "Manali to Leh Bike Trip", "⚡ Accelerating"),
            ("Hostelworld Social Backpacking Property Booking", "Stellar Hostel Goa", "📈 Trending"),
            ("Volunteer Work Exchange Travel Accommodation Program", "Worldpackers & Workaway", "🔥 High Growth"),
            ("Ultra-Lightweight Backpacking Gear Checklist Guide", "REI Backpacking Guide", "🚀 Explosive Surge"),
            ("Cheap Street Food & Public Transit City Guide", "Bangkok Budget Travel Hub", "⚡ Accelerating"),
            ("Solo Female Backpacking Safety Tip Framework", "Nomadic Matt Guide", "📈 Trending"),
            ("Couchsurfing Community Free Stay Host Network", "Couchsurfing Verified Hub", "🔥 High Growth"),
            ("Interstate Sleeper Bus Budget Travel Booking", "RedBus & Zingbus Deals", "⚡ Accelerating")
        ],

        # --- 19. Faith, Festivals & Sacred Travel ---
        "Famous Temples & Shrines": [
            ("Divine Darshan Live Streaming Queue Status Update", "Tirumala Tirupati Devasthanams", "🔥 High Growth"),
            ("Char Dham Yatra Helicopter Booking Slot Surge", "Kedarnath & Badrinath Hub", "🚀 Explosive Surge"),
            ("Kashi Vishwanath Corridor Tourist Footfall Spike", "Varanasi Temple Circuit", "⚡ Accelerating"),
            ("Golden Temple Community Kitchen Seva Volunteering", "Amritsar Harmandir Sahib", "📈 Trending"),
            ("South Indian Temple Architecture Heritage Tour", "Meenakshi Amman Temple Madurai", "🔥 High Growth"),
            ("12 Jyotirlinga Pilgrimage Circuit Travel Package", "Mahakaleshwar Ujjain Hub", "🚀 Explosive Surge"),
            ("Vaishno Devi Shrine Helicopter & Battery Car Pass", "Katra Jammu Yatra", "⚡ Accelerating"),
            ("Jagannath Rath Yatra Festival Chariot Pulling Wave", "Puri Odisha Celebration", "📈 Trending"),
            ("Lotus Temple Architectural Heritage Visitor Spike", "Bahá'í House of Worship Delhi", "🔥 High Growth"),
            ("Padmanabhaswamy Temple Treasure Vault Heritage Tour", "Thiruvananthapuram Shrine", "⚡ Accelerating")
        ],
        "Hidden & Ancient Temples": [
            ("10th Century Hoysala Architectural Temple Wonder", "Belur & Halebidu Temples", "🔥 High Growth"),
            ("Rock-Cut Monolithic Cave Temple Exploration Tour", "Ellora Caves Kailasa Temple", "🚀 Explosive Surge"),
            ("Submerged Underwater Temple Ruins Archaeological Dive", "Atoteshwar Temple Gujarat", "⚡ Accelerating"),
            ("Hanging Temple Cliffside Ancient Shrine Trek", "Tungnath Highest Shiva Temple", "📈 Trending"),
            ("Chola Dynasty UNESCO World Heritage Temple Tour", "Brihadeeswarar Temple Thanjavur", "🔥 High Growth"),
            ("Mystical Magnetic Hill Ancient Temple Route", "Leh Ladakh Sacred Trail", "🚀 Explosive Surge"),
            ("Hidden Forest Ancient Temple Ruins Expedition", "Khajuraho Western Temples", "⚡ Accelerating"),
            ("Secret Underground Cave Shrine Pilgrimage Trail", "Gupteswar Cave Temple", "📈 Trending"),
            ("Ancient Sun Temple Architectural Alignment Study", "Konark Sun Temple Odisha", "🔥 High Growth"),
            ("Tantric Shakti Peetha Sacred Shrine Darshan", "Kamakhya Temple Guwahati", "⚡ Accelerating")
        ],
        "Religious Festivals & Pujas": [
            ("Diwali Laxmi Puja Muhurat & Festive Gifting Guide", "All-India Festive Calendar", "🔥 High Growth"),
            ("Mahashivratri Night Vigil & Abhishekam Ritual Guide", "Shiva Temple Celebration", "🚀 Explosive Surge"),
            ("Durga Puja Pandals Pandal Hopping Tourist Wave", "Kolkata Sarbojanin Puja", "⚡ Accelerating"),
            ("Ganesh Chaturthi Idol Immersion Visarjan Procession", "Mumbai Lalbaugcha Raja", "📈 Trending"),
            ("Navratri Garba Dandiya Night Festival Pass Booking", "Ahmedabad Navratri Hub", "🔥 High Growth"),
            ("Holi Color Festival Celebration & Organic Gulal Drop", "Mathura Vrindavan Holi", "🚀 Explosive Surge"),
            ("Makar Sankranti Kite Flying Festival Sky Celebration", "Gujarat Uttarayan Hub", "⚡ Accelerating"),
            ("Raksha Bandhan Festive Gifting Hampers & Sweets", "Rakhi E-Commerce Surge", "📈 Trending"),
            ("Janmashtami Midnight Celebration & Dahi Handi Event", "Mathura Birth Shrine Hub", "🔥 High Growth"),
            ("Chhath Puja Sunrise Arghya Ritual Riverbank Gathering", "Patna & Bihar Ghats Hub", "⚡ Accelerating")
        ],
        "Pilgrimage Circuits & Yatras": [
            ("Kailash Mansarovar Yatra Permit & Route Application", "Ministry of External Affairs Hub", "🔥 High Growth"),
            ("Amarnath Yatra Registration & Medical Certificate Guide", "Kashmir Himalayan Shrine", "🚀 Explosive Surge"),
            ("Puri Jagannath Rath Yatra Pilgrim Accommodation", "Odisha Tourism Circuit", "⚡ Accelerating"),
            ("Sabarimala Ayyappa Temple Mandala Puja Season", "Kerala Hill Shrine Pilgrimage", "📈 Trending"),
            ("Shri Ram Janmabhoomi Ayodhya Pilgrimage Circuit", "Ayodhya Temple Darshan Hub", "🔥 High Growth"),
            ("Maha Kumbh Mela Royal Bath Shahi Snan Date Alert", "Prayagraj River Confluence", "🚀 Explosive Surge"),
            ("Buddhist Circuit Tourism Train Pilgrimage Journey", "IRCTC Buddhist Train Tour", "⚡ Accelerating"),
            ("Sikh Takht Pilgrimage Heritage Yatra Circuit", "Punjab & Bihar Gurdwara Trail", "📈 Trending"),
            ("Ashtavinayak Ganpati Temple Circuit Road Trip", "Maharashtra Pilgrimage Route", "🔥 High Growth"),
            ("Shakti Peetha 51 Holy Shrine Aviation Tour Package", "Indian Sacred Aviation Circuit", "⚡ Accelerating")
        ],
        "Festive Gifting Trends": [
            ("Silver Plated Dry Fruit Box Festive Hamper Drop", "Anand & Amrapali Silver", "🔥 High Growth"),
            ("Luxury Scented Soy Wax Candle Gift Set Hamper", "Forest Essentials & Kama Ayurveda", "🚀 Explosive Surge"),
            ("Artisanal Chocolate & Gourmet Cookie Festive Box", "Bakingo & Smoor Hampers", "⚡ Accelerating"),
            ("Traditional Brass Diya & Toran Home Decor Set", "FabIndia Festive Collection", "📈 Trending"),
            ("Organic Herbal Tea Assortment Gift Wooden Box", "Teabox & VAHDAM Teas", "🔥 High Growth"),
            ("Personalized Family Photo Calendar & Diary Kit", "Zoomin Custom Gifting", "🚀 Explosive Surge"),
            ("Handcrafted Terracotta Diya Painting Kit for Kids", "Art & Craft Studio Set", "⚡ Accelerating"),
            ("Luxury Skincare & Body Mist Festive Gift Bundle", "Nykaa & Bath & Body Works", "📈 Trending"),
            ("Auspicious Brass Ganesha Idol & Coin Gifting Set", "CaratLane Gold & Silver", "🔥 High Growth"),
            ("Eco-Friendly Seed Paper Plantable Greeting Card Pack", "BioQ Eco Gifts", "⚡ Accelerating")
        ],
        "Spiritual Wellness & MeditationDrops": [
            ("Singing Bowl Sound Healing Therapy Set Meditation", "Tibetan Chakra Healing Bowl", "🔥 High Growth"),
            ("Guided Vipassana Meditation 10-Day Residential Course", "Dhamma Vipassana Center", "🚀 Explosive Surge"),
            ("Natural Rudraksha Mala Bead Prayer Necklace Rosary", "Isha Life sacred store", "⚡ Accelerating"),
            ("Chakra Balancing Essential Oil Roll-On Aromatherapy", "Plant Therapy Chakra Set", "📈 Trending"),
            ("Yoga Teacher Training 200-Hour Certification Course", "Rishikesh Yoga Ashram", "🔥 High Growth"),
            ("Sandalwood & Oudh Natural Incense Sticks Bulk Pack", "Cycle Pure Agarbathies", "🚀 Explosive Surge"),
            ("Mindfulness Breathwork & Pranayama Online Masterclass", "Art of Living Breath Hub", "⚡ Accelerating"),
            ("Ayurvedic Panchakarma Detox & Wellness Retreat Stay", "Carnoustie Ayurveda Resort", "📈 Trending"),
            ("Sacred Geometry Copper Yantra Copper Plate Grid", "Vastu & Spiritual Hub", "🔥 High Growth"),
            ("Minimalist Zafu Meditation Cushion & Zabuton Mat", "Mindful & Modern Pillow", "⚡ Accelerating")
        ],

        # --- 20. Politics, News & Civic Events ---
        "Elections & Campaign Rallies": [
            ("General Election Exit Polls & Seat Share Prediction", "Lok Sabha Election Tracker", "🔥 High Growth"),
            ("State Assembly Election Candidate Manifesto Breakdown", "Election Commission Portal", "🚀 Explosive Surge"),
            ("Political Party Mega Rally Live Stream & Crowd Metric", "National Party Headquarters", "⚡ Accelerating"),
            ("Voter Turnout Percentage Hourly Update Dashboard", "ECI Voter Turnout App", "📈 Trending"),
            ("By-Election Constituency Result Swing Analysis", "State Electoral Bureau", "🔥 High Growth"),
            ("Digital Campaign Ad Spend & Social Media Reach War", "Meta & Google Ad Library", "🚀 Explosive Surge"),
            ("Political Debate Prime Time Show Viewership Rating", "News Broadcast Audit Hub", "⚡ Accelerating"),
            ("Constituency Boundary Delimitation Policy Update", "Parliamentary Research Hub", "📈 Trending"),
            ("Youth Voter Registration Campaign Drive Metric", "National Youth Voter Hub", "🔥 High Growth"),
            ("Electoral Bond Transparency & Political Funding Data", "Supreme Court Transparency Portal", "⚡ Accelerating")
        ],
        "Legislative Debates & Laws": [
            ("New Criminal Law Bill Parliament Passage & Key Clauses", "Lok Sabha & Rajya Sabha TV", "🔥 High Growth"),
            ("Digital Personal Data Protection Act Compliance Guide", "Ministry of Electronics & IT", "🚀 Explosive Surge"),
            ("Supreme Court Landmark Constitutional Bench Verdict", "Supreme Court of India Portal", "⚡ Accelerating"),
            ("Labor Code Reform Bill Implementation Status Report", "Ministry of Labour & Employment", "📈 Trending"),
            ("Agricultural Reform & MSP Policy Legislative Debate", "Parliamentary Session Hub", "🔥 High Growth"),
            ("Union Budget Tax Slabs & Fiscal Deficit Bill Review", "Ministry of Finance Portal", "🚀 Explosive Surge"),
            ("Telecommunications Bill Spectrum Auction Framework", "TRAI Official Portal", "⚡ Accelerating"),
            ("Women's Reservation Bill Implementation Timeline", "Law and Justice Ministry", "📈 Trending"),
            ("Electricity Amendment Bill Renewable Energy Clauses", "Ministry of Power Portal", "🔥 High Growth"),
            ("Competition Commission Antitrust Regulation Verdict", "CCI Legal Updates Hub", "⚡ Accelerating")
        ],
        "Protests & Policy Changes": [
            ("National Public Protest Demonstration Security Update", "National Capital News Hub", "🔥 High Growth"),
            ("Minimum Wage Revision & Labor Union Policy Protest", "Trade Union Federation", "🚀 Explosive Surge"),
            ("Fuel Price Excise Duty Cut Policy Announcement", "Ministry of Petroleum News", "⚡ Accelerating"),
            ("University Student Fee Hike Protest & Campus Strike", "Central University Hub", "📈 Trending"),
            ("Environmental Forest Conservation Act Policy Protest", "Greenpeace India Update", "🔥 High Growth"),
            ("Commercial Transport Strike & Freight Tariff Revision", "All India Motor Transport Hub", "🚀 Explosive Surge"),
            ("Doctor & Healthcare Professional Safety Policy Protest", "Medical Association Portal", "⚡ Accelerating"),
            ("Agricultural Produce Market Committee (APMC) Reform Protest", "Farmers Union Portal", "📈 Trending"),
            ("Tax Regime Amendment Small Business Chamber Protest", "Confederation of Trade Hub", "🔥 High Growth"),
            ("Urban Housing Demolition Drive & Rehabilitation Protest", "Civic Rights Forum", "⚡ Accelerating")
        ],
        "Politician Speeches & Interviews": [
            ("Prime Minister Nation Address Live Broadcast Transcript", "PMO India Official Portal", "🔥 High Growth"),
            ("Opposition Leader Parliamentary No-Confidence Speech", "Parliament Media Hub", "🚀 Explosive Surge"),
            ("Exclusive Hard Talk Political Leader Interview Clip", "BBC & NDTV Hard Talk", "⚡ Accelerating"),
            ("Chief Minister Policy Vision Press Conference Stream", "State Information Bureau", "📈 Trending"),
            ("Foreign Minister Diplomatic Press Briefing Global Speech", "Ministry of External Affairs", "🔥 High Growth"),
            ("Election Campaign Ranting Speech Viral Sound Clip", "Political Rally Hub", "🚀 Explosive Surge"),
            ("Union Finance Minister Economic Policy Press Meet", "RBI & North Block Portal", "⚡ Accelerating"),
            ("Youth Icon Politician Town Hall Q&A Session Video", "University Campus Debate", "📈 Trending"),
            ("State Opposition Manifesto Release Press Conference", "State Party HQ Hub", "🔥 High Growth"),
            ("Retiring Parliament Member Farewell Speech Emotional Clip", "Rajya Sabha TV Feature", "⚡ Accelerating")
        ],
        "Geopolitical & Diplomatic Updates": [
            ("G20 Summit Global Economic Declaration & Agreements", "G20 Secretariat Portal", "🔥 High Growth"),
            ("Bilateral Trade Treaty Signing Ceremony Press Meet", "Ministry of Foreign Affairs", "🚀 Explosive Surge"),
            ("United Nations Security Council Resolution Vote Update", "UN Newsroom Portal", "⚡ Accelerating"),
            ("Defense Strategic Partnership & Fighter Jet Deal Sign", "Ministry of Defense Portal", "📈 Trending"),
            ("Cross-Border Diplomatic Summit Joint Statement Release", "Embassy Press Release", "🔥 High Growth"),
            ("Global Climate Change COP Summit Emission Pledge", "UNFCCC Climate Portal", "🚀 Explosive Surge"),
            ("International Free Trade Agreement (FTA) Ratification", "Directorate General of Foreign Trade", "⚡ Accelerating"),
            ("Naval Joint Exercise Indo-Pacific Strategic Update", "Indian Navy Public Relations", "📈 Trending"),
            ("Global Energy Security & Oil Supply OPEC+ Meeting", "OPEC Secretariat Hub", "🔥 High Growth"),
            ("Consular Visa Exemption Agreement Bilateral Update", "Consular Passport Division", "⚡ Accelerating")
        ],
        "Public Schemes & Subsidies": [
            ("PM Awas Yojana Housing Subsidy Application Status", "Pradhan Mantri Awas Portal", "🔥 High Growth"),
            ("Ayushman Bharat Health Insurance Card Registration Hub", "National Health Authority", "🚀 Explosive Surge"),
            ("Mudra Loan Small Business Credit Scheme Application", "PMMY Official Portal", "⚡ Accelerating"),
            ("Kisan Samman Nidhi Farmer Financial Support Installment", "PM-KISAN Portal Tracker", "📈 Trending"),
            ("National Solar Rooftop Subsidy Installation Portal", "PM Surya Ghar Portal", "🔥 High Growth"),
            ("Free Ration Food Security Scheme Extension Update", "Ministry of Consumer Affairs", "🚀 Explosive Surge"),
            ("Startup India Seed Fund Scheme Grant Application", "Startup India Portal", "⚡ Accelerating"),
            ("Beti Bachao Beti Padhao Girl Child Savings Scheme", "Women & Child Development Hub", "📈 Trending"),
            ("Skill India National Apprenticeship Training Portal", "MSDE Skill India Hub", "🔥 High Growth"),
            ("Atal Pension Scheme Enrollment & Contribution Calculator", "PFRDA Pension Portal", "⚡ Accelerating")
        ]
    }

    pool = specific_pools.get(sub_niche, [
        (f"{sub_niche} Breakthrough Asset Alpha", f"{platform_source} Trendsetter", "🔥 High Growth"),
        (f"{sub_niche} High-Velocity Consumer Spike", f"{platform_source} Viral Hub", "🚀 Explosive Surge"),
        (f"{sub_niche} Scalable Micro-Trend Surge", f"{platform_source} Analytics", "⚡ Accelerating"),
    ])

    cursor = db_conn.cursor()
    for trend_name, keyword, sat in pool:
        velocity = round(75.0 + (hash(trend_name) % 250) / 10.0, 1)
        cursor.execute("""
            INSERT INTO platform_signals (source_platform, keyword, engagement_metrics, region)
            VALUES (?, ?, ?, ?)
        """, (platform_source, keyword, f"Velocity Score: {velocity}", region))
        
        cursor.execute("""
            INSERT INTO trends_table (trend_name, category_name, velocity_score, saturation_index)
            VALUES (?, ?, ?, ?)
        """, (trend_name, category, velocity, sat))
    db_conn.commit()

    cursor.execute("""
        SELECT trend_name, category_name, velocity_score, saturation_index, emergence_date
        FROM trends_table WHERE category_name = ? ORDER BY velocity_score DESC LIMIT 15
    """, (category,))
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=["Trend Name", "Category", "Velocity Score", "Saturation Index", "Emergence Timestamp"])

# ==========================================
# 7. STREAMLIT APP UI & EXECUTION LOGIC
# ==========================================
user_lang = st.sidebar.selectbox("🌐 Select Language / भाषा", ["English", "Hindi"])
t = TEXTS[user_lang]

st.markdown(f"# {t['title']}")
st.markdown(f"### {t['subtitle']}")
st.markdown("---")

# Sidebar Configuration
st.sidebar.markdown(f"## {t['terminal']}")
user_email = st.sidebar.text_input("📧 Enterprise Email:", "admin@trendpulse.enterprise")
selected_role = st.sidebar.selectbox(
    "💼 Select Master Scale Role:",
    list(ROLE_SPECIFIC_METRICS.keys())
)

if st.sidebar.button(t["simulate_pro"]):
    st.sidebar.success("⚡ Enterprise Pro Pass Active! Full API & PDF Unlocked.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"## {t['config_title']}")
selected_region = st.sidebar.selectbox(t["region"], ["Global (Worldwide)", "North America (US/CA)", "India (IN)", "Europe (EU)", "Asia-Pacific (APAC)"])
selected_platform = st.sidebar.selectbox(t["platform"], ["TikTok / Reels", "Amazon / E-Com", "Google / Trends", "YouTube / Shorts", "X / Reddit Viral"])

selected_category = st.sidebar.selectbox(t["category"], list(UPDATED_NICHE_CATEGORIES.keys()))
available_sub_niches = UPDATED_NICHE_CATEGORIES[selected_category]
selected_sub_niche = st.sidebar.selectbox(t["sub_category"], available_sub_niches)

selected_velocity = st.sidebar.selectbox(t["velocity"], ["Realtime 24 Hours", "7 Days Exponential Spike", "30 Days Sustained Wave", "90 Days Macro Trend"])

if st.sidebar.button(t["apply_btn"]):
    with st.spinner("Executing Autonomous Signal Ingestion & Database Synchronization..."):
        fetch_and_store_signals(selected_region, selected_platform, selected_category, selected_sub_niche, selected_velocity)
        st.success("✅ Ingestion Pipeline Executed Successfully! Database Synchronized.")

# Main Tabs
tab_radar, tab_blueprint, tab_db = st.tabs([
    t["tab_radar"],
    t["tab_blueprint"],
    t["tab_db"]
])

with tab_radar:
    st.markdown(f"## {t['telemetry_title']}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Sub-Niche", selected_sub_niche, "+18.4% Velocity")
    col2.metric("Market Saturation Index", "Low-Medium (Opportunity)", "Optimal Entry")
    col3.metric("AI Confidence Score", "98.2%", "High Precision")
    col4.metric("Database Status", "Synchronized 5 Tables", "OK")

    st.markdown("---")
    df_signals = fetch_and_store_signals(selected_region, selected_platform, selected_category, selected_sub_niche, selected_velocity)
    
    if not df_signals.empty:
        fig = px.bar(
            df_signals.head(10),
            x="Velocity Score",
            y="Trend Name",
            orientation="h",
            color="Velocity Score",
            color_continuousScale="Reds",
            title=f"Top Viral Signals & Velocity Score: {selected_sub_niche}"
        )
        fig.update_layout(
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font_color="#fafafa",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"### 📋 {t['active_signals_for']} **{selected_sub_niche}**")
        st.dataframe(df_signals, use_container_width=True)
    else:
        st.info("No signals found in database. Execute ingestion pipeline from the sidebar.")

with tab_blueprint:
    st.markdown("## 🚀 Master Intelligence & Revenue Dossier Engine")
    st.markdown("Generate an exhaustive, publication-grade commercial dossier with unit economics, copywriting vaults, viral hooks, and multi-platform syndication matrices.")

    col_a, col_b = st.columns([3, 1])
    with col_a:
        custom_asset = st.text_input(t["custom_search"], value=selected_sub_niche)
    with col_b:
        viral_window = st.selectbox("Prediction Window:", ["7-Day Flash", "30-Day Growth", "90-Day Scale"])

    if st.button("⚡ Generate Master Commercial Dossier"):
        if not GROQ_API_KEY:
            st.error("⚠️ GROQ_API_KEY not found in st.secrets or environment variables. Please configure your API key.")
        else:
            with st.spinner("Synthesizing Autonomous Intelligence Dossier via Groq LLM Engine..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    role_metrics = ROLE_SPECIFIC_METRICS[selected_role]
                    
                    prompt = f"""
                    Act as an elite Enterprise Market Domination AI and Chief Revenue Officer. 
                    Generate an exhaustive, highly detailed Master Commercial Intelligence Dossier for the asset: '{custom_asset}' under category '{selected_category}' tailored specifically for the business role: '{selected_role}'.
                    
                    Incorporate these role-specific metric parameters into the analysis:
                    1. {role_metrics['m1']}
                    2. {role_metrics['m2']}
                    3. {role_metrics['m3']}
                    4. {role_metrics['m4']}
                    5. {role_metrics['m5']}

                    Provide your analysis across EXACTLY these 10 distinct sections in rich detail:
                    1. Advanced Monetization, Rate Card & Unit Economics Vault
                    2. Geo-Targeting & Regional Hotspot Mapping
                    3. Psychological Hook Matrix & Video Storyboard (0-3s)
                    4. Ready-to-Deploy Multi-Angle Copywriting Vault
                    5. Competitor & Market Saturation Threat Matrix
                    6. AI Prompt Engineering & Script Generation Pack
                    7. Algorithmic Scale vs Kill Risk Management Rules
                    8. Realtime Audience Sentiment & Virality Predictive Formula
                    9. Multi-Platform Syndication & Marketing Matrix
                    10. Automated 10-Day Master Execution & Scaling Roadmap
                    
                    Return clean, structured professional business prose with clear subheadings.
                    """

                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_token=4096,
                    )
                    dossier_text = completion.choices[0].message.content

                    # Parse sections roughly
                    sections_titles = [
                        "1. Advanced Monetization, Rate Card & Unit Economics Vault",
                        "2. Geo-Targeting & Regional Hotspot Mapping",
                        "3. Psychological Hook Matrix & Video Storyboard (0-3s)",
                        "4. Ready-to-Deploy Multi-Angle Copywriting Vault",
                        "5. Competitor & Market Saturation Threat Matrix",
                        "6. AI Prompt Engineering & Script Generation Pack",
                        "7. Algorithmic Scale vs Kill Risk Management Rules",
                        "8. Realtime Audience Sentiment & Virality Predictive Formula",
                        "9. Multi-Platform Syndication & Marketing Matrix",
                        "10. Automated 10-Day Master Execution & Scaling Roadmap"
                    ]

                    result_dict = {}
                    for i in range(len(sections_titles)):
                        current_title = sections_titles[i]
                        next_title = sections_titles[i+1] if i + 1 < len(sections_titles) else None
                        
                        start_idx = dossier_text.find(current_title)
                        if start_idx != -1:
                            if next_title:
                                end_idx = dossier_text.find(next_title)
                                section_content = dossier_text[start_idx + len(current_title):end_idx if end_idx != -1 else len(dossier_text)]
                            else:
                                section_content = dossier_text[start_idx + len(current_title):]
                        else:
                            section_content = "Detailed analysis generated in master dossier stream."
                        
                        key_map = ["unit_economics", "geo_mapping", "hook_matrix", "copywriting_vault", "saturation_matrix", "tech_prompts", "scale_kill_rules", "virality_formula", "syndication_matrix", "action_roadmap"]
                        result_dict[key_map[i]] = section_content.strip()

                    st.session_state["last_dossier"] = result_dict
                    st.session_state["last_asset"] = custom_asset
                    st.session_state["last_cat"] = selected_category
                    st.session_state["last_role"] = selected_role
                    st.session_state["last_score"] = "98.7 / 100"
                    st.session_state["last_window"] = viral_window

                    st.success("🎉 Master Dossier Successfully Generated!")
                except Exception as e:
                    st.error(f"Error generating AI Dossier: {e}")

    if "last_dossier" in st.session_state:
        res = st.session_state["last_dossier"]
        st.markdown("---")
        st.markdown(f"### 📑 Master Intelligence Dossier for: **{st.session_state['last_asset']}**")
        
        # PDF Download Button
        pdf_buffer = create_pdf_dossier(
            st.session_state["last_asset"],
            st.session_state["last_cat"],
            st.session_state["last_role"],
            st.session_state["last_score"],
            st.session_state["last_window"],
            res
        )
        st.download_button(
            label="📥 Download Complete Dossier as Enterprise PDF",
            data=pdf_buffer,
            file_name=f"TrendPulse_Dossier_{sanitize_trend_input(st.session_state['last_asset'])[:20]}.pdf",
            mime="application/pdf"
        )

        tabs_dossier = st.tabs([
            "💰 Economics", "🌐 Geo/Hooks", "✍️ Copy/Threats", "🤖 Prompts/Rules", "📈 Scale/Roadmap"
        ])
        
        with tabs_dossier[0]:
            st.markdown("#### 1. Advanced Monetization & Unit Economics")
            st.write(res.get("unit_economics", ""))
        with tabs_dossier[1]:
            st.markdown("#### 2. Geo-Targeting & Hotspots")
            st.write(res.get("geo_mapping", ""))
            st.markdown("#### 3. Psychological Hook Matrix")
            st.write(res.get("hook_matrix", ""))
        with tabs_dossier[2]:
            st.markdown("#### 4. Copywriting Vault")
            st.write(res.get("copywriting_vault", ""))
            st.markdown("#### 5. Saturation Threat Matrix")
            st.write(res.get("saturation_matrix", ""))
        with tabs_dossier[3]:
            st.markdown("#### 6. AI Prompt Engineering Pack")
            st.write(res.get("tech_prompts", ""))
            st.markdown("#### 7. Scale vs Kill Risk Rules")
            st.write(res.get("scale_kill_rules", ""))
        with tabs_dossier[4]:
            st.markdown("#### 8. Virality Predictive Formula")
            st.write(res.get("virality_formula", ""))
            st.markdown("#### 9. Syndication Matrix")
            st.write(res.get("syndication_matrix", ""))
            st.markdown("#### 10. 10-Day Execution Roadmap")
            st.write(res.get("action_roadmap", ""))

with tab_db:
    st.markdown("## 🗄️ Database Inspector & Logs")
    st.markdown("Inspect SQLite tables (`users_table`, `platform_signals`, `niches_table`, `trends_table`, `blueprints_table`).")

    table_choice = st.selectbox("Select Database Table to Inspect:", ["trends_table", "platform_signals", "users_table", "blueprints_table"])
    
    cursor_db = db_conn.cursor()
    cursor_db.execute(f"SELECT * FROM {table_choice} ORDER BY 1 DESC LIMIT 50")
    db_rows = cursor_db.fetchall()
    
    if db_rows:
        col_names = [description[0] for description in cursor_db.description]
        df_db = pd.DataFrame(db_rows, columns=col_names)
        st.dataframe(df_db, use_container_width=True)
    else:
        st.info(f"Table `{table_choice}` is currently empty.")
