import os
import json
import datetime
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
gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")

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
def get_emotional_embedding(text: str):
    emotions = emotion_classifier(text)
    if emotions and isinstance(emotions, list) and len(emotions) > 0:
        emotions_sorted = sorted(emotions[0], key=lambda x: x["score"], reverse=True)
        return emotions_sorted[0]["label"]
    return "neutral"


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
            emotion = get_emotional_embedding(f"{subj} {obj}")
            t["emotion"] = emotion  # attach emotion to triplet
            subj_ind = Entity(subj.replace(" ", "_"))
            obj_ind = Entity(obj.replace(" ", "_"))
            relatesTo[subj_ind].append(obj_ind)
            subj_ind.hasQualifier = [qual]
            subj_ind.hasEmotion = [emotion]
    return onto


def export_ontology(onto, filename):
    onto.save(file=filename, format="rdfxml")
    print(f"Ontology exported to {filename} (GraphDB-ready).")


# --- Emotion distribution chart ---
def save_emotion_distribution(triplets, out_dir):
    emotions = [t.get("emotion", "neutral") for t in triplets]
    counts = Counter(emotions)
    data = dict(counts)
    # Save JSON
    with open(os.path.join(out_dir, "emotion_stats.json"), "w") as f:
        json.dump(data, f, indent=2)
    # Plot bar chart
    plt.figure(figsize=(10, 5))
    plt.bar(
        data.keys(),
        data.values(),
        color=[EMOTION_COLORS.get(e, "#808080") for e in data.keys()],
    )
    plt.xticks(rotation=45, ha="right")
    plt.title("Emotion Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "emotion_stats.png"))
    plt.close()
    print(f"Emotion stats saved to {out_dir}")


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
    return run_dir
