# poetic_ontology_builder/builder.py
from .utils import extract_triplets_gemini, build_ontology, export_ontology, visualize_graph_interactive

class PoeticBuilder:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir

    def build(self, text_path):
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
        triplets = extract_triplets_gemini(text)
        if not triplets:
            print("No triplets extracted. Exiting.")
            return
        ontology = build_ontology(triplets)
        owl_path = f"{self.output_dir}/sublime_graph.owl"
        html_path = f"{self.output_dir}/sublime_graph.html"
        export_ontology(ontology, filename=owl_path)
        visualize_graph_interactive(triplets, filename=html_path)
        print(f"Ontology: {owl_path}\nGraph: {html_path}")
