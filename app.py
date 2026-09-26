import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# ==========================================
# 1. CORE DATA STRUCTURES & CONFIGURATIONS
# ==========================================

MASTER_PLATFORMS = [
    {"id": "tiktok", "name": "TikTok Trends", "icon": "🎵"},
    {"id": "instagram", "name": "Instagram & Meta Ads", "icon": "📸"},
    {"id": "google", "name": "Google Search Intent", "icon": "🔎"},
    {"id": "pinterest", "name": "Pinterest Discovery", "icon": "📌"},
    {"id": "x", "name": "X (Twitter) Realtime", "icon": "🧵"},
    {"id": "reddit", "name": "Reddit Communities", "icon": "👽"},
    {"id": "amazon", "name": "Amazon Movers", "icon": "🛒"},
    {"id": "youtube", "name": "YouTube Shorts", "icon": "▶️"},
    {"id": "linkedin", "name": "LinkedIn B2B", "icon": "💼"},
    {"id": "producthunt", "name": "Product Hunt & GitHub", "icon": "🚀"},
    {"id": "etsy", "name": "Etsy & D2C", "icon": "🛍️"},
    {"id": "news", "name": "Google News / RSS", "icon": "📰"},
]

OPERATING_ROLES = [
    {
        "id": "ecom",
        "name": "E-Commerce Merchant & D2C",
        "icon": "🛍️",
        "desc": "Product sourcing, margins, and ad copy.",
    },
    {
        "id": "creator",
        "name": "Viral Content Creator",
        "icon": "🎬",
        "desc": "Hooks, scripts, and engagement loops.",
    },
    {
        "id": "affiliate",
        "name": "Affiliate Marketer",
        "icon": "💸",
        "desc": "Funnels, bridge pages, and high-ticket offers.",
    },
    {
        "id": "realestate",
        "name": "Real Estate & High-Ticket",
        "icon": "🏢",
        "desc": "Lead gen, local targeting, and psychology.",
    },
    {
        "id": "saas",
        "name": "SaaS Founder & Solopreneur",
        "icon": "💻",
        "desc": "Product-market fit, PAS copy, and Product Hunt.",
    },
    {
        "id": "trader",
        "name": "Stock & Crypto Analyst",
        "icon": "📈",
        "desc": "Sentiment scores, risk warnings, and catalysts.",
    },
]

