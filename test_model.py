import os
from langchain_google_genai import ChatGoogleGenerativeAI

print("Testing model connection...")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    print(llm.invoke("Hi").content)
    print("gemini-1.5-flash works!")
except Exception as e:
    print(f"Error with gemini-1.5-flash: {e}")

try:
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash")
    print(llm.invoke("Hi").content)
    print("models/gemini-1.5-flash works!")
except Exception as e:
    print(f"Error with models/gemini-1.5-flash: {e}")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
    print(llm.invoke("Hi").content)
    print("gemini-1.5-flash-latest works!")
except Exception as e:
    print(f"Error with gemini-1.5-flash-latest: {e}")
