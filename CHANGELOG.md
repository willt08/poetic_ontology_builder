# Changelog

## 1.1.0
- **Enneagram chart:** polar radar chart (`enneagram_chart.png`) and JSON profile (`enneagram_stats.json`) derived from the text's aggregated emotion field, mapping all 28 GoEmotions labels to the 9 Enneagram types
- **Precise emotion stats:** `get_emotional_scores` now returns the full probability distribution; `save_emotion_distribution` computes mean, std dev, max, min, and total per emotion with error-bar bar chart
- **Gemini 2.5 Flash:** updated from deprecated 1.5 model
- **Python 3.10+:** dropped 3.8 support; CI updated to Python 3.11
- **Dependencies:** fixed malformed `--only-binary` flag in `requirements.txt`; added `numpy`; synced versions across `requirements.txt`, `pyproject.toml`, and `setup.py`
- **CLI:** `--open` now also auto-opens `enneagram_chart.png`
- **Repo hygiene:** removed tracked PyVis static assets (`lib/`) and scratch `test.txt`

## 1.0.1
- Added `--open` flag for cross‑platform auto‑open of graph and emotion chart
- Improved CLI for WSL compatibility
- Polished README and packaging for PyPI readiness
