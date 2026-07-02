🤖 AI Humanizer
Humanize AI-generated text with advanced NLP and intelligent rewriting

Badges
Python 3.10+ | FastAPI 0.115.0 | MIT License | PRs Welcome

📋 Table of Contents
- Features
- Quick Start
- Installation
- Configuration
- API Usage
- Project Structure
- Docker Deployment
- Testing
- Contributing
- License

✨ Features
✅ Smart Text Humanization - Advanced NLP-based rewriting
✅ Multiple Tones - Academic, Natural, Blog, Professional, Conversational
✅ 3 Style Levels - Conservative, Balanced, Creative
✅ Technical Term Preservation - Keeps scientific/technical terms intact
✅ Batch Processing - Humanize multiple texts at once
✅ Text Analysis - Get metrics and readability scores
✅ Tone Comparison - Compare different tones side by side
✅ 100% Free - Local humanization (no API key needed)
✅ API Fallback - Uses RewriteAI/Gemini/Groq if available
✅ Fast & Lightweight - Optimized for performance
✅ Docker Support - Easy deployment with Docker

🚀 Quick Start
1. Clone Repository
git clone https://github.com/your-username/intelligent-text-humanizer.git
cd intelligent-text-humanizer

2. Install Dependencies
pip install -r requirements.txt

3. Setup Environment
cp .env.example .env

4. Download NLP Models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"

5. Run the API
python -m backend.main

6. Open Browser
http://localhost:8000/docs

📦 Installation
Prerequisites
- Python 3.9+
- pip (Python package manager)

Virtual Environment (Recommended)
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate

Install Dependencies
pip install -r requirements.txt

Download NLP Models
# SpaCy model
python -m spacy download en_core_web_sm

# NLTK data
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"

⚙️ Configuration
Environment Variables
Create .env file from .env.example:

# Required
REWRITE_API_KEY=your_rewriteai_key_here

# Optional
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here

API Settings
Variable                Default     Description
API_TIMEOUT             30          Request timeout (seconds)
MAX_TEXT_LENGTH         5000        Max text length
RATE_LIMIT_REQUESTS     60          Requests per minute
DEFAULT_TONE            academic    Default tone
DEBUG                   true        Debug mode

🔌 API Usage
Humanize Text
Endpoint: POST /api/humanize

Request:
{
    "text": "Microscopic identification was carried out...",
    "tone": "academic",
    "style": "balanced",
    "preserve_technical": true
}

Response:
{
    "original_text": "Microscopic identification was carried out...",
    "humanized_text": "Microscopic identification was performed...",
    "tone": "academic",
    "style": "balanced",
    "word_count": 45,
    "processing_time": 0.234,
    "method_used": "local",
    "timestamp": "2026-07-02T09:08:15.123456"
}

Batch Humanization
Endpoint: POST /api/humanize/batch

Request:
{
    "texts": ["Text 1", "Text 2", "Text 3"],
    "tone": "academic",
    "style": "balanced",
    "preserve_technical": true
}

Analyze Text
Endpoint: POST /api/analyze

Request:
{
    "text": "Microscopic identification was carried out..."
}

Response:
{
    "sentence_count": 5,
    "word_count": 120,
    "char_count": 600,
    "avg_word_length": 5.0,
    "readability_score": 45.2,
    "difficulty_level": "Hard",
    "vocabulary_richness": 0.65,
    "technical_terms": ["mycelium", "hyphae", "conidiophore"]
}

Compare Tones
Endpoint: POST /api/compare

Request:
{
    "text": "Microscopic identification was carried out...",
    "tones": ["academic", "natural", "conversational"],
    "style": "balanced",
    "preserve_technical": true
}

🎯 Available Tones
Tone            Style           Best For
Academic        Formal          Research papers, essays
Natural         Balanced        General writing
Blog            Casual          Blog posts, articles
Professional    Formal          Business, reports
Conversational  Very Casual     Chat, social media

📁 Project Structure
intelligent-text-humanizer/
│
├── .env                          # Environment variables (API keys)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker compose configuration
│
├── backend/                      # Backend code
│   ├── __init__.py               # Package init
│   ├── config.py                 # Configuration
│   ├── models.py                 # Data models
│   ├── main.py                   # FastAPI app
│   │
│   ├── routes/                   # API routes
│   │   ├── __init__.py
│   │   └── humanize.py           # Humanization endpoints
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── humanizer.py          # Main orchestrator
│   │   ├── humanize.py           # Core with cache
│   │   ├── local_humanizer.py    # Local only
│   │   └── api_humanizer.py      # API calls
│   │
│   └── vocabulary/               # Word data
│       ├── __init__.py
│       ├── robotic_phrases.py    # AI phrases to replace
│       ├── synonyms.py           # Synonym database
│       ├── transitions.py        # Transition words
│       ├── tone_settings.py      # Tone configurations
│       └── domain_terms.py       # Technical terms
│
├── frontend/                     # Web interface
│   └── index.html                # Frontend HTML
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_humanizer.py
│   └── test_api.py
│
├── scripts/                      # Helper scripts
│   ├── download_word_data.py     # Download word embeddings
│   └── setup.sh                  # Setup script
│
├── logs/                         # Application logs
└── uploads/                      # Uploaded files

🐳 Docker Deployment
Build and Run
# Build the image
docker build -t ai-humanizer .

# Run the container
docker run -d --name ai-humanizer -p 8000:8000 --env-file .env ai-humanizer

Docker Compose
# Start all services
docker-compose up -d

# Build and start
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart humanizer-api

🧪 Testing
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=backend

# Run specific test
pytest tests/test_humanizer.py -v

📊 API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

🤝 Contributing
1. Fork the repository
2. Create your feature branch (git checkout -b feature/amazing)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to branch (git push origin feature/amazing)
5. Open a Pull Request

Development Setup
# Clone repository
git clone https://github.com/your-username/intelligent-text-humanizer.git
cd intelligent-text-humanizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 mypy isort pre-commit

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

📝 License
This project is licensed under the MIT License.

🙏 Acknowledgments
- FastAPI - Modern web framework
- RewriteAI - AI humanization API
- Google Gemini - AI model
- Groq - AI inference
- spaCy - NLP library
- NLTK - Natural Language Toolkit

📞 Contact
- GitHub: your-username
- Email: your-email@example.com

⭐ Show Your Support
If you like this project, please consider giving it a ⭐ on GitHub!

Made with Zariab Ahmed 
