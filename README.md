<!-- Badges -->

[![PyPI version](https://img.shields.io/pypi/v/poetic-ontology-builder.svg)](https://pypi.org/project/poetic-ontology-builder/)
[![Python versions](https://img.shields.io/pypi/pyversions/poetic-ontology-builder.svg)](https://pypi.org/project/poetic-ontology-builder/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build](https://img.shields.io/github/actions/workflow/status/willt08/poetic_ontology_builder/python-package.yml)](https://github.com/willt08/poetic_ontology_builder/actions)

# Poetic Ontology Builder

**Author:** Willinton Triana Cardona  
**Version:** 1.0.0

> _"Every text carries emotional weight. This tool extracts its meaning, weaves it into an ontology, and illuminates its emotional resonance"_

Poetic Ontology Builder transforms any text into a **living knowledge graph** enriched with **emotional embeddings**.  
It combines **large language models** for knowledge extraction (Gemini), **Rosa** (a fine‑tuned BERT model for GoEmotions), and **ontology construction** (OWL + RDF) into an interactive, beautiful visualization.

---

## Features

- **Knowledge graph extraction:**  
  Extracts **subject‑predicate‑object** triplets with contextual qualifiers from any text.
- **Emotional embedding:**  
  Integrates **ROSA** — a fine‑tuned BERT model trained on the GoEmotions dataset — to detect and color‑map emotional tones.
- **Ontology export:**  
  Generates **GraphDB‑ready OWL files** for semantic storage and querying.
- **Interactive graph visualization:**  
  Force‑directed, emotion‑color‑coded graphs with **poetic tooltips**.
- **Emotional analytics:**  
  Exports **emotion distribution JSON** and **a bar chart** summarizing emotional fields.
- **Timestamped outputs:**  
  Each run produces a clean folder:
  ```
  outputs/YYYYMMDD_HHMMSS/
  ├── sublime_graph.owl
  ├── sublime_graph.html
  ├── emotion_stats.json
  ├── emotion_stats.png
  ```

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/yourusername/poetic_ontology_builder.git
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

### Open the interactive graph & emotion chart after generation:

```bash
poetic-ontology text.txt --open
```

---

## Output

1. **Ontology:**  
   `sublime_graph.owl` — an RDF/OWL representation (GraphDB‑ready).
2. **Interactive Graph:**  
   `sublime_graph.html` — force‑directed graph with emotion‑colored nodes and tooltips.
3. **Emotion Analytics:**
   - `emotion_stats.json` — raw emotional counts.
   - `emotion_stats.png` — a bar chart of the emotional field.

---

## Emotional Palette

Each emotion is mapped to a **distinct color** based on its polarity and tone.  
Example:

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
- **Google Gemini**: Triplet & knowledge extraction
- **OWLready2**: Ontology management
- **PyVis**: Interactive graph visualization

---

## License

MIT License © 2025 Willinton Triana Cardona
