from setuptools import setup, find_packages

setup(
    name="poetic_ontology_builder",
    version="1.1.0",
    description="A tool for generating ontological knowledge graphs with emotional embeddings from text.",
    author="Willinton Triana Cardona",
    author_email="",
    url="https://huggingface.co/willt-dc/Rosa-V1",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.46.0",
        "torch>=2.0.0",
        "matplotlib>=3.8.0",
        "pyvis>=0.3.2",
        "numpy>=1.24.0",
        "owlready2",
        "python-dotenv",
        "google-generativeai>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "poetic-ontology=poetic_ontology_builder.cli:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.10",
)
