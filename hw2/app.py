"""RAG Question Answering System with Google Gemini and Chroma.

This module provides document loading, vector storage with Chroma,
and a modern LangChain Expression Language (LCEL) retrieval pipeline
for querying local text and markdown notes with source citations.
"""

from __future__ import annotations

import logging
import os
import re
import sys
import warnings
from pathlib import Path
from typing import Any, Iterator, List, Optional, Union

# Suppress library deprecation and SSL version warnings for clean terminal presentation
warnings.filterwarnings("ignore")
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("langchain_core").setLevel(logging.ERROR)
logging.getLogger("langchain_community").setLevel(logging.ERROR)

from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Assert GOOGLE_API_KEY is present
assert os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"), (
    "GOOGLE_API_KEY environment variable is not set."
)

# LangChain Core & Loader Base
try:
    from langchain_core.document_loaders import BaseLoader
except ImportError:
    from langchain_community.document_loaders.base import BaseLoader

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Google GenAI & Vector Store Components
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

try:
    import yaml
except ImportError:
    yaml = None

# Paths configuration
BASE_DIR: Path = Path(__file__).resolve().parent
PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / ".chromadb"))
NOTES_DIRECTORY: Path = BASE_DIR / "notes"
RAG_DATA_DIRECTORY: Path = BASE_DIR.parent / "02_LangChain" / "07_RAG" / "rag_data" / "txt"

# Standardized fallback message for boundary checks
FALLBACK_MESSAGE: str = (
    "No relevant notes were found in the knowledge base to answer your question."
)


class CustomNoteLoader(BaseLoader):
    """Document loader for parsing and chunking local markdown and text notes.

    Inherits from BaseLoader to scan directories for markdown (.md) and plain
    text (.txt) notes, extracts structured metadata (titles, headers, tags),
    and splits the body text into standard LangChain Document objects.
    """

    def __init__(
        self,
        directory_path: Union[str, Path],
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        glob_pattern: str = "**/*",
    ) -> None:
        """Initialize the CustomNoteLoader with directory and chunking parameters.

        Args:
            directory_path: Filesystem path to directory containing notes.
            chunk_size: Maximum character count per document chunk.
            chunk_overlap: Number of characters to overlap across adjacent chunks.
            glob_pattern: Glob pattern used for recursive file matching.
        """
        self.directory_path: Path = Path(directory_path)
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.glob_pattern: str = glob_pattern
        self.text_splitter: RecursiveCharacterTextSplitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        )

    def _parse_file(self, file_path: Path) -> List[Document]:
        """Parse a single file, extract structural metadata, and chunk into Documents.

        Args:
            file_path: Absolute or relative Path pointing to the note file.

        Returns:
            A list of Document objects with extracted metadata and split text.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Failed to read {file_path}: {e}")
            return []

        title: Optional[str] = None
        tags: List[str] = []
        body = content

        # 1. Parse YAML frontmatter if present
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if fm_match:
            fm_content = fm_match.group(1)
            body = content[fm_match.end() :]
            if yaml:
                try:
                    meta_dict = yaml.safe_load(fm_content)
                    if isinstance(meta_dict, dict):
                        title = meta_dict.get("title")
                        raw_tags = meta_dict.get("tags", [])
                        if isinstance(raw_tags, list):
                            tags.extend([str(t).strip() for t in raw_tags])
                        elif isinstance(raw_tags, str):
                            tags.extend([t.strip() for t in raw_tags.split(",")])
                except Exception:
                    pass

        # 2. Extract title from top header if not found in frontmatter
        header_lines = [
            line.strip()
            for line in body.splitlines()
            if line.strip().startswith("#")
        ]

        if not title:
            for h in header_lines:
                if h.startswith("# "):
                    title = h[2:].strip()
                    break
            if not title:
                title = file_path.stem.replace("_", " ").title()

        # 3. Extract inline hashtags from content (e.g. #security, #rag)
        inline_tags = re.findall(r"(?:^|\s)#([a-zA-Z0-9_\-]+)", body)
        for t in inline_tags:
            if t.lower() not in [tag.lower() for tag in tags]:
                tags.append(t)

        # 4. Format headers and tags as strings for Chroma vectorstore compatibility
        headers_str = "; ".join(header_lines) if header_lines else ""
        tags_str = ", ".join(tags) if tags else ""

        # 5. Split body into chunks
        chunks = self.text_splitter.split_text(body)
        if not chunks:
            chunks = [body] if body.strip() else []

        documents: List[Document] = []
        for idx, chunk in enumerate(chunks):
            metadata = {
                "source": str(file_path.resolve()),
                "filename": file_path.name,
                "title": str(title),
                "headers": headers_str,
                "tags": tags_str,
                "file_type": file_path.suffix.lower(),
                "chunk_index": idx,
                "total_chunks": len(chunks),
            }
            documents.append(Document(page_content=chunk, metadata=metadata))

        return documents

    def lazy_load(self) -> Iterator[Document]:
        """Lazily parse and yield Document chunks from supported files in the directory.

        Yields:
            Document: Each split document chunk with enriched metadata.
        """
        if not self.directory_path.exists():
            return

        supported_extensions = {".md", ".txt"}
        for file_path in sorted(self.directory_path.glob(self.glob_pattern)):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                for doc in self._parse_file(file_path):
                    yield doc

    def load(self) -> List[Document]:
        """Eagerly load and chunk all notes into a list of Document objects.

        Returns:
            List of all generated Document chunks across all parsed files.
        """
        return list(self.lazy_load())


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    """Initialize and return the Google Gemini embedding model.

    Returns:
        Configured GoogleGenerativeAIEmbeddings instance using gemini-embedding-001.

    Raises:
        AssertionError: If neither GOOGLE_API_KEY nor GEMINI_API_KEY is in the environment.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    assert api_key, "Google API key is required to initialize embeddings."
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001"),
        google_api_key=api_key,
    )