MASTER_CATEGORIES = {
    "commerce": {
        "name": "Commerce & High-Margin Products",
        "icon": "🛍️",
        "subniches": [
            "TikTok Shop & Live Deals",
            "Amazon Hot Movers & Bestsellers",
            "D2C Breakout & DTC Brands",
            "Problem-Solver Gadgets",
            "Print-on-Demand & Custom Merch",
            "Upcoming High-Demand Drops",
        ],
    },
    "realestate": {
        "name": "Real Estate & High-Ticket Props",
        "icon": "🏢",
        "subniches": [
            "Rental Yield Hotspots",
            "PropTech & Smart Homes",
            "Luxury Estates & Villas",
            "Commercial & Co-Working Spaces",
            "Fractional Real Estate & REITs",
            "Upcoming Transit & Metro Hubs",
        ],
    },
    "automobile": {
        "name": "Automobile, EV & Mobility",
        "icon": "🚗",
        "subniches": [
            "EV Launches & Battery Tech",
            "ADAS, Dashcams & Smart Tech",
            "Car & Bike Accessories / Gadgets",
            "Auto Reviews & Mileage Hacks",
            "Custom Bike & Supercar Buzz",
            "Commuter Vehicle Price Drops",
        ],
    },
    "parenting": {
        "name": "Parenting, Baby Care & Kids",
        "icon": "👶",
        "subniches": [
            "Baby Gear & Smart Strollers",
            "Early Childhood EdTech & Toys",
            "Modern Parenting & Routine Hacks",
            "Kids Nutrition & Organic Foods",
            "Maternity & Postpartum Care",
            "Family Lifestyle & Travel Gear",
        ],
    },
    "pets": {
        "name": "Pets & Animal Care",
        "icon": "🐾",
        "subniches": [
            "Pet Health & Nutrition",
            "Dog & Cat Training Hacks",
            "Smart Pet Accessories & Tech",
            "Cute & Funny Pet Virals",
            "Grooming & Hygiene Products",
            "Breed Guides & Adoption Signals",
        ],
    },
    "finance": {
        "name": "Finance, Crypto & Wealth Building",
        "icon": "💰",
        "subniches": [
            "Credit Card & Reward Hacks",
            "Stock Market & Algo Trading Bots",
            "Crypto & Web3 Signals",
            "Side Hustles & Passive Income",
            "Personal Tax & Saving Strategies",
            "Real Estate & Fractional Investing",
        ],
    },
    "business": {
        "name": "Business, Startups & Entrepreneurship",
        "icon": "💼",
        "subniches": [
            "Startup Funding & Pitch Decks",
            "Solopreneur & One-Person Business",
            "AI Automation Agencies (AAA)",
            "Freelancing & Agency Scaling",
            "Growth Hacking & B2B Marketing",
            "E-Commerce Supply Chain & Fulfillment",
        ],
    },
    "digital": {
        "name": "Digital Products & AI Tools",
        "icon": "💻",
        "subniches": [
            "Vibe Coding & Code Extensions",
            "Generative AI & SaaS Tools",
            "Notion & Productivity Dashboards",
            "Digital Ebooks & Online Courses",
            "UI/UX Templates & Prompt Packs",
            "No-Code App Builders & Micro-Tools",
        ],
    },
    "education": {
        "name": "Education, Careers & Jobs",
        "icon": "🎓",
        "subniches": [
            "Govt Exam Dates & Prep Hacks",
            "AI Upskilling & Tech Roadmaps",
            "Study Abroad Scholarships & Visas",
            "Resume, Portfolio & Interview Hacks",
            "Remote Job & Hiring Alerts",
            "College Campus & Placement Trends",
        ],
    },
    "sustainability": {
        "name": "Sustainability & Green Tech",
        "icon": "🌿",
        "subniches": [
            "Solar Power & Home Energy",
            "Zero-Waste Lifestyle & Reusables",
            "Organic & Sustainable Fashion",
            "Clean Tech & Carbon Offsets",
            "Eco-Friendly Packaging Solutions",
            "Electric Mobility & Micro-Transit",
        ],
    },
    "movies": {
        "name": "Movies, OTT & Series",
        "icon": "🎬",
        "subniches": [
            "Box Office Collections & Predictions",
            "OTT Releases & Platform Buzz",
            "Teasers, Trailers & Fan Theories",
            "Celebrity Cast Interviews & BTS",
            "Regional Cinema Surges",
            "Reviews, Recaps & Ending Explained",
        ],
    },
    "music": {
        "name": "Music & Viral Sound Tracks",
        "icon": "🎵",
        "subniches": [
            "Trending TikTok & Reels Sounds",
            "Album Drops & Concert Tours",
            "Regional & Folk Remix Surges",
            "Indie Artists & Unsigned Talent",
            "Lo-Fi & Instrumental Tracks",
            "Dance Challenges & Cover Videos",
        ],
    },
    "popculture": {
        "name": "Pop Culture, Memes & Drama",
        "icon": "🎭",
        "subniches": [
            "Viral Meme Formats & Parodies",
            "Creator Scandals & Internet Drama",
            "Nostalgia & Throwback Trends",
            "Fan Theories & Fandom Culture",
            "Viral Challenges & Trends",
            "Reality TV & Live Broadcast Buzz",
        ],
    },
    "gaming": {
        "name": "Anime, Gaming & Fandom",
        "icon": "🐉",
        "subniches": [
            "Esports Tournaments & Highlights",
            "Mobile & PC Gaming Drops",
            "Anime Episode Releases & Manga Leaks",
            "Cosplay & Comic Conventions",
            "Streamer Highlights & Clipped Moments",
            "Gaming PC, Console & Gear Drops",
        ],
    },
    "celebrities": {
        "name": "Celebrities & Sports Stars",
        "icon": "🌟",
        "subniches": [
            "Cricket & Sports Idols",
            "Movie & OTT Stars",
            "Viral Influencers & Vloggers",
            "Tournament & League Buzz",
            "Celebrity Fashion & Outfits",
            "Pop Culture Controversies",
        ],
    },
    "beauty": {
        "name": "Beauty, Skincare & Lifestyle",
        "icon": "💄",
        "subniches": [
            "UGC Skincare Hacks",
            "K-Beauty & Glass Skin Trends",
            "Anti-Aging & Beauty Devices",
            "Men's Grooming & Beard Care",
            "Haircare Treatment Trends",
            "Minimalist Capsule Wardrobes",
        ],
    },
    "health": {
        "name": "Health, Fitness & Biohacking",
        "icon": "🏋️",
        "subniches": [
            "Gym & Home Workout Gear",
            "Whey & Supplement Drops",
            "Biohacking & Wearable Tech (Oura/Whoop)",
            "Weight Loss & Nutrition Diets",
            "Mental Health & Burnout Recovery",
            "Recovery Gear & Cold Plunges",
        ],
    },
    "travel": {
        "name": "Travel, Hotels & Food",
        "icon": "✈️",
        "subniches": [
            "Trending Destinations",
            "Hidden Tourist Places",
            "Luxury Hotels & Resort Stays",
            "Gourmet & Regional Cuisines",
            "Street Food Surges",
            "Budget & Backpacker Escapes",
        ],
    },
    "faith": {
        "name": "Faith, Festivals & Sacred Travel",
        "icon": "🛕",
        "subniches": [
            "Famous Temples & Shrines",
            "Hidden & Ancient Temples",
            "Religious Festivals & Pujas",
            "Pilgrimage Circuits & Yatras",
            "Festive Gifting Trends",
            "Spiritual Wellness & Meditation Drops",
        ],
    },
    "politics": {
        "name": "Politics, News & Civic Events",
        "icon": "🏛️",
        "subniches": [
            "Elections & Campaign Rallies",
            "Legislative Debates & Laws",
            "Protests & Policy Changes",
            "Politician Speeches & Interviews",
            "Geopolitical & Diplomatic Updates",
            "Public Schemes & Subsidies",
        ],
    },
}

