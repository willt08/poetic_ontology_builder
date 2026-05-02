import os
import json
import datetime
import numpy as np
import torch
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import google.generativeai as genai
from owlready2 import get_ontology, Thing, DataProperty, ObjectProperty
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from pyvis.network import Network
from collections import Counter

# --- ENV & MODELS ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

ROSA_MODEL = "willt-dc/Rosa-V1"
tokenizer = AutoTokenizer.from_pretrained(ROSA_MODEL, token=HF_TOKEN)
rosa_model = AutoModelForSequenceClassification.from_pretrained(
    ROSA_MODEL, token=HF_TOKEN
)
emotion_classifier = pipeline(
    "text-classification", model=rosa_model, tokenizer=tokenizer, top_k=None
)

# Emotion colors (GoEmotions 28+neutral)
EMOTION_COLORS = {
    "admiration": "#FFD700",
    "amusement": "#FFB347",
    "anger": "#FF0000",
    "annoyance": "#FF4500",
    "approval": "#32CD32",
    "caring": "#FF69B4",
    "confusion": "#9370DB",
    "curiosity": "#00CED1",
    "desire": "#FF1493",
    "disappointment": "#708090",
    "disapproval": "#8B0000",
    "disgust": "#556B2F",
    "embarrassment": "#CD5C5C",
    "excitement": "#FFA500",
    "fear": "#8B008B",
    "gratitude": "#7CFC00",
    "grief": "#483D8B",
    "joy": "#FFFF00",
    "love": "#FF69B4",
    "nervousness": "#20B2AA",
    "optimism": "#ADFF2F",
    "pride": "#DAA520",
    "realization": "#6495ED",
    "relief": "#3CB371",
    "remorse": "#A0522D",
    "sadness": "#1E90FF",
    "surprise": "#FF6347",
    "neutral": "#A9A9A9",
}

# Enneagram type names
ENNEAGRAM_TYPES = {
    1: "Reformer",
    2: "Helper",
    3: "Achiever",
    4: "Individualist",
    5: "Investigator",
    6: "Loyalist",
    7: "Enthusiast",
    8: "Challenger",
    9: "Peacemaker",
}

# Maps each GoEmotion label to its primary Enneagram type
ENNEAGRAM_EMOTION_MAP = {
    "admiration":     3,  # Achiever – seeks admiration/validation
    "amusement":      7,  # Enthusiast – playfulness
    "anger":          8,  # Challenger – instinctual anger/power
    "annoyance":      1,  # Reformer – critical perfectionism
    "approval":       2,  # Helper – needs approval/to be needed
    "caring":         2,  # Helper – giving care
    "confusion":      5,  # Investigator – seeks clarity
    "curiosity":      5,  # Investigator – knowledge seeking
    "desire":         7,  # Enthusiast – wanting more
    "disappointment": 4,  # Individualist – deep feeling of loss
    "disapproval":    1,  # Reformer – moral judgment
    "disgust":        1,  # Reformer – moral standards
    "embarrassment":  4,  # Individualist – shame/sensitivity
    "excitement":     7,  # Enthusiast – enthusiasm
    "fear":           6,  # Loyalist – anxiety/fear
    "gratitude":      2,  # Helper – love/appreciation
    "grief":          4,  # Individualist – melancholy
    "joy":            7,  # Enthusiast – joy
    "love":           2,  # Helper – love
    "nervousness":    6,  # Loyalist – anxiety
    "optimism":       3,  # Achiever – forward-looking positivity
    "pride":          3,  # Achiever – pride in achievement
    "realization":    5,  # Investigator – insight
    "relief":         9,  # Peacemaker – resolution/peace
    "remorse":        4,  # Individualist – guilt/melancholy
    "sadness":        4,  # Individualist – melancholy
    "surprise":       7,  # Enthusiast – novelty
    "neutral":        9,  # Peacemaker – equanimity
}


# --- Gemini triplet extraction ---
def extract_triplets_gemini(text: str):
    prompt = f"""
    Extract knowledge triples from the text.
    For each, provide: subject, predicate, object, and emotional/epistemic qualifier.
    Output as strict JSON list of dicts:
    [{{"subject":"...","predicate":"...","object":"...","qualifier":"..."}}]
    Text: {text}
    """
    try:
        response = gemini_model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        triplets = json.loads(raw_text)
        return [
            {
                "subject": t.get("subject") or "Unknown",
                "predicate": t.get("predicate") or "Unknown",
                "object": t.get("object") or "Unknown",
                "qualifier": t.get("qualifier") or "unspecified",
            }
            for t in triplets
        ]
    except Exception as e:
        print(
            "⚠️ Parsing failed. Raw Gemini output:\n",
            getattr(response, "text", "No content"),
        )
        return []