def get_vectorstore(persist_directory: str = PERSIST_DIRECTORY) -> Chroma:
    """Initialize or load the local Chroma vector database.

    Args:
        persist_directory: Directory path where Chroma database files are stored.

    Returns:
        An active Chroma vectorstore instance connected to the persistent directory.
    """
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=get_embedding_function(),
    )


def ingest_documents(data_path: Path, vectorstore: Chroma) -> int:
    """Load notes using CustomNoteLoader and store them in the Chroma vector database.

    Args:
        data_path: Directory path containing the source notes.
        vectorstore: Target Chroma vectorstore instance for document storage.

    Returns:
        Integer count of total document chunks successfully indexed.
    """
    if not data_path.exists():
        return 0

    loader = CustomNoteLoader(data_path)
    documents = loader.load()
    if not documents:
        return 0

    vectorstore.add_documents(documents)
    return len(documents)


def reindex_knowledge_base(target_dir: Path, vectorstore: Chroma) -> int:
    """Reset and re-index all notes from target directory into the Chroma collection.

    Args:
        target_dir: Directory containing Markdown or text notes.
        vectorstore: Target Chroma vectorstore instance.

    Returns:
        Integer count of document chunks newly indexed.
    """
    existing_data = vectorstore.get()
    existing_ids = existing_data.get("ids", []) if existing_data else []
    if existing_ids:
        vectorstore.delete(ids=existing_ids)
    return ingest_documents(target_dir, vectorstore)


def format_docs(docs: List[Document]) -> str:
    """Format retrieved documents with structured metadata for citation generation.

    Args:
        docs: List of retrieved Document objects from vectorstore search.

    Returns:
        A formatted string containing labeled document metadata and content blocks.
    """
    formatted_pieces = []
    for i, doc in enumerate(docs, 1):
        filename = doc.metadata.get("filename", "unknown_source")
        title = doc.metadata.get("title", "Untitled Section")
        chunk_idx = doc.metadata.get("chunk_index", 0)
        formatted_pieces.append(
            f"[Document {i}]\n"
            f"Filename: {filename}\n"
            f"Section Title: {title}\n"
            f"Chunk Index: {chunk_idx}\n"
            f"Content:\n{doc.page_content.strip()}"
        )
    return "\n\n".join(formatted_pieces)