# ==========================================
# 2. FLASK ROUTES & API ENDPOINTS
# ==========================================


@app.route("/")
def index():
    """Renders the main TrendPulse AI Dashboard UI."""
    return render_template_string(HTML_TEMPLATE, categories=MASTER_CATEGORIES)


@app.route("/api/trends", methods=["GET"])
def get_trends():
    """Returns trending signals across platforms and categories."""
    category = request.args.get("category", "commerce")
    # Mock dynamic trend feed based on selected category
    subniches = MASTER_CATEGORIES.get(category, {}).get(
        "subniches", ["General Trending Topic"]
    )

    trends = [
        {
            "id": "tr_001",
            "title": f"Surge in {subniches[0]} Market Demand",
            "category": category,
            "subniche": subniches[0],
            "velocity_score": 92,
            "saturation_risk": "Low (🟢)",
            "platforms": ["TikTok", "Amazon", "Google"],
        },
        {
            "id": "tr_002",
            "title": f"Viral Breakout in {subniches[1] if len(subniches) > 1 else subniches[0]}",
            "category": category,
            "subniche": subniches[1] if len(subniches) > 1 else subniches[0],
            "velocity_score": 85,
            "saturation_risk": "Medium (🟡)",
            "platforms": ["Instagram", "Pinterest"],
        },
    ]
    return jsonify({"status": "success", "trends": trends})