# --- Emotion scoring ---
def get_emotional_scores(text: str) -> dict:
    """Returns the full probability distribution over all emotion labels."""
    results = emotion_classifier(text)
    if results and isinstance(results, list) and len(results) > 0:
        return {item["label"]: float(item["score"]) for item in results[0]}
    return {"neutral": 1.0}


def get_emotional_embedding(text: str) -> str:
    scores = get_emotional_scores(text)
    return max(scores, key=scores.get)


# --- Ontology builder ---
def build_ontology(triplets, ontology_name="sublime_graph"):
    onto = get_ontology(f"http://example.org/{ontology_name}.owl")
    with onto:

        class Entity(Thing):
            pass

        class relatesTo(ObjectProperty):
            pass

        class hasQualifier(DataProperty):
            pass

        class hasEmotion(DataProperty):
            pass

        for t in triplets:
            subj, pred, obj, qual = (
                t["subject"],
                t["predicate"],
                t["object"],
                t["qualifier"],
            )
            scores = get_emotional_scores(f"{subj} {obj}")
            top_emotion = max(scores, key=scores.get)
            t["emotion"] = top_emotion
            t["emotion_scores"] = scores
            subj_ind = Entity(subj.replace(" ", "_"))
            obj_ind = Entity(obj.replace(" ", "_"))
            relatesTo[subj_ind].append(obj_ind)
            subj_ind.hasQualifier = [qual]
            subj_ind.hasEmotion = [top_emotion]
    return onto


def export_ontology(onto, filename):
    onto.save(file=filename, format="rdfxml")
    print(f"Ontology exported to {filename} (GraphDB-ready).")


# --- Emotion distribution chart (precise stats) ---
def save_emotion_distribution(triplets, out_dir):
    all_scores = [t.get("emotion_scores", {}) for t in triplets]
    all_labels = list(EMOTION_COLORS.keys())

    # Per-emotion mean, std, max, total across all triplets
    stats = {}
    for label in all_labels:
        values = np.array([s.get(label, 0.0) for s in all_scores], dtype=float)
        if values.size > 0:
            stats[label] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "max": float(np.max(values)),
                "min": float(np.min(values)),
                "total": float(np.sum(values)),
            }

    # Dominant-emotion count per triplet
    dominant_counts = dict(Counter(t.get("emotion", "neutral") for t in triplets))

    output = {
        "triplet_count": len(triplets),
        "emotion_stats": stats,
        "dominant_emotion_counts": dominant_counts,
    }
    with open(os.path.join(out_dir, "emotion_stats.json"), "w") as f:
        json.dump(output, f, indent=2)

    # Plot: mean scores sorted descending, only emotions above threshold
    threshold = 0.005
    filtered = {k: v for k, v in stats.items() if v["mean"] >= threshold}
    ordered = dict(sorted(filtered.items(), key=lambda x: x[1]["mean"], reverse=True))
    labels = list(ordered.keys())
    means = np.array([ordered[l]["mean"] for l in labels])
    stds = np.array([ordered[l]["std"] for l in labels])
    colors = [EMOTION_COLORS.get(l, "#808080") for l in labels]

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    bars = ax.bar(
        labels, means, yerr=stds, capsize=4,
        color=colors, edgecolor="white", linewidth=0.4,
        error_kw={"ecolor": "white", "alpha": 0.5},
    )
    for bar, mean in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + stds[bars.patches.index(bar)] + 0.001,
            f"{mean * 100:.1f}%",
            ha="center", va="bottom", fontsize=7, color="white",
        )
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", color="white", fontsize=8)
    ax.set_ylabel("Mean Probability", color="white")
    ax.set_title("Emotion Distribution — Mean Score ± Std Dev", color="white", pad=10)
    ax.tick_params(colors="white")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["bottom", "left"]:
        ax.spines[spine].set_color("#555")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "emotion_stats.png"), dpi=150, facecolor="#1e1e1e")
    plt.close()
    print(f"Emotion stats saved to {out_dir}")


