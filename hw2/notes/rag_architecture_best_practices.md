---
title: RAG Architecture and Retrieval Best Practices
tags: [rag, langchain, lcel, vectorstore, embeddings]
category: architecture
author: COT5930 Engineering Team
---

# RAG Architecture and Retrieval Best Practices

Retrieval-Augmented Generation (RAG) grounds language models by dynamically retrieving relevant facts from an external knowledge store before generating a response.

## Core RAG Pipeline Components

### Document Ingestion and Chunking
Document parsing transforms raw files into retrievable chunks:
- **Chunk Size and Overlap:** A chunk size between 500 and 1,000 characters with 10% to 20% overlap balances semantic completeness with retriever precision.
- **Header and Metadata Preservation:** Extracting document titles, section headers, and taxonomy tags ensures the retriever retains critical structural context.

### Vector Embeddings and Indexing
- Dense vector representations capture semantic meaning across high-dimensional spaces.
- Models like Google Gemini Embeddings (`gemini-embedding-001`) generate high-dimensional vectors (e.g., 3072 dimensions) for granular distance and cosine similarity matching.
- Vector stores like Chroma persist embeddings locally with metadata indexing.

## LangChain Expression Language (LCEL)

Modern LangChain architectures utilize LCEL to build declarative, streaming-ready chains:
- **Runnables:** Standardized interfaces across all components (`invoke`, `batch`, `stream`).
- **Composition:** Pipe operators (`|`) seamlessly chain retrievers, prompt templates, language models, and output parsers.
- **Context Injection:** `RunnablePassthrough` allows parallel dictionary routing of context documents and the user's raw query into prompt slots.