@app.route("/api/blueprint", methods=["POST"])
def generate_blueprint():
    """Generates the 6-Module Hybrid Strategy Blueprint based on Trend + Role."""
    data = request.json or {}
    trend_title = data.get("trend_title", "AI-Powered Automation Shift")
    role = data.get("role", "creator")

    # Role-specific tailored outputs
    role_actions = {
        "ecom": {
            "title": "E-Commerce Merchant Blueprint",
            "action": "Winning Product Angle: Source high-margin variants, run UGC unboxing ads on TikTok Shop with a 3-second hook.",
        },
        "creator": {
            "title": "Viral Content Creator Blueprint",
            "action": "Engagement CTA: 'Comment AI below and I will send you the complete 2026 prompt directory directly.'",
        },
        "affiliate": {
            "title": "Affiliate Marketer Blueprint",
            "action": "Bridge Page Angle: Emphasize time-saving benefits with a 48-hour scarcity timer.",
        },
        "realestate": {
            "title": "Real Estate Agent Blueprint",
            "action": "Client Psychology Pitch: Highlight transit corridor connectivity and high rental yields.",
        },
        "saas": {
            "title": "SaaS Founder Blueprint",
            "action": "PAS Framework: Problem (Manual workflows waste 10 hours), Agitate (Missed revenue), Solve (Deploy our 1-click agentic tool).",
        },
        "trader": {
            "title": "Trader & Analyst Blueprint",
            "action": "Sentiment Catalyst: Bullish breakout confirmation driven by institutional search volume spikes.",
        },
    }

    selected_role_action = role_actions.get(
        role, role_actions["creator"]
    )

    blueprint = {
        "module_1_validation": {
            "velocity_score": "94% (Rising Trajectory)",
            "saturation_warning": "Low Competition Index",
            "target_persona": "High-intent tech adopters & digital entrepreneurs",
        },
        "module_2_hooks": {
            "visual_hook": "Split-screen comparison showing 2024 manual workflow vs 2026 automated agentic dashboard.",
            "spoken_hook": "Stop wasting hours on manual tasks. Here is the exact blueprint taking over the internet.",
            "audio_track": "Trending Upbeat Lo-Fi / Electronic Pulse",
        },
        "module_3_script": {
            "short_form": "[0-3s] Hook overlay: 'The 2026 shift nobody is talking about.'\n[3-30s] Breakdown of the core mechanism.\n[30-45s] Call to action.",
            "hashtags": "#TrendPulse #Tech2026 #AIAutomation #GrowthHacking",
        },
        "module_4_role_action": selected_role_action,
        "module_5_funnel": {
            "primary_route": "Top-of-Funnel Viral Reel -> Mid-Funnel Free Resource -> Bottom-of-Funnel High-Ticket Offer",
        },
        "module_6_power_prompts": {
            "midjourney": "Cinematic product mockup of futuristic AI workspace, neon accent lighting, 8k resolution --ar 9:16",
            "elevenlabs": "Energetic, confident, professional tech reviewer tone with subtle dynamic pacing.",
            "cursor_prompt": "Create a responsive React component for a live velocity meter dashboard with Tailwind CSS.",
        },
    }

    return jsonify({"status": "success", "blueprint": blueprint})


