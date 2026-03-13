import os

# Anthropic API (used via direct fetch in app)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Vector DB
VECTOR_DB_PATH = "data/vector_db"

# TTS
TTS_LANG = "en"

# Video
SLIDE_DURATION = 6  # seconds per slide
VIDEO_FPS = 24
VIDEO_SIZE = (1280, 720)
