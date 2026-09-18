import os
import readline
from langchain_classic import hub
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openrouter import ChatOpenRouter
from langchain_openai import OpenAIEmbeddings
llm = ChatOpenRouter(model=os.getenv("OPENROUTER_MODEL"))

vectorstore = Chroma(
     persist_directory="./rag_data/.chromadb",
     embedding_function=OpenAIEmbeddings(
         model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "google/gemini-embedding-001"),
         openai_api_key=os.getenv("OPENROUTER_API_KEY"),
         openai_api_base="https://openrouter.ai/api/v1",
         model_kwargs={"encoding_format": "float"},
         check_embedding_ctx_length=False,
     )
)

retriever = vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("Welcome to my RAG application.  Ask me a question and I will answer it from the documents in my database shown below")
# Iterate over documents and dump metadata
document_data_sources = set()
for doc_metadata in retriever.vectorstore.get()['metadatas']:
    document_data_sources.add(doc_metadata['source']) 
for doc in document_data_sources:
    print(f"  {doc}")

while True:
    line = input("llm>> ")
    if line:
        result = rag_chain.invoke(line)
        print(result)
    else:
        break
