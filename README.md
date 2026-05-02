<!-- Badges -->

[![PyPI version](https://img.shields.io/pypi/v/poetic-ontology-builder.svg)](https://pypi.org/project/poetic-ontology-builder/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build](https://img.shields.io/github/actions/workflow/status/willt08/poetic_ontology_builder/python-package.yml)](https://github.com/willt08/poetic_ontology_builder/actions)

# Poetic Ontology Builder

**Author:** Willinton Triana Cardona  
**Version:** 1.1.0

> _"Every text carries emotional weight. This tool extracts its meaning, weaves it into an ontology, and illuminates its emotional resonance"_

Poetic Ontology Builder transforms any text into a **living knowledge graph** enriched with **emotional embeddings**.  
It combines **Google Gemini 2.5 Flash** for knowledge extraction, **Rosa** (a fine‑tuned BERT model for GoEmotions), and **ontology construction** (OWL + RDF) into an interactive, beautiful visualization — including a full **Enneagram personality profile** derived from the text's emotional field.

---

## Features

- **Knowledge graph extraction:**  
  Extracts **subject‑predicate‑object** triplets with contextual qualifiers from any text using **Gemini 2.5 Flash**.
- **Emotional embedding:**  
  Integrates **ROSA** — a fine‑tuned BERT model trained on the GoEmotions dataset — to detect the full probability distribution across 28 emotion labels per triplet.
- **Precise emotional analytics:**  
  Computes **mean, std dev, max, and total** per emotion across all triplets. Outputs a dark‑themed bar chart with error bars and percentage labels.
- **Enneagram chart:**  
  Maps the aggregated emotion distribution onto the **9 Enneagram types** and renders a polar radar chart showing the dominant personality archetype of the text.
- **Ontology export:**  
  Generates **GraphDB‑ready OWL files** for semantic storage and querying.
- **Interactive graph visualization:**  
  Force‑directed, emotion‑color‑coded graphs with **poetic tooltips**.
- **Timestamped outputs:**  
  Each run produces a clean folder:
  ```
  outputs/YYYYMMDD_HHMMSS/
  ├── sublime_graph.owl
  ├── sublime_graph.html
  ├── emotion_stats.json
  ├── emotion_stats.png
  ├── enneagram_stats.json
  └── enneagram_chart.png
  ```

---

## Requirements

- Python **3.10** or higher
- A **Gemini API key** (Google AI Studio)
- A **Hugging Face token** with access to `willt-dc/Rosa-V1`

---

## Installation

**From PyPI:**

```bash
pip install poetic-ontology-builder
```

**For local development (editable):**

```bash
git clone https://github.com/willt08/poetic_ontology_builder.git
cd poetic_ontology_builder
pip install -e .
```

---

## Configuration

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token
```

---

## Usage

### From a text file:

```bash
poetic-ontology path/to/textfile.txt
```

### From an inline string:

```bash
poetic-ontology "And Socrates said: When the soul returns into itself..."
```

### Open all outputs automatically after generation:

```bash
poetic-ontology rilke.txt --open
```

---

## Output

1. **Ontology:**  
   `sublime_graph.owl` — RDF/OWL representation, GraphDB‑ready.
2. **Interactive Graph:**  
   `sublime_graph.html` — force‑directed graph with emotion‑colored nodes and tooltips.
3. **Emotion Analytics:**
   - `emotion_stats.json` — mean, std dev, max, min, total per emotion + dominant emotion counts per triplet.
   - `emotion_stats.png` — dark‑themed bar chart of mean probability scores ± std dev.
4. **Enneagram Profile:**
   - `enneagram_stats.json` — score and normalized score for each of the 9 types, plus dominant type.
   - `enneagram_chart.png` — polar radar chart of the text's Enneagram emotional profile.

---

## Enneagram Mapping

Each GoEmotions label is mapped to its primary Enneagram type based on core motivational emotion clusters:

| Type | Name | Key Emotions |
|------|------|-------------|
| 1 | Reformer | annoyance, disapproval, disgust |
| 2 | Helper | caring, love, gratitude, approval |
| 3 | Achiever | admiration, pride, optimism |
| 4 | Individualist | sadness, grief, disappointment, remorse, embarrassment |
| 5 | Investigator | curiosity, confusion, realization |
| 6 | Loyalist | fear, nervousness |
| 7 | Enthusiast | joy, excitement, amusement, desire, surprise |
| 8 | Challenger | anger |
| 9 | Peacemaker | neutral, relief |

---

## Emotional Palette

Each emotion is mapped to a **distinct color** based on its polarity and tone:

- **Joy / Love / Pride** → Warm yellows & pinks
- **Grief / Fear / Anger** → Deep blues & reds
- **Neutral** → Gray

---

## Roadmap

- [ ] BFO/SUMO alignment for deeper ontological grounding
- [ ] PyPI release for global access
- [ ] Web interface for non‑technical users
- [ ] Multi‑modal inputs (image + text)

---

## Acknowledgements

- **ROSA**: Emotional BERT model fine‑tuned on GoEmotions
- **Google Gemini 2.5 Flash**: Triplet & knowledge extraction
- **OWLready2**: Ontology management
- **PyVis**: Interactive graph visualization

---

## License

MIT License © 2025 Willinton Triana Cardona
