# Building a Knowledge Graph from Textbooks using NLP
 
An end-to-end NLP pipeline that extracts domain concepts from technical textbooks and structures them as a queryable **Knowledge Graph** — built without LLMs, using only classical NLP and graph algorithms.
 
---
 
## The Problem
 
Textbooks hold rich relational information between concepts, but students have no way to navigate it structurally. 
A student reading about *backpropagation* doesn't know what they need to understand first, or how it connects to everything else in the chapter. This project makes those connections explicit and queryable.
 
---
 
## What It Actually Does
 
This pipeline takes raw textbook PDF pages and produces an interactive knowledge graph where nodes are domain concepts and edges represent co-occurrence relationships — with a small subset enriched by semantic dependency parsing.
 
```
PDF pages (OCR)
      │
      ▼
Sentence extraction
      │
      ▼
Concept extraction (spaCy noun chunks + filtering)
      │
      ▼
Co-occurrence graph (top concepts per chapter)
      │
      ▼
Merged multi-chapter graph
      │
      ▼
Graph algorithms (PageRank, communities, shortest path)
      │
      ▼
Visualization (full graph + ego graphs per concept)
```
 
---
 
## Design Decisions & What I Learned
 
This notebook documents the full development journey — every dead end included. Here's what I tried and why I made each decision:
 
### Concept Extraction
 
**Why not spaCy's default NER?**
spaCy's `en_core_web_sm` is trained on news data — it labeled *"integer degrees"* as `PERSON`. Academic concepts are common nouns, not proper nouns. Default NER is the wrong tool.
 
**Why noun chunks over individual tokens?**
Tokens give you `"logic"` and `"circuit"` separately. Noun chunks give you `"logic circuit"` as one unit — which is the actual concept.
 
**Why not TextRank?**
I tested TextRank and compared it against noun chunks. TextRank captured richer multi-word phrases and importance scores, but missed page-level tracking and introduced more noise from modifiers. Noun chunks with custom filtering gave more consistent results for this use case. Both are implemented in the notebook for comparison and could be a valid addition with further work done in it.
 
**Filtering pipeline:**
Three layers of pruning keep concept candidates clean:
- `BOOK_STRUCTURE` — drops textbook metadata (*chapter, figure, table*)
- `GENERIC_TERMS` — drops non-specific words (*type, value, result*)
- `SINGLE_WORD_GENERIC` — drops standalone ambiguous nouns (*computer, system*)
 
### Relation Extraction
 
I implemented and tested two approaches:
 
**Bootstrapping** — find sentences where two known concepts co-occur, extract text between them, count repeating patterns. In theory this surfaces relations like `"is a"`, `"converts to"` automatically. In practice, a single chapter doesn't have enough repeated concept pairs for reliable pattern frequencies. OCR noise compounds the problem.
 
**Dependency parsing** — extract subject-verb-object triples from grammatical structure. This works on clean sentences and produces semantic labels (`IS_A`, `REQUIRES`, `PART_OF`). But it requires both concepts to appear together in a direct grammatical relationship in the same sentence — rare with top concepts in one chapter.
 
**What I used in the final graph:** Co-occurrence edges with semantic enrichment where dependency parsing finds a direct relationship. In practice, we drop the semantic enrichment for further work because only ~1% of the edges could be enriched, further work to be done.
 
### Graph Construction
 
**Why not use all concepts as nodes?**
With 1647 concept candidates and only 277 triples, 75% of nodes were isolated — no edges. A graph you can't traverse isn't useful.
 
**The fix — co-occurrence on top concepts:**
Keep only the top N concepts per chapter. Connect any two that appear in the same sentence. This trades semantic precision for connectivity — the result is a navigable graph.
 
**The honest tradeoff:**
> "We just threw away our relationships so our edges are just connections without semantic meaning and precision." — notebook, cell 72
 
It's a limitation, not a bug.
 
---
 
## Results
 
**Per-chapter graphs** capture domain-specific vocabulary automatically:
- Chapter 1 (Digital Systems) → binary number, hexadecimal, abstraction
- Chapter 2 (Boolean Algebra) → boolean function, k-map, prime implicant
- Chapter 3 (Combinational Circuits) → full adder, multiplexer, 2s complement
 
**Merged graph** (3 chapters): 125 nodes, 1388 edges, 97% connected.
 
**Cross-chapter concepts** (appear in all chapters) = foundational concepts a student should learn first:
```
circuit, design, input, case
```
 
**PageRank** identifies the most central concepts per chapter without any manual annotation.
 
**Ego graphs** show a concept's immediate neighborhood — the student-facing view that makes the graph navigable.
 
---
 
## Tech Stack
 
| Component | Library |
|---|---|
| OCR | pytesseract + Pillow |
| NLP | spaCy (en_core_web_sm) |
| Concept ranking (tested) | pytextrank |
| Graph construction | NetworkX |
| Visualization | matplotlib, pyvis |
 
---
 
## Limitations
 
- **OCR quality** — publisher PDFs use custom font encoding. The text layer is corrupted, so OCR is required. This introduces noise that propagates through every downstream step.
- **Co-occurrence edges** — edges mean "these concepts appeared in the same sentence", not "these concepts are semantically related".
- **Single domain** — tested on one Digital Systems textbook. Filtering parameters (generic terms, book structure words) may need adjustment for other domains.
- **Chapter size** — bootstrapping relation extraction requires more text than one chapter provides for reliable pattern frequency.
 
---
 
## What's Next
 
- [ ] **Clean PDF** — rerun on a properly encoded PDF (OpenStax) to measure improvement in semantic edge count
- [ ] **Semantic labeling** — complement the co-currence graph with extracted relationships (ideally only relationship will connect concepts) 
- [ ] **Graph RAG** — connect to an LLM to answer student queries grounded in graph paths, not hallucinated prerequisites
- [ ] **Streamlit app** — upload PDF → explore graph → query learning paths
- [ ] **Heading extraction** — use TOC pages as high-confidence anchor nodes
- [ ] **Coreference resolution** — resolve "it", "this circuit" to the right concept node
- [ ] **Neo4j** — replace NetworkX with a persistent graph database for production scale
 












