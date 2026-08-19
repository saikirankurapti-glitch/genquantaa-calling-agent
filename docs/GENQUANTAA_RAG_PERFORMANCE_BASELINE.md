# GenQuantaa Calling Agent — RAG Performance Baseline

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Baseline Measurement  

---

## 1. Subsystem Performance Latency

- **Document Parsing (Docling 10-page PDF):** ~800 ms – 1,500 ms
- **Embedding Generation (OpenAI batch 20 chunks):** ~120 ms – 250 ms
- **pgvector IVFFlat Cosine Query (Top-5):** ~15 ms – 45 ms
- **End-to-End Context Assembly:** ~35 ms – 75 ms
