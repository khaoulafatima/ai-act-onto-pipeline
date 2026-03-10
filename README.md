# AI-Assisted Ontology Construction Pipeline for the EU AI Act
An AI-assisted pipeline for constructing a semantic web ontology from the EU AI Act 


This repository contains a proof-of-concept ontology modelling key concepts of the **European Union Artificial Intelligence Act (EU AI Act)**. The ontology was constructed from the official legal text using a pipeline that combines **Python preprocessing** and **Large Language Model (LLM)-assisted ontology extraction and generation**.

The process includes extracting relevant concepts such as AI system categories, actors (e.g., providers, deployers), obligations, authorities, prohibited AI practices, and regulatory artefacts, and representing them formally in **OWL using the Turtle syntax**.

The repository contains:

- the **Python scripts** used to preprocess and segment the EU AI Act text,
- the **prompts** used to extract ontology elements and generate the ontology with an LLM,
- the resulting **EU AI Act ontology (.ttl)**,
- **competency questions and SPARQL queries** used to evaluate the ontology,

The ontology aims to provide a structured semantic representation of the EU AI Act that can support legal knowledge representation, querying, and further research in AI regulation.
