import os
import readline
from langchain_classic import hub
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openrouter import ChatOpenRouter
from langchain_openai import OpenAIEmbeddings
import chainlit as cl

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

@cl.on_chat_start
async def on_chat_start():
    logo = cl.Image(name="logo", display="inline", url="https://codelabs.cs.pdx.edu/images/pdx-cs-logo.png")
    await cl.Message(content="", elements=[logo]).send()

    welcome_text = (
        "**Welcome to the PSU Generative Security Chatbot!**\n\n"
        "Ask me anything from my set of documents.\n\n"
    )
    await cl.Message(content=welcome_text).send()

@cl.on_message
async def on_message(message: cl.Message):
    user_query = message.content
    answer = rag_chain.invoke(user_query)
    await cl.Message(content=answer).send()

