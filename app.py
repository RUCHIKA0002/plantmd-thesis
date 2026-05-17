import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from database import init_db, save_scan, get_all_scans, get_scan_stats
from detector import detect_disease, chat_about_disease

init_db()

# Theme toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
for key, default in [("diagnosis", None), ("chat_history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# Theme colors
if st.session_state.dark_mode:
    bg_color = "#0a1628"
    card_bg = "rgba(13, 33, 55, 0.85)"
    text_color = "#e0e0e0"
    sub_text = "#8899aa"
    border_color = "#2d6a4f"
    metric_bg = "rgba(26, 47, 74, 0.9)"
    sidebar_bg = "rgba(10, 22, 40, 0.95)"
    theme_icon = "☀️"
    theme_label = "Light Mode"
else:
    bg_color = "#f0f7f0"
    card_bg = "rgba(255, 255, 255, 0.88)"
    text_color = "#1a3a2a"
    sub_text = "#5a7a6a"
    border_color = "#2d6a4f"
    metric_bg = "rgba(240, 247, 240, 0.95)"
    sidebar_bg = "rgba(220, 240, 220, 0.95)"
    theme_icon = "🌙"
    theme_label = "Dark Mode"

# Background plant image + CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {{ font-family: 'Poppins', sans-serif; }}

.stApp {{
    background-image: url('https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1920&q=80');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: {'rgba(10, 22, 40, 0.82)' if st.session_state.dark_mode else 'rgba(240, 247, 235, 0.85)'};
    backdrop-filter: blur(3px);
    z-index: 0;
}}

[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    backdrop-filter: blur(15px) !important;
    border-right: 1px solid {border_color} !important;
}}

[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

.main-header {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 1px solid {border_color};
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(45, 106, 79, 0.2);
}}

.header-title {{
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4CAF50, #81C784, #2d6a4f);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}}

.header-subtitle {{
    color: {sub_text};
    font-size: 0.95rem;
    margin-top: 5px;
}}

.glass-card {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    color: {text_color};
}}

.healthy-card {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 2px solid #4CAF50;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
}}

.diseased-card {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 2px solid #e74c3c;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(231, 76, 60, 0.3);
}}

.warning-card {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 2px solid #e67e22;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(230, 126, 34, 0.3);
}}

