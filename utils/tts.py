import os
import tempfile
from config.config import TTS_LANG


def text_to_speech(text: str, output_path: str = None) -> str:
    """Convert text to speech. Returns path to mp3 file."""
    from gtts import gTTS
    tts = gTTS(text=text, lang=TTS_LANG, slow=False)
    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        output_path = tmp.name
        tmp.close()
    tts.save(output_path)
    return output_path
