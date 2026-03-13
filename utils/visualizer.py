import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import base64
import re


MATH_TOPICS = {
    "vector": ["vector", "dot product", "cross product", "magnitude", "direction"],
    "matrix": ["matrix", "transformation", "eigenvalue", "eigenvector", "determinant", "inverse"],
    "regression": ["regression", "linear regression", "least squares", "correlation", "r-squared"],
    "distribution": ["distribution", "normal", "gaussian", "probability", "histogram", "bell curve", "standard deviation"],
    "calculus": ["derivative", "integral", "limit", "differentiation", "slope", "tangent"],
    "trig": ["sine", "cosine", "tangent", "trigonometry", "angle", "sin", "cos"],
    "quadratic": ["quadratic", "parabola", "polynomial", "roots", "x squared"],
    "linear": ["linear", "line", "slope", "intercept", "y=mx", "linear equation"],
}


def detect_topic(query: str) -> str:
    q = query.lower()
    for topic, keywords in MATH_TOPICS.items():
        if any(kw in q for kw in keywords):
            return topic
    return "general"


def fig_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_b64


def plot_vectors():
    fig, ax = plt.subplots(figsize=(7, 6), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    vectors = [(3, 1, "#4ade80", "v₁ = (3,1)"), (1, 4, "#60a5fa", "v₂ = (1,4)"), (4, 5, "#f472b6", "v₁+v₂ = (4,5)")]
    for vx, vy, color, label in vectors:
        ax.annotate("", xy=(vx, vy), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2.5))
        ax.text(vx + 0.1, vy + 0.1, label, color=color, fontsize=10)
    ax.axhline(0, color="#333", lw=0.5)
    ax.axvline(0, color="#333", lw=0.5)
    ax.set_xlim(-1, 6); ax.set_ylim(-1, 7)
    ax.grid(True, color="#222", alpha=0.5)
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.set_title("Vector Addition", color="white", fontsize=14, pad=10)
    return fig_to_base64(fig)


def plot_matrix_transform():
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), facecolor="#0f1117")
    original = np.array([[0,1,1,0,0],[0,0,1,1,0]])
    M = np.array([[2,1],[0.5,1.5]])
    transformed = M @ original
    for ax, pts, title, color in zip(axes,
            [original, transformed],
            ["Original Shape", "After Matrix Transform"],
            ["#60a5fa", "#f472b6"]):
        ax.set_facecolor("#0f1117")
        ax.fill(pts[0], pts[1], alpha=0.4, color=color)
        ax.plot(pts[0], pts[1], color=color, lw=2)
        ax.axhline(0, color="#333", lw=0.5); ax.axvline(0, color="#333", lw=0.5)
        ax.grid(True, color="#222", alpha=0.5)
        ax.set_title(title, color="white", fontsize=12)
        ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
        ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.5, 3.5)
    fig.suptitle("Matrix Transformation", color="white", fontsize=14)
    fig.patch.set_facecolor("#0f1117")
    return fig_to_base64(fig)


def plot_regression():
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y = 2.5 * x + 3 + np.random.normal(0, 3, 50)
    m, b = np.polyfit(x, y, 1)
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    ax.scatter(x, y, color="#60a5fa", alpha=0.7, s=40, label="Data points")
    ax.plot(x, m*x+b, color="#f472b6", lw=2.5, label=f"y = {m:.2f}x + {b:.2f}")
    for xi, yi in zip(x[::5], y[::5]):
        ax.plot([xi, xi], [yi, m*xi+b], color="#fbbf24", alpha=0.4, lw=1)
    ax.set_title("Linear Regression", color="white", fontsize=14)
    ax.legend(facecolor="#1a1a2e", labelcolor="white")
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.grid(True, color="#222", alpha=0.5)
    return fig_to_base64(fig)


def plot_distribution():
    fig, ax = plt.subplots(figsize=(8, 5), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    x = np.linspace(-4, 4, 300)
    for mean, std, color, label in [
        (0, 1, "#4ade80", "μ=0, σ=1"),
        (0, 2, "#60a5fa", "μ=0, σ=2"),
        (1, 0.5, "#f472b6", "μ=1, σ=0.5"),
    ]:
        y = (1/(std*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mean)/std)**2)
        ax.plot(x, y, color=color, lw=2.5, label=label)
        ax.fill_between(x, y, alpha=0.1, color=color)
    ax.set_title("Normal Distributions", color="white", fontsize=14)
    ax.legend(facecolor="#1a1a2e", labelcolor="white")
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.grid(True, color="#222", alpha=0.5)
    return fig_to_base64(fig)