.metric-card {{
    background: {metric_bg};
    backdrop-filter: blur(15px);
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

.metric-value {{
    font-size: 1.8rem;
    font-weight: 700;
    color: #4CAF50;
}}

.metric-label {{
    font-size: 0.75rem;
    color: {sub_text};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.treatment-step {{
    background: {'rgba(45, 106, 79, 0.15)' if st.session_state.dark_mode else 'rgba(45, 106, 79, 0.08)'};
    border-left: 4px solid #4CAF50;
    border-radius: 8px;
    padding: 12px 15px;
    margin: 8px 0;
    color: {text_color};
    backdrop-filter: blur(10px);
}}

.upload-zone {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 2px dashed {border_color};
    border-radius: 16px;
    padding: 40px 20px;
    text-align: center;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {card_bg};
    backdrop-filter: blur(15px);
    border-radius: 12px;
    padding: 5px;
    border: 1px solid {border_color};
}}

.stTabs [data-baseweb="tab"] {{
    color: {sub_text};
    border-radius: 8px;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, #2d6a4f, #4CAF50) !important;
    color: white !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #2d6a4f, #4CAF50);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(45, 106, 79, 0.4);
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(45, 106, 79, 0.6);
}}

h1, h2, h3, h4 {{ color: {text_color} !important; }}
p, li, label {{ color: {text_color}; }}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

.stChatMessage {{
    background: {card_bg} !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid {border_color} !important;
    border-radius: 12px !important;
}}
</style>
""", unsafe_allow_html=True)

# Header + Theme Toggle
col_head, col_toggle = st.columns([5, 1])
with col_head:
    st.markdown(f"""
    <div class="main-header">
        <p class="header-title">🌿 PlantMD</p>
        <p class="header-subtitle">AI-Powered Plant Disease Detection | Master's Thesis 2025</p>
    </div>
    """, unsafe_allow_html=True)
with col_toggle:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button(f"{theme_icon} {theme_label}"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:15px;">
        <div style="font-size:3rem;">🌿</div>
        <h2 style="color:#4CAF50; margin:5px 0;">PlantMD</h2>
        <p style="color:{sub_text}; font-size:0.8rem;">AI Plant Disease Detection</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown(f"""
    <div style="color:{text_color}; line-height:2;">
    <b style="color:#4CAF50;">How to use:</b><br>
    1. Go to <b>Detect</b> tab<br>
    2. Upload plant photo<br>
    3. Click <b>Analyze</b><br>
    4. Chat for details<br>
    5. Check Analytics
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    scans = get_all_scans()
    if scans:
        stats = get_scan_stats()
        st.markdown(f"<b style='color:#4CAF50;'>Live Stats</b>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Total", stats["total"])
        c2.metric("Diseased", stats["diseased"])
    st.divider()
    st.markdown(f"<p style='color:{sub_text}; font-size:0.75rem; text-align:center;'>Powered by Groq AI<br>Master Thesis 2025</p>", unsafe_allow_html=True)

# Tabs
tab_detect, tab_chat, tab_history, tab_analytics = st.tabs([
    "🔬 Detect", "💬 Chat", "📋 History", "📊 Analytics"
])

# ── TAB 1: DETECT ─────────────────────────────────────────
with tab_detect:
    col_upload, col_result = st.columns([1, 1], gap="large")
    with col_upload:
        st.markdown(f"<h3 style='color:#4CAF50;'>Upload Plant Image</h3>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose a clear photo", type=["jpg", "jpeg", "png", "webp"])
        if uploaded:
            st.image(Image.open(uploaded), use_container_width=True, caption="Your plant")
            if st.button("🔬 Analyze Plant", type="primary", use_container_width=True):
                with st.spinner("AI analyzing your plant..."):
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
            st.markdown(f"""
            <div class="upload-zone">
                <div style="font-size:3rem;">📸</div>
                <h3 style="color:#4CAF50;">Drop image here</h3>
                <p style="color:{sub_text};">JPG, PNG, WEBP supported</p>
                <p style="color:{sub_text}; font-size:0.8rem;">Use clear, well-lit photos for best results</p>
            </div>
            """, unsafe_allow_html=True)

    with col_result:
        if st.session_state.diagnosis is None:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; padding:50px 20px;">
                <div style="font-size:4rem;">🌱</div>
                <h3 style="color:#4CAF50;">Ready to Diagnose</h3>
                <p style="color:{sub_text};">Upload a plant image to detect diseases instantly using AI</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            r = st.session_state.diagnosis
            card_class = {"healthy": "healthy-card", "diseased": "diseased-card", "warning": "warning-card"}.get(r["status"], "glass-card")
            status_emoji = {"healthy": "✅", "diseased": "🔴", "warning": "⚠️"}.get(r["status"], "🔍")
            status_color = {"healthy": "#4CAF50", "diseased": "#e74c3c", "warning": "#e67e22"}.get(r["status"], "#4CAF50")

            st.markdown(f"""
            <div class="{card_class}">
                <h2 style="color:{status_color}; margin:0;">{status_emoji} {r['disease_name']}</h2>
                <p style="color:{sub_text}; font-style:italic;">{r.get('scientific_name', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            m1.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{status_color};">{r["severity"]}</div><div class="metric-label">Severity</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="metric-card"><div class="metric-value">{r["confidence"]}%</div><div class="metric-label">Confidence</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{status_color};">{r["urgency"]}</div><div class="metric-label">Urgency</div></div>', unsafe_allow_html=True)
            st.progress(r["confidence"] / 100)
            st.divider()

            st.markdown(f"<h4 style='color:#4CAF50;'>Observation</h4><p style='color:{text_color};'>{r['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#4CAF50;'>Treatments</h4>", unsafe_allow_html=True)
            for t in r["treatments"]:
                st.markdown(f'<div class="treatment-step">{t}</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<h4 style='color:#4CAF50;'>Causes</h4>", unsafe_allow_html=True)
                for cause in r["causes"]:
                    st.markdown(f"<p style='color:{text_color};'>• {cause}</p>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<h4 style='color:#4CAF50;'>Prevention</h4>", unsafe_allow_html=True)
                for tip in r["prevention"]:
                    st.markdown(f"<p style='color:{text_color};'>• {tip}</p>", unsafe_allow_html=True)

            if r.get("affected_parts"):
                st.markdown(f"<p style='color:{sub_text};'>Affected: <b style='color:#4CAF50;'>{', '.join(r['affected_parts'])}</b></p>", unsafe_allow_html=True)

# ── TAB 2: CHAT ───────────────────────────────────────────
with tab_chat:
    st.markdown(f"<h3 style='color:#4CAF50;'>Chat About Your Plant</h3>", unsafe_allow_html=True)
    if st.session_state.diagnosis is None:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:30px;"><p style="color:{sub_text};">Run detection first in Detect tab</p></div>', unsafe_allow_html=True)
    else:
        r = st.session_state.diagnosis
        st.markdown(f'<div class="glass-card"><p style="color:{sub_text}; margin:0;">Chatting about: <b style="color:#4CAF50;">{r["disease_name"]}</b> | Confidence: <b style="color:#4CAF50;">{r["confidence"]}%</b></p></div>', unsafe_allow_html=True)
        suggestions = ["How long will treatment take?", "Is this contagious to other plants?", "What organic treatments can I use?", "When should I see improvement?"]
        st.markdown(f"<p style='color:{sub_text}; font-size:0.85rem; margin-top:10px;'>Suggested questions:</p>", unsafe_allow_html=True)
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

# ── TAB 3: HISTORY ────────────────────────────────────────
with tab_history:
    st.markdown(f"<h3 style='color:#4CAF50;'>Scan History</h3>", unsafe_allow_html=True)
    scans = get_all_scans()
    if not scans:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:30px;"><p style="color:{sub_text};">No scans yet!</p></div>', unsafe_allow_html=True)
    else:
        stats = get_scan_stats()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total"]}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e74c3c;">{stats["diseased"]}</div><div class="metric-label">Diseased</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#4CAF50;">{stats["healthy"]}</div><div class="metric-label">Healthy</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="metric-value">{stats["avg_confidence"]}%</div><div class="metric-label">Avg Conf</div></div>', unsafe_allow_html=True)
        st.divider()
        df = pd.DataFrame(scans)[["timestamp","disease_name","status","severity","confidence","urgency"]]
        df.columns = ["Time","Disease","Status","Severity","Confidence %","Urgency"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", data=df.to_csv(index=False).encode(), file_name="plantmd_history.csv", mime="text/csv")

# ── TAB 4: ANALYTICS ──────────────────────────────────────
with tab_analytics:
    st.markdown(f"<h3 style='color:#4CAF50;'>Analytics Dashboard</h3>", unsafe_allow_html=True)
    scans = get_all_scans()
    if len(scans) < 2:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:30px;"><p style="color:{sub_text};">Run at least 2 scans to see analytics.</p></div>', unsafe_allow_html=True)
    else:
        df = pd.DataFrame(scans)
        stats = get_scan_stats()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total"]}</div><div class="metric-label">Total</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e74c3c;">{stats["diseased"]}</div><div class="metric-label">Diseased</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#4CAF50;">{stats["healthy"]}</div><div class="metric-label">Healthy</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="metric-value">{stats["avg_confidence"]}%</div><div class="metric-label">Avg Conf</div></div>', unsafe_allow_html=True)
        st.divider()
        bg = '#0d2137' if st.session_state.dark_mode else '#f0f7f0'
        tc = 'white' if st.session_state.dark_mode else '#1a3a2a'
        plt.style.use('dark_background' if st.session_state.dark_mode else 'default')
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<h4 style='color:#4CAF50;'>Status Distribution</h4>", unsafe_allow_html=True)
            status_counts = df["status"].value_counts()
            colors_map = {"healthy": "#4CAF50", "diseased": "#e74c3c", "warning": "#e67e22"}
            fig, ax = plt.subplots(figsize=(4, 4), facecolor=bg)
            ax.set_facecolor(bg)
            ax.pie(status_counts.values, labels=status_counts.index,
                colors=[colors_map.get(s, "#888") for s in status_counts.index],
                autopct="%1.1f%%", startangle=90, textprops={'color': tc})
            st.pyplot(fig)
            plt.close()
        with c2:
            st.markdown(f"<h4 style='color:#4CAF50;'>Top Diseases</h4>", unsafe_allow_html=True)
            top = df["disease_name"].value_counts().head(6)
            fig2, ax2 = plt.subplots(figsize=(5, 4), facecolor=bg)
            ax2.set_facecolor(bg)
            top.plot(kind="barh", ax=ax2, color="#4CAF50")
            ax2.tick_params(colors=tc)
            ax2.set_xlabel("Count", color=tc)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()
        st.markdown(f"<h4 style='color:#4CAF50;'>Confidence Distribution</h4>", unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(8, 3), facecolor=bg)
        ax3.set_facecolor(bg)
        ax3.hist(df["confidence"].astype(int), bins=10, color="#4CAF50", edgecolor=bg)
        ax3.tick_params(colors=tc)
        ax3.set_xlabel("Confidence %", color=tc)
        ax3.set_ylabel("Count", color=tc)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()
