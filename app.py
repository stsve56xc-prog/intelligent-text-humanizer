
import streamlit as st
import random
import re
import nltk
import numpy as np
from nltk.corpus import wordnet as wn

nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Humanizer",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# LOAD VOCABULARY (Cached)
# ============================================================
@st.cache_data
def load_vocabulary():
    """Load vocabulary from GloVe (if available)"""
    vocab = {}
    try:
        with open('backend/word_data/glove/glove.6B.100d.txt', 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 30000:
                    break
                parts = line.split()
                if len(parts) >= 101:
                    vocab[parts[0]] = True
    except:
        pass
    return vocab

vocab = load_vocabulary()

# ============================================================
# GET SYNONYMS FROM WORDNET
# ============================================================
def get_synonyms(word):
    """Get synonyms from WordNet"""
    syns = []
    try:
        for synset in wn.synsets(word):
            for lemma in synset.lemmas():
                syn = lemma.name().replace('_', ' ')
                if syn != word and syn not in syns:
                    syns.append(syn)
    except:
        pass
    return syns[:10]

# ============================================================
# HUMANIZE FUNCTION
# ============================================================
def humanize_text(text, tone="academic"):
    """Humanize text using WordNet + GloVe"""
    
    # Split into words
    words = text.split()
    humanized = []
    
    for word in words:
        clean = re.sub(r'[^\w\s]', '', word).lower()
        new_word = word
        
        # Only replace meaningful words
        if len(clean) > 3 and clean in vocab:
            syns = get_synonyms(clean)
            if syns and random.random() < 0.4:
                new = random.choice(syns)
                if word[0].isupper():
                    new = new.capitalize()
                if word[-1] in '.!?,;:':
                    new += word[-1]
                new_word = new
        
        humanized.append(new_word)
    
    return " ".join(humanized)

# ============================================================
# UI
# ============================================================
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #58a6ff; text-align: center; }
    .result-box { background: #0d1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🤖 AI Humanizer</p>', unsafe_allow_html=True)
st.markdown("### ✨ Humanize AI text using WordNet + GloVe (400,000 words)")

# Input
text = st.text_area("📝 Paste your text:", height=200)

# Tone selection
tone = st.selectbox("🎨 Tone", ["academic", "natural", "blog", "professional"])

if st.button("✨ Humanize", type="primary"):
    if text and len(text.strip()) > 10:
        with st.spinner("🔄 Humanizing..."):
            result = humanize_text(text, tone)
            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
            
            # Stats
            st.caption(f"📊 Original: {len(text.split())} words | Humanized: {len(result.split())} words")
            st.balloons()
    else:
        st.error("⚠️ Please enter at least 10 characters.")

st.caption("🤖 Powered by WordNet (155,000 words) + GloVe (400,000 words)")
