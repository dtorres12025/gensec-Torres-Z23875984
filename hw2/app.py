import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Assert GOOGLE_API_KEY is present
assert os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"), (
    "GOOGLE_API_KEY environment variable is not set."
)

# LangChain LCEL & Core Components
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Google GenAI & Vector Store Components
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Paths configuration
BASE_DIR = Path(__file__).resolve().parent
PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / ".chromadb"))
DATA_DIRECTORY = BASE_DIR.parent / "02_LangChain" / "07_RAG" / "rag_data" / "txt"


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
    Load text files from directory, split into chunks, and store in vector database.
    """
    if not data_path.exists():
        return 0

    loader = DirectoryLoader(str(data_path), glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    if not documents:
        return 0

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    vectorstore.add_documents(chunks)
    return len(chunks)


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

    # Seed with sample data if the vector database is currently empty
    existing_count = vectorstore._collection.count()
    if existing_count == 0 and DATA_DIRECTORY.exists():
        print(f"Vector store is empty. Ingesting documents from {DATA_DIRECTORY}...")
        count = ingest_documents(DATA_DIRECTORY, vectorstore)
        print(f"Successfully indexed {count} document chunks.")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    rag_chain = build_rag_chain(retriever)

    print("Welcome to my RAG application. Ask me a question and I will answer it from the documents in my database shown below")
    
    # Retrieve and display unique document sources
    collection_data = vectorstore.get()
    document_data_sources = set()
    if collection_data and collection_data.get("metadatas"):
        for doc_metadata in collection_data["metadatas"]:
            if doc_metadata and "source" in doc_metadata:
                document_data_sources.add(doc_metadata["source"])

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
