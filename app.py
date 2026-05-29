import streamlit as st
import tempfile
import os
from utils.agent_orchestrator import run_pipeline

# ── PAGE CONFIG ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veritas ESG",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a5c38;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .verdict-high { color: #d32f2f; font-weight: 600; }
    .verdict-medium { color: #f57c00; font-weight: 600; }
    .verdict-low { color: #388e3c; font-weight: 600; }
    .stProgress > div > div {
        background-color: #1a5c38;
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Veritas ESG")
    st.markdown("*Truth in Sustainability*")
    st.divider()

    st.markdown("### How it works")
    st.markdown("""
    **Layer 1 — Document Intelligence**
    - 🧠 Brain 1: PDF Ingestion
    - 🧠 Brain 2: Claim Extraction

    **Layer 2 — Agentic Verification**
    - 🧠 Brain 3: Strategy Planning
    - 🧠 Brain 4: Evidence Retrieval
    - 🧠 Brain 5: Verdict Judgment
    """)

    st.divider()

    st.markdown("### Verdict Guide")
    st.markdown("""
    ✅ **Verified** — Evidence supports claim

    ⚠️ **Unverified** — Insufficient evidence

    🚨 **Contradicted** — Evidence conflicts
    """)

    st.divider()

    st.markdown("### Tech Stack")
    st.markdown("""
    - Groq (Llama 3.3 70B)
    - LangChain ReAct
    - Tavily Search
    - PyMuPDF
    """)

    st.divider()
    st.caption("Built by Navya Rangwani")
    st.caption("VES Institute of Technology")

# ── MAIN HEADER ──────────────────────────────────────────────────────
st.markdown('<p class="main-header">🌿 Veritas ESG</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Autonomous ESG Greenwashing Detection — powered by Agentic AI</p>', unsafe_allow_html=True)

st.divider()

# ── FILE UPLOAD SECTION ──────────────────────────────────────────────
col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.markdown("### Upload ESG Report")
    uploaded_file = st.file_uploader(
        "Drop a corporate ESG, sustainability, or CSR report here",
        type=["pdf"],
        help="Supports any corporate ESG report in PDF format. Try Infosys, Tata Motors, or Mahindra ESG reports."
    )

with col_info:
    st.markdown("### Where to get ESG reports")
    st.markdown("""
    Search for any of these:
    - *"Infosys ESG report 2024 PDF"*
    - *"Tata Motors sustainability report PDF"*
    - *"Mahindra ESG report PDF"*

    All publicly available on company investor relations pages.
    """)

# ── RUN ANALYSIS ─────────────────────────────────────────────────────
if uploaded_file is not None:
    st.success(f"✅ Uploaded: **{uploaded_file.name}**")
    st.divider()

    if st.button("🚀 Run Greenwashing Analysis", type="primary", use_container_width=True):

        # save uploaded file to temp path
        # Streamlit gives us bytes — we need a real file path for PyMuPDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # ── LIVE PROGRESS LOG ─────────────────────────────────────────
        st.markdown("### 🤖 Agent Activity")
        progress_container = st.container()
        log_box = progress_container.empty()
        progress_messages = []

        def update_progress(msg: str):
            progress_messages.append(msg)
            # show last 6 messages so user sees live updates
            display = "\n".join(progress_messages[-6:])
            log_box.code(display, language=None)

        # ── RUN PIPELINE ──────────────────────────────────────────────
        results = []
        with st.spinner("Veritas ESG agent is running..."):
            try:
                results = run_pipeline(tmp_path, progress_callback=update_progress)
            except Exception as e:
                st.error(f"Pipeline error: {str(e)}")
                st.error("Check your API keys in the .env file and try again.")
            finally:
                # always clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        log_box.empty()  # clear the live log

        # ── RESULTS ──────────────────────────────────────────────────
        if not results:
            st.warning("⚠️ No verifiable ESG claims were found in this document.")
            st.info("This can happen if the report uses mostly qualitative language without specific metrics. Try a different ESG report.")

        else:
            st.divider()
            st.markdown("## 📊 Analysis Results")

            # summary metrics
            total = len(results)
            verified = sum(1 for r in results if r["verdict"] == "Verified")
            contradicted = sum(1 for r in results if r["verdict"] == "Contradicted")
            unverified = sum(1 for r in results if r["verdict"] == "Unverified")
            high_risk = sum(1 for r in results if "High Risk" in r.get("risk_level", ""))

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("📋 Total Claims", total)
            col2.metric("✅ Verified", verified)
            col3.metric("🚨 Contradicted", contradicted)
            col4.metric("⚠️ Unverified", unverified)
            col5.metric("🔴 High Risk", high_risk)

            st.divider()

            # sort: contradicted first, then unverified, then verified
            sorted_results = sorted(
                results,
                key=lambda x: {"Contradicted": 0, "Unverified": 1, "Verified": 2}[x["verdict"]]
            )

            st.markdown("### 🔍 Claim-by-Claim Breakdown")
            st.caption("Contradicted claims appear first. Click any claim to expand.")

            for i, result in enumerate(sorted_results):
                verdict = result["verdict"]
                badge = result["badge"]
                confidence = result["confidence"]
                risk = result.get("risk_level", "")
                claim_preview = result["claim_text"][:80]

                # auto-expand contradicted claims
                expanded = verdict == "Contradicted"

                with st.expander(
                    f"{badge} Claim {i+1}: {claim_preview}{'...' if len(result['claim_text']) > 80 else ''}",
                    expanded=expanded
                ):
                    col_a, col_b = st.columns([3, 2])

                    with col_a:
                        st.markdown("**Full Claim:**")
                        st.info(result["claim_text"])

                        st.markdown("**Agent Reasoning:**")
                        st.markdown(result["reasoning"])

                        if result["sources"]:
                            st.markdown("**Evidence Sources:**")
                            for source in result["sources"]:
                                if source.get("url"):
                                    title = source.get("title") or source.get("url")
                                    st.markdown(f"- [{title}]({source['url']})")

                    with col_b:
                        st.markdown("**Verdict:**")
                        if verdict == "Verified":
                            st.success(f"{badge} {verdict}")
                        elif verdict == "Contradicted":
                            st.error(f"{badge} {verdict}")
                        else:
                            st.warning(f"{badge} {verdict}")

                        st.markdown(f"**Risk Level:** {risk}")
                        st.markdown(f"**Confidence:** {confidence}%")
                        st.progress(confidence / 100)

                        st.divider()

                        st.markdown("**Claim Details:**")
                        st.markdown(f"- **Metric:** {result['metric_type']}")
                        st.markdown(f"- **Value:** {result['value']}")
                        st.markdown(f"- **Year:** {result['year']}")
                        st.markdown(f"- **Found on page:** {result['page']}")

            # footer
            st.divider()
            st.markdown(
                '<p class="footer">Veritas ESG — Autonomous ESG Assurance | '
                'Built with LangChain · Groq · Tavily · Streamlit</p>',
                unsafe_allow_html=True
            )

# ── EMPTY STATE ───────────────────────────────────────────────────────
else:
    st.markdown("### 👆 Upload an ESG report to get started")
    st.markdown("""
    Veritas ESG will automatically:
    1. Extract all measurable sustainability claims from the report
    2. Plan a verification strategy for each claim
    3. Search for independent external evidence
    4. Judge each claim as Verified, Unverified, or Contradicted
    5. Generate a confidence-scored audit report
    """)

    st.info("💡 Tip: Start with the Infosys or Tata Motors ESG report — both are publicly available and work well with this system.")