# ==========================================
# 3. EMBEDDED FRONTEND INTERFACE (HTML/CSS/JS)
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrendPulse AI - Full Stack Execution Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
    <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <span class="text-2xl">🚀</span>
            <h1 class="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">TrendPulse AI</h1>
        </div>
        <div class="text-sm text-slate-400">12 Master Platforms • 20 Categories • 6 Operating Roles</div>
    </header>

    <main class="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Sidebar Controls -->
        <div class="lg:col-span-1 space-y-6">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <h3 class="font-semibold text-slate-200 mb-3">👤 Operating Role</h3>
                <select id="roleSelect" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500">
                    <option value="creator">🎬 Viral Content Creator</option>
                    <option value="ecom">🛍️ E-Commerce Merchant</option>
                    <option value="affiliate">💸 Affiliate Marketer</option>
                    <option value="realestate">🏢 Real Estate Agent</option>
                    <option value="saas">💻 SaaS Founder</option>
                    <option value="trader">📈 Stock & Crypto Analyst</option>
                </select>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <h3 class="font-semibold text-slate-200 mb-3">📁 Categories (20)</h3>
                <div class="space-y-1.5 max-h-[450px] overflow-y-auto pr-1">
                    {% for key, cat in categories.items() %}
                    <button onclick="loadTrends('{{ key }}')" class="category-btn w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-slate-800 transition flex items-center space-x-2 text-slate-300">
                        <span>{{ cat.icon }}</span>
                        <span class="truncate">{{ cat.name }}</span>
                    </button>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="lg:col-span-3 space-y-6">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h2 class="text-lg font-bold mb-4 flex items-center justify-between">
                    <span>🔥 Active Trend Signals</span>
                    <span id="currentCategoryTitle" class="text-xs bg-indigo-500/20 text-indigo-400 px-2.5 py-1 rounded-full border border-indigo-500/30">Category: Commerce</span>
                </h2>
                <div id="trendsContainer" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Dynamic Trends Loaded Here -->
                </div>
            </div>

            <!-- Blueprint Output Section -->
            <div id="blueprintContainer" class="bg-slate-900 border border-slate-800 rounded-xl p-6 hidden">
                <div class="flex justify-between items-center mb-4 border-b border-slate-800 pb-3">
                    <h3 class="text-lg font-bold text-cyan-400">⚡ Execution Strategy Blueprint</h3>
                    <button onclick="copyBlueprint()" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3 py-1.5 rounded-lg transition">📋 Copy Full Script</button>
                </div>
                <div id="blueprintContent" class="space-y-4 text-sm text-slate-300">
                    <!-- Populated via JS -->
                </div>
            </div>
        </div>
    </main>

    <script>
        let currentCategory = 'commerce';

        function loadTrends(categoryKey) {
            currentCategory = categoryKey;
            document.getElementById('currentCategoryTitle').innerText = 'Category: ' + categoryKey.toUpperCase();
            
            fetch('/api/trends?category=' + categoryKey)
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('trendsContainer');
                    container.innerHTML = '';
                    data.trends.forEach(trend => {
                        container.innerHTML += `
                            <div class="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col justify-between space-y-3">
                                <div>
                                    <div class="flex justify-between items-start mb-2">
                                        <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded">${trend.subniche}</span>
                                        <span class="text-xs text-emerald-400 font-semibold">🔥 ${trend.velocity_score}%</span>
                                    </div>
                                    <h4 class="font-semibold text-slate-100">${trend.title}</h4>
                                    <p class="text-xs text-slate-400 mt-1">Saturation: ${trend.saturation_risk}</p>
                                </div>
                                <button onclick="generateBlueprint('${trend.title}')" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2 rounded-lg transition">
                                    ⚡ Generate Blueprint
                                </button>
                            </div>
                        `;
                    });
                });
        }

        function generateBlueprint(trendTitle) {
            const role = document.getElementById('roleSelect').value;
            fetch('/api/blueprint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ trend_title: trendTitle, role: role })
            })
            .then(res => res.json())
            .then(data => {
                const bp = data.blueprint;
                const container = document.getElementById('blueprintContainer');
                container.classList.remove('hidden');
                
                document.getElementById('blueprintContent').innerHTML = `
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                            <h4 class="font-semibold text-indigo-400 mb-2">📊 Validation & Hooks</h4>
                            <p><strong>Velocity:</strong> ${bp.module_1_validation.velocity_score}</p>
                            <p class="mt-1"><strong>Visual Hook:</strong> ${bp.module_2_hooks.visual_hook}</p>
                            <p class="mt-1"><strong>Audio:</strong> ${bp.module_2_hooks.audio_track}</p>
                        </div>
                        <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                            <h4 class="font-semibold text-cyan-400 mb-2">💼 Role-Specific Action</h4>
                            <p class="font-medium text-white">${bp.module_4_role_action.title}</p>
                            <p class="mt-1 text-slate-300">${bp.module_4_role_action.action}</p>
                        </div>
                    </div>
                    <div class="bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <h4 class="font-semibold text-emerald-400 mb-2">🚀 Power-User Prompts (Advanced)</h4>
                        <p class="text-xs font-mono text-slate-400"><strong>Midjourney:</strong> ${bp.module_6_power_prompts.midjourney}</p>
                        <p class="text-xs font-mono text-slate-400 mt-1"><strong>Cursor Agentic:</strong> ${bp.module_6_power_prompts.cursor_prompt}</p>
                    </div>
                `;
                container.scrollIntoView({ behavior: 'smooth' });
            });
        }

        // Load default commerce trends on start
        loadTrends('commerce');
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
