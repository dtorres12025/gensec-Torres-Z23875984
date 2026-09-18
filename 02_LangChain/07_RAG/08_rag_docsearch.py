import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import readline

vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(
        model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "google/gemini-embedding-001"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        model_kwargs={"encoding_format": "float"},
        check_embedding_ctx_length=False,
    ),
    persist_directory="./rag_data/.chromadb"
)

def search_db(query):
    docs = vectorstore.similarity_search(query)
    print(f"Query database for: {query}")
    if docs:
        print(f"Closest document match in database: {docs[0].metadata['source']}")
    else:
        print("No matching documents")

print("RAG database initialized.")
retriever = vectorstore.as_retriever()
document_data_sources = set()
for doc_metadata in retriever.vectorstore.get()['metadatas']:
    document_data_sources.add(doc_metadata['source']) 
for doc in document_data_sources:
    print(f"  {doc}")

print("This program queries documents in the RAG database that are similar to whatever is entered.")
while True:
    line = input(">> ")
    if line:
        search_db(line)
    else:
        break
