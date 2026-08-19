# GenQuantaa Calling Agent — Knowledge Base & Vector RAG Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document specifies the end-to-end Knowledge Base document ingestion, Docling hybrid chunking, OpenAI vector embedding generation, PostgreSQL 17 `pgvector` IVFFlat search, and voice conversation context injection pipeline.

---

## 2. Ingestion & Retrieval Pipeline

```
[ User Document Upload ]
           │
           │ PDF / DOCX / TXT / MD
           ▼
┌────────────────────────────────────────────────────────┐
│  MinIO Storage (`genquantaa-voice-audio`)              │
│  - Path: `knowledge_base/{org_id}/{doc_uuid}/file`     │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Document Parsing & Hybrid Chunker
                         ▼
┌────────────────────────────────────────────────────────┐
│  OpenAI Embedding API (`text-embedding-3-small`)       │
│  - Generates 1,536-dimensional float vector            │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Batch Vector Insert
                         ▼
┌────────────────────────────────────────────────────────┐
│  PostgreSQL 17 Database (`knowledge_base_chunks`)      │
│  - Column: `embedding vector(1536)`                    │
│  - Index: `IVFFlat` (`vector_cosine_ops`, `lists=100`) │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Vector Search (Filtered by `organization_id`)
                         ▼
┌────────────────────────────────────────────────────────┐
│  Voice Agent LLM Context Ingestion                     │
│  - Top-5 context chunks appended to LLM system prompt  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Ownership Classification Matrix

- **GENQUANTAA OWNED:** `KnowledgeBaseClient` (`api/db/knowledge_base_client.py`), `knowledge_base_documents` schema, `knowledge_base_chunks` schema, MinIO document storage, server-side multi-tenant query filtering.
- **VECTOR DATABASE:** PostgreSQL 17 + `pgvector` extension.
- **EMBEDDING PROVIDERS:** OpenAI (`text-embedding-3-small`), HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`).
