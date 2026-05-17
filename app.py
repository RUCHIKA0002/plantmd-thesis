import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from database import init_db, save_scan, get_all_scans, get_scan_stats
from detector import detect_disease, chat_about_disease

init_db()

# Custom CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2137 0%, #0a1628 100%);
        border-right: 1px solid #1e3a5f;
    }
    
    /* Cards */
    .disease-card {
        background: linear-gradient(135deg, #1a2f4a, #0d2137);
        border: 1px solid #2d6a4f;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(45, 106, 79, 0.3);
    }
    
    .healthy-card {
        background: linear-gradient(135deg, #1a3a2a, #0d2137);
        border: 2px solid #2d6a4f;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 25px rgba(45, 106, 79, 0.4);
    }
    
    .diseased-card {
        background: linear-gradient(135deg, #3a1a1a, #0d2137);
        border: 2px solid #c0392b;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 25px rgba(192, 57, 43, 0.4);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #3a2a1a, #0d2137);
        border: 2px solid #e67e22;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 25px rgba(230, 126, 34, 0.4);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a2f4a, #0d2137);
        border: 1px solid #2d6a4f;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #8899aa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Treatment steps */
    .treatment-step {
        background: linear-gradient(90deg, #1a3a2a, #1a2f4a);
        border-left: 4px solid #2d6a4f;
        border-radius: 8px;
        padding: 12px 15px;
        margin: 8px 0;
        color: #e0e0e0;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(135deg, #0d2137, #1a3a2a);
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid #2d6a4f;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4CAF50, #2d6a4f, #81C784);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .header-subtitle {
        color: #8899aa;
        font-size: 1rem;
        margin-top: 5px;
    }
    
    /* Upload zone */
    .upload-zone {
        border: 2px dashed #2d6a4f;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background: rgba(45, 106, 79, 0.05);
    }
    
    /* Confidence bar */
    .conf-bar-container {
        background: #1a2f4a;
        border-radius: 10px;
        height: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #0d2137;
        border-radius: 10px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #8899aa;
        padding: 8px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2d6a4f, #1a5c3a) !important;
        color: white !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2d6a4f, #1a5c3a);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(45, 106, 79, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(45, 106, 79, 0.6);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Text colors */
    h1, h2, h3 { color: #e0e0e0 !important; }
    p, li { color: #b0c4d8; }
    
    /* Chat messages */
    .stChatMessage {
        background: #1a2f4a !important;
        border-radius: 12px !important;
        border: 1px solid #2d6a4f !important;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid #2d6a4f;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session state
for key, default in [("diagnosis", None), ("chat_history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# Header
st.markdown("""
<div class="main-header">
    <p class="header-title">🌿 PlantMD</p>
    <p class="header-subtitle">AI-Powered Plant Disease Detection System | Master's Thesis Project</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <h2 style="color:#4CAF50;">🌿 PlantMD</h2>
        <p style="color:#8899aa; font-size:0.8rem;">AI Plant Disease Detection</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style="color:#b0c4d8;">
    <b style="color:#4CAF50;">How to use:</b><br><br>
    1. Go to <b>Detect</b> tab<br>
    2. Upload plant photo<br>
    3. Click <b>Analyze</b><br>
    4. Chat for more details<br>
    5. Check History & Analytics
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Stats in sidebar
    scans = get_all_scans()
    if scans:
        stats = get_scan_stats()
        st.markdown("<b style='color:#4CAF50;'>Live Stats</b>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Total", stats["total"])
        col2.metric("Diseased", stats["diseased"])

    st.divider()
    st.markdown("<p style='color:#8899aa; font-size:0.75rem; text-align:center;'>Powered by Groq AI<br>Master Thesis 2025</p>", unsafe_allow_html=True)

# Tabs
tab_detect, tab_chat, tab_history, tab_analytics = st.tabs([
    "🔬 Detect", "💬 Chat", "📋 History", "📊 Analytics"
])

# ── TAB 1: DETECT ──────────────────────────────────────────
with tab_detect:
    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("<h3 style='color:#4CAF50;'>Upload Plant Image</h3>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Choose a clear photo of affected leaf",
            type=["jpg", "jpeg", "png", "webp"],
        )
        if uploaded:
            st.image(Image.open(uploaded), use_container_width=True, caption="Your plant")
            if st.button("🔬 Analyze Plant", type="primary", use_container_width=True):
                with st.spinner("AI is analyzing your plant..."):
                    try:
                        uploaded.seek(0)
                        result = detect_disease(uploaded)
                        st.session_state.diagnosis = result
                        st.session_state.chat_history = []
                        save_scan(result)
                        st.success("Analysis complete!")
                    except Exception as e:
                        st.error(f"Failed: {e}")
        else:
            st.markdown("""
            <div class="upload-zone">
                <h3 style="color:#4CAF50;">📸 Upload Image</h3>
                <p style="color:#8899aa;">JPG, PNG, WEBP supported</p>
                <p style="color:#8899aa; font-size:0.85rem;">Best results with clear, well-lit photos</p>
            </div>
            """, unsafe_allow_html=True)

    with col_result:
        if st.session_state.diagnosis is None:
            st.markdown("""
            <div class="disease-card" style="text-align:center; padding:40px;">
                <h2 style="color:#4CAF50;">🌱</h2>
                <h3 style="color:#4CAF50;">Ready to Analyze</h3>
                <p style="color:#8899aa;">Upload a plant image to detect diseases instantly</p>
                <br>
                <p style="color:#8899aa; font-size:0.85rem;">Tips for best results:</p>
                <p style="color:#8899aa; font-size:0.8rem;">Use natural daylight</p>
                <p style="color:#8899aa; font-size:0.8rem;">Focus on affected area</p>
                <p style="color:#8899aa; font-size:0.8rem;">Avoid blurry photos</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            r = st.session_state.diagnosis
            card_class = {"healthy": "healthy-card", "diseased": "diseased-card", "warning": "warning-card"}.get(r["status"], "disease-card")
            status_emoji = {"healthy": "✅", "diseased": "🔴", "warning": "⚠️"}.get(r["status"], "🔍")
            status_color = {"healthy": "#4CAF50", "diseased": "#e74c3c", "warning": "#e67e22"}.get(r["status"], "#4CAF50")

            st.markdown(f"""
            <div class="{card_class}">
                <h2 style="color:{status_color}; margin:0;">{status_emoji} {r['disease_name']}</h2>
                <p style="color:#8899aa; font-style:italic; margin:5px 0;">{r.get('scientific_name', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{status_color};">{r['severity']}</div>
                <div class="metric-label">Severity</div></div>""", unsafe_allow_html=True)
            m2.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:#4CAF50;">{r['confidence']}%</div>
                <div class="metric-label">Confidence</div></div>""", unsafe_allow_html=True)
            m3.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{status_color};">{r['urgency']}</div>
                <div class="metric-label">Urgency</div></div>""", unsafe_allow_html=True)

            st.progress(r["confidence"] / 100)
            st.divider()

            st.markdown("<h4 style='color:#4CAF50;'>Observation</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b0c4d8;'>{r['description']}</p>", unsafe_allow_html=True)

            st.markdown("<h4 style='color:#4CAF50;'>Recommended Treatments</h4>", unsafe_allow_html=True)
            for t in r["treatments"]:
                st.markdown(f'<div class="treatment-step">{t}</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<h4 style='color:#4CAF50;'>Causes</h4>", unsafe_allow_html=True)
                for cause in r["causes"]:
                    st.markdown(f"<p style='color:#b0c4d8;'>• {cause}</p>", unsafe_allow_html=True)
            with c2:
                st.markdown("<h4 style='color:#4CAF50;'>Prevention</h4>", unsafe_allow_html=True)
                for tip in r["prevention"]:
                    st.markdown(f"<p style='color:#b0c4d8;'>• {tip}</p>", unsafe_allow_html=True)

            if r.get("affected_parts"):
                st.markdown(f"<p style='color:#8899aa;'>Affected parts: <b style='color:#4CAF50;'>{', '.join(r['affected_parts'])}</b></p>", unsafe_allow_html=True)

            st.info("Switch to Chat tab to ask follow-up questions")

# ── TAB 2: CHAT ────────────────────────────────────────────
with tab_chat:
    st.markdown("<h3 style='color:#4CAF50;'>Chat About Your Plant</h3>", unsafe_allow_html=True)

    if st.session_state.diagnosis is None:
        st.markdown("""
        <div class="disease-card" style="text-align:center; padding:30px;">
            <h3 style="color:#4CAF50;">💬</h3>
            <p style="color:#8899aa;">Run a detection first in the Detect tab</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        r = st.session_state.diagnosis
        st.markdown(f"""
        <div class="disease-card">
            <p style="color:#8899aa; margin:0;">Chatting about: <b style="color:#4CAF50;">{r['disease_name']}</b> | Confidence: <b style="color:#4CAF50;">{r['confidence']}%</b></p>
        </div>
        """, unsafe_allow_html=True)

        suggestions = [
            "How long will treatment take?",
            "Is this contagious to other plants?",
            "What organic treatments can I use?",
            "When should I see improvement?",
        ]
        st.markdown("<p style='color:#8899aa; font-size:0.85rem;'>Suggested questions:</p>", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}"):
                st.session_state["_auto_q"] = s

        st.divider()
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        auto_q = st.session_state.pop("_auto_q", None)
        if question := (st.chat_input("Ask about disease or treatment...") or auto_q):
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = chat_about_disease(question, st.session_state.diagnosis, st.session_state.chat_history[:-1])
                st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

        if st.session_state.chat_history:
            if st.button("Clear chat"):
                st.session_state.chat_history = []
                st.rerun()

# ── TAB 3: HISTORY ─────────────────────────────────────────
with tab_history:
    st.markdown("<h3 style='color:#4CAF50;'>Scan History</h3>", unsafe_allow_html=True)
    scans = get_all_scans()
    if not scans:
        st.markdown("""
        <div class="disease-card" style="text-align:center; padding:30px;">
            <p style="color:#8899aa;">No scans yet. Run your first detection!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        stats = get_scan_stats()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total"]}</div><div class="metric-label">Total Scans</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e74c3c;">{stats["diseased"]}</div><div class="metric-label">Diseased</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#4CAF50;">{stats["healthy"]}</div><div class="metric-label">Healthy</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="metric-value">{stats["avg_confidence"]}%</div><div class="metric-label">Avg Confidence</div></div>', unsafe_allow_html=True)
        st.divider()
        df = pd.DataFrame(scans)[["timestamp","disease_name","status","severity","confidence","urgency"]]
        df.columns = ["Time","Disease","Status","Severity","Confidence %","Urgency"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", data=df.to_csv(index=False).encode(), file_name="plantmd_history.csv", mime="text/csv")

# ── TAB 4: ANALYTICS ───────────────────────────────────────
with tab_analytics:
    st.markdown("<h3 style='color:#4CAF50;'>Analytics Dashboard</h3>", unsafe_allow_html=True)
    scans = get_all_scans()
    if len(scans) < 2:
        st.markdown("""
        <div class="disease-card" style="text-align:center; padding:30px;">
            <p style="color:#8899aa;">Run at least 2 scans to see analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = pd.DataFrame(scans)
        stats = get_scan_stats()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total"]}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e74c3c;">{stats["diseased"]}</div><div class="metric-label">Diseased</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#4CAF50;">{stats["healthy"]}</div><div class="metric-label">Healthy</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="metric-value">{stats["avg_confidence"]}%</div><div class="metric-label">Avg Conf</div></div>', unsafe_allow_html=True)
        st.divider()

        plt.style.use('dark_background')
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4 style='color:#4CAF50;'>Status Distribution</h4>", unsafe_allow_html=True)
            status_counts = df["status"].value_counts()
            colors = {"healthy": "#4CAF50", "diseased": "#e74c3c", "warning": "#e67e22"}
            fig, ax = plt.subplots(figsize=(4, 4), facecolor='#0d2137')
            ax.set_facecolor('#0d2137')
            ax.pie(status_counts.values, labels=status_counts.index,
                colors=[colors.get(s, "#888") for s in status_counts.index],
                autopct="%1.1f%%", startangle=90,
                textprops={'color': 'white'})
            st.pyplot(fig)
            plt.close()

        with c2:
            st.markdown("<h4 style='color:#4CAF50;'>Top Diseases</h4>", unsafe_allow_html=True)
            top = df["disease_name"].value_counts().head(6)
            fig2, ax2 = plt.subplots(figsize=(5, 4), facecolor='#0d2137')
            ax2.set_facecolor('#0d2137')
            top.plot(kind="barh", ax=ax2, color="#4CAF50")
            ax2.tick_params(colors='white')
            ax2.set_xlabel("Count", color='white')
            ax2.spines['bottom'].set_color('#2d6a4f')
            ax2.spines['left'].set_color('#2d6a4f')
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()

        st.markdown("<h4 style='color:#4CAF50;'>Confidence Distribution</h4>", unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(8, 3), facecolor='#0d2137')
        ax3.set_facecolor('#0d2137')
        ax3.hist(df["confidence"].astype(int), bins=10, color="#4CAF50", edgecolor="#0d2137")
        ax3.tick_params(colors='white')
        ax3.set_xlabel("Confidence %", color='white')
        ax3.set_ylabel("Count", color='white')
        ax3.spines['bottom'].set_color('#2d6a4f')
        ax3.spines['left'].set_color('#2d6a4f')
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
