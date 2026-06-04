# Automated Textbook Knowledge Graph Extraction Pipeline

An end-to-end Natural Language Processing (NLP) pipeline designed to extract structured domain concepts, semantic relationships, and hierarchical structural layout data from technical textbooks
, converting unstructured text into a queryable, localized **Knowledge Graph**.

## Project Overview
Textbooks hold rich structural, hierarchical, and relational information, but extracting this data manually to map a domain curriculum is incredibly labor-intensive. This project provides a programmatic solution by feeding raw textbook documents through an multi-stage layout extraction and NLP processing pipeline.

**Core Design Choice:** This pipeline intentionally avoids relying on Large Language Models (LLMs) for the foundational entity and relationship extraction phases. Instead, it prioritizes a localized, deterministic, and highly compute-efficient NLP approach. This allows for total control over the parsing rules, zero API dependency costs, and predictable execution speeds. The pipeline implements and contrasts dual entity mining strategies (**Rule-Based Noun Chunking** vs. **Graph-Based TextRank**) and extracts semantic dependencies to construct directed relationship maps.

---

## Tech Stack & Key Libraries
* **Document Ingestion & OCR:** `PyMuPDF (fitz)` (text layout metadata analysis), `pytesseract` (Tesseract OCR fallback for scanned materials), and `Pillow (PIL)`.
* **Core NLP Framework:** `spaCy (en_core_web_sm)` (Tokenization, Lemmatization, Part-of-Speech Tagging, Syntactic Parsing).
* **Graph-based Extraction:** `pytextrank` (Network-based phrase ranking and importance metrics).
* **Graph Representation & Visualization:** `NetworkX` (Directed multi-node graphs) and `spaCy.displacy` (dependency parsing visual traces).

---

## Architecture & Pipeline Workflows

### 1. Document Ingestion & Font-Size Heuristics
* Parses document text blocks along with precise metadata (bounding boxes, font face, and **font size**).
* Filters and captures multi-level structural elements like headers, chapter topics, and section definitions using font-size layout markers.

### 2. Iterative Concept Mining & Custom Filtering
Standard Named Entity Recognition (NER) models frequently fail to extract niche, domain-specific hardware and software concepts (e.g., *digital circuits*, *logic gates*, *hexadecimal conversion*). To bypass this, this pipeline maps and validates **Noun Chunks** using a rule-driven cleanup architecture:
* **`clean_chunk()`:** Discards structural determiner prefixes (*the, an, this, those*).
* **Vocabulary Stop-Lists:** Utilizes three layers of programmatic pruning configurations:
    * `BOOK_STRUCTURE`: Strips metadata text (*chapter, appendix, section, table*).
    * `GENERIC_TERMS`: Removes structural words (*type, kind, value, example, result*).
    * `SINGLE_WORD_GENERIC`: Eliminates standalone non-differentiated phrases (*computer, system, range*).

### 3. Concept Strategy Evaluation: Noun Chunks vs. TextRank
The pipeline extracts candidate concepts using two decoupled approaches to contrast precision against coverage:
* **Noun Chunking:** Yields high-precision local concepts, maps them down to exact page numbers, and filters specific multi-word tokens cleanly.
* **PyTextRank Extension:** Applies graph-based ranking directly to the document co-occurrence network, computing global structural importance scores (`phrase.rank`) for entities across text boundaries.

### 4. Semantic Relation Extraction
To map edges between concepts, the pipeline implements two separate extraction methodologies:
* **Bootstrapped String-Patterns:** Scans sentences containing target concept pairs, analyzes text spans matching regular expressions (`rf'\b{base}(?:s|es|ed|ing)?\b'`), and counts bridging phrase patterns.
* **Syntactic Dependency Parsing:** Evaluates the token-level structure. By querying dependency tags (looking for `nsubj`/`nsubjpass` dependencies on the left, and traversing paths through `VERB` and `AUX` tokens to target objects), it programmatically extracts context-rich verbs.
* **`RELATION_MAP` Mapping:** Standardizes extracted actions into deterministic global edge properties (`IS_A`, `PART_OF`, `USES`, `REQUIRES`).

### 5. Graph Assembly (`NetworkX`)
Compiles the valid concept nodes (decorated with `count` and unique `pages` metadata) and semantic directed relation triples (`Subject -> Relation -> Object`) into a NetworkX `DiGraph` instance for topological analysis.

## Future Roadmap
- [ ] **UI & Scalability**: Build an interactive frontend using Streamlit and transition the NetworkX data layer into a scalable Neo4j graph database.

- [ ] **Graph-RAG & LLMs**: Link an LLM via LangChain to trace multi-hop relationship paths between concepts and serve as a factual, hallucination-free student chatbot.

- [ ] **Student Application**: Deploy a student-facing interface featuring personalized curriculum mapping and prerequisite concept tracking based on directed edges.

- [ ] **Advanced NLP**: Integrate neural Coreference Resolution models (fastcoref) to resolve ambiguous pronouns ("it", "this circuit") and capture missing graph links.
