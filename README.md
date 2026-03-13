# AI Visual Math Tutor 📐

An AI-powered math tutoring app with visual explanations, graphs, and lesson video generation.

https://github.com/user-attachments/assets/b60cbc6d-34e8-4b89-8877-27d4fa1637d7

## Features

- 🤖 **AI explanations** powered by Claude (Anthropic)
- 📚 **RAG from your textbooks** — upload any math/stats PDF
- 🌐 **Web search fallback** via DuckDuckGo
- 📊 **Auto-generated graphs** for vectors, matrices, regression, distributions, calculus, trig, and more
- 📑 **Lesson slide generator** — structured 5-slide mini lessons
- 🎙️ **AI narration** via gTTS
- 🎬 **Downloadable lesson video** (slides + voice)

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key (or enter it in the sidebar)
export ANTHROPIC_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here

# 3. Run the app
cd math_tutor
streamlit run app.py
```

## Project Structure

```
math_tutor/
├── app.py                    # Main Streamlit UI
├── requirements.txt
├── config/
│   └── config.py             # Settings (model, chunk size, etc.)
├── models/
│   ├── llm.py                # Anthropic API wrapper + prompts
│   └── embeddings.py         # sentence-transformers embeddings
├── utils/
│   ├── rag_pipeline.py       # PDF loading, chunking, FAISS index
│   ├── web_search.py         # DuckDuckGo search
│   ├── visualizer.py         # matplotlib graph generators
│   ├── lesson_builder.py     # Parse LLM output into slides
│   ├── tts.py                # gTTS text-to-speech
│   └── video_generator.py    # moviepy slide+audio video export
└── data/
    ├── textbooks/            # Store uploaded PDFs here
    └── vector_db/            # FAISS indexes saved here
```

## Supported Visualization Types

| Topic | Graph Type |
|-------|-----------|
| Vectors | Arrow/quiver plot |
| Matrices | Shape transformation (before/after) |
| Linear Regression | Scatter + regression line + residuals |
| Distributions | Normal distribution curves |
| Calculus | Function + tangent line (derivative) |
| Trigonometry | sin/cos/tan curves |
| Quadratic | Parabola families |
| Linear equations | Line families (y=mx+b) |

## How It Works

1. User types a math question
2. System checks for uploaded textbook (RAG) — falls back to web search
3. Context fed to Claude for explanation
4. Topic detected → matching graph auto-generated
5. "Generate Lesson Video" → Claude structures 5 slides → gTTS narrates → moviepy exports MP4

## Notes

- Video generation requires `moviepy` and `gtts` — install separately if needed
- RAG requires `faiss-cpu` and `sentence-transformers`
- The app works without a textbook — web search handles general queries
