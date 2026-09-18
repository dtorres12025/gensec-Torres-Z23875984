import os
import requests
import readline
from bs4 import BeautifulSoup
from langchain_openrouter import ChatOpenRouter

def summarize_url(url):
    llm = ChatOpenRouter(model=os.getenv("OPENROUTER_MODEL"), temperature=0)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
    else:
        return "Failed to scrape the website"
    prompt = f"Explain the security issue in the following article: {text}"
    response = llm.invoke(prompt)
    return response


# url = "https://krebsonsecurity.com/2024/02/arrests-in-400m-sim-swap-tied-to-heist-at-ftx/"
print("Welcome to my URL summarizer.  Enter a URL about a security incident and I will summarize the security issue it involves.  A blank line exits.")
while True:
    content = input("llm>> ")
    if content:
        result = summarize_url(content)
        print(result.content)
    else:
        break
