import streamlit as st
import os, sys, re, base64, tempfile

sys.path.insert(0, os.path.dirname(__file__))

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Visual Math Tutor",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #0d1117;
    color: #e6edf3;
}
.stApp { background: #0d1117; }

/* Sidebar */
[data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #21262d; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #8b949e !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e6edf3 !important; }

/* Input */
.stTextInput input {
    background: #161b22 !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 8px !important;
    font-size: 15px !important; padding: 12px 16px !important;
}
.stTextInput input:focus { border-color: #58a6ff !important; box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important; }

/* Buttons */
.stButton > button {
    background: #238636; color: #fff !important; border: 1px solid #2ea043;
    border-radius: 6px; font-weight: 600; font-size: 13px;
    padding: 8px 18px; transition: all .15s;
}
.stButton > button:hover { background: #2ea043; }
.stButton > button[kind="secondary"] {
    background: transparent; color: #58a6ff !important;
    border: 1px solid #30363d;
}

/* Section cards */
.section-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 20px 24px; margin: 12px 0;
}
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 10px; font-weight: 600;
}
.what-header  { color: #58a6ff; }
.intuition-header { color: #3fb950; }
.steps-header { color: #d2a8ff; }
.formula-header { color: #ffa657; }
.practice-header { color: #79c0ff; }

.section-body { font-size: 15px; line-height: 1.75; color: #c9d1d9; }

/* Step rows */
.step-row {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 10px 0; border-bottom: 1px solid #21262d;
}
.step-row:last-child { border-bottom: none; }
.step-num {
    background: #d2a8ff22; color: #d2a8ff;
    border: 1px solid #d2a8ff44;
    border-radius: 50%; width: 28px; height: 28px; min-width: 28px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; font-family: 'IBM Plex Mono', monospace;
}
.step-text { font-size: 14px; line-height: 1.65; color: #c9d1d9; padding-top: 3px; }

/* Formula box */
.formula-box {
    background: #1c2128; border: 1px solid #ffa65733;
    border-left: 3px solid #ffa657; border-radius: 6px;
    padding: 14px 18px; font-family: 'IBM Plex Mono', monospace;
    font-size: 15px; color: #ffa657; letter-spacing: .5px;
}

/* Practice box */
.practice-box {
    background: #1c2128; border: 1px solid #79c0ff33;
    border-radius: 8px; padding: 18px 20px;
}
.practice-problem { font-size: 15px; color: #e6edf3; font-weight: 500; margin-bottom: 10px; }
.practice-hint {
    font-size: 13px; color: #8b949e;
    background: #0d1117; border-radius: 6px; padding: 10px 14px; margin-top: 8px;
}

/* Visual hint */
.visual-hint {
    font-size: 13px; color: #8b949e; font-style: italic;
    border-left: 2px solid #30363d; padding-left: 12px; margin-top: 8px;
}

/* Chat history */
.msg-user {
    background: #1c2128; border-left: 3px solid #58a6ff;
    border-radius: 8px; padding: 12px 16px; margin: 8px 0;
    font-size: 15px; color: #e6edf3;
}
.msg-meta {
    font-size: 11px; color: #8b949e;
    font-family: 'IBM Plex Mono', monospace; margin-bottom: 6px;
}

/* Graph section */
.graph-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #3fb950; margin-bottom: 10px; font-weight: 600;
}

/* Quick example chips */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }

/* Source badge */
.source-badge {
    display: inline-block; font-size: 11px; padding: 3px 10px;
    border-radius: 20px; margin-bottom: 14px; font-weight: 500;
}
.source-rag { background: #238636; color: #fff; }
.source-web { background: #1f6feb; color: #fff; }

/* Divider */
hr { border-color: #21262d !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def parse_section(text, tag):
    match = re.search(rf'\[{tag}\](.*?)\[/{tag}\]', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def parse_steps(steps_raw):
    lines = [l.strip() for l in steps_raw.split('\n') if l.strip()]
    steps = []
    buf = []
    for line in lines:
        m = re.match(r'^Step\s*(\d+)[:\.]?\s*(.*)', line, re.IGNORECASE)
        if m:
            if buf:
                steps[-1]['text'] += ' ' + ' '.join(buf)
                buf = []
            steps.append({'num': m.group(1), 'text': m.group(2)})
        elif steps:
            buf.append(line)
    if buf and steps:
        steps[-1]['text'] += ' ' + ' '.join(buf)
    if not steps:
        # fallback: split by newlines
        for i, line in enumerate(lines, 1):
            steps.append({'num': str(i), 'text': line})
    return steps

def render_explanation(explanation_text, img_b64, img_title, source):
    what     = parse_section(explanation_text, "WHAT_IT_IS")
    intuition= parse_section(explanation_text, "INTUITION")
    steps_raw= parse_section(explanation_text, "STEP_BY_STEP")
    formula  = parse_section(explanation_text, "KEY_FORMULA")
    vis_hint = parse_section(explanation_text, "VISUAL_HINT")
    practice = parse_section(explanation_text, "PRACTICE_PROBLEM")

    # Source badge
    if source == "rag":
        st.markdown('<span class="source-badge source-rag">📚 From your textbook</span>', unsafe_allow_html=True)
    elif source == "web":
        st.markdown('<span class="source-badge source-web">🌐 Web search</span>', unsafe_allow_html=True)

    # Two columns: explanation left, graph right
    col_exp, col_graph = st.columns([3, 2], gap="large")

    with col_exp:
        # What it is
        if what:
            st.markdown(f"""
<div class="section-card">
  <div class="section-header what-header">📌 What it is</div>
  <div class="section-body">{what}</div>
</div>""", unsafe_allow_html=True)

        # Intuition
        if intuition:
            st.markdown(f"""
<div class="section-card">
  <div class="section-header intuition-header">💡 The Intuition</div>
  <div class="section-body">{intuition}</div>
</div>""", unsafe_allow_html=True)

        # Step by step
        if steps_raw:
            steps = parse_steps(steps_raw)
            steps_html = "".join(
                f'<div class="step-row"><div class="step-num">{s["num"]}</div><div class="step-text">{s["text"]}</div></div>'
                for s in steps
            )
            st.markdown(f"""
<div class="section-card">
  <div class="section-header steps-header">🔢 Step-by-Step</div>
  {steps_html}
</div>""", unsafe_allow_html=True)

        # Formula
        if formula:
            st.markdown(f"""
<div class="section-card">
  <div class="section-header formula-header">📐 Key Formula</div>
  <div class="formula-box">{formula}</div>
</div>""", unsafe_allow_html=True)

        # Practice
        if practice:
            prob_match = re.search(r'Problem:\s*(.+?)(?:Hint:|$)', practice, re.DOTALL)
            hint_match = re.search(r'Hint:\s*(.+)', practice, re.DOTALL)
            prob = prob_match.group(1).strip() if prob_match else practice
            hint = hint_match.group(1).strip() if hint_match else ""
            hint_html = f'<div class="practice-hint">💬 Hint: {hint}</div>' if hint else ""
            st.markdown(f"""
<div class="section-card">
  <div class="section-header practice-header">✏️ Try It Yourself</div>
  <div class="practice-box">
    <div class="practice-problem">{prob}</div>
    {hint_html}
  </div>
</div>""", unsafe_allow_html=True)

    with col_graph:
        if img_b64:
            st.markdown(f'<div class="graph-label">📊 {img_title}</div>', unsafe_allow_html=True)
            st.image(base64.b64decode(img_b64), use_container_width=True)
            if vis_hint:
                st.markdown(f'<div class="visual-hint">{vis_hint}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="section-card" style="text-align:center; padding: 40px 20px; color: #8b949e;">
  <div style="font-size: 32px; margin-bottom: 10px;">📐</div>
  <div style="font-size: 13px;">No graph available for this topic yet</div>
</div>""", unsafe_allow_html=True)


# ─── Session state ─────────────────────────────────────────────────────────────
VALID_PROVIDERS = list(__import__("models.llm", fromlist=["PROVIDERS"]).PROVIDERS.keys())

DEFAULTS = {
    "history": [],
    "rag_index": None,
    "rag_chunks": [],
    "doc_name": None,
    "last_explanation": "",
    "last_query": "",
    "provider": "Ollama (Local)",
    "model": "qwen2.5:7b",
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Force-reset stale provider name if it no longer exists in PROVIDERS
if st.session_state.provider not in VALID_PROVIDERS:
    st.session_state.provider = "Ollama (Local)"
    st.session_state.model = "qwen2.5:7b"

# ─── Sidebar ───────────────────────────────────────────────────────────────────
from models.llm import PROVIDERS

with st.sidebar:
    st.markdown("## 📐 Math Tutor")
    st.markdown("---")

    # Provider selection
    st.markdown("**🤖 AI Provider**")
    provider_keys = list(PROVIDERS.keys())
    saved = st.session_state.provider
    default_idx = provider_keys.index(saved) if saved in provider_keys else 0
    provider = st.selectbox("AI Provider", provider_keys, index=default_idx, label_visibility="collapsed")
    st.session_state.provider = provider
    pinfo = PROVIDERS[provider]

    # Status note
    badge = pinfo.get("badge", "green")
    note  = pinfo.get("note", "")
    if badge == "green":
        st.success(note)
    elif badge == "warning":
        st.warning(note)
    else:
        st.error(note)

    # Model selection
    model_list = pinfo["models"]
    model = st.selectbox("Model", model_list, label_visibility="collapsed")
    st.session_state.model = model

    # Ollama-specific UI
    if provider == "Ollama (Local)":
        import requests as _req
        ollama_url = st.text_input("Ollama URL", value=os.getenv("OLLAMA_URL", "http://localhost:11434"))
        os.environ["OLLAMA_URL"] = ollama_url

        # Check connection and model status
        try:
            r = _req.get(ollama_url + "/api/tags", timeout=2)
            running_models = [m["name"] for m in r.json().get("models", [])]
            model_ready = any(model.split(":")[0] in m for m in running_models)
            if model_ready:
                st.success(f"✓ Ollama running · {model} ready")
            else:
                st.warning(f"⚠️ {model} not pulled yet. Run:")
                st.code(f"ollama pull {model}", language="bash")
        except Exception:
            st.error("❌ Ollama not running")
            st.markdown(f"**Quick setup:**")
            st.markdown(f"1. [Download Ollama]({pinfo['get_key_url']})")
            st.code(f"ollama serve", language="bash")
            st.code(f"ollama pull {model}", language="bash")
    else:
        # API key input
        env_var = pinfo["env"]
        placeholder_map = {
            "ANTHROPIC_API_KEY": "sk-ant-...",
            "OPENAI_API_KEY": "sk-...",
            "GEMINI_API_KEY": "AIza...",
        }
        key_url = pinfo.get("get_key_url", "")
        if key_url:
            st.markdown(f"[🔑 Get API key →]({key_url})")
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.getenv(env_var, ""),
            placeholder=placeholder_map.get(env_var, "paste key here"),
        )
        if api_key:
            os.environ[env_var] = api_key
        if os.getenv(env_var):
            st.success("✓ Key is set")
        else:
            st.caption("Paste your key above to get started")

    st.markdown("---")
    st.markdown("**Response depth**")
    mode = st.radio("Response depth", ["Concise", "Detailed"], horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Upload Textbook (optional)**")
    uploaded_pdf = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
    if uploaded_pdf and uploaded_pdf.name != st.session_state.doc_name:
        with st.spinner("Indexing..."):
            try:
                from utils.rag_pipeline import process_uploaded_pdf
                idx, chunks = process_uploaded_pdf(uploaded_pdf, uploaded_pdf.name)
                st.session_state.rag_index = idx
                st.session_state.rag_chunks = chunks
                st.session_state.doc_name = uploaded_pdf.name
                st.success(f"✓ {len(chunks)} chunks indexed")
            except Exception as e:
                st.warning(f"RAG unavailable: {e}")

    if st.session_state.doc_name:
        st.caption(f"📚 {st.session_state.doc_name}")

    st.markdown("---")
    st.markdown("**Generate Lesson**")
    gen_video = st.button("🎬 Build Lesson Video", use_container_width=True,
                           disabled=not st.session_state.last_explanation)
    if not st.session_state.last_explanation:
        st.caption("Ask a question first.")

    if st.session_state.history:
        st.markdown("---")
        if st.button("🗑 Clear chat", use_container_width=True):
            st.session_state.history = []
            st.session_state.last_explanation = ""
            st.session_state.last_query = ""
            st.rerun()

# ─── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# AI Visual Math Tutor")
st.markdown("*Step-by-step explanations · Visual graphs · Lesson videos*")
st.markdown("---")

# Chat history (collapsed, just questions)
if st.session_state.history:
    with st.expander(f"💬 Conversation history ({len(st.session_state.history)} messages)", expanded=False):
        for msg in st.session_state.history:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-user"><span class="msg-meta">YOU</span>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-user" style="border-left-color:#3fb950"><span class="msg-meta">TUTOR</span>{msg["content"][:200]}...</div>', unsafe_allow_html=True)

# ─── Input ─────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([6, 1])
with col_in:
    user_input = st.text_input(
        "Your question", placeholder="Ask any math question — e.g. Explain eigenvectors, How does linear regression work?",
        label_visibility="collapsed", key="user_input"
    )
with col_btn:
    ask_btn = st.button("Ask →", use_container_width=True)

# Quick examples
st.markdown("**Quick examples:**")
ex_cols = st.columns(5)
examples = [
    "Explain eigenvectors",
    "What is linear regression?",
    "How do derivatives work?",
    "Explain normal distribution",
    "What is matrix multiplication?",
]
example_query = None
for col, ex in zip(ex_cols, examples):
    with col:
        if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
            example_query = ex

# ─── Process query ──────────────────────────────────────────────────────────────
query = example_query or (user_input if ask_btn and user_input.strip() else None)

if query:
    _prov = st.session_state.provider
    _env_var = PROVIDERS[_prov]["env"]
    _key_url = PROVIDERS[_prov].get("get_key_url", "")
    _needs_key = bool(_env_var) and not os.getenv(_env_var)
    if _needs_key:
        st.error(f"⚠️ No API key set for {_prov}. [Get one here]({_key_url}) then paste it in the sidebar.")
    else:
        st.session_state.history.append({"role": "user", "content": query})
        st.session_state.last_query = query

        with st.spinner("Thinking through the explanation..."):
            # Context retrieval
            context = ""
            source = "llm"
            if st.session_state.rag_index and st.session_state.rag_chunks:
                try:
                    from utils.rag_pipeline import retrieve
                    ctx = retrieve(query, st.session_state.rag_index, st.session_state.rag_chunks)
                    if ctx.strip():
                        context = ctx
                        source = "rag"
                except Exception:
                    pass

            if not context:
                try:
                    from utils.web_search import web_search
                    context = web_search(query)
                    if context:
                        source = "web"
                except Exception:
                    pass

            # Craft user message
            depth_note = "Be thorough and detailed." if mode == "Detailed" else "Be concise but complete."
            user_msg = f"{depth_note}\n\nTopic/Question: {query}"
            if context:
                user_msg += f"\n\nReference material:\n{context[:3000]}"

            # Call LLM
            from models.llm import call_llm, EXPLANATION_SYSTEM
            try:
                explanation = call_llm(EXPLANATION_SYSTEM, user_msg, max_tokens=1800,
                                       provider=st.session_state.provider,
                                       model=st.session_state.model)
            except Exception as e:
                explanation = f"[WHAT_IT_IS]Error: {e}[/WHAT_IT_IS][INTUITION][/INTUITION][STEP_BY_STEP][/STEP_BY_STEP][KEY_FORMULA][/KEY_FORMULA][VISUAL_HINT][/VISUAL_HINT][PRACTICE_PROBLEM][/PRACTICE_PROBLEM]"

            # Visualization
            from utils.visualizer import generate_visualization
            img_b64, img_title = generate_visualization(query)

            st.session_state.last_explanation = explanation
            st.session_state.history.append({
                "role": "assistant",
                "content": explanation,
                "img_b64": img_b64,
                "img_title": img_title,
                "source": source,
            })
        st.rerun()

# ─── Show latest answer ─────────────────────────────────────────────────────────
latest = next((m for m in reversed(st.session_state.history) if m["role"] == "assistant"), None)
if latest:
    st.markdown("---")
    render_explanation(
        latest["content"],
        latest.get("img_b64"),
        latest.get("img_title", "Visualization"),
        latest.get("source", "llm"),
    )

# ─── Lesson Video Generation ────────────────────────────────────────────────────
if gen_video and st.session_state.last_explanation:
    st.markdown("---")
    st.markdown("## 🎬 Generating Your Lesson")

    with st.spinner("Building structured lesson slides..."):
        from models.llm import call_llm, LESSON_SYSTEM
        from utils.lesson_builder import parse_lesson_slides, slides_to_narration

        try:
            lesson_raw = call_llm(
                LESSON_SYSTEM,
                f"Topic: {st.session_state.last_query}\n\nExplanation context:\n{st.session_state.last_explanation[:2000]}",
                max_tokens=900,
                provider=st.session_state.provider,
                model=st.session_state.model,
            )
            slides = parse_lesson_slides(lesson_raw)
        except Exception as e:
            st.error(f"Lesson error: {e}")
            slides = []

    if slides:
        # Show slide preview
        st.markdown("### 📑 Lesson Slides Preview")
        slide_cols = st.columns(min(len(slides), 5))
        for i, (slide, col) in enumerate(zip(slides, slide_cols)):
            with col:
                colors = ["#58a6ff", "#3fb950", "#d2a8ff", "#ffa657", "#79c0ff"]
                color = colors[i % len(colors)]
                st.markdown(f"""
<div style="background:#161b22; border:1px solid #21262d; border-top: 3px solid {color};
     border-radius:8px; padding:14px; min-height:120px;">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:{color}; margin-bottom:6px;">SLIDE {i+1}</div>
  <div style="font-size:13px; color:#e6edf3; font-weight:600; margin-bottom:8px;">{slide['title']}</div>
  <div style="font-size:12px; color:#8b949e; line-height:1.5;">{slide['content'][:120]}{'...' if len(slide['content'])>120 else ''}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        with st.spinner("Generating AI narration and video... (this takes ~30 seconds)"):
            try:
                from utils.tts import text_to_speech
                from utils.video_generator import create_lesson_video

                narration = slides_to_narration(slides)
                audio_path = text_to_speech(narration)
                video_path = create_lesson_video(slides, audio_path)

                with open(video_path, "rb") as vf:
                    video_bytes = vf.read()

                st.markdown("### 🎥 Your Lesson Video")
                st.video(video_bytes)
                st.download_button(
                    "⬇️ Download Lesson Video",
                    data=video_bytes,
                    file_name=f"{st.session_state.last_query[:30].replace(' ','_')}_lesson.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )
                os.unlink(audio_path)
                os.unlink(video_path)

            except ImportError as e:
                st.warning(f"Video packages not installed: {e}")
                st.info("Install `gtts` and `moviepy` to enable video export. The slides above are your lesson content.")
            except Exception as e:
                st.error(f"Video generation error: {e}")
