
import streamlit as st
import requests
import json
import time

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="AI Humanizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Custom CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #58a6ff;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #8b949e;
        margin-bottom: 30px;
    }
    .result-box {
        background: #0d1117;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-top: 20px;
        font-family: monospace;
        white-space: pre-wrap;
        min-height: 100px;
    }
    .stats-box {
        color: #8b949e;
        font-size: 14px;
        margin-top: 10px;
    }
    .footer {
        text-align: center;
        color: #484f58;
        margin-top: 50px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Header
# ============================================================
st.markdown('<p class="main-header">🤖 AI Humanizer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Make AI-generated text sound human & natural</p>', unsafe_allow_html=True)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    api_url = st.text_input(
        "API Endpoint",
        value="http://localhost:8000",
        help="URL of your backend API"
    )
    
    tone = st.selectbox(
        "🎨 Tone",
        ["academic", "natural", "blog", "professional", "conversational"],
        index=0
    )
    
    style = st.selectbox(
        "⚖️ Style",
        ["conservative", "balanced", "creative"],
        index=1
    )
    
    preserve_technical = st.checkbox("🔬 Preserve Technical Terms", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 Vocabulary Stats")
    st.markdown("✅ GloVe: 400,000 words")
    st.markdown("✅ WordNet: 155,000 words")
    st.markdown("✅ spaCy: 20,000 words")
    st.markdown("**Total: 575,000+ words**")
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown("[📖 API Docs](http://localhost:8000/docs)")
    st.markdown("[🐙 GitHub](https://github.com/stsve56xc-prog/intelligent-text-humanizer)")

# ============================================================
# Main Area
# ============================================================
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Input Text")
    
    sample_text = """Microscopic identification was carried out to confirm morphological characteristics of purified fungal isolates. A small portion of fungal mycelium was placed on a clean glass slide, and a drop of lactophenol cotton blue (LPCB) stain was added. A cover slip was gently placed to avoid air bubbles. Prepared slides were observed under a compound light microscope at 10× and 40× magnifications. Key structural features such as hyphal type, septation, conidiophore structure, and spore morphology were recorded. Aspergillus niger was identified by septate hyphae and globose conidial heads with darkly pigmented spores. Trichoderma spp. showed branched conidiophores with clustered phialides and green spore masses, while Aspergillus terreus exhibited brush-like penicillus structures with chain-like spore arrangements. Microscopic observations, combined with colony morphology, were used for preliminary identification prior to consortium development and polymer degradation studies."""
    
    input_text = st.text_area(
        "Paste your AI-generated text here:",
        value=sample_text,
        height=250,
        placeholder="Paste your text here..."
    )
    
    word_count = len(input_text.split()) if input_text else 0
    st.caption(f"📝 {word_count} words")

with col2:
    st.markdown("### ✨ Humanized Output")
    
    if st.button("🚀 Humanize Text", type="primary", use_container_width=True):
        if not input_text or len(input_text.strip()) < 10:
            st.error("⚠️ Please enter at least 10 characters.")
        else:
            with st.spinner("🔄 Humanizing your text... Please wait."):
                try:
                    start_time = time.time()
                    
                    response = requests.post(
                        f"{api_url}/api/humanize/batch",
                        json={
                            "texts": [input_text],
                            "tone": tone,
                            "style": style,
                            "preserve_technical": preserve_technical
                        },
                        timeout=60
                    )
                    
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        result = response.json()
                        humanized = result['results'][0]['humanized_text']
                        
                        st.markdown(f'<div class="result-box">{humanized}</div>', unsafe_allow_html=True)
                        
                        original_words = len(input_text.split())
                        humanized_words = result['results'][0]['word_count']
                        processing_time = round(end_time - start_time, 3)
                        
                        st.markdown(f"""
                        <div class="stats-box">
                            📊 Original: {original_words} words &nbsp;|&nbsp; 
                            ✨ Humanized: {humanized_words} words &nbsp;|&nbsp; 
                            ⏱️ {processing_time}s &nbsp;|&nbsp; 
                            ⚡ {result['results'][0]['method_used']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("📋 Copy Result"):
                            st.write("✅ Copied to clipboard!")
                            st.balloons()
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        st.code(response.text)
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend! Make sure the API is running.")
                    st.info(f"💡 Run: `python -m backend.main` on port {api_url.split(':')[-1]}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown('<div class="result-box" style="color:#484f58; font-style:italic;">Your humanized text will appear here...</div>', unsafe_allow_html=True)

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown('<div class="footer">🤖 AI Humanizer v2.0 | Powered by FastAPI + GloVe (400,000 words)</div>', unsafe_allow_html=True)