# --- Enneagram radar chart ---
def save_enneagram_chart(triplets, out_dir):
    all_scores = [t.get("emotion_scores", {}) for t in triplets]
    if not all_scores:
        print("⚠️ No emotion scores found — skipping enneagram chart.")
        return

    # Mean score per emotion across all triplets
    mean_per_emotion = {
        label: float(np.mean([s.get(label, 0.0) for s in all_scores]))
        for label in EMOTION_COLORS
    }

    # Aggregate into enneagram type scores (average of mapped emotions per type)
    type_emotion_values: dict[int, list] = {i: [] for i in range(1, 10)}
    for emotion, type_num in ENNEAGRAM_EMOTION_MAP.items():
        type_emotion_values[type_num].append(mean_per_emotion.get(emotion, 0.0))

    type_scores = {
        i: float(np.mean(vals)) if vals else 0.0
        for i, vals in type_emotion_values.items()
    }

    # Normalize relative to the highest type score
    max_score = max(type_scores.values()) or 1.0
    type_scores_norm = {i: v / max_score for i, v in type_scores.items()}

    # Radar chart
    N = 9
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    values = [type_scores_norm[i] for i in range(1, 10)] + [type_scores_norm[1]]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [f"Type {i}\n{ENNEAGRAM_TYPES[i]}" for i in range(1, 10)],
        size=9, color="white",
    )
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(
        ["20%", "40%", "60%", "80%", "100%"], size=7, color="#888"
    )
    ax.tick_params(colors="#888")
    ax.spines["polar"].set_color("#444")
    ax.grid(color="#444", linewidth=0.5)

    ax.plot(angles, values, linewidth=2, linestyle="solid", color="#FF6B6B")
    ax.fill(angles, values, alpha=0.30, color="#FF6B6B")

    # Annotate raw scores at each vertex
    for i, (angle, norm_val) in enumerate(zip(angles[:-1], values[:-1])):
        raw = type_scores[i + 1]
        offset = 0.10
        ax.annotate(
            f"{raw:.4f}",
            xy=(angle, norm_val),
            xytext=(angle, min(norm_val + offset, 1.15)),
            ha="center", va="center", fontsize=7.5, color="white",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#333", alpha=0.75, edgecolor="none"),
        )

    dominant = max(type_scores, key=type_scores.get)
    ax.set_title(
        f"Enneagram Emotional Profile\nDominant: Type {dominant} — {ENNEAGRAM_TYPES[dominant]}",
        size=13, color="white", pad=30,
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(out_dir, "enneagram_chart.png"), dpi=150, facecolor="#1e1e1e"
    )
    plt.close()

    # Save JSON
    enneagram_data = {
        f"type_{i}": {
            "name": ENNEAGRAM_TYPES[i],
            "score": type_scores[i],
            "normalized_score": type_scores_norm[i],
        }
        for i in range(1, 10)
    }
    enneagram_data["dominant_type"] = dominant
    enneagram_data["dominant_name"] = ENNEAGRAM_TYPES[dominant]
    with open(os.path.join(out_dir, "enneagram_stats.json"), "w") as f:
        json.dump(enneagram_data, f, indent=2)

    print(f"Enneagram chart saved to {out_dir}")


# --- Poetic interactive graph ---
def visualize_graph_interactive(triplets, filename):
    if not triplets:
        print("⚠️ No data to visualize. Skipping HTML graph.")
        return
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="white",
        directed=True,
    )
    net.barnes_hut()

    for t in triplets:
        subj, pred, obj, qual, emotion = (
            t["subject"],
            t["predicate"],
            t["object"],
            t["qualifier"],
            t.get("emotion", "neutral"),
        )
        color = EMOTION_COLORS.get(emotion, "#808080")
        tooltip_subj = f"<b>{subj}</b><br>Emotion: {emotion}<br>Qualifier: {qual}"
        tooltip_obj = f"<b>{obj}</b><br>Emotion: {emotion}"
        net.add_node(subj, label=subj, color=color, title=tooltip_subj)
        net.add_node(obj, label=obj, color=color, title=tooltip_obj)
        net.add_edge(subj, obj, label=pred, title=f"Relation: {pred}")

    net.show_buttons(filter_=["physics"])
    net.write_html(filename, notebook=False)
    print(f"Interactive graph saved to {filename}")


# --- Orchestration ---
def process_text(text_input, out_dir="outputs"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(out_dir, timestamp)
    os.makedirs(run_dir, exist_ok=True)

    triplets = extract_triplets_gemini(text_input)
    if not triplets:
        print("⚠️ No triplets extracted. Exiting.")
        return None

    ontology = build_ontology(triplets)
    export_ontology(ontology, os.path.join(run_dir, "sublime_graph.owl"))
    visualize_graph_interactive(triplets, os.path.join(run_dir, "sublime_graph.html"))
    save_emotion_distribution(triplets, run_dir)
    save_enneagram_chart(triplets, run_dir)
    return run_dir
