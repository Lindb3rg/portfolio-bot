import gradio as gr
from anthropic import Anthropic
from tools.certification import CertificateTool
from api_config import API_KEY, API_MODEL
from config.config import IDENTITY, TOOLS, TASK_SPECIFIC_INSTRUCTIONS
from utils.logger import log_event
import time
from dotenv import load_dotenv

from chatbot2 import ChatBot,SessionState


load_dotenv()


def create_gradio_interface():
    # Define the chat interface and state handling
    def predict(message, history, state):
        if state is None:
            state = {"chatbot": ChatBot(SessionState())}
            state["chatbot"]._setup_context()
        
        # Process the user message
        chatbot = state["chatbot"]
        response_generator = chatbot.process_user_input(message)
        
        # Stream the response
        response = ""
        for char in response_generator:
            response += char
            yield response, history + [[message, response]], state
    
    # Create Gradio blocks
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        state = gr.State(None)
        
        msg.submit(
            predict,
            [msg, chatbot, state],
            [msg, chatbot, state]
        )
        
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.queue().launch()