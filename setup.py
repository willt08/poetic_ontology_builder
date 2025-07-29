from setuptools import setup, find_packages

setup(
    name="poetic_ontology_builder",
    version="1.0.1",
    description="A tool for generating ontological knowledge graphs with emotional embeddings from text.",
    author="Willinton Triana Cardona",
    author_email="",
    url="https://huggingface.co/willt-dc/Rosa-V1",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.32.0",
        "torch>=2.0.0",
        "matplotlib",
        "pyvis",
        "owlready2",
        "python-dotenv",
        "google-generativeai",
    ],
    entry_points={
        "console_scripts": [
            "poetic-ontology=poetic_ontology_builder.cli:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
)
