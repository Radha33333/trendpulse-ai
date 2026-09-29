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

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

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
        CREATE TABLE IF NOT EXISTS platform_signals (
            signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_platform TEXT,
            keyword TEXT,
            engagement_metrics TEXT,
            region TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        "live_sync": "⚡ Live API Connected & Synced",
    }
}
t = TEXTS["English"]

# ==========================================
# 4. COMPREHENSIVE SUB-NICHE DATA ENGINE (ALL 120 SUB-NICHES COVERED)
# ==========================================
MASTER_SUB_NICHE_POOLS = {
    # E-Commerce
    "TikTok Shop & Live Deals": [("Flash Drop: Korean Skincare Bundle", "Laneige & Innisfree", "🚀 Explosive Surge"), ("Viral Sunset Projector Lamp Restock", "RGB Ambient", "🔥 High Growth"), ("Portable Neck Fan Heatwave Special", "JisuLife Fans", "⚡ Accelerating"), ("Corduroy Tote Bags College Drop", "Minimalist Canvas", "📈 Trending"), ("Mini Wireless Car Vacuum Sellout", "Baseus Auto", "🔥 High Growth")],
    "Amazon Hot Movers & Bestsellers": [("Smart LED Desk Lamp Wireless Charger", "BenQ & TaoTronics", "🔥 High Growth"), ("Electric Toothbrush Sonic Wave", "Philips Sonicare", "🚀 Explosive Surge"), ("Compact Dehumidifier Small Rooms", "Pro Breeze", "⚡ Accelerating"), ("Magnetic Power Bank Magsafe", "Anker MagGo", "📈 Trending"), ("Dermatologist Retinol Serum Surge", "CeraVe", "🔥 High Growth")],
    "D2C Breakout & DTC Brands": [("Matcha Ceremonial Grade Green Tea", "Teabloom & Tenzo", "🚀 Explosive Surge"), ("Non-Toxic Ceramic Cookware Expansion", "Our Place Always Pan", "🔥 High Growth"), ("Micro-Exfoliating Body Wash", "Nécessaire", "⚡ Accelerating"), ("Bamboo Bedding Sheets", "Boll & Branch", "📈 Trending"), ("Functional Mushroom Coffee Boom", "Four Sigmatic", "🔥 High Growth")],
    "Problem-Solver Gadgets": [("Keyless Smart Door Lock Fingerprint", "Eufy Security", "🔥 High Growth"), ("Automatic Self-Cleaning Litter Box", "Litter-Robot 4", "🚀 Explosive Surge"), ("Cordless Electric Spin Scrubber", "Rubbermaid Reveal", "⚡ Accelerating"), ("Tile Bluetooth Smart Tracker Pack", "Tile Pro Series", "📈 Trending"), ("Solar-Powered Security Camera", "Ring Floodlight", "🔥 High Growth")],
    "Print-on-Demand & Custom Merch": [("Vintage Graphic Oversized Tee Drop", "Streetwear Custom", "🔥 High Growth"), ("Embossed Leather Passport Holder", "Monogram Studio", "🚀 Explosive Surge"), ("Acrylic Spotify Song Plaque", "CustomTune", "⚡ Accelerating"), ("Line Art Pet Portrait Canvas", "Pawprint Prints", "📈 Trending"), ("Custom Neon Name Sign LED Decor", "GlowingVibes", "🔥 High Growth")],
    "Upcoming High-Demand Drops": [("Next-Gen AR Smart Glasses Pre-Order", "Ray-Ban Meta Gen 2", "🚀 Explosive Surge"), ("Limited Liquid Cooling PC Case", "Lian Li Dynamic Evo", "🔥 High Growth"), ("AI Smart Plant Care Monitor", "PlantIn Sensor Pro", "⚡ Accelerating"), ("Modular Travel Jacket Neck Pillow", "BAUBAX Ultimate", "📈 Trending"), ("Biodegradable Sneaker Line Drop", "Allbirds Tree Dasher 3", "🔥 High Growth")],

    # Real Estate
    "Rental Yield Hotspots": [("IT Corridor Studio Apartment Yield", "Whitefield, Bengaluru", "🔥 High Growth"), ("Suburban Gated Villa Community Rental", "Gachibowli, Hyderabad", "🚀 Explosive Surge"), ("Commercial High-Street Retail Leasing", "Bandra West, Mumbai", "⚡ Accelerating"), ("Student Housing PG Asset Investment", "North Campus, Delhi", "📈 Trending"), ("IT Park Adjoining 2BHK Rental Demand", "Hinjewadi, Pune", "🔥 High Growth")],
    "PropTech & Smart Homes": [("IoT Centralized HVAC Automation Hub", "Schneider Electric Wiser", "🔥 High Growth"), ("AI Security Camera Facial Recognition", "Hikvision Smart", "🚀 Explosive Surge"), ("Motorized Curtain Integration", "Somfy Smart Motor", "⚡ Accelerating"), ("Digital Intercom Video Door Phone", "Godrej SmartHome", "📈 Trending"), ("Smart Water Flow Meter Leak Valve", "Flo by Moen", "🔥 High Growth")],
    "Luxury Estates & Villas": [("Cliffside Panoramic Ocean View Villa", "Assagao, Goa", "🔥 High Growth"), ("Ultra-Luxury Golf Course Estate Drop", "DLF Phase 5, Gurugram", "🚀 Explosive Surge"), ("Heritage Bungalow Restoration Wave", "Alipore, Kolkata", "⚡ Accelerating"), ("Private Island Gated Community Plot", "Kochi Backwaters", "📈 Trending"), ("Super-Luxury Skyscraper Penthouse", "Worli Sea Face, Mumbai", "🔥 High Growth")],
    "Commercial & Co-Working Spaces": [("Managed Enterprise Office Floor Leasing", "WeWork BKC, Mumbai", "🔥 High Growth"), ("Grade-A Tech Park Office Absorption", "Manyata Tech Park, BLR", "🚀 Explosive Surge"), ("High-Street Retail Showroom Leasing", "Connaught Place, Delhi", "⚡ Accelerating"), ("Flexi-Desk Co-Working Hub Expansion", "Cyber City, Gurugram", "📈 Trending"), ("Startup Incubator Plug-and-Play Lease", "Koramangala Hub, BLR", "🔥 High Growth")],
    "Fractional Real Estate & REITs": [("Commercial Grade-A Office REIT Dividend", "Embassy Office REIT", "🔥 High Growth"), ("Retail Mall Fractional Ownership", "Phoenix Mills REIT", "🚀 Explosive Surge"), ("Warehouse Logistics Park Tokenization", "StashAway PropTech", "⚡ Accelerating"), ("Hospitality Hotel REIT Expansion", "Lemon Tree Portfolio", "📈 Trending"), ("Commercial Realty Crowdfunding Drop", "PropertyShare Portal", "🔥 High Growth")],
    "Upcoming Transit & Metro Hubs": [("Metro Station Commercial Property Spike", "Central Secretariat, Delhi", "🔥 High Growth"), ("High-Speed Rail Corridor Appreciation", "Mumbai-Ahmedabad Bullet Train", "🚀 Explosive Surge"), ("Airport Express Residential Boom", "Aerocity Link, New Delhi", "⚡ Accelerating"), ("Outer Ring Road Metro Real Estate", "ORR Metro, Bengaluru", "📈 Trending"), ("Suburban Circular Railway Hub Investment", "Panvel Transit Hub, Mumbai", "🔥 High Growth")],

    # Automobile
    "EV Launches & Battery Tech": [("Solid-State Battery Range Breakthrough", "Tata Motors EV R&D", "🚀 Explosive Surge"), ("Affordable Long-Range Electric SUV", "Mahindra BE.6", "🔥 High Growth"), ("Fast-Charging Cell Production Milestone", "Ola Electric Gigafactory", "⚡ Accelerating"), ("Electric Two-Wheeler Subsidy Wave", "Ather Rizta & Ola S1", "📈 Trending"), ("Commercial Electric Delivery Van Fleet", "Tata Ace EV", "🔥 High Growth")],
    "ADAS, Dashcams & Smart Tech": [("Dual-Channel 4K GPS Dashcam Review", "70mai & Qubo Dashcam", "🔥 High Growth"), ("ADAS Retrofit Kit Integration", "Mobility AI Suite", "🚀 Explosive Surge"), ("Blind Spot Detection Sensor Drop", "Bosch Automotive Tech", "⚡ Accelerating"), ("AI Smart Rearview Mirror Display", "Foxbox Auto Mirror", "📈 Trending"), ("OBD-II Realtime Diagnostics Scanner", "Veepeak Bluetooth OBD", "🔥 High Growth")],
    "Car & Bike Accessories / Gadgets": [("Portable High-Pressure Cordless Washer", "Karcher & Baseus", "🔥 High Growth"), ("Magnetic Wireless Smartphone Mount", "Spigen MagFit", "🚀 Explosive Surge"), ("Ergonomic Car Neck Pillow & Cushion", "Trax & Autofurnish", "⚡ Accelerating"), ("Motorcycle Bluetooth Helmet Intercom", "Cardo Packtalk Edge", "📈 Trending"), ("Ambient Interior LED Strip Lighting", "Govee Car LED", "🔥 High Growth")],
    "Auto Reviews & Mileage Hacks": [("Real-World Fuel Economy & Mileage Test", "Autocar India", "🔥 High Growth"), ("Compact SUV Comparison & Value Test", "Brezza vs Nexon", "🚀 Explosive Surge"), ("Engine Decarbonization Mileage Hack", "GoMechanic Service", "⚡ Accelerating"), ("Hybrid vs Petrol Cost Analysis", "Grand Vitara & Hyryder", "📈 Trending"), ("Second-Hand Diesel SUV Guide", "Big Boy Toyz & Spinny", "🔥 High Growth")],
    "Custom Bike & Supercar Buzz": [("Custom Cafe Racer Build Showcase", "Royal Enfield Interceptor Mod", "🔥 High Growth"), ("Supercar V12 Exhaust Sound Run", "Lamborghini Revuelto", "🚀 Explosive Surge"), ("Matte PPF Wrap & Ceramic Coating", "3M Car Care Studio", "⚡ Accelerating"), ("Track-Day Superbike Carbon Fairings", "Ducati Panigale V4R", "📈 Trending"), ("Off-Road Rally Modification Build", "Modified Isuzu V-Cross", "🔥 High Growth")],
    "Commuter Vehicle Price Drops": [("Festive Clearance Discount Hatchbacks", "Maruti Swift & WagonR", "🔥 High Growth"), ("Entry-Level Commuter Bike Price Slash", "Hero Splendor Deals", "🚀 Explosive Surge"), ("Compact Sedan Corporate Discount", "Hyundai Aura & Tata Tigor", "⚡ Accelerating"), ("Inventory Clearance Electric Scooters", "Bajaj Chetak & TVS iQube", "📈 Trending"), ("Pre-Owned Commuter Car Correction", "CarDekho & Spinny", "🔥 High Growth")],

    # Parenting & Kids
    "Baby Gear & Smart Strollers": [("AI Smart Baby Stroller Self-Driving Push", "GlüxKind Ella", "🚀 Explosive Surge"), ("Convertible Wooden High Chair Trend", "Stokke Tripp Trapp", "🔥 High Growth"), ("Ergonomic Baby Hipseat Carrier Launch", "LÍLLÉbaby Complete", "⚡ Accelerating"), ("Compact Travel Lightweight Pram Drop", "Babyzen Yoyo 3", "📈 Trending"), ("Smart Video Baby Monitor Heart Rate Track", "Owlet Dream Duo", "🔥 High Growth")],
    "Early Childhood EdTech & Toys": [("Montessori Wooden Sorting Toys", "Lovevery Play Kits", "🔥 High Growth"), ("Interactive STEM Coding Robot for Kids", "Sphero Mini Edu", "🚀 Explosive Surge"), ("Audio Storytelling Pod Device Surge", "Yoto Player & Tonies", "⚡ Accelerating"), ("Augmented Reality Alphabet Cards", "Shifu Orboot", "📈 Trending"), ("Eco-Friendly Building Blocks Set", "Magna-Tiles Pro", "🔥 High Growth")],
    "Modern Parenting & Routine Hacks": [("Gentle Sleep Training Audio Program", "Taking Cara Babies", "🔥 High Growth"), ("Bento Box School Lunch Prep Containers", "PlanetBox Rover", "🚀 Explosive Surge"), ("Toddler Emotion Regulation Flashcards", "Big Life Journal", "⚡ Accelerating"), ("Minimalist Nursery Wardrobe Capsule", "Hanna Andersson Baby", "📈 Trending"), ("Digital Family Schedule Wall Calendar", "Skylight Calendar", "🔥 High Growth")],
    "Kids Nutrition & Organic Foods": [("Cold-Pressed Organic Baby Puree Pouches", "Serenity Kids Meals", "🔥 High Growth"), ("Toddler Multivitamin Immunity Gummies", "Hiya Health Kids", "🚀 Explosive Surge"), ("Allergen Introduction Peanut Butter Mix", "Lil Mixins Pack", "⚡ Accelerating"), ("Plant-Based Kids Protein Shake Launch", "Ripple Kids Milk", "📈 Trending"), ("Zero-Sugar Electrolyte Hydration Cubes", "KinderMed Hydrate", "🔥 High Growth")],
    "Maternity & Postpartum Care": [("Postpartum Recovery Herbal Sitz Bath", "Frida Mom Kit", "🔥 High Growth"), ("High-Waist Supportive Maternity Leggings", "Belly Bandit Active", "🚀 Explosive Surge"), ("Electric Hands-Free Wearable Breast Pump", "Elvie & Willow Go", "⚡ Accelerating"), ("Organic Nursing Pillow Ergonomic Support", "Boppy Luxe", "📈 Trending"), ("Stretch Mark Prevention Belly Butter", "Burt's Bees Mama", "🔥 High Growth")],
    "Family Lifestyle & Travel Gear": [("Expandable Family Cabin Luggage Set", "Monos Carry-On Pro", "🔥 High Growth"), ("Inflatable Airplane Travel Bed for Toddlers", "PlanePal Seat", "🚀 Explosive Surge"), ("Portable UV Sterilizer Sanitizer Wand", "Hiccapop Pod", "⚡ Accelerating"), ("Leakproof Family Picnic Cooler Backpack", "YETI Hopper BackFlip", "📈 Trending"), ("Kids Ride-On Suitcase Travel Companion", "Trunki Original", "🔥 High Growth")],

    # Pets
    "Pet Health & Nutrition": [("Grain-Free Raw Freeze-Dried Dog Food", "Stella & Chewy's", "🔥 High Growth"), ("Joint Support Glucosamine Chewable Treats", "Zesty Paws Mobility", "🚀 Explosive Surge"), ("Probiotic Digestive Health Powder", "Purina Pro Plan FortiFlora", "⚡ Accelerating"), ("Organic Salmon Oil Skin & Coat Booster", "Zesty Paws Omega", "📈 Trending"), ("Veterinary Formula Calming Anxiety Drops", "VetriScience Composure", "🔥 High Growth")],
    "Dog & Cat Training Hacks": [("Interactive Puzzle Feeder Slow Bowl", "Outward Hound", "🔥 High Growth"), ("Clicker Training Professional Kit", "Karen Pryor Clicker", "🚀 Explosive Surge"), ("Anti-Bark Ultrasonic Training Device", "Modus Ultrasonic", "⚡ Accelerating"), ("Cat Scratching Cardboard Lounge Pad", "PetFusion Mega", "📈 Trending"), ("Professional Pet Agility Training Tunnel", "Outward Hound Active", "🔥 High Growth")],
    "Smart Pet Accessories & Tech": [("Automatic Wi-Fi Pet Feeder HD Camera", "PetSafe Smart Feed", "🔥 High Growth"), ("GPS Smart Collar Activity Tracker", "Fi Series 3 Collar", "🚀 Explosive Surge"), ("Smart Self-Cleaning Water Fountain", "Petlibro Capsule", "⚡ Accelerating"), ("App-Controlled Laser Toy for Cats", "Wicked Mouse Ball", "📈 Trending"), ("Smart Microchip Pet Door Access", "SureFlap Connect", "🔥 High Growth")],
    "Cute & Funny Pet Virals": [("Talking Pet Button Communication Set", "FluentPet HexTiles", "🔥 High Growth"), ("Funny Shark Costume Hoodie for Cats", "Frisco Apparel", "🚀 Explosive Surge"), ("Cat Window Hammock Suction Perch", "K&H Pet Products", "⚡ Accelerating"), ("Doggie GoPro Harness Mount Strap", "Fetch Mount", "📈 Trending"), ("Interactive Flapping Bird Cat Teaser", "Flapping Duck Toy", "🔥 High Growth")],
    "Grooming & Hygiene Products": [("Deshedding Undercoat Grooming Brush", "FURminator Tool", "🔥 High Growth"), ("Waterless Dry Shampoo Foam for Dogs", "Burt's Bees Grooming", "🚀 Explosive Surge"), ("Odor-Eliminating Bamboo Pet Wipes", "Earth Rated Wipes", "⚡ Accelerating"), ("Professional Pet Nail Grinder Electric", "Casfuy Silent Grinder", "📈 Trending"), ("Organic Oatmeal Anti-Itch Pet Shampoo", "Earthbath Oatmeal", "🔥 High Growth")],
    "Breed Guides & Adoption Signals": [("Golden Retriever Puppy Socialization Guide", "AKC Breed Standard", "🔥 High Growth"), ("Rescue Cat Integration Shelter Adoption", "Petfinder Local Hub", "🚀 Explosive Surge"), ("French Bulldog Health & Breathing Care", "Frenchie Club", "⚡ Accelerating"), ("German Shepherd Working Line Training", "K9 Police Standard", "📈 Trending"), ("Adopt Don't Shop Shelter Awareness Drive", "PETA Rescue", "🔥 High Growth")],

    # Finance & Crypto
    "Credit Card & Reward Hacks": [("Lifetime Free Reward Credit Card Upgrade", "HDFC Regalia & Amex", "🔥 High Growth"), ("Airport Lounge Access Milestone Hack", "ICICI Sapphiro Cards", "🚀 Explosive Surge"), ("Fuel Surcharge Waiver Optimization", "SBI Octane Card", "⚡ Accelerating"), ("UPI Credit Card Linking Cashback Surge", "Axis Bank Rupay", "📈 Trending"), ("International Forex Zero Markup Card", "Niyo Global & Fi", "🔥 High Growth")],
    "Stock Market & Algo Trading Bots": [("Nifty 50 Intraday Breakout Level", "Nifty 50 Index", "🔥 High Growth"), ("Bank Nifty Options Chain Open Interest", "Bank Nifty Futures", "🚀 Explosive Surge"), ("Algorithmic Momentum Crossover Bot", "Quant Scalpers Bot", "⚡ Accelerating"), ("FII/DII Net Cash Flow Reversal", "NSE Institutional Flow", "📈 Trending"), ("Smallcap Sector Rotation Accumulation", "BSE Smallcap Index", "🔥 High Growth")],
    "Crypto & Web3 Signals": [("Bitcoin Halving On-Chain Liquidity Flow", "BTC Whale Tracker", "🔥 High Growth"), ("Layer-2 Gas Fee Optimization Surge", "Arbitrum & Optimism", "🚀 Explosive Surge"), ("Solana Memecoin Volume Accumulation", "Raydium & Jupiter DEX", "⚡ Accelerating"), ("DeFi Staking Yield APY Rebalancing", "Lido Finance StETH", "📈 Trending"), ("Bitcoin ETF Institutional Inflows", "BlackRock iShares BTC", "🔥 High Growth")],
    "Side Hustles & Passive Income": [("Digital Notion Template E-Commerce Store", "Gumroad Creator Hub", "🔥 High Growth"), ("Automated YouTube Faceless Channel Agency", "VidIQ AI Suite", "🚀 Explosive Surge"), ("Freelance AI Prompt Engineering Gig Spike", "Upwork Enterprise Pool", "⚡ Accelerating"), ("Print-on-Demand Passive Store Setup", "Printify & Shopify", "📈 Trending"), ("Substack Paid Newsletter Monetization", "Substack Writer Growth", "🔥 High Growth")],
    "Personal Tax & Saving Strategies": [("New Tax Regime Deduction Optimization", "ClearTax Portal Guide", "🔥 High Growth"), ("ELSS Tax Saver Mutual Fund SIP Spike", "Groww & Zerodha Coin", "🚀 Explosive Surge"), ("HRA Claim & Rent Receipt Automation", "Tax2Win Portal", "⚡ Accelerating"), ("Capital Gains Tax Harvesting Strategy", "ET Money Wealth", "📈 Trending"), ("NPS Tier-1 Additional Tax Rebate Hack", "National Pension System", "🔥 High Growth")],
    "Real Estate & Fractional Investing": [("Commercial Realty Fractional Yield Syndicate", "hBits Property Share", "🔥 High Growth"), ("REIT Dividend Payout Yield Analysis", "Embassy & Mindspace", "🚀 Explosive Surge"), ("Real Estate Crowdfunding Portal Spike", "PropertyShare India", "⚡ Accelerating"), ("Land Banking Micro-Market Investment", "North Goa Land Syndicate", "📈 Trending"), ("Co-Living Asset Syndication Fund", "Zolo PropTech Yield", "🔥 High Growth")],

    # Business
    "Startup Funding & Pitch Decks": [("Seed Round VC Term Sheet Playbook", "Y Combinator Safe Deck", "🔥 High Growth"), ("AI Startup Pitch Deck Valuation Metric", "Sequoia Capital", "🚀 Explosive Surge"), ("Angel Investor Syndicate Network Drop", "LetsVenture & AngelList", "⚡ Accelerating"), ("Series A Revenue Milestone & Burn Multiple", "Bessemer Cloud Index", "📈 Trending"), ("Bootstrapped to Multi-Million ARR Founder", "Indie Hackers Podcast", "🔥 High Growth")],
    "Solopreneur & One-Person Business": [("One-Person Multi-Million Dollar SaaS", "Pieter Levels Blueprint", "🔥 High Growth"), ("Solopreneur Tech Stack Automated Workflow", "Make.com & Airtable", "🚀 Explosive Surge"), ("Micro-Agency Scaling with Zero Hires", "Double Your Freelancing", "⚡ Accelerating"), ("Digital Product Storefront Conversion Rate", "Gumroad & Lemon Squeezy", "📈 Trending"), ("Personal Brand Content Distribution Engine", "AuthoredUp & Typefully", "🔥 High Growth")],
    "AI Automation Agencies (AAA)": [("Voice AI Agent Lead Generation Bot Setup", "Vapi & Retell AI", "🔥 High Growth"), ("Custom LLM RAG Knowledge Base Deployment", "LangChain & Pinecone", "🚀 Explosive Surge"), ("Customer Support Chatbot Agency Blueprint", "Voiceflow & Make.com", "⚡ Accelerating"), ("AI Content Repurposing Workflow Agency", "Opus Clip & Castmagic", "📈 Trending"), ("Lead Scoring AI Pipeline Automation", "HubSpot + OpenAI", "🔥 High Growth")],
    "Freelancing & Agency Scaling": [("Upwork Top Rated Plus Proposal Template", "Upwork Scaling Guide", "🔥 High Growth"), ("Freelancer to 7-Figure Agency Owner", "Bureau of Digital Playbook", "🚀 Explosive Surge"), ("High-Ticket Retainer Client Acquisition", "Agency Growth Accelerator", "⚡ Accelerating"), ("Subcontractor Management & Offshore Talent", "OnlineJobs.ph & Upwork", "📈 Trending"), ("Creative Agency Client Onboarding Portal", "Bonsai & Dubsado", "🔥 High Growth")],
    "Growth Hacking & B2B Marketing": [("Viral Loop Product-Led Growth Architecture", "Reforge Growth Series", "🔥 High Growth"), ("B2B Cold Email Deliverability & Warmup", "Instantly & Warmup", "🚀 Explosive Surge"), ("LinkedIn Personal Branding Ghostwriting Stack", "Taplio & Shield App", "⚡ Accelerating"), ("Programmatic SEO Content Scaling Blueprint", "Ahrefs & WordPress", "📈 Trending"), ("Interactive Product Demo Funnel Spike", "Toucan & Navattic", "🔥 High Growth")],
    "E-Commerce Supply Chain & Fulfillment": [("Third-Party Logistics Same-Day Fulfillment", "Delhivery & Shiprocket", "🔥 High Growth"), ("Cross-Border D2C Freight Forwarding", "Flexport & Freightos", "🚀 Explosive Surge"), ("Warehouse Inventory Management Software", "Fishbowl & Katana", "⚡ Accelerating"), ("Sustainable Biodegradable Packaging Supply", "EcoEnclose Bulk Hub", "📈 Trending"), ("Amazon FBA Preparation Center Service", "FBA Prep Logistics", "🔥 High Growth")],

    # Digital Products & AI Tools
    "Vibe Coding & Code Extensions": [("Cursor IDE AI Pair Programming Mastery", "Cursor AI & Claude 3.5", "🔥 High Growth"), ("GitHub Copilot Workspace Integration", "GitHub Copilot", "🚀 Explosive Surge"), ("AI Refactoring & Code Analysis Extension", "CodiumAI & Tabnine", "⚡ Accelerating"), ("Natural Language Full-Stack App Generation", "v0 by Vercel & Bolt.new", "📈 Trending"), ("Automated Unit Test Generation AI Plugin", "Jest & Codium", "🔥 High Growth")],
    "Generative AI & SaaS Tools": [("Cinematic Text-to-Video AI Model Spike", "OpenAI Sora & Runway Gen-3", "🔥 High Growth"), ("Advanced Voice Cloning & Multilingual Dubbing", "ElevenLabs V3 Studio", "🚀 Explosive Surge"), ("AI Presentation Deck Instant Generation", "Gamma App & Tome", "⚡ Accelerating"), ("Professional AI Headshot Studio Generator", "Photoleap & Aragon", "📈 Trending"), ("AI Meeting Transcription & Summarizer", "Fireflies.ai & Otter.ai", "🔥 High Growth")],
    "Notion & Productivity Dashboards": [("Ultimate Second Brain Productivity Notion", "Tiago Forte Framework", "🔥 High Growth"), ("Notion Creator Business OS & Tracker", "Pana Workplace Template", "🚀 Explosive Surge"), ("Student Academic Planner & Grade Tracker", "Notion Campus Hub", "⚡ Accelerating"), ("AI-Integrated Notion Project Management", "Notion AI Workspace", "📈 Trending"), ("Freelance Client CRM Notion Kit", "Solopreneur Notion OS", "🔥 High Growth")],
    "Digital Ebooks & Online Courses": [("Mastering AI Prompt Engineering Ebook", "Gumroad Best Seller", "🔥 High Growth"), ("Solopreneur $10K/Month Business Course", "Skool Community Hub", "🚀 Explosive Surge"), ("High-Ticket Closing & Sales Psychology", "Sabri Suby Series", "⚡ Accelerating"), ("Advanced Python Algorithmic Trading", "QuantConnect Ebook", "📈 Trending"), ("YouTube Automation Masterclass", "Tube Mastery Academy", "🔥 High Growth")],
    "UI/UX Templates & Prompt Packs": [("Figma SaaS Design System & UI Kit", "Untitled UI & Shadcn", "🔥 High Growth"), ("ChatGPT Master Prompt Engineering Bundle", "PromptBase Verified", "🚀 Explosive Surge"), ("Mobile App iOS 18 & Material 3 UI Kit", "Designmodo UI Vault", "⚡ Accelerating"), ("Midjourney v6 Photorealistic Prompt Library", "AI Artist Vault", "📈 Trending"), ("Landing Page Tailwind CSS Templates", "Tailwind UI & Cruip", "🔥 High Growth")],
    "No-Code App Builders & Micro-Tools": [("Bubble.io Full-Stack No-Code Masterclass", "Bubble Academy Hub", "🔥 High Growth"), ("Webflow Enterprise Design & CMS Spike", "Webflow Showcase", "🚀 Explosive Surge"), ("Make.com Multi-App Automation Blueprint", "Automation Agency", "⚡ Accelerating"), ("FlutterFlow Native Mobile App Builder", "FlutterFlow Studio", "📈 Trending"), ("Airtable Relational Database App Builder", "Airtable Apps Hub", "🔥 High Growth")],

    # Education
    "Govt Exam Dates & Prep Hacks": [("UPSC Civil Services Prelims Admit Card", "UPSC Portal", "🔥 High Growth"), ("Banking IBPS PO Exam Preparation Strategy", "Testbook Mock", "🚀 Explosive Surge"), ("SSC CGL Tier-1 Exam Syllabus Analysis", "Staff Selection Commission", "⚡ Accelerating"), ("JEE Advanced Engineering Roadmap", "NTA JEE Portal", "📈 Trending"), ("NEET Medical Entrance Mock Test Series", "Allen & Aakash", "🔥 High Growth")],
    "AI Upskilling & Tech Roadmaps": [("Generative AI & LLM Engineer Roadmap", "DeepLearning.AI", "🔥 High Growth"), ("Full-Stack AI Developer Bootcamp", "Scaler & UpGrad", "🚀 Explosive Surge"), ("Data Science & Machine Learning Path", "Kaggle", "⚡ Accelerating"), ("Cybersecurity & Ethical Hacking Course", "EC-Council", "📈 Trending"), ("Cloud Computing AWS & Azure Architect", "A Cloud Guru", "🔥 High Growth")],
    "Study Abroad Scholarships & Visas": [("US F-1 Student Visa Slot Availability", "US Travel Docs", "🔥 High Growth"), ("UK Post-Study Work Visa Policy", "British Council UK", "🚀 Explosive Surge"), ("Germany Tuition-Free University Guide", "DAAD Portal", "⚡ Accelerating"), ("Canada Study Permit SDS Stream Update", "CIC Canada", "📈 Trending"), ("Erasmus Mundus Master Scholarship List", "European Commission", "🔥 High Growth")],
    "Resume, Portfolio & Interview Hacks": [("ATS-Friendly Resume Template & Optimizer", "Novoresume & Teal", "🔥 High Growth"), ("Developer Portfolio Website Template", "Vercel Kit", "🚀 Explosive Surge"), ("STAR Method Behavioral Interview Guide", "Interview Query", "⚡ Accelerating"), ("LinkedIn Profile Optimization & Headline", "AuthoredUp", "📈 Trending"), ("Tech FAANG Coding Interview Prep", "LeetCode & NeetCode", "🔥 High Growth")],
    "Remote Job & Hiring Alerts": [("Top Remote Tech Companies Hiring Now", "We Work Remotely", "🔥 High Growth"), ("Async Remote Software Engineering Jobs", "Toptal", "🚀 Explosive Surge"), ("Remote Customer Success Hiring Surge", "HubSpot", "⚡ Accelerating"), ("AI Training Remote Freelance Gigs", "Outlier AI", "📈 Trending"), ("Remote Product Design Agency Openings", "Dribbble Jobs", "🔥 High Growth")],
    "College Campus & Placement Trends": [("Campus Placement Tech Package Trends", "IIT Placement Reports", "🔥 High Growth"), ("College Hackathon Winning Strategy", "Devpost Portal", "🚀 Explosive Surge"), ("Student Entrepreneurship Grant", "Startup India Hub", "⚡ Accelerating"), ("Cultural Fest Sponsorship Trend", "Mood Indigo", "📈 Trending"), ("D2C Campus Ambassador Program Launch", "Red Bull Campus", "🔥 High Growth")],

    # Sustainability
    "Solar Power & Home Energy": [("PM Surya Ghar Rooftop Solar Subsidy", "PM Surya Ghar Yojana", "🔥 High Growth"), ("Hybrid Solar Inverter & Battery Storage", "Growatt & Luminous", "🚀 Explosive Surge"), ("Portable Solar Generator for Camping", "Jackery Explorer", "⚡ Accelerating"), ("Bifacial Solar Panel High-Efficiency", "Adani & Waaree", "📈 Trending"), ("Solar Water Heater Residential Upgrade", "V-Guard Solar", "🔥 High Growth")],
    "Zero-Waste Lifestyle & Reusables": [("Reusable Silicone Food Storage Bag Kit", "Stasher Bags", "🔥 High Growth"), ("Zero-Waste Shampoo Bar Solid Set", "Ethique Sustainable", "🚀 Explosive Surge"), ("Compostable Bamboo Toothbrush Pack", "The Bam & Boo Co.", "⚡ Accelerating"), ("Organic Cotton Produce Bags Set", "Simple Ecology", "📈 Trending"), ("Countertop Electric Kitchen Composter", "Lomi Composter", "🔥 High Growth")],
    "Organic & Sustainable Fashion": [("100% Organic Cotton Oversized Hoodie", "Pact & Organic Basics", "🔥 High Growth"), ("Recycled Ocean Plastic Sneaker Drop", "Rothy's & Adidas", "🚀 Explosive Surge"), ("Hemp Fabric Eco-Friendly Casual Wear", "Wama & Jungmaven", "⚡ Accelerating"), ("Second-Hand Vintage Thrift Marketplace", "Depop & Grailed", "📈 Trending"), ("Fair Trade Certified Denim Jacket", "Nudie Jeans Co.", "🔥 High Growth")],
    "Clean Tech & Carbon Offsets": [("Corporate Carbon Footprint Tracking SaaS", "Persefoni & Watershed", "🔥 High Growth"), ("Verified Direct Air Capture Carbon Credit", "Climeworks", "🚀 Explosive Surge"), ("Green Hydrogen Energy Plant Investment", "Reliance Green Energy", "⚡ Accelerating"), ("Blockchain Tree Planting Carbon Offset", "Pachama Forest", "📈 Trending"), ("Industrial Waste Heat Recovery System", "Alfa Laval", "🔥 High Growth")],
    "Eco-Friendly Packaging Solutions": [("Mushroom Mycelium Biodegradable Box", "Ecovative Design", "🔥 High Growth"), ("Compostable Bubble Mailer Envelope Pack", "EcoEnclose", "🚀 Explosive Surge"), ("Water-Activated Paper Packaging Tape", "Shurtape Eco-Tape", "⚡ Accelerating"), ("Recycled Kraft Paper Honeycomb Wrap", "Geami Packaging", "📈 Trending"), ("Plant-Based Cornstarch Mailing Bag", "BioBag International", "🔥 High Growth")],
    "Electric Mobility & Micro-Transit": [("Lightweight Foldable Electric Scooter", "Xiaomi Scooter 4 Pro", "🔥 High Growth"), ("Urban Electric Cargo Bike Family Transport", "Rad Power RadWagon", "🚀 Explosive Surge"), ("Electric Assist Pedal Bicycle Commuter", "Lectric XP 3.0", "⚡ Accelerating"), ("Smart Electric Skateboard Cruiser", "Boosted Board", "📈 Trending"), ("Shared Micro-Mobility Fleet Hub", "Lime & Bird", "🔥 High Growth")],

    # Movies & OTT
    "Box Office Collections & Predictions": [("Blockbuster Opening Weekend Box Office", "Pan-India Release", "🔥 High Growth"), ("Advance Booking Ticket Sales Tracker", "BookMyShow", "🚀 Explosive Surge"), ("Global Worldwide Gross Collection Milestone", "Box Office Mojo", "⚡ Accelerating"), ("Weekend vs Weekday Box Office Retention", "Trade Analyst", "📈 Trending"), ("Regional Cinema Blockbuster Surge", "Mollywood Hit", "🔥 High Growth")],
    "OTT Releases & Platform Buzz": [("Netflix Global Top 10 Series Drop", "Netflix Original", "🔥 High Growth"), ("Amazon Prime Video Weekend Premiere", "Prime Video", "🚀 Explosive Surge"), ("Disney+ Hotstar Regional Drama Finale", "Hotstar Special", "⚡ Accelerating"), ("Apple TV+ Sci-Fi Epic Season Premiere", "Apple TV+", "📈 Trending"), ("SonyLIV Crime Thriller Trending Spike", "SonyLIV Original", "🔥 High Growth")],
    "Teasers, Trailers & Fan Theories": [("Cinematic Trailer YouTube #1 Record Break", "Movie Teaser Hub", "🔥 High Growth"), ("Easter Egg Breakdown Video Surge", "Film Theories", "🚀 Explosive Surge"), ("Multiverse Cameo Rumor Discussion Thread", "Reddit r/Marvel", "⚡ Accelerating"), ("Character First Look Poster Viral Reaction", "Instagram Handle", "📈 Trending"), ("VFX Breakdown & Behind-the-Scenes", "Corridor Crew", "🔥 High Growth")],
    "Celebrity Cast Interviews & BTS": [("Unscripted Cast Roundtable Interview Clip", "Hollywood Reporter", "🔥 High Growth"), ("Behind-The-Scenes Stunt Training Reel", "Tom Cruise Action", "🚀 Explosive Surge"), ("Actors Read Mean Tweets Segment", "Jimmy Kimmel Live", "⚡ Accelerating"), ("Hot Ones Spicy Wing Celebrity Interview", "First We Feast", "📈 Trending"), ("Vogue 73 Questions Home Tour Video", "Vogue YouTube", "🔥 High Growth")],
    "Regional Cinema Surges": [("Mollywood Survival Thriller Phenomenon", "Malayalam Cinema", "🔥 High Growth"), ("Tollywood Action Epic Pan-India Release", "Telugu Cinema", "🚀 Explosive Surge"), ("Kollywood Mass Entertainer Opening Surge", "Tamil Superstar", "⚡ Accelerating"), ("Sandalwood Mythological Action Drama", "Kannada Blockbuster", "📈 Trending"), ("Pollywood Punjabi Romantic Comedy Hit", "Punjabi Cinema", "🔥 High Growth")],
    "Reviews, Recaps & Ending Explained": [("Complex Sci-Fi Movie Ending Explained", "Explanation Hub", "🔥 High Growth"), ("Season Finale Plot Twist Review Wave", "TV Series Recap", "🚀 Explosive Surge"), ("Honest Movie Trailer Satirical Review", "Screen Junkies", "⚡ Accelerating"), ("Rotten Tomatoes Critical Consensus", "RT Aggregate", "📈 Trending"), ("Binge-Worthy Recap in 15 Minutes", "ManOfRecaps", "🔥 High Growth")],

    # Music
    "Trending TikTok & Reels Sounds": [("Viral 15-Second Dance Challenge Audio", "TikTok Sound #1", "🔥 High Growth"), ("Aesthetic Cinematic Transition Beat", "Instagram Reels Audio", "🚀 Explosive Surge"), ("Funny Comedy Skit Voiceover Sound Byte", "Viral Meme Audio", "⚡ Accelerating"), ("Emotional Piano Melodic Loop", "CapCut Template", "📈 Trending"), ("Upbeat Synth-Pop Summer Anthem Track", "Spotify Viral 50", "🔥 High Growth")],
    "Album Drops & Concert Tours": [("Global Pop Icon World Tour Sellout Spike", "Taylor Swift Tour", "🔥 High Growth"), ("Surprise Album Midnight Drop Streaming", "Drake & Kendrick", "🚀 Explosive Surge"), ("Rock Band Reunion Tour Ticket Pre-Sale", "Oasis Reunion", "⚡ Accelerating"), ("Hip-Hop Artist Studio Album Tracklist", "Travis Scott", "📈 Trending"), ("K-Pop Group World Arena Tour Broadcast", "BTS & BLACKPINK", "🔥 High Growth")],
    "Regional & Folk Remix Surges": [("Rajasthani Folk Electronic Club Remix", "Jaipur Fusion", "🔥 High Growth"), ("Punjabi Bhangra Dhol Wedding Anthem", "Chandigarh DJ Hit", "🚀 Explosive Surge"), ("South Indian Kuthu Bass-Boosted Remix", "Chennai Street Dance", "⚡ Accelerating"), ("Bihari Lok Geet Modern Electronic Mix", "Patna Fusion Beat", "📈 Trending"), ("Bengali Baul Acoustic Lo-Fi Chillout", "Santiniketan Indie", "🔥 High Growth")],
    "Indie Artists & Unsigned Talent": [("Unsigned Bedroom Pop Artist Single", "SoundCloud Indie", "🔥 High Growth"), ("Lo-Fi Study Beats Instrumental Drop", "Lofi Girl Stream", "🚀 Explosive Surge"), ("Indie Rock Garage Session Video", "KEXP Studio", "⚡ Accelerating"), ("Acoustic Singer-Songwriter Busking", "London Underground", "📈 Trending"), ("DIY Home Studio Masterclass Release", "DistroKid Hub", "🔥 High Growth")],
    "Lo-Fi & Instrumental Tracks": [("Rainy Day Coffee Shop Lo-Fi Playlist", "Lofi Girl Study", "🔥 High Growth"), ("Deep Focus Ambient Piano Instrumental", "Calm Sleep Music", "🚀 Explosive Surge"), ("Cyberpunk Neon City Synthwave Beats", "Synthwave Radio", "⚡ Accelerating"), ("Vintage Vinyl Jazz Cafe Instrumental", "Retro Jazzhop", "📈 Trending"), ("Binaural Beats Alpha Wave Productivity", "Focus Flow Audio", "🔥 High Growth")],
    "Dance Challenges & Cover Videos": [("Viral TikTok Choreography Tutorial", "Matt Steffanina", "🔥 High Growth"), ("Full-Band Metal Cover of Pop Song", "Our Last Night", "🚀 Explosive Surge"), ("A Cappella Vocal Harmony Cover Video", "Pentatonix Style", "⚡ Accelerating"), ("Street Flash Mob Surprise Dance", "Times Square Flashmob", "📈 Trending"), ("K-Pop Cover Dance Street Performance", "K-Pop In Public", "🔥 High Growth")],

    # Pop Culture
    "Viral Meme Formats & Parodies": [("Brand New Exploding Brain Meme Format", "Reddit r/MemeEconomy", "🔥 High Growth"), ("AI Deepfake Celebrity Funny Parody", "TikTok AI Meme", "🚀 Explosive Surge"), ("Corporate Job Saturation Office Humor", "Corporate Natalie", "⚡ Accelerating"), ("Expectation vs Reality Travel Meme", "Instagram Meme Page", "📈 Trending"), ("Cat Staring Blankly at Wall Meme", "Confused Cat Loop", "🔥 High Growth")],
    "Creator Scandals & Internet Drama": [("Exposed: Fake Giveaway Sponsorship", "Creator House LA", "🔥 High Growth"), ("Creator House Eviction & Secret Fallout", "Mumbai Creator Pod", "🚀 Explosive Surge"), ("3AM Podcast Apology Video Record", "Delhi Influencer Hub", "⚡ Accelerating"), ("Behind-The-Scenes Agency Pay Cut Leak", "Supercreator Agency", "📈 Trending"), ("Reality Show Feud & Altercation Drama", "MTV Splitsvilla", "🔥 High Growth")],
    "Nostalgia & Throwback Trends": [("2000s Early Internet Windows XP Vibe", "Y2K Aesthetic", "🔥 High Growth"), ("Retro Walkman & Cassette Tape Revival", "Sony Walkman", "🚀 Explosive Surge"), ("Childhood Snacks Taste Test Nostalgia", "90s Food Trend", "🔥 High Growth"), ("Classic Arcade 8-Bit Gaming Cabinet", "Pac-Man Arcade", "📈 Trending"), ("Disposable Film Camera Photography", "Fujifilm QuickSnap", "🔥 High Growth")],
    "Fan Theories & Fandom Culture": [("MCU Secret Wars Multiverse Theory", "Marvel Reddit Hub", "🔥 High Growth"), ("Anime Final Season Plot Foreshadowing", "One Piece Lore", "🚀 Explosive Surge"), ("Pop Star Easter Egg Album Hidden Message", "Taylor Swift Fandom", "⚡ Accelerating"), ("Sci-Fi Universe Timeline Connection", "Star Wars Lore", "📈 Trending"), ("Video Game Secret Boss & Ending", "Elden Ring Wiki", "🔥 High Growth")],
    "Viral Challenges & Trends": [("24-Hour Extreme Wilderness Survival", "MrBeast Challenge", "🔥 High Growth"), ("Ice Bath Cold Plunge Endurance Test", "Huberman Protocol", "🚀 Explosive Surge"), ("Zero-Sugar 30-Day Clean Eating Reset", "Fitness Challenge", "⚡ Accelerating"), ("75 Hard Mental Toughness Challenge", "Andy Frisella", "📈 Trending"), ("Spicy Ramen Extreme Noodle Challenge", "Samyang Ghost Pepper", "🔥 High Growth")],
    "Reality TV & Live Broadcast Buzz": [("Reality Dating Show Final Rose Drama", "Love Island & Splitsvilla", "🔥 High Growth"), ("Live Talent Show Golden Buzzer Spike", "AGT Hub", "🚀 Explosive Surge"), ("Cooking Show Pressure Test Drama", "MasterChef Finalist", "⚡ Accelerating"), ("Survival Reality Show Tribal Council", "Survivor Series", "📈 Trending"), ("Dance Reality Show Trophy Winner", "Super Dancer", "🔥 High Growth")],

    # Anime & Gaming
    "Esports Tournaments & Highlights": [("Valorant Champions Grand Final Clutch", "VCT Masters", "🔥 High Growth"), ("Counter-Strike 2 Major Championship Ace", "CS2 Katowice", "🚀 Explosive Surge"), ("League of Legends Worlds Game 5", "LoL Worlds", "⚡ Accelerating"), ("Dota 2 The International Aegis Lift", "TI Grand Finals", "📈 Trending"), ("Mobile Games Esports World Cup", "BGMI World Cup", "🔥 High Growth")],
    "Mobile & PC Gaming Drops": [("AAA Open-World RPG Global Launch", "GTA VI / Cyberpunk", "🔥 High Growth"), ("Mobile RPG Gacha Banner Character Drop", "Genshin Impact", "🚀 Explosive Surge"), ("Steam Deck OLED Console Restock", "Valve Store", "⚡ Accelerating"), ("Battle Royale Season Update & Map Drop", "Fortnite & PUBG", "📈 Trending"), ("Indie Roguelike Masterpiece Release", "Hades II & Silksong", "🔥 High Growth")],
    "Anime Episode Releases & Manga Leaks": [("Anime Season Finale Epic Fight Episode", "Demon Slayer", "🔥 High Growth"), ("Manga Chapter Spoiler Leak & Raw Scan", "One Piece Leaks", "🚀 Explosive Surge"), ("New Anime Studio Announcement Teaser", "MAPPA Teaser", "⚡ Accelerating"), ("Shonen Jump Chapter Plot Twist", "Shonen Jump", "📈 Trending"), ("Isekai Fantasy Anime Premiere Spike", "Crunchyroll", "🔥 High Growth")],
    "Cosplay & Comic Conventions": [("Comic-Con Masterpiece Cosplay Showcase", "San Diego Comic-Con", "🔥 High Growth"), ("Anime Convention Armor Crafting Prop", "Anime Expo", "🚀 Explosive Surge"), ("Professional Cosplayer Transformation Clip", "Instagram Cosplay", "⚡ Accelerating"), ("Comic Con Exclusive Collectible Drop", "Hot Toys & Funko", "📈 Trending"), ("Gaming Convention Cosplay Contest", "Gamescom Hub", "🔥 High Growth")],
    "Streamer Highlights & Clipped Moments": [("Twitch Streamer Epic Rage Quit Reaction", "Kai Cenat & xQc", "🔥 High Growth"), ("VTuber Virtual Idol Debut Subscriber", "Hololive Debut", "🚀 Explosive Surge"), ("Streamer Charity Livestream Record Goal", "Markiplier Stream", "⚡ Accelerating"), ("Just Chatting Stream Drama Interaction", "HasanAbi Hub", "📈 Trending"), ("Speedrun World Record Glitchless Execution", "Speedrun.com", "🔥 High Growth")],
    "Gaming PC, Console & Gear Drops": [("NVIDIA RTX 5090 Graphics Card Launch", "NVIDIA GeForce", "🔥 High Growth"), ("Custom Water-Cooled RGB Gaming Rig", "Lian Li Build", "🚀 Explosive Surge"), ("Mechanical Hall Effect Magnetic Keyboard", "Wooting 60HE", "⚡ Accelerating"), ("Ultra-Lightweight Gaming Mouse Spike", "Logitech G Pro X", "📈 Trending"), ("OLED 240Hz Gaming Monitor Drop", "ASUS ROG", "🔥 High Growth")],

    # Celebrities & Sports
    "Cricket & Sports Idols": [("Virat Kohli Century Match Winning Knock", "ICC & IPL", "🔥 High Growth"), ("MS Dhoni Last-Over Finish Tactical", "CSK IPL", "🚀 Explosive Surge"), ("Rohit Sharma Pull Shot Highlight Reel", "Team India", "⚡ Accelerating"), ("Jasprit Bumrah Yorker Wicket Spike", "Test Bowling", "📈 Trending"), ("Olympic Gold Medalist Javelin Throw", "Neeraj Chopra", "🔥 High Growth")],
    "Movie & OTT Stars": [("Bollywood Superstar Birthday Teaser Drop", "Shah Rukh Khan", "🔥 High Growth"), ("Pan-India Action Hero Workout Reel", "Yash & Prabhas", "🚀 Explosive Surge"), ("Hollywood Red Carpet Cannes Look", "Zendaya Style", "⚡ Accelerating"), ("OTT Web Series Breakout Star Interview", "Netflix Star", "📈 Trending"), ("Celebrity Talk Show Candid Confession", "Koffee with Karan", "🔥 High Growth")],
    "Viral Influencers & Vloggers": [("MrBeast Massive Island Philanthropy Video", "MrBeast Channel", "🔥 High Growth"), ("Daily Vlog Travel Milestone Vlog Drop", "Casey Neistat", "🚀 Explosive Surge"), ("Beauty Influencer Makeup Transformation", "Huda Kattan", "⚡ Accelerating"), ("Tech Reviewer Durability Drop Test", "JerryRigEverything", "📈 Trending"), ("Food Vlogger Street Food Tour", "Mark Wiens", "🔥 High Growth")],
    "Tournament & League Buzz": [("IPL Mega Auction Player Retention Bid War", "IPL Auction", "🔥 High Growth"), ("ICC T20 World Cup Trophy Lift", "ICC Cricket", "🚀 Explosive Surge"), ("Premier League Title Matchup", "Arsenal vs Man City", "⚡ Accelerating"), ("UEFA Champions League Comeback", "UCL Quarter-Finals", "📈 Trending"), ("Wimbledon Royal Box Spectator Buzz", "Wimbledon Hub", "🔥 High Growth")],
    "Celebrity Fashion & Outfits": [("Met Gala Avant-Garde Celebrity Outfit", "Met Gala Style", "🔥 High Growth"), ("Airport Casual Streetwear Paparazzi Reel", "Airport Fashion", "🚀 Explosive Surge"), ("Luxury Designer Wedding Lehenga Showcase", "Sabyasachi Bridal", "⚡ Accelerating"), ("Sneakerhead Rare Collection Footwear Flex", "Complex Sneaker", "📈 Trending"), ("Cannes Film Festival Gown Red Carpet", "Cannes Red Carpet", "🔥 High Growth")],
    "Pop Culture Controversies": [("Celebrity Twitter Feud & Public Apology", "Twitter Drama", "🔥 High Growth"), ("Award Show Stage Altercation Shock", "Oscars Drama", "🚀 Explosive Surge"), ("Brand Ambassador Contract Termination", "PR Crisis", "⚡ Accelerating"), ("Reality TV Cast Member Bullying Scandal", "Network Statement", "📈 Trending"), ("Influencer Fake Charity Audit Leak", "Investigator Report", "🔥 High Growth")],

    # Beauty & Skincare
    "UGC Skincare Hacks": [("Ice Rolling Skin De-Puffing Morning Routine", "Skin Icing Trend", "🔥 High Growth"), ("Slugging Petroleum Jelly Barrier Repair", "CeraVe & Vaseline", "🚀 Explosive Surge"), ("Double Cleansing Oil K-Beauty Ritual", "Anua Cleansing Oil", "⚡ Accelerating"), ("Dermaplaning Exfoliation Face Shaving", "Schick Silk Touch", "📈 Trending"), ("Under-Eye Color Correcting Brightener", "Pink Powder Trend", "🔥 High Growth")],
    "K-Beauty & Glass Skin Trends": [("Snail Mucin Essence Barrier Repair", "Cosrx Snail 96", "🔥 High Growth"), ("Korean Sheet Mask Hydration Challenge", "Mediheal Masks", "🚀 Explosive Surge"), ("Centella Asiatica Calming Toner Pad", "Anua Heartleaf", "⚡ Accelerating"), ("Ginseng & Retinol Eye Cream Anti-Aging", "Beauty of Joseon", "📈 Trending"), ("Glass Skin Cushion Foundation Dewy Drop", "Tirtir Cushion", "🔥 High Growth")],
    "Anti-Aging & Beauty Devices": [("LED Light Therapy Face Mask Wrinkle Device", "CurrentBody Mask", "🔥 High Growth"), ("Microcurrent Facial Toning Device", "NuFace Trinity", "🚀 Explosive Surge"), ("Radio Frequency Skin Tightening Wand", "Tripollar Stop", "⚡ Accelerating"), ("Ultrasonic Skin Spatula Blackhead Remover", "Skin Scrubber", "📈 Trending"), ("Cryotherapy Facial Ice Globe Coolers", "Ice Globes Trend", "🔥 High Growth")],
    "Men's Grooming & Beard Care": [("Argan Organic Beard Growth Oil Drop", "Beardo & Ustraa", "🔥 High Growth"), ("Cordless T-Blade Hair Trimmer for Fades", "Wahl Detailer", "🚀 Explosive Surge"), ("Activated Charcoal Deep Cleansing Face Wash", "Brickell Men's", "⚡ Accelerating"), ("Solid Cologne Travel Balm Fragrance", "Fulton & Roark", "📈 Trending"), ("Matte Finish Hair Styling Clay Wax", "Bed Head Wax", "🔥 High Growth")],
    "Haircare Treatment Trends": [("Bond Repair Treatment Mask Damaged Hair", "Olaplex No. 3", "🔥 High Growth"), ("Scalp Exfoliating Scrub Rosemary Oil", "Mielle Organics", "🚀 Explosive Surge"), ("Heatless Silk Curling Ribbon Headband", "Kitsch Curler", "⚡ Accelerating"), ("Professional Hair Blowout Airwrap Styler", "Dyson Airwrap", "📈 Trending"), ("Keratin Smoothing Hair Treatment Drop", "GK Hair Keratin", "🔥 High Growth")],
    "Minimalist Capsule Wardrobes": [("10-Piece Minimalist Capsule Wardrobe", "COS & Everlane", "🔥 High Growth"), ("Neutral Linen Button-Down Shirt", "Uniqlo Linen", "🚀 Explosive Surge"), ("High-Waisted Straight Leg Tailored Trouser", "Massimo Dutti", "⚡ Accelerating"), ("Organic Cotton White Crewneck T-Shirt", "COS Minimalist", "📈 Trending"), ("Tailored Wool Blend Blazer Jacket", "Zara Minimalist", "🔥 High Growth")],

    # Health & Fitness
    "Gym & Home Workout Gear": [("Adjustable Dumbbell Set Space Saver", "Nuobell & PowerBlock", "🔥 High Growth"), ("Heavy Resistance Band Set Home Training", "WODFitters Bands", "🚀 Explosive Surge"), ("Ergonomic Pull-Up Bar Doorway Station", "Iron Gym", "⚡ Accelerating"), ("Anti-Slip Rubber Gym Floor Mat Tiles", "ProGym Rubber", "📈 Trending"), ("Olympic Barbell & Bumper Plate Set", "Rogue Fitness", "🔥 High Growth")],
    "Whey & Supplement Drops": [("100% Whey Protein Isolate Chocolate Drop", "Optimum Nutrition", "🔥 High Growth"), ("Micronized Creatine Monohydrate Powder", "MuscleBlaze", "🚀 Explosive Surge"), ("Pre-Workout Explosive Energy Formula", "C4 Original", "⚡ Accelerating"), ("Plant-Based Organic Pea Protein Powder", "Orgain Organic", "📈 Trending"), ("BCAA Intra-Workout Electrolyte Recovery", "Scivation Xtend", "🔥 High Growth")],
    "Biohacking & Wearable Tech (Oura/Whoop)": [("Smart Health Ring Sleep Tracker Gen 4", "Oura Ring", "🔥 High Growth"), ("Athletic Performance Strain Wearable Band", "Whoop Strap 4.0", "🚀 Explosive Surge"), ("Continuous Glucose Monitor Sensor", "Abbott Libre", "⚡ Accelerating"), ("Sleep Mask with EEG Brainwave Sensors", "Muse S Headband", "📈 Trending"), ("Red Light Therapy Full-Body Panel", "Platinum Lights", "🔥 High Growth")],
    "Weight Loss & Nutrition Diets": [("Ketogenic Diet Macro Calculator & Prep", "Keto Hub", "🔥 High Growth"), ("Intermittent Fasting 16:8 Protocol App", "Zero Fasting App", "🚀 Explosive Surge"), ("GLP-1 Weight Loss High-Protein Plan", "Roman Health", "⚡ Accelerating"), ("Mediterranean Diet Cookbook Drop", "Bestseller Guide", "📈 Trending"), ("Calorie Deficit Tracking App Suite", "MyFitnessPal", "🔥 High Growth")],
    "Mental Health & Burnout Recovery": [("Guided Meditation & Sleep Story App", "Headspace & Calm", "🔥 High Growth"), ("CBT Journal Workbook for Burnout", "Recovery Journal", "🚀 Explosive Surge"), ("Weighted Anxiety Stress Relief Blanket", "Baloo Living", "⚡ Accelerating"), ("Aromatherapy Essential Oil Diffuser Hub", "InnoGear", "📈 Trending"), ("Online Licensed Therapy Counseling Drop", "BetterHelp", "🔥 High Growth")],
    "Recovery Gear & Cold Plunges": [("Portable Inflatable Cold Plunge Tub", "Ice Barrel Hub", "🔥 High Growth"), ("Percussion Deep Tissue Massage Gun", "Theragun PRO", "🚀 Explosive Surge"), ("Compression Leg Boots Lymphatic Drainage", "Normatec 3", "⚡ Accelerating"), ("Therapeutic Heating Compression Wrap", "Hyperice Venom", "📈 Trending"), ("Professional Sports Recovery Foam Roller", "TriggerPoint", "🔥 High Growth")],

    # Travel & Food
    "Trending Destinations": [("Offbeat Alpine Mountain Valley Tourism", "Spiti & Zanskar", "🔥 High Growth"), ("Tropical Island Beach Resort Booking", "Andaman Islands", "🚀 Explosive Surge"), ("Cultural Heritage UNESCO Town Getaway", "Udaipur & Hampi", "⚡ Accelerating"), ("Wildlife Tiger Safari Jungle Lodge", "Ranthambore", "📈 Trending"), ("Tea Plantation Hill Station Homestay", "Munnar & Wayanad", "🔥 High Growth")],
    "Hidden Tourist Places": [("Hidden Valley Trekking Expedition Surge", "Zuluk Sikkim", "🔥 High Growth"), ("Offbeat Cliffside Sunset Viewpoint", "Vagamon Forest", "🚀 Explosive Surge"), ("Secret Waterfall Camping Spot Discovery", "Tirthan Valley", "⚡ Accelerating"), ("Stargazing Eco-Lodge Weekend Getaway", "Yercaud Hills", "📈 Trending"), ("Unexplored Caves & Rock Formations", "Kurnool Caves", "🔥 High Growth")],
    "Luxury Hotels & Resort Stays": [("Palace Heritage Hotel Royal Suite Booking", "Taj Lake Palace", "🔥 High Growth"), ("Private Pool Cliffside Luxury Villa Stay", "W Goa & The Leela", "🚀 Explosive Surge"), ("Boutique Treehouse Resort Wilderness", "JW Marriott", "⚡ Accelerating"), ("Overwater Pool Villa Island Luxury Stay", "Maldives Resorts", "📈 Trending"), ("Golf Resort & Spa Luxury Staycation", "ITC Grand Bharat", "🔥 High Growth")],
    "Gourmet & Regional Cuisines": [("Authentic Coastal Seafood Thali Experience", "Malvani Feast", "🔥 High Growth"), ("Fine Dining Chef Tasting Molecular Gastronomy", "Mumbai Bistro", "🚀 Explosive Surge"), ("Traditional Awadhi Dum Biryani Feast", "Lucknow Heritage", "⚡ Accelerating"), ("Wood-Fired Neapolitan Pizza Trend", "Boutique Pizzeria", "📈 Trending"), ("Farm-to-Table Organic Gourmet Bistro", "Goa Organic Cafes", "🔥 High Growth")],
    "Street Food Surges": [("Viral Cheese Burst Street Food Snack Reel", "Mumbai Street Food", "🔥 High Growth"), ("Kolkata Puchka & Kathi Roll Food Tour", "Park Street Food", "🚀 Explosive Surge"), ("Hyderabad Mirchi Bajji & Irani Chai", "Charminar Foodie", "⚡ Accelerating"), ("Old Delhi Paratha & Dahi Bhalla Hub", "Chandni Chowk", "📈 Trending"), ("Bangalore Masala Dosa & Filter Coffee", "Malleshwaram Hub", "🔥 High Growth")],
    "Budget & Backpacker Escapes": [("Hostel Backpacking Europe Interrail Guide", "Hostelworld", "🔥 High Growth"), ("Budget Solo Backpacking Southeast Asia", "Thailand Trail", "🚀 Explosive Surge"), ("Himalayan Village Backpacking Hostel Stay", "Kasol Hostels", "⚡ Accelerating"), ("Weekend Road Trip Budget Camping Gear", "Decathlon Guide", "📈 Trending"), ("Cheap Flight Booking Error Fare Finder", "Skyscanner", "🔥 High Growth")],

    # Faith & Sacred Travel
    "Famous Temples & Shrines": [("Char Dham Yatra Pilgrimage Registration", "Uttarakhand Tourism", "🔥 High Growth"), ("Tirupati Balaji VIP Break Darshan Surge", "TTD Portal", "🚀 Explosive Surge"), ("Kashi Vishwanath Corridor Heritage Darshan", "Varanasi Trust", "⚡ Accelerating"), ("Ayodhya Ram Mandir Festival Crowd Spike", "Ram Janmabhoomi", "📈 Trending"), ("Vaishno Devi Helicopter Ticket Booking", "SVDS Board", "🔥 High Growth")],
    "Hidden & Ancient Temples": [("Unexplored Hoysala Architecture Trail", "Belur & Halebidu", "🔥 High Growth"), ("Ancient Rock-Cut Cave Temple Tour", "Ellora & Badami", "🚀 Explosive Surge"), ("Secret Chola Dynasty Temple Heritage", "Thanjavur Trail", "⚡ Accelerating"), ("Hidden 1000-Pillar Temple Wonder", "Warangal Pillar", "📈 Trending"), ("Megalithic Temple Site Exploration", "Lepakshi Temple", "🔥 High Growth")],
    "Religious Festivals & Pujas": [("Diwali Laxmi Puja Muhurat & Decor Trend", "Diwali Hub", "🔥 High Growth"), ("Maha Shivratri Night Vigil & Puja", "Shivratri Events", "🚀 Explosive Surge"), ("Navratri Durga Puja Pandal Hopping", "Kolkata Navratri", "⚡ Accelerating"), ("Ganesh Chaturthi Eco-Friendly Idol Drop", "Mumbai Ganpati", "📈 Trending"), ("Holi Festival Organic Colors Celebration", "Mathura Holi", "🔥 High Growth")],
    "Pilgrimage Circuits & Yatras": [("Kailash Mansarovar Yatra Permit & Route", "MEA Portal", "🔥 High Growth"), ("Amarnath Yatra Registration Certificate", "SASB Portal", "🚀 Explosive Surge"), ("Panch Kedar Trekking Circuit Pilgrimage", "Garhwal Yatra", "⚡ Accelerating"), ("Ashtavinayak Ganpati Circuit Road Trip", "Maharashtra Tour", "📈 Trending"), ("Twelve Jyotirlinga Special Train Tour", "IRCTC Pilgrim", "🔥 High Growth")],
    "Festive Gifting Trends": [("Luxury Dry Fruits Artisanal Chocolate Hamper", "Fabindia Hamper", "🔥 High Growth"), ("Silver Plated Coin & Laxmi Ganesha Idol", "Silver Studio", "🚀 Explosive Surge"), ("Handmade Soy Wax Scented Candle Set", "Earthy Touch", "⚡ Accelerating"), ("Ethnic Designer Kurta Festive Apparel", "Manyavar Festive", "📈 Trending"), ("Aromatherapy Wellness Gift Hamper", "Soulflower", "🔥 High Growth")],
    "Spiritual Wellness & Meditation Drops": [("Vipassana 10-Day Silent Meditation Course", "Vipassana Hub", "🔥 High Growth"), ("Yoga Teacher Training Ashram Retreat", "Rishikesh Yoga", "🚀 Explosive Surge"), ("Tibetan Singing Bowl Sound Bath Set", "Chakra Healing", "⚡ Accelerating"), ("Mindfulness & Breathwork Masterclass Pass", "Art of Living", "📈 Trending"), ("Natural Rudraksha Mala Bead Necklace", "Varanasi Beads", "🔥 High Growth")],

    # Politics & News
    "Elections & Campaign Rallies": [("General Election Exit Poll Sentiment Analysis", "Election Commission", "🔥 High Growth"), ("Political Party Manifesto & Policy Drop", "National Party Portal", "🚀 Explosive Surge"), ("Assembly Election Campaign Rally Broadcast", "News Wire", "⚡ Accelerating"), ("Voter Turnout Live Tracking Dashboard", "ECI App", "📈 Trending"), ("Constituency High-Profile Candidate Debate", "News Debate Hub", "🔥 High Growth")],
    "Legislative Debates & Laws": [("Parliamentary Budget Session Live Debate", "Sansad TV", "🔥 High Growth"), ("New Criminal Law Bill Implementation", "Ministry of Law", "🚀 Explosive Surge"), ("Supreme Court Landmark Constitutional Verdict", "Supreme Court", "⚡ Accelerating"), ("Tax Reform & Financial Bill Amendment", "Ministry of Finance", "📈 Trending"), ("Data Protection & Digital Privacy Law", "Ministry of IT", "🔥 High Growth")],
    "Protests & Policy Changes": [("National Labor Strike & Trade Union Protest", "News Bulletin", "🔥 High Growth"), ("Agricultural Policy Reform Demonstration", "Farmers Union", "🚀 Explosive Surge"), ("Fuel Price Hike & Transport Tariff Protest", "City Transport", "⚡ Accelerating"), ("Civic Infrastructure Urban Tax Reform", "Municipal Notice", "📈 Trending"), ("Student Union University Fee Hike Protest", "Campus Hub", "🔥 High Growth")],
    "Politician Speeches & Interviews": [("Prime Minister Independence Day Address", "PMO India", "🔥 High Growth"), ("Opposition Leader No-Confidence Speech", "Lok Sabha", "🚀 Explosive Surge"), ("Exclusive Hard-Hitting Political Interview", "BBC & NDTV", "⚡ Accelerating"), ("State Chief Minister Press Conference", "State Info Bureau", "📈 Trending"), ("Union Budget Presentation Live Speech", "Parliament Budget", "🔥 High Growth")],
    "Geopolitical & Diplomatic Updates": [("G20 Summit Global Economic Communique", "G20 Portal", "🔥 High Growth"), ("Bilateral Trade Agreement Signing Bulletin", "MEA India", "🚀 Explosive Surge"), ("International Border Security & Defense Pact", "Ministry of Defense", "⚡ Accelerating"), ("Global Climate Change Treaty COP Summit", "COP Climate Hub", "📈 Trending"), ("UN Security Council Diplomatic Debate", "UN News", "🔥 High Growth")],
    "Public Schemes & Subsidies": [("PM Awas Yojana Housing Subsidy Portal", "PMAY Portal", "🔥 High Growth"), ("Ayushman Bharat Health Insurance Card", "National Health Authority", "🚀 Explosive Surge"), ("Mudra Loan Small Business Financing", "PMMY Portal", "⚡ Accelerating"), ("Kisan Samman Nidhi Farmer Income Support", "PM-KISAN Tracker", "📈 Trending"), ("Skill India Apprenticeship Training Portal", "MSDE Hub", "🔥 High Growth")]
}

