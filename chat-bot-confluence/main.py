from chunker import load_and_chunk_docs
from faiss_vector import build_faiss_index
from query import query_index
from pathlib import Path
import json
import llm_service
import requests

file_path = Path('all_chunks.json')

if file_path.exists() and file_path.stat().st_size > 0:
    chunks = json.loads(file_path.read_text(encoding="utf-8"))
else :
    chunks = load_and_chunk_docs()
    print("🔢 Building FAISS index...")
    build_faiss_index(chunks)

import google.generativeai as genai

system_message = ("You are a helpful assistant that answers based on provided context. \
    With the given context frame a very concise informative answer and provide with the link for more details. \
    Bring the context of evalueweb web it is asked about web development. Only use the provided context if it directly answers the user’s question. If the query is small talk continue without context \
    ")


def chat(message, history, model):
    # Convert conversation into Gemini's expected format
    messages = []


    if model=='gemini-2.0-flash':
        for user_message, assistant_message in history:
            messages.append({"role": "user", "parts": [{"text": user_message}]})
            messages.append({"role": "model", "parts": [{"text": assistant_message}]})
        messages.append({"role": "user", "parts": [{"text": query_index(message, chunks)}]})
        # Configure API key
        genai.configure(api_key="AIzaSyDAX14bCo6Cxd7knHf0TfM3IpF-7ulNoy4")

        # Create Gemini model
        gemini = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_message
        )

        # Stream response
        stream = gemini.generate_content(messages, stream=True)
        response = ''
        for chunk in stream:
            response += chunk.candidates[0].content.parts[0].text or ''
            yield response
    elif model=='llama-3.2' :
        # Stream from local LLaMA
        print(model)
        messages.append({"role": "system", "content": system_message})
        for user_message, assistant_message in history:
            messages.append({"role": "user", "content": user_message})
            messages.append({"role": "assistant", "content": assistant_message})
        messages.append({"role": "user", "content": query_index(message, chunks)})

        OLLAMA_API = "http://localhost:11434/api/chat"
        HEADERS = {"Content-Type": "application/json"}
        MODEL = "llama3.2"
        print(messages)
        payload = {
            "model": MODEL,
            "messages": messages,
            "stream": False
        }
        response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
        print(response.json()['message']['content'])
        yield response.json()['message']['content']


import gradio as gr
# Build UI
with gr.Blocks() as demo:
    model_selector = gr.Dropdown(
        ["gemini-2.0-flash", "llama-3.2"],
        value="gemini-2.0-flash",
        label="Select Model"
    )

    gr.ChatInterface(
        fn=chat,
        additional_inputs=[model_selector]
    )

demo.launch()