from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from typing import Iterator, List, Optional, Union
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Assert GOOGLE_API_KEY is present
assert os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"), (
    "GOOGLE_API_KEY environment variable is not set."
)

# LangChain Core & Loader Base
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
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
BASE_DIR = Path(__file__).resolve().parent
PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / ".chromadb"))
NOTES_DIRECTORY = BASE_DIR / "notes"
RAG_DATA_DIRECTORY = BASE_DIR.parent / "02_LangChain" / "07_RAG" / "rag_data" / "txt"


class CustomNoteLoader(BaseLoader):
    """
    Custom document loader for text (.txt) and markdown (.md) files.
    Inherits from langchain_community.document_loaders.base.BaseLoader.
    Parses titles, headers, and metadata tags into Document metadata,
    and chunks the text into standard LangChain Document objects.
    """

    def __init__(
        self,
        directory_path: str | Path,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        glob_pattern: str = "**/*",
    ):
        self.directory_path = Path(directory_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.glob_pattern = glob_pattern
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def _parse_file(self, file_path: Path) -> List[Document]:
        """Parse a single file, extract structural metadata, and chunk into Documents."""
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
        """Lazy load documents from directory matching text and markdown extensions."""
        if not self.directory_path.exists():
            return

        supported_extensions = {".md", ".txt"}
        for file_path in sorted(self.directory_path.glob(self.glob_pattern)):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                for doc in self._parse_file(file_path):
                    yield doc

    def load(self) -> List[Document]:
        """Eagerly load and chunk all notes into a list of Document objects."""
        return list(self.lazy_load())


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    """Initialize and return Google Gemini embedding model."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001"),
        google_api_key=api_key,
    )


def get_vectorstore(persist_directory: str = PERSIST_DIRECTORY) -> Chroma:
    """Initialize or load the Chroma vector database."""
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=get_embedding_function()
    )


def ingest_documents(data_path: Path, vectorstore: Chroma) -> int:
    """
    Load documents from directory using CustomNoteLoader, chunk, and store in vector database.
    """
    if not data_path.exists():
        return 0

    loader = CustomNoteLoader(data_path)
    documents = loader.load()
    if not documents:
        return 0

    vectorstore.add_documents(documents)
    return len(documents)


def format_docs(docs):
    """Format retrieved documents for prompt context."""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(retriever, llm=None):
    """
    Construct the modern LangChain Expression Language (LCEL) RAG chain.
    Chain structure:
      Input (question) -> {context, question} -> Prompt -> LLM -> StrOutputParser
    """
    if llm is None:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "models/gemini-3.6-flash"),
            google_api_key=api_key,
            temperature=0,
        )

    # Standard RAG Prompt Template (equivalent to rlm/rag-prompt)
    rag_prompt = ChatPromptTemplate.from_template(
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Use three sentences maximum and keep the answer concise.\n\n"
        "Question: {question}\n\n"
        "Context: {context}\n\n"
        "Answer:"
    )

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def main():
    """Main execution loop for interactive RAG querying."""
    print("Initializing RAG vector database with Google Gemini...")
    vectorstore = get_vectorstore()

    # Determine primary notes directory or fallback
    target_dir = NOTES_DIRECTORY if NOTES_DIRECTORY.exists() else RAG_DATA_DIRECTORY

    # Seed with sample data if the vector database is currently empty
    existing_count = vectorstore._collection.count()
    if existing_count == 0 and target_dir.exists():
        print(f"Vector store is empty. Ingesting documents from {target_dir}...")
        count = ingest_documents(target_dir, vectorstore)
        print(f"Successfully indexed {count} document chunks.")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    rag_chain = build_rag_chain(retriever)

    print("Welcome to my RAG application. Ask me a question and I will answer it from the documents in my database shown below")
    
    # Retrieve and display unique document sources and metadata
    collection_data = vectorstore.get()
    document_data_sources = set()
    if collection_data and collection_data.get("metadatas"):
        for doc_metadata in collection_data["metadatas"]:
            if doc_metadata and "source" in doc_metadata:
                title = doc_metadata.get("title", "")
                source_display = doc_metadata["source"]
                if title:
                    source_display += f" (Title: {title})"
                document_data_sources.add(source_display)

    if document_data_sources:
        for source in sorted(document_data_sources):
            print(f"  {source}")
    else:
        print("  (No documents currently indexed)")

    print("\nEnter your question (press Enter or Ctrl+C to exit):")
    while True:
        try:
            line = input("llm>> ").strip()
            if not line:
                break
            result = rag_chain.invoke(line)
            print(result)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
