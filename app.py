import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from database import init_db, save_scan, get_all_scans, get_scan_stats
from detector import detect_disease, chat_about_disease
from pdf_report import generate_pdf

init_db()

st.set_page_config(
    page_title="PlantMD - Thesis Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

for key, default in [("diagnosis", None), ("chat_history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown("## PlantMD")
    st.caption("AI Plant Disease Detection\nMaster's Thesis Project")
    st.divider()
    st.markdown("""
    **How to use:**
    1. Go to Detect tab
    2. Upload a plant photo
    3. Click Analyze
    4. Chat for more details
    5. Download PDF report
    """)
    st.divider()
    st.caption("Powered by Google Gemini Vision | 2025")

tab_detect, tab_chat, tab_history, tab_analytics = st.tabs([
    "Detect", "Chat", "History", "Analytics"
])

with tab_detect:
    st.header("Plant Disease Detection")
    st.caption("Upload a clear, well-lit photo of the affected leaf or plant part.")
    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        uploaded = st.file_uploader(
            "Choose plant image",
            type=["jpg", "jpeg", "png", "webp"],
        )
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption="Uploaded image", use_container_width=True)
            if st.button("Analyze Plant", type="primary", use_container_width=True):
                with st.spinner("Gemini AI is analyzing your plant..."):
                    try:
                        uploaded.seek(0)
                        result = detect_disease(uploaded)
                        st.session_state.diagnosis = result
                        st.session_state.chat_history = []
                        save_scan(result)
                        st.success("Analysis complete!")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
                        st.info("Check your GEMINI_API_KEY in .env and try again.")

    with col_result:
        if st.session_state.diagnosis is None:
            st.info("Results will appear here after analysis.")
            st.markdown("""
            **Tips for best results:**
            - Use natural daylight
            - Focus on the affected area
            - Avoid blurry or dark photos
            """)
        else:
            r = st.session_state.diagnosis
            status_map = {"healthy": "HEALTHY", "warning": "WARNING", "diseased": "DISEASED"}
            st.markdown(f"## {status_map.get(r['status'], 'UNKNOWN')} - {r['disease_name']}")
            if r.get("scientific_name"):
                st.caption(f"*{r['scientific_name']}*")
            m1, m2, m3 = st.columns(3)
            m1.metric("Severity", r["severity"])
            m2.metric("Confidence", f"{r['confidence']}%")
            m3.metric("Urgency", r["urgency"])
            st.progress(r["confidence"] / 100)
            st.divider()
            st.markdown("**Observation**")
            st.write(r["description"])
            st.markdown("**Treatments**")
            for t in r["treatments"]:
                st.success(t)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Causes**")
                for cause in r["causes"]:
                    st.markdown(f"- {cause}")
            with c2:
                st.markdown("**Prevention**")
                for tip in r["prevention"]:
                    st.markdown(f"- {tip}")
            if r.get("affected_parts"):
                st.markdown("**Affected parts:** " + ", ".join(r["affected_parts"]))
            st.divider()
            pdf_bytes = generate_pdf(r)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"plantmd_{r['disease_name'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.caption("Switch to Chat tab to ask follow-up questions.")

with tab_chat:
    st.header("Chat About Your Plant")
    if st.session_state.diagnosis is None:
        st.warning("Run a detection first in the Detect tab.")
    else:
        r = st.session_state.diagnosis
        st.info(f"Chatting about: **{r['disease_name']}** | Severity: {r['severity']} | Confidence: {r['confidence']}%")
        st.markdown("**Suggested questions:**")
        suggestions = [
            "How long will treatment take?",
            "Is this disease contagious to other plants?",
            "What organic treatments can I use?",
            "When should I see improvement?",
        ]
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            if cols[i % 2].button(suggestion, key=f"sug_{i}"):
                st.session_state["_auto_q"] = suggestion
        st.divider()
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        auto_q = st.session_state.pop("_auto_q", None)
        if question := (st.chat_input("Ask anything about the disease or treatment...") or auto_q):
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = chat_about_disease(
                        question,
                        st.session_state.diagnosis,
                        st.session_state.chat_history[:-1],
                    )
                st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
        if st.session_state.chat_history:
            if st.button("Clear chat"):
                st.session_state.chat_history = []
                st.rerun()

with tab_history:
    st.header("Scan History")
    st.caption("All past scans stored locally.")
    scans = get_all_scans()
    if not scans:
        st.info("No scans yet. Run your first detection in the Detect tab.")
    else:
        stats = get_scan_stats()
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Scans", stats["total"])
        s2.metric("Diseased", stats["diseased"])
        s3.metric("Healthy", stats["healthy"])
        s4.metric("Avg Confidence", f"{stats['avg_confidence']}%")
        st.divider()
        df = pd.DataFrame(scans)[["timestamp", "disease_name", "status", "severity", "confidence", "urgency"]]
        df.columns = ["Time", "Disease", "Status", "Severity", "Confidence %", "Urgency"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode()
        st.download_button("Download as CSV", data=csv, file_name="plantmd_scan_history.csv", mime="text/csv")

with tab_analytics:
    st.header("Analytics")
    st.caption("Visualizations for your thesis results chapter.")
    scans = get_all_scans()
    if len(scans) < 2:
        st.info("Run at least 2 scans to see analytics.")
    else:
        df = pd.DataFrame(scans)
        stats = get_scan_stats()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Scans", stats["total"])
        m2.metric("Diseased", stats["diseased"])
        m3.metric("Healthy", stats["healthy"])
        m4.metric("Avg Confidence", f"{stats['avg_confidence']}%")
        st.divider()
        chart1, chart2 = st.columns(2)
        with chart1:
            st.markdown("**Detection Status Distribution**")
            status_counts = df["status"].value_counts()
            colors = {"healthy": "#2d6a4f", "diseased": "#c0392b", "warning": "#e67e22"}
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(
                status_counts.values,
                labels=status_counts.index,
                colors=[colors.get(s, "#888") for s in status_counts.index],
                autopct="%1.1f%%",
                startangle=90,
            )
            ax.set_title("Status Distribution")
            st.pyplot(fig)
            plt.close()
        with chart2:
            st.markdown("**Top Detected Diseases**")
            top_diseases = df["disease_name"].value_counts().head(8)
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            top_diseases.plot(kind="barh", ax=ax2, color="#2d6a4f")
            ax2.set_xlabel("Count")
            ax2.set_title("Most Frequent Diseases")
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()
        st.divider()
        st.markdown("**Confidence Score Distribution**")
        fig3, ax3 = plt.subplots(figsize=(8, 3))
        ax3.hist(df["confidence"].astype(int), bins=10, color="#2d6a4f", edgecolor="white")
        ax3.set_xlabel("Confidence %")
        ax3.set_ylabel("Count")
        ax3.set_title("Model Confidence Distribution Across All Scans")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()