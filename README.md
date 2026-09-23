# intent-router
Intent Router is a three-tiered hybrid gateway that optimizes LLM workflows by intercepting simple commands. Using regex and a classical ML pipeline (TF-IDF, SVM, spaCy NER), it executes deterministic tasks locally. This bypasses the LLM to reduce latency and save tokens, reserving heavy models strictly for complex queries.
