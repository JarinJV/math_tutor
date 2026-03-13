from sentence_transformers import SentenceTransformer
from config.config import EMBEDDING_MODEL

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_texts(texts: list[str]) -> list:
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False).tolist()
