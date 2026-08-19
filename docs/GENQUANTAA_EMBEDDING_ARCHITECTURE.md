# GenQuantaa Calling Agent — Embedding & Vector Index Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Provider Specification  

---

## 1. Supported Embedding Models

| Embedding Provider | Model Name | Dimensions | Vector Distance Metric | PostgreSQL Index Type | Production Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **OpenAI** | `text-embedding-3-small` | 1,536 | Cosine (`vector_cosine_ops`) | `IVFFlat` (`lists=100`) | PRIMARY / ACTIVE |
| **OpenAI** | `text-embedding-3-large` | 3,072 | Cosine | `IVFFlat` | Supported |
| **SentenceTransformers** | `all-MiniLM-L6-v2` | 384 | Cosine | `IVFFlat` | Supported (Local) |

---

## 2. Multi-Tenant Server-Side Scoping

Vector search queries execute directly against `knowledge_base_chunks` with mandatory server-side WHERE clauses:

```sql
SELECT c.id, c.chunk_text, 1 - (c.embedding <=> $1::vector) as similarity
FROM knowledge_base_chunks c
JOIN knowledge_base_documents d ON c.document_id = d.id
WHERE c.organization_id = $2 AND d.is_active = true
ORDER BY c.embedding <=> $1::vector
LIMIT $3;
```
