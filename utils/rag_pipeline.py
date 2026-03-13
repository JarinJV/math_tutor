import os
import pickle
import numpy as np
from pathlib import Path
from config.config import VECTOR_DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def load_pdf(file_path: str) -> str:
    """Extract text from PDF."""
    if not PYPDF_AVAILABLE:
        raise ImportError("pypdf not installed")
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def build_vector_store(chunks: list[str], doc_name: str):
    """Build and save FAISS index from chunks."""
    if not FAISS_AVAILABLE:
        raise ImportError("faiss-cpu not installed")
    from models.embeddings import embed_texts

    embeddings = embed_texts(chunks)
    embeddings_np = np.array(embeddings, dtype="float32")

    dim = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    safe_name = doc_name.replace(" ", "_").replace("/", "_")

    faiss.write_index(index, f"{VECTOR_DB_PATH}/{safe_name}.faiss")
    with open(f"{VECTOR_DB_PATH}/{safe_name}_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    return index, chunks


def load_vector_store(doc_name: str):
    """Load saved FAISS index."""
    if not FAISS_AVAILABLE:
        return None, []
    safe_name = doc_name.replace(" ", "_").replace("/", "_")
    faiss_path = f"{VECTOR_DB_PATH}/{safe_name}.faiss"
    chunks_path = f"{VECTOR_DB_PATH}/{safe_name}_chunks.pkl"

    if not os.path.exists(faiss_path):
        return None, []

    index = faiss.read_index(faiss_path)
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks


def retrieve(query: str, index, chunks: list[str], top_k: int = 4) -> str:
    """Retrieve top-k relevant chunks for a query."""
    if index is None or not chunks:
        return ""
    from models.embeddings import embed_texts

    query_embedding = np.array(embed_texts([query]), dtype="float32")
    distances, indices = index.search(query_embedding, top_k)
    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return "\n\n".join(results)


def process_uploaded_pdf(uploaded_file, doc_name: str) -> tuple:
    """Process an uploaded Streamlit file object."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    text = load_pdf(tmp_path)
    os.unlink(tmp_path)
    chunks = chunk_text(text)
    index, chunks = build_vector_store(chunks, doc_name)
    return index, chunks