# ==========================================
# 5. PIPELINE & DATA ENGINE
# ==========================================
@st.cache_data(ttl=300)
def fetch_live_google_trends(keyword, region_code="IN"):
    if not PYTRENDS_AVAILABLE:
        return None
    try:
        pytrends = TrendReq(hl='en-US', tz=330)
        pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo=region_code, gprop='')
        data = pytrends.interest_over_time()
        if not data.empty and keyword in data.columns:
            latest_score = int(data[keyword].iloc[-1])
            avg_score = int(data[keyword].mean())
            return [
                (f"Google Search Surge: {keyword}", f"Live Interest Index: {latest_score}/100 (Avg: {avg_score})", "🔥 High Growth"),
                (f"Breakout Regional Query: {keyword}", f"Search Velocity Peak (Geo: {region_code})", "🚀 Explosive Surge"),
                (f"Rising Consumer Intent: {keyword}", f"Engagement Multiplier Active", "⚡ Accelerating")
            ]
    except Exception:
        pass
    return None

@st.cache_data(ttl=300)
def fetch_and_store_signals(region, platform_source, category, sub_niche, timeframe):
    results = []
    items = []
    
    geo_code = "IN" if "IN" in region else ("US" if "US" in region else ("GB" if "GB" in region else ""))
    
    if PYTRENDS_AVAILABLE and ("Google Trends" in platform_source or (sub_niche and sub_niche != "All Sub-Niches")):
        query_keyword = sub_niche if sub_niche != "All Sub-Niches" else category
        items = fetch_live_google_trends(query_keyword, geo_code)

    if not items:
        if sub_niche and sub_niche in MASTER_SUB_NICHE_POOLS:
            items = MASTER_SUB_NICHE_POOLS[sub_niche]
        else:
            # Fallback if All Sub-Niches is selected, pick items across the category sub-niches
            category_sub_niches = UPDATED_NICHE_CATEGORIES.get(category, [])
            items = []
            for sub in category_sub_niches[:5]:
                if sub in MASTER_SUB_NICHE_POOLS:
                    items.extend(MASTER_SUB_NICHE_POOLS[sub][:2])
            if not items:
                items = [
                    (f"Breakout Trend in {category}", f"Target Node #{i+1}", "🔥 High Growth" if i % 2 == 0 else "⚡ Accelerating")
                    for i in range(10)
                ]

    for i, (item, entity, velocity) in enumerate(items):
        base_vol = 1250000 - (i * 95400)
        results.append({
            "Keyword": item,
            "Entity": entity,
            "Volume": f"{base_vol:,} Interactions ({region})",
            "Velocity": velocity
        })

    try:
        cursor = db_conn.cursor()
        for r in results:
            cursor.execute(
                "INSERT INTO platform_signals (source_platform, keyword, engagement_metrics, region) VALUES (?, ?, ?, ?)",
                (platform_source, f"{r['Keyword']} ({r['Entity']})", r["Volume"], region)
            )
        db_conn.commit()
    except Exception:
        pass
    return results

