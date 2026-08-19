# GenQuantaa Calling Agent — Knowledge Base & RAG Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits the Knowledge Base ingestion pipeline, document chunking, vector embedding generation, PostgreSQL `pgvector` IVFFlat vector indexing, cosine similarity search, and multi-tenant isolation in GenQuantaa Calling Agent.

---

## 2. RAG System Components

- **Database Client:** `api/db/knowledge_base_client.py` (`KnowledgeBaseClient`)
- **API Endpoint:** `/api/v1/knowledge-base/*` (`api/routes/knowledge_base.py`)
- **Storage Layer:** MinIO object storage (`genquantaa-voice-audio` bucket)
- **Vector Database:** PostgreSQL 17 + `pgvector` extension
- **Embedding Models:** OpenAI `text-embedding-3-small` (1,536-dim) & HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (384-dim).

---

## 3. Database Schema Audit

### 3.1 `knowledge_base_documents` Table
- `id` (BigInteger, Primary Key)
- `document_uuid` (UUID string, Unique, Indexed)
- `organization_id` (Integer, Foreign Key -> `organizations.id`, Indexed)
- `created_by` (Integer, Foreign Key -> `users.id`)
- `filename`, `file_size_bytes`, `file_hash`, `mime_type`
- `retrieval_mode` (`chunked` or `full_document`)
- `full_text` (Text content for full document mode)
- `processing_status` (`pending`, `processing`, `completed`, `failed`)

### 3.2 `knowledge_base_chunks` Table
- `id` (BigInteger, Primary Key)
- `document_id` (Integer, Foreign Key -> `knowledge_base_documents.id`, OnDelete CASCADE)
- `organization_id` (Integer, Foreign Key -> `organizations.id`, Indexed)
- `chunk_text` (Text)
- `contextualized_text` (Enriched text chunk)
- `chunk_index` (Integer)
- `embedding_model` (String(200))
- `embedding_dimension` (Integer)
- `embedding` (`Vector(1536)` column with `IVFFlat` vector index using `vector_cosine_ops`)