def plot_derivative():
    x = np.linspace(-3, 3, 300)
    y = x**3 - 2*x
    dy = 3*x**2 - 2
    x0 = 1.0
    y0 = x0**3 - 2*x0
    slope = 3*x0**2 - 2
    tangent = slope*(x - x0) + y0
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    ax.plot(x, y, color="#60a5fa", lw=2.5, label="f(x) = x³ - 2x")
    ax.plot(x, tangent, color="#f472b6", lw=2, linestyle="--", label=f"Tangent at x=1 (slope={slope:.1f})")
    ax.scatter([x0], [y0], color="#fbbf24", s=100, zorder=5)
    ax.set_ylim(-6, 6); ax.set_title("Derivative as Tangent Slope", color="white", fontsize=14)
    ax.legend(facecolor="#1a1a2e", labelcolor="white")
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.grid(True, color="#222", alpha=0.5)
    return fig_to_base64(fig)


def plot_trig():
    x = np.linspace(0, 2*np.pi, 300)
    fig, ax = plt.subplots(figsize=(8, 5), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    ax.plot(x, np.sin(x), color="#4ade80", lw=2.5, label="sin(x)")
    ax.plot(x, np.cos(x), color="#60a5fa", lw=2.5, label="cos(x)")
    ax.plot(x, np.tan(np.clip(x, -1.5, 1.5)), color="#f472b6", lw=2, label="tan(x) [clipped]", alpha=0.7)
    ax.axhline(0, color="#444", lw=0.8)
    xticks = [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]
    ax.set_xticks(xticks)
    ax.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"], color="#888")
    ax.set_ylim(-2, 2); ax.set_title("Trigonometric Functions", color="white", fontsize=14)
    ax.legend(facecolor="#1a1a2e", labelcolor="white")
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.grid(True, color="#222", alpha=0.5)
    return fig_to_base64(fig)


def plot_quadratic():
    x = np.linspace(-5, 5, 300)
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    for a, color, label in [(1, "#4ade80", "x²"), (2, "#60a5fa", "2x²"), (-1, "#f472b6", "-x²"), (0.5, "#fbbf24", "0.5x²")]:
        ax.plot(x, a*x**2, color=color, lw=2, label=label)
    ax.axhline(0, color="#444", lw=0.8); ax.axvline(0, color="#444", lw=0.8)
    ax.set_ylim(-15, 20); ax.set_title("Quadratic Functions: f(x) = ax²", color="white", fontsize=14)
    ax.legend(facecolor="#1a1a2e", labelcolor="white")
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.grid(True, color="#222", alpha=0.5)
    return fig_to_base64(fig)


def plot_linear():
    x = np.linspace(-5, 5, 100)
    fig, ax = plt.subplots(figsize=(7, 5), facecolor="#0f1117")
    ax.set_facecolor("#0f1117")
    lines = [(2, 1, "#4ade80", "y=2x+1"), (-1, 3, "#60a5fa", "y=-x+3"), (0.5, -2, "#f472b6", "y=0.5x-2"), (3, 0, "#fbbf24", "y=3x")]
    for m, b, color, label in lines:
        ax.plot(x, m*x+b, color=color, lw=2, label=label)
    ax.axhline(0, color="#444", lw=0.8); ax.axvline(0, color="#444", lw=0.8)
    ax.set_ylim(-10, 10); ax.set_title("Linear Functions: y = mx + b", color="white", fontsize=14)
    ax.legend(facecolor="#1a1a2e", labelcolor="white", loc="upper left")
    ax.tick_params(colors="#888"); ax.spines[:].set_color("#333")
    ax.grid(True, color="#222", alpha=0.5)
    return fig_to_base64(fig)


TOPIC_PLOTTERS = {
    "vector": plot_vectors,
    "matrix": plot_matrix_transform,
    "regression": plot_regression,
    "distribution": plot_distribution,
    "calculus": plot_derivative,
    "trig": plot_trig,
    "quadratic": plot_quadratic,
    "linear": plot_linear,
}


def generate_visualization(query: str) -> tuple[str | None, str]:
    """Return (base64_png_or_None, chart_title)."""
    topic = detect_topic(query)
    plotter = TOPIC_PLOTTERS.get(topic)
    if plotter:
        img_b64 = plotter()
        titles = {
            "vector": "Vector Visualization",
            "matrix": "Matrix Transformation",
            "regression": "Regression Analysis",
            "distribution": "Probability Distribution",
            "calculus": "Calculus — Derivatives",
            "trig": "Trigonometric Functions",
            "quadratic": "Quadratic Functions",
            "linear": "Linear Functions",
        }
        return img_b64, titles.get(topic, "Visualization")
    return None, ""
