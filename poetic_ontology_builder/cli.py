import argparse
import os
import sys
import platform
import subprocess
from poetic_ontology_builder.utils import process_text


def safe_open(path):
    """Cross-platform safe opener."""
    if "microsoft" in platform.uname().release.lower():  # WSL
        subprocess.run(["explorer.exe", os.path.abspath(path).replace("/", "\\")])
    elif sys.platform.startswith("darwin"):  # macOS
        subprocess.run(["open", path])
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", path])
    elif sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore
    else:
        print(f"Unable to auto-open: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Poetic Ontology Builder: Generate ontological and emotional knowledge graphs from text."
    )
    parser.add_argument("input", help="Input text file or raw text string.")
    parser.add_argument(
        "-o", "--out", default="outputs", help="Output directory (default: outputs/)."
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated graph and emotion chart after processing.",
    )
    args = parser.parse_args()

    # Read input (file or raw string)
    if os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            text_input = f.read()
    else:
        text_input = args.input

    # Process
    print("Generating Poetic Ontology...")
    run_dir = process_text(text_input, out_dir=args.out)
    if not run_dir:
        sys.exit(1)

    print(f"\n✨ Poetic Ontology generated in: {run_dir}")
    print(f" - Ontology: {os.path.join(run_dir, 'sublime_graph.owl')}")
    print(f" - Graph: {os.path.join(run_dir, 'sublime_graph.html')}")
    print(f" - Emotion stats: {os.path.join(run_dir, 'emotion_stats.json')}")
    print(f" - Emotion chart: {os.path.join(run_dir, 'emotion_stats.png')}")

    if args.open:
        safe_open(os.path.join(run_dir, "sublime_graph.html"))
        safe_open(os.path.join(run_dir, "emotion_stats.png"))


if __name__ == "__main__":
    main()