def build_rag_chain(retriever: Any, llm: Optional[Any] = None) -> Any:
    """Construct the modern LCEL RAG chain with boundary checks and citation formatting.

    Implements programmatic boundary checks: if the retriever returns zero
    relevant documents (e.g. falling below the similarity score threshold),
    the chain immediately routes to FALLBACK_MESSAGE without calling the LLM.

    Args:
        retriever: Vectorstore retriever instance for document search.
        llm: Optional language model instance; defaults to ChatGoogleGenerativeAI.

    Returns:
        A compiled LCEL Runnable chain capable of processing queries with boundary checks.
    """
    if llm is None:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "models/gemini-3.6-flash"),
            google_api_key=api_key,
            temperature=0,
        )

    rag_prompt = ChatPromptTemplate.from_template(
        "You are an assistant for question-answering tasks over reference notes.\n"
        "Use the following retrieved context documents to answer the user's question.\n\n"
        "Instructions:\n"
        "1. Synthesize a comprehensive, accurate, and direct answer based strictly on the provided context.\n"
        "2. At the end of your answer, provide a dedicated 'Sources:' section with clear, numbered citations.\n"
        "3. Each citation must strictly list the source note filename, section title, and chunk index corresponding to the document(s) used.\n"
        "   Example format:\n"
        "   Sources:\n"
        "   1. generative_security_intro.md - Introduction to Generative AI Security (Chunk 0)\n"
        "   2. rag_architecture_best_practices.md - RAG Architecture and Retrieval Best Practices (Chunk 1)\n"
        "4. If the context does not contain enough information to answer the question, or if the question is outside the scope of the notes, respond strictly with:\n"
        f"'{FALLBACK_MESSAGE}'\n"
        "Do not hallucinate facts or invent sources.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    # Core generation chain when valid context is present
    generation_chain = (
        RunnablePassthrough.assign(context=lambda x: format_docs(x["raw_docs"]))
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    # Retrieval step that captures raw documents for boundary inspection
    def retrieve_with_boundary_check(question: str) -> dict:
        """Retrieve documents and package them with the original question."""
        docs = retriever.invoke(question)
        return {"question": question, "raw_docs": docs}

    # Branching: if raw_docs is empty, return FALLBACK_MESSAGE directly
    rag_chain = (
        RunnableLambda(retrieve_with_boundary_check)
        | RunnableBranch(
            (lambda x: len(x.get("raw_docs", [])) == 0, lambda _: FALLBACK_MESSAGE),
            generation_chain,
        )
    )

    return rag_chain


def answer_question(question: str, rag_chain: Any) -> str:
    """Execute a question through the RAG chain and apply boundary validation.

    Args:
        question: Natural language question string from the user.
        rag_chain: Compiled LCEL RAG chain.

    Returns:
        Synthesized answer with citations, or the standardized fallback message.
    """
    clean_question = question.strip()
    if not clean_question:
        return FALLBACK_MESSAGE

    try:
        response = rag_chain.invoke(clean_question)
        return response
    except Exception as e:
        return f"Error executing query: {e}"


def main(argv: Optional[List[str]] = None) -> None:
    """Run the CLI application for question answering over local notes.

    Supports interactive query prompt, single query execution via CLI arguments,
    and automatic or manual knowledge base re-indexing (--reindex).

    Args:
        argv: Optional list of command-line argument strings.
    """
    args = argv if argv is not None else sys.argv[1:]

    print("=" * 65)
    print(" COT5930 - Interactive Note QA System (Google Gemini & Chroma)")
    print("=" * 65)
    print(f"Local Persistence (.chromadb): {PERSIST_DIRECTORY}")
    print("Embedding Model: models/gemini-embedding-001")
    print("Language Model:  models/gemini-3.6-flash")
    print("-" * 65)

    vectorstore = get_vectorstore()
    target_dir = NOTES_DIRECTORY if NOTES_DIRECTORY.exists() else RAG_DATA_DIRECTORY

    # Check for manual re-indexing flag
    if "--reindex" in args:
        print(f"Re-indexing knowledge base from {target_dir}...")
        count = reindex_knowledge_base(target_dir, vectorstore)
        print(f"Successfully re-indexed {count} document chunks into .chromadb/.")
        args = [a for a in args if a != "--reindex"]

    # Auto-ingest documents if vector store is currently empty
    existing_count = vectorstore._collection.count()
    if existing_count == 0 and target_dir.exists():
        print(f"Vector store is empty. Ingesting notes from {target_dir}...")
        count = ingest_documents(target_dir, vectorstore)
        print(f"Successfully indexed {count} document chunks into .chromadb/.")

    # Configure retriever with similarity score threshold for boundary checking
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.65, "k": 3},
    )
    rag_chain = build_rag_chain(retriever)

    print("Indexed Knowledge Base Notes:")
    collection_data = vectorstore.get()
    indexed_sources = set()
    if collection_data and collection_data.get("metadatas"):
        for doc_metadata in collection_data["metadatas"]:
            if doc_metadata and "filename" in doc_metadata:
                fn = doc_metadata["filename"]
                title = doc_metadata.get("title", "")
                display = f"{fn} (Title: {title})" if title else fn
                indexed_sources.add(display)

    if indexed_sources:
        for source in sorted(indexed_sources):
            print(f"  * {source}")
    else:
        print("  (No documents currently indexed)")

    print("-" * 65)

    # Single-query execution mode via CLI argument
    if args:
        cli_query = " ".join(args).strip()
        print(f"question>> {cli_query}\n")
        print("Processing question with boundary check...\n")
        result = answer_question(cli_query, rag_chain)
        print("-" * 65)
        print(result)
        print("-" * 65 + "\n")
        return

    # Interactive prompt loop
    print("Enter your question below. (Type 'exit', 'quit', or press Ctrl+C to exit)")
    print("=" * 65 + "\n")

    while True:
        try:
            line = input("question>> ").strip()
            if not line or line.lower() in {"exit", "quit", "q"}:
                print("Goodbye!")
                break

            print("\nProcessing question with boundary check...\n")
            result = answer_question(line, rag_chain)
            print("-" * 65)
            print(result)
            print("-" * 65 + "\n")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
