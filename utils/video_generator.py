import os, tempfile, textwrap
import numpy as np
from config.config import VIDEO_FPS, VIDEO_SIZE


def render_slide_image(slide: dict, index: int, output_dir: str, img_b64=None) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    import base64
    from io import BytesIO
    from PIL import Image as PILImage

    fig = plt.figure(figsize=(VIDEO_SIZE[0]/100, VIDEO_SIZE[1]/100), facecolor="#0d1117")

    if img_b64 and index == 2:  # Slide 3: formula + graph side by side
        gs = GridSpec(1, 2, figure=fig, left=0.05, right=0.95, wspace=0.08)
        ax_text = fig.add_subplot(gs[0, 0])
        ax_img  = fig.add_subplot(gs[0, 1])
        # draw graph
        img_data = base64.b64decode(img_b64)
        pil_img = PILImage.open(BytesIO(img_data))
        ax_img.imshow(pil_img)
        ax_img.axis("off")
        _draw_slide_text(ax_text, slide, index)
    else:
        ax = fig.add_subplot(111)
        _draw_slide_text(ax, slide, index)

    path = os.path.join(output_dir, f"slide_{index:02d}.png")
    fig.savefig(path, dpi=100, facecolor="#0d1117", bbox_inches="tight")
    plt.close(fig)
    return path


def _draw_slide_text(ax, slide, index):
    ax.set_facecolor("#0d1117")
    ax.axis("off")
    colors = ["#58a6ff", "#3fb950", "#d2a8ff", "#ffa657", "#79c0ff"]
    accent = colors[index % len(colors)]

    # Slide number
    ax.text(0.97, 0.96, f"{index+1}/5", transform=ax.transAxes,
            fontsize=12, color="#444", ha="right", va="top", family="monospace")
    # Accent bar
    ax.plot([0.04, 0.96], [0.88, 0.88], color=accent, lw=2.5, transform=ax.transAxes)
    # Title
    ax.text(0.5, 0.78, slide["title"], transform=ax.transAxes,
            fontsize=28, color="white", ha="center", va="center",
            fontweight="bold")
    # Content
    content = textwrap.fill(slide["content"], width=65)
    ax.text(0.5, 0.42, content, transform=ax.transAxes,
            fontsize=15, color="#c9d1d9", ha="center", va="center", linespacing=1.7)
    # Footer
    ax.text(0.5, 0.04, "AI Visual Math Tutor", transform=ax.transAxes,
            fontsize=10, color="#21262d", ha="center")


def create_lesson_video(slides: list[dict], audio_path: str, output_path: str = None, img_b64=None) -> str:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path = tmp.name
        tmp.close()

    with tempfile.TemporaryDirectory() as tmpdir:
        slide_paths = [render_slide_image(s, i, tmpdir, img_b64 if i == 2 else None)
                       for i, s in enumerate(slides)]

        audio = AudioFileClip(audio_path)
        slide_dur = audio.duration / max(len(slides), 1)

        clips = [ImageClip(p).set_duration(slide_dur) for p in slide_paths]
        video = concatenate_videoclips(clips, method="compose").set_audio(audio)
        video.write_videofile(output_path, fps=VIDEO_FPS, codec="libx264",
                              audio_codec="aac", logger=None)
    return output_path
