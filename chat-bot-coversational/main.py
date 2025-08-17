import os
import google.generativeai as genai

system_message = "You are a helpful AI assistant."

def chat(message, history):
    # Convert conversation into Gemini's expected format
    messages = []
    for user_message, assistant_message in history:
        messages.append({"role": "user", "parts": [{"text": user_message}]})
        messages.append({"role": "model", "parts": [{"text": assistant_message}]})
    messages.append({"role": "user", "parts": [{"text": message}]})

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

import gradio as gr

gr.ChatInterface(fn=chat).launch()