# ==========================================
# 6. MASTER LLM DOSSIER GENERATOR & PDF
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
    return re.sub(r'\s+', ' ', cleaned).strip()

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

def generate_master_enterprise_dossier(keyword_asset, category, sub_niche, target_role, platform, timeframe, velocity_score):
    clean_asset = sanitize_trend_input(keyword_asset)
    metrics_template = ROLE_SPECIFIC_METRICS.get(target_role, ROLE_SPECIFIC_METRICS["🛍️ E-Commerce Merchants & D2C Brands"])
    
    default_response = {
        "viral_score": f"{velocity_score}%",
        "prediction_window": f"Active Timing Window ({timeframe})",
        "unit_economics": f"• **{metrics_template['m1']}:** Optimized tier\n• **{metrics_template['m2']}:** INR 1,500 – INR 2,800 benchmark\n• **Brand Rate Card (Reel/Short):** INR 15,000 – INR 25,000 per post\n• **Affiliate Commission Stack:** 12% per confirmed conversion",
        "geo_mapping": "• **Primary Tier-1 Hotspots:** Mumbai, Bengaluru, Delhi-NCR, Pune\n• **Emerging Tier-2 Hubs:** Jaipur, Indore, Chandigarh, Lucknow",
        "hook_matrix": f"• **FOMO Hook:** \"The secret strategy behind {clean_asset} that elite operators are hiding...\"\n• **Storyboard:** [0-3s] High-end cinematic visual hook transitioning into narrative.",
        "copywriting_vault": f"• **Problem-Solver Angle:** \"Struggling with {clean_asset}? Here is the ultimate modern solution to scale instantly.\"",
        "saturation_matrix": "• **Saturation Index:** Moderate (62% saturated, high incoming demand)\n• **Strategic Edge:** Ultra-fast 48-hour delivery & micro-community branding",
        "tech_prompts": f"• **ChatGPT Prompt:** Write a 30-second high-retention script for {clean_asset}.",
        "scale_kill_rules": "• **The Kill Rule:** If ad budget crosses INR 4,000/day with 0 conversions in 24h -> PAUSE IMMEDIATELY.",
        "virality_formula": "• **Formula:** Virality Score = ((3s Watch Retention * Shares) / Impressions)",
        "syndication_matrix": "• **Instagram Reels:** Trending audio loops with high-contrast text overlays.\n• **YouTube Shorts:** Optimized thumbnail and evening publishing window.",
        "action_roadmap": "1. HOUR 1-6: Setup & affiliate integration.\n2. DAY 3: Optimization via rules.\n3. DAY 10: Scaling."
    }
    
    if not GROQ_API_KEY:
        return default_response
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
Return ONLY a raw valid JSON object (no markdown, no backticks).
Generate a customized Commercial Intelligence & Revenue Scale Dossier for:
- Asset/Trend: "{clean_asset}"
- Category: "{category} ({sub_niche})"
- Target Role: "{target_role}"
Ensure all monetary values use 'INR '.
JSON Format:
{{
  "viral_score": "{velocity_score}%",
  "prediction_window": "timing window",
  "unit_economics": "• **{metrics_template['m1']}:** ...\\n• **{metrics_template['m2']}:** INR ...\\n• **Brand Rate Card:** INR 15,000",
  "geo_mapping": "• **Primary Tier-1:** Mumbai, Bengaluru...",
  "hook_matrix": "• **FOMO Hook:** ...",
  "copywriting_vault": "• **Angle:** ...",
  "saturation_matrix": "• **Index:** Moderate...",
  "tech_prompts": "• **Prompt:** ...",
  "scale_kill_rules": "• **Kill Rule:** INR 4,000/day...",
  "virality_formula": "• **Formula:** ...",
  "syndication_matrix": "• **Reels:** ...",
  "action_roadmap": "1. Setup... 2. Scale..."
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
# 7. MAIN UI LAYOUT
# ==========================================
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.title(t["title"])
    st.caption(t["subtitle"])

with st.expander(t["terminal"], expanded=False):
    st.session_state["is_premium"] = st.checkbox(t["simulate_pro"], value=st.session_state["is_premium"])

st.markdown(f"### {t['config_title']}")
with st.form(key="filter_form"):
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
    with f_col1:
        geo_option = st.selectbox(t["region"], ["India (IN)", "United States (US)", "United Kingdom (GB)", "Global (ALL)"])
        geo_map = {"India (IN)": "IN", "United States (US)": "US", "United Kingdom (GB)": "GB", "Global (ALL)": "ALL"}
    with f_col2:
        platform_source = st.selectbox(t["platform"], ["🎵 TikTok Trends", "📸 Instagram Reels", "🔎 Google Trends", "🛒 Amazon Movers"], index=0)
    with f_col3:
        selected_category = st.selectbox(t["category"], options=list(UPDATED_NICHE_CATEGORIES.keys()), index=0)
    with f_col4:
        sub_niche_options = UPDATED_NICHE_CATEGORIES.get(selected_category, [])
        selected_sub_niche = st.selectbox(t["sub_category"], options=["All Sub-Niches"] + sub_niche_options, index=0)
    with f_col5:
        timeframe = st.selectbox(t["velocity"], ["Realtime Spike (24h)", "Short-Term Trend (7 Days)", "Viral Surge (3-7 Days)"])
    
    apply_filters = st.form_submit_button(t["apply_btn"], use_container_width=True)

st.markdown("---")

tab_radar, tab_blueprint, tab_db = st.tabs([t["tab_radar"], t["tab_blueprint"], t["tab_db"]])

with tab_radar:
    st.subheader(t["telemetry_title"])
    active_signals = fetch_and_store_signals(geo_map[geo_option], platform_source, selected_category, selected_sub_niche, timeframe)
    signal_scores = {item["Keyword"]: round(99.4 - (i * 2.1), 1) for i, item in enumerate(active_signals)}
    df_signals = pd.DataFrame(active_signals)

    st.markdown(f"**Active Ingested Signals for:** `{selected_category}` -> `{selected_sub_niche}`")
    st.dataframe(df_signals.rename(columns={"Keyword": "Trending Asset Signal", "Entity": "Specific Entity / Target", "Volume": "Engagement / Volume", "Velocity": "Velocity Status"}), use_container_width=True, hide_index=True)

with tab_blueprint:
    st.subheader("🚀 Master Intelligence & Revenue Dossier Engine")
    if not st.session_state["is_premium"]:
        st.warning("🔒 MASTER INTELLIGENCE & REVENUE SUITE IS LOCKED")
        st.link_button("🔥 Upgrade to Pro & Unlock Master Engine", STRIPE_CHECKOUT_URL, use_container_width=True)
    else:
        st.success("🔓 MASTER PRO ENGINE ACTIVE")
        temp_signals = fetch_and_store_signals(geo_map[geo_option], platform_source, selected_category, selected_sub_niche, timeframe)
        asset_list = [item["Keyword"] for item in temp_signals]
        selected_asset = st.selectbox("🎯 Select Ingested Asset:", options=asset_list, index=0)
        target_role = st.selectbox("👤 Operating Role:", list(ROLE_SPECIFIC_METRICS.keys()), index=0)
        
        if st.button("🚀 Generate Master Dossier & PDF", use_container_width=True):
            dossier_result = generate_master_enterprise_dossier(selected_asset, selected_category, selected_sub_niche, target_role, platform_source, timeframe, 95.2)
            pdf_buffer = create_pdf_dossier(selected_asset, selected_category, target_role, 95.2, timeframe, dossier_result)
            st.download_button(
                label="📥 Download Official PDF Commercial & Revenue Dossier",
                data=pdf_buffer,
                file_name=f"TrendPulse_Dossier_{sanitize_trend_input(selected_asset)[:20]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            for sec_title, sec_content in dossier_result.items():
                with st.expander(sec_title.replace('_', ' ').title(), expanded=False):
                    st.markdown(sec_content)

with tab_db:
    st.subheader("🗄️ Database Inspector")
    df_table = pd.read_sql_query("SELECT * FROM platform_signals ORDER BY signal_id DESC LIMIT 30", db_conn)
    st.dataframe(df_table, use_container_width=True)
