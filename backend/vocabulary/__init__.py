"""
Vocabulary Database for Local Text Humanizer
Contains static mappings for rule-based text naturalization.
"""

# 1. AI-heavy signifiers and boilerplate structural clichés to replace
ROBOTIC_PHRASES = {
    "delve into": "explore",
    "it is important to note that": "notably",
    "furthermore": "also",
    "moreover": "in addition",
    "in conclusion": "overall",
    "testament to": "proof of",
    "not only but also": "and",
    "consequently": "so",
    "utilized": "used",
    "pivotal role": "key part",
    "beacon of": "sign of",
    "tapestry": "structure",
}

# 2. Comprehensive synonym mapping layer for phrase diversification
SYNONYMS = {
    "identify": ["detect", "recognize", "find", "discern", "pinpoint"],
    "analyze": ["examine", "study", "look into", "evaluate", "inspect"],
    "observe": ["see", "track", "watch", "notice", "monitor"],
    "execute": ["run", "carry out", "perform", "do", "implement"],
    "obtain": ["get", "gather", "collect", "acquire", "secure"],
    "demonstrate": ["show", "prove", "display", "indicate", "reveal"],
    "concerning": ["about", "regarding", "on", "dealing with"],
    "subsequent": ["next", "following", "later", "succeeding"],
}

# 3. Conversational and structural transition bridges
TRANSITIONS = [
    "on the other hand",
    "to put it simply",
    "that said",
    "at the same time",
    "moving forward",
]

# 4. Intensity parameters and structural rules matching the user profiles
TONE_SETTINGS = {
    "academic": {
        "preservation_strength": 0.9,
        "cliche_removal": True,
        "sentence_variation": True,
    },
    "natural": {
        "preservation_strength": 0.5,
        "cliche_removal": True,
        "sentence_variation": True,
    },
    "conversational": {
        "preservation_strength": 0.2,
        "cliche_removal": True,
        "sentence_variation": True,
    }
}

# 5. Core scientific domains and technical namespaces to protect from raw truncation
DOMAIN_TERMS = {
    "biotechnology", "phylogenetic", "rRNA", "sequencing", "alignment",
    "toroidal", "vortex", "lattice", "geometry", "substrate", "photon",
    "hypersurface", "cross-section", "derivation", "chromatography"
}

__all__ = [
    "ROBOTIC_PHRASES",
    "SYNONYMS",
    "TRANSITIONS",
    "TONE_SETTINGS",
    "DOMAIN_TERMS",
]
