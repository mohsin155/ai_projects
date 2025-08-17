import gradio as gr
from chat_service import chat
with gr.Blocks() as demo:
    model_selector = gr.Dropdown(
        ["gemini-2.5-flash", ],
        value="gemini-2.5-flash",
        label="Select Model"
    )

    gr.ChatInterface(
        fn=chat,
        additional_inputs=[model_selector]
    )

demo.launch()