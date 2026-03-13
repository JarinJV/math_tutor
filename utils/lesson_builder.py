import re


def parse_lesson_slides(lesson_text: str) -> list[dict]:
    """Parse LLM lesson output into list of {title, content} dicts."""
    slides = []
    pattern = r"SLIDE (\d+) TITLE:\s*(.+?)\nSLIDE \1 CONTENT:\s*(.+?)(?=\nSLIDE \d+|$)"
    matches = re.findall(pattern, lesson_text, re.DOTALL)
    for num, title, content in matches:
        slides.append({
            "number": int(num),
            "title": title.strip(),
            "content": content.strip(),
        })
    # fallback if no matches
    if not slides:
        lines = [l for l in lesson_text.strip().split("\n") if l.strip()]
        for i in range(0, len(lines), 2):
            title = lines[i] if i < len(lines) else f"Slide {i//2+1}"
            content = lines[i+1] if i+1 < len(lines) else ""
            slides.append({"number": i//2+1, "title": title, "content": content})
    return slides[:5]


def slides_to_narration(slides: list[dict]) -> str:
    """Build a narration script from slides."""
    parts = []
    for slide in slides:
        parts.append(f"{slide['title']}. {slide['content']}")
    return "  ".join(parts)
