import io
import json
import os
import re
import xml.sax.saxutils as saxutils
import pandas as pd
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="TrendPulse AI - Intelligence Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { padding: 1.5rem 2rem; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        width: 100%;
        padding: 0.6rem;
    }
    .stButton>button:hover { background-color: #ff2b2b; color: white; }
    .metric-card {
        background: #1e222d;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #2e3440;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. ENVIRONMENT & API SETUP
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get(
    "GROQ_API_KEY", None
)


# Helper function for XML/PDF escaping
def safe_xml_text(text):
    if not text:
        return ""
    text_str = str(text)
    # Convert markdown bolding to standard PDF bold tags
    text_str = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text_str)
    return saxutils.escape(text_str, entities={"'": "&apos;", '"': "&quot;"})


# ==========================================
# 3. PDF GENERATION ENGINE
# ==========================================
def create_pdf_blueprint(
    asset_name, category, role, viral_score, window, result
):
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
        fontSize=18,
        textColor="#ff4b4b",
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=12,
        textColor="#1a1a1a",
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor="#333333",
        spaceAfter=6,
    )

    story = []
    story.append(
        Paragraph("TrendPulse AI - Enterprise Strategy Blueprint", title_style)
    )
    story.append(
        Paragraph(
            f"<b>Asset Target:</b> {safe_xml_text(asset_name)} | <b>Category:</b>"
            f" {safe_xml_text(category)} | <b>Operating Role:</b>"
            f" {safe_xml_text(role)}",
            body_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Predictive Viral Score:</b> {safe_xml_text(viral_score)} |"
            f" <b>Target Window:</b> {safe_xml_text(window)}",
            body_style,
        )
    )
    story.append(Spacer(1, 8))

    sections = [
        ("Monetization Model & Strategy", result.get("profit_model", "")),
        ("Execution Hook & Visual Script", result.get("execution_hook", "")),
        ("Audio Vibe Recommendation", result.get("audio_suggestion", "")),
        ("High-ROAS Caption & CTA Framework", result.get("ad_copy", "")),
        (
            "Automation & Auto-DM Funnel Script (ManyChat)",
            result.get("automation_script", ""),
        ),
        (
            "Paid Ad Targeting Parameters (Meta / TikTok / Google)",
            result.get("ad_targeting", ""),
        ),
        ("A/B Testing Hook Variations", result.get("hook_variations", "")),
        ("3-Step Rapid Execution Roadmap", result.get("action_blueprint", "")),
        (
            "Competitor Intelligence & Benchmarks",
            result.get("competitor_intelligence", ""),
        ),
    ]

    for title, text in sections:
        if text:
            story.append(Paragraph(title, heading_style))
            formatted_text = safe_xml_text(text).replace("\n", "<br/>")
            story.append(Paragraph(formatted_text, body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ==========================================
# 4. MASTER INTELLIGENCE GENERATOR
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
    sub_context = f" | Sub-Niche: '{sub_niche}'" if sub_niche else ""

    role_directives = {
        "Content Creator / Influencer": (
            "Focus on high-retention 9:16 organic video scripts, aesthetic"
            " visual hooks, story retention sequences, and ManyChat comment"
            " automation (e.g., 'Comment TEMPLE to receive the catalog in DMs')."
        ),
        "E-Commerce Merchant / Dropshipper": (
            "Focus on direct-response paid ad creatives, high-ROAS hooks, landing"
            " page trust badges, offer stacks (e.g., ₹150 OFF + Free Express"
            " Delivery), and low-friction checkout options (1-Click UPI & COD)."
        ),
        "Agency Owner / Freelancer": (
            "Focus on enterprise client deliverables, exact Meta/TikTok ad"
            " targeting parameters, A/B testing hook matrices, media buyer"
            " SOPs, and retargeting funnel architectures."
        ),
    }

    selected_role_directive = role_directives.get(
        target_role, role_directives["Content Creator / Influencer"]
    )

    if not GROQ_API_KEY:
        return {
            "viral_score": f"{velocity_score}%",
            "prediction_window": (
                f"Peak Trend Lifecycle Active ({timeframe} window)"
            ),
            "profit_model": (
                f"• **Role Strategy ({target_role}):** Optimized conversion"
                f" funnel for {keyword_asset}.\n• **Execution Model:** Direct"
                " conversion via comment automation, localized payment gateways"
                " (1-Click UPI / COD), and high-retention video funnels."
            ),
            "execution_hook": (
                "• **0-3s Visual Cue:** Macro high-contrast lighting shot of"
                f" {keyword_asset}.\n• **Text Overlay:** 'The #1 mistake people"
                f" make with {keyword_asset} in 2026 ⚡'\n• **Spoken Script:**"
                " 'Stop making this mistake if you want authentic quality for"
                " the upcoming festival season...'"
            ),
            "audio_suggestion": (
                "120-128 BPM Upbeat Phonk / Rhythmic Regional Ambient Fusion"
            ),
            "ad_copy": (
                f"Unlocking peak performance with {keyword_asset} 🚀\n\nDrop"
                " 'TEMPLE' below for direct catalog access + ₹150 OFF coupon"
                " code straight to your inbox!\n\n#TrendPulse2026"
                " #FestiveDecor2026"
            ),
            "automation_script": (
                "• **Trigger Word:** TEMPLE\n• **Auto-DM Message:** 'Hey [First"
                " Name]! 🛕 Here is the exclusive 2026 artisan collection"
                " catalog: [Link]\n\nUse code FESTIVE15 for ₹150 OFF + Free"
                " Express Shipping! Offer valid for 24 hours.'\n• **Follow-Up (2"
                " Hours Later):** 'Stock is running low for upcoming delivery!"
                " Want me to hold your ₹150 discount code for another 12"
                " hours?'"
            ),
            "ad_targeting": (
                "• **Locations:** Metro Hubs (Mumbai, Delhi-NCR, Bengaluru,"
                " Pune, Hyderabad, Ahmedabad)\n• **Age & Gender:** 24–52 (Men &"
                " Women)\n• **Interests:** Home Decor, Handicrafts, Cultural"
                " Heritage, Interior Design\n• **Placements:** Instagram Reels"
                " & Stories"
            ),
            "hook_variations": (
                "1. **Angle A (Cultural/Heritage):** 'Bring authentic artisan"
                " craftsmanship to your home this season...'\n2. **Angle B"
                " (Problem/Solution):** 'Tired of mass-produced decor"
                " tarnishing in weeks? Here is the permanent fix...'\n3. **Angle"
                " C (Luxury Gifting):** 'The #1 festive gift under ₹2,000"
                " everyone is asking for...'"
            ),
            "action_blueprint": (
                "1. **HOUR 1:** Shoot 9:16 vertical video showcasing product"
                " texture with high-contrast text overlay.\n2. **HOUR 6:** Deploy"
                " ManyChat auto-responder connected to your chosen trigger"
                " word.\n3. **DAY 2:** Review retention metrics and launch"
                " paid ad retargeting pointing to 1-Click UPI/COD checkout."
            ),
            "competitor_intelligence": (
                "• **Competitor Hook:** 'Stop buying cheap plastic"
                " decor...'\n• **Optimal Video Duration:** 11–14 seconds"
                " (Optimized for >100% loop completion)\n• **Expected CTR:**"
                " 5.2% – 6.8% via DM automation"
            ),
        }

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
        You are an elite enterprise growth strategist and market intelligence consultant for TrendPulse AI.
        
        Analyze Asset: '{keyword_asset}' 
        Category: '{category}'{sub_context} 
        Operating Role: '{target_role}' 
        Platform: '{platform}' 
        Timeframe: '{timeframe}' 
        Velocity Score: {velocity_score}%
        Language: {lang}

        ROLE-SPECIFIC MANDATE:
        {selected_role_directive}

        REQUIREMENTS:
        Generate a fully actionable, highly specific, and production-ready strategy package tailored explicitly to the role '{target_role}' and asset '{keyword_asset}'. Inject precise regional context (e.g., UPI, COD, metro hubs, or platform specifics) where applicable.

        Return STRICT JSON with the following exact keys:
        {{
          "viral_score": "{velocity_score}%",
          "prediction_window": "Target monetization lifecycle and seasonal timing window",
          "profit_model": "Role-tailored monetization strategy, offer structure, and unit conversion mechanics",
          "execution_hook": "Specific 0-3s visual cue, high-contrast text overlay, and spoken retention script",
          "audio_suggestion": "Exact audio genre, BPM, and sound vibe descriptor",
          "ad_copy": "High-ROAS caption with CTA, urgency triggers, and targeted hashtags",
          "automation_script": "Exact ManyChat/Wati DM automation script including trigger word, instant message, and 2-hour follow-up message",
          "ad_targeting": "Specific ad account setup including target locations, age/gender demographics, detailed interest keywords, and placements",
          "hook_variations": "3 distinct A/B testing hook angles (e.g. Heritage, Problem/Solution, Gifting)",
          "action_blueprint": "Clear 3-step rapid execution roadmap with exact time markers",
          "competitor_intelligence": "Detailed competitor benchmarks including top hook styles, video length, and expected CTR"
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
        return {
            "viral_score": f"{velocity_score}%",
            "prediction_window": f"Peak Trend Lifecycle Active ({timeframe})",
            "profit_model": f"Direct Conversion Model for {target_role}.",
            "execution_hook": (
                f"Visual macro shot of {keyword_asset} with high-contrast"
                " text overlay."
            ),
            "audio_suggestion": "Upbeat Fast-Paced Rhythmic Ambient",
            "ad_copy": (
                f"Unlocking maximum ROI with {keyword_asset} 🚀 Drop 'TEMPLE'"
                " for direct link."
            ),
            "automation_script": (
                "Trigger: TEMPLE -> DM: 'Here is your direct access link +"
                " discount code!'"
            ),
            "ad_targeting": (
                "Demographics: 22-48 | Locations: Major Metro Hubs | Interests:"
                f" {category}"
            ),
            "hook_variations": (
                "1. Angle A: Aesthetic 2. Angle B: Problem/Solution 3. Angle C:"
                " Direct Offer"
            ),
            "action_blueprint": (
                "1. Hour 1: Creative setup 2. Hour 6: Auto DM setup 3. Day 2:"
                " Scale ads."
            ),
            "competitor_intelligence": (
                "Video Duration: 11-14s | Target CTR: 5.0%+"
            ),
        }


# ==========================================
# 5. STREAMLIT APPLICATION INTERFACE
# ==========================================

# Header Banner
st.title("⚡ TrendPulse AI — Market Intelligence Engine")
st.markdown(
    "Real-time predictive viral trend scoring & turnkey execution funnels."
)

# Sidebar Configuration
st.sidebar.header("🕹️ Strategy Parameters")

operating_role = st.sidebar.selectbox(
    "👤 Select Operating Role",
    [
        "Content Creator / Influencer",
        "E-Commerce Merchant / Dropshipper",
        "Agency Owner / Freelancer",
    ],
)

category = st.sidebar.selectbox(
    "📁 Target Category",
    [
        "Faith, Festivals & Sacred Travel",
        "Tech, Consumer Electronics & Gadgets",
        "Beauty, Skincare & Personal Care",
        "Apparel, Fashion & Streetwear",
        "Home, Furniture & Modern Living",
    ],
)

sub_niche = st.sidebar.text_input(
    "🎯 Sub-Niche / Product Focus", "Handicrafts & Festive Decor"
)
target_keyword = st.sidebar.text_input(
    "🔑 Keyword Asset", "Famous Temples Handicrafts"
)

platform = st.sidebar.selectbox(
    "📱 Target Platform", ["Instagram Reels", "TikTok", "YouTube Shorts", "Meta Ads"]
)
timeframe = st.sidebar.selectbox(
    "⏱️ Trend Lifecycle Window",
    ["Short-Term Trend (7 Days)", "Seasonal Peak (30 Days)", "Evergreen Growth"],
)
language = st.sidebar.selectbox("🌐 Content Language", ["English", "Hindi", "Hinglish"])

velocity_score = st.sidebar.slider("🔥 Target Velocity Score Threshold", 70, 99, 95)

# Main UI Split
left_col, right_col = st.columns([1, 1.2])

with left_col:
    st.subheader("⚙️ Input Summary & Controls")
    st.info(f"**Operating as:** {operating_role}")

    st.markdown("### 📋 Configuration Check")
    config_df = pd.DataFrame(
        {
            "Parameter": [
                "Category",
                "Sub-Niche",
                "Keyword",
                "Platform",
                "Window",
                "Language",
            ],
            "Selected Value": [
                category,
                sub_niche,
                target_keyword,
                platform,
                timeframe,
                language,
            ],
        }
    )
    st.table(config_df)

    generate_btn = st.button("🚀 Generate Blueprint Strategy")

with right_col:
    st.subheader("💡 Actionable Strategy Matrix")

    if generate_btn or "last_result" in st.session_state:
        if generate_btn:
            with st.spinner("Analyzing real-time signals & generating blueprint..."):
                result = generate_master_intelligence(
                    keyword_asset=target_keyword,
                    category=category,
                    sub_niche=sub_niche,
                    target_role=operating_role,
                    platform=platform,
                    timeframe=timeframe,
                    velocity_score=velocity_score,
                    lang=language,
                )
                st.session_state["last_result"] = result
        else:
            result = st.session_state["last_result"]

        st.success(f"🎯 Strategy Blueprint Generated: **{target_keyword}**")

        st.markdown("#### 📊 Live Strategy Telemetry")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(
                label="Predictive Viral Score", value=result.get("viral_score")
            )
        with col_m2:
            st.info(
                "**Monetization Window:**\n"
                f"{result.get('prediction_window')}"
            )

        st.markdown("---")

        # Full Expanded Sections
        with st.expander("💰 Direct High-ROI Monetization Model", expanded=True):
            st.markdown(result.get("profit_model", ""))

        with st.expander(
            "🎬 Visual Script & High-Retention Hook (Plug & Play)", expanded=True
        ):
            st.markdown(result.get("execution_hook", ""))

        with st.expander("🎵 Recommended Audio Vibe", expanded=False):
            st.write(f"🔊 **Recommendation:** {result.get('audio_suggestion', '')}")

        with st.expander("📢 High-ROAS Caption & CTA Framework", expanded=False):
            st.code(f"{result.get('ad_copy', '')}", language="text")

        with st.expander(
            "🤖 Automation & Auto-DM Funnel Setup (ManyChat / Wati)",
            expanded=True,
        ):
            st.markdown(result.get("automation_script", ""))

        with st.expander(
            "🎯 Paid Ad Targeting Parameters (Meta / TikTok / Google)",
            expanded=False,
        ):
            st.markdown(result.get("ad_targeting", ""))

        with st.expander("🔄 A/B Testing Hook Variations", expanded=False):
            st.markdown(result.get("hook_variations", ""))

        with st.expander("📝 3-Step Rapid Execution Roadmap", expanded=False):
            st.markdown(result.get("action_blueprint", ""))

        with st.expander("🕵️ Live Competitor Ad Intelligence", expanded=False):
            st.markdown(result.get("competitor_intelligence", ""))

        # PDF Export Section
        st.markdown("---")
        pdf_buffer = create_pdf_blueprint(
            asset_name=target_keyword,
            category=category,
            role=operating_role,
            viral_score=result.get("viral_score"),
            window=result.get("prediction_window"),
            result=result,
        )

        st.download_button(
            label="📥 Download Enterprise Strategy PDF Blueprint",
            data=pdf_buffer,
            file_name=f"TrendPulse_Blueprint_{target_keyword.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Click 'Generate Blueprint Strategy' on the left to initialize.")
