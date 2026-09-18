import os
import readline
import math
import numpy
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "google/gemini-embedding-001"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    # Google AI Studio's OpenRouter embeddings route rejects the openai SDK's
    # default base64 encoding_format, and rejects LangChain's default of sending
    # pre-tokenized integer inputs. Force float output and disable tokenization.
    model_kwargs={"encoding_format": "float"},
    check_embedding_ctx_length=False,
)
base_string = "The quick brown fox"
base_vector = embeddings.embed_query(base_string)

def calculate(test_string):
    test_vector = embeddings.embed_query(test_string)
    euclidean_distance = math.sqrt(sum((x - y) ** 2 for x, y in zip(base_vector, test_vector)))
    print(f"Euclidean distance is: {euclidean_distance}")
    cosine = cosine_similarity([base_vector],[test_vector])
    print(f"Cosine distance is: {1-cosine[0][0]}")

print('''Welcome to my embedding application.  Type a phrase and I will create an embedding for it and output its euclidean and cosine distances away from the text "The quick brown fox"''')
while True:
    line = input(">> ")
    if line:
        calculate(line)
    else:
        break
