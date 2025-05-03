
# Ej klar

import os
import glob
from dotenv import load_dotenv
import gradio as gr
from utils.logger import logger
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from vector_store import VectorStore
from langchain.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

from config.config import SYSTEM_PROMPT


load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")
VECTOR_DB_NAME = os.getenv("VECTOR_DB_NAME", "faiss_index")
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')
folders = glob.glob("knowledge-base/*")

embeddings = OpenAIEmbeddings()
vector_store = None

if os.path.exists(VECTOR_DB_NAME) and os.path.isdir(VECTOR_DB_NAME):
    try:
        logger.info(f"Loading existing vector store from {VECTOR_DB_NAME}...")
        vector_store = FAISS.load_local(VECTOR_DB_NAME, embeddings, allow_dangerous_deserialization=True)
        logger.info(f"Vector store loaded successfully with {len(vector_store.index_to_docstore_id)} documents")
    except Exception as e:
        logger.warning(f"Error loading existing vector store: {e}")
        logger.info("Creating new vector store...")
        vector_store = None


if vector_store is None:
    logger.info("Creating new vector store...")
    store = VectorStore(folders)
    store.prepare_documents()
    store.create_vector_store()
    vector_store = store.vector_store
    

    vector_store.save_local(VECTOR_DB_NAME)
    logger.info(f"Vector store saved to {VECTOR_DB_NAME}")

system_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{question}")
])


print(system_prompt)

llm = ChatOpenAI(temperature=0.7, model_name=MODEL)
memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
retriever = vector_store.as_retriever()
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm, 
    retriever=retriever, 
    memory=memory,
    combine_docs_chain_kwargs={"prompt": system_prompt}
)


def user_input(message, history):
    """Process user input and add to chat history"""
    logger.info(f"Received message: {message}")
    return "", history + [[message, None]]

def bot_response(history):
    """Generate bot response based on the latest user message"""
    
    
    
    try:
        user_message = history[-1][0]
        logger.info(f"Processing message: {user_message}")
        
        result = conversation_chain.invoke({"question": user_message})
        bot_message = result["answer"]
        
        logger.info("Successfully generated response")
        history[-1][1] = bot_message
        return history
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        logger.error(error_msg)
        history[-1][1] = f"Sorry, an error occurred: {str(e)}"
        return history


with gr.Blocks(title="Adam Lindberg Resumé Assistant", theme=gr.themes.Origin(spacing_size="md", radius_size="lg")) as chat:
    gr.Markdown("# Adam Lindberg Resumé Assistant")
    gr.Markdown("Ask questions about Adam")
    
    chatbot = gr.Chatbot(height=600)
    first_load = gr.State(True)
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type your question here...",
            label="Your Question",
            scale=8
        )
        submit_btn = gr.Button("Submit", scale=1)
        clear_btn = gr.Button("Clear Conversation",scale=1)
    
    
    
    
    msg.submit(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_response, chatbot, chatbot
    )
    
    def init_chat(first_load_state):
        welcome_message = "👋 Welcome to Adam Lindberg's resumé chatbot! I can tell you a little about Adam, his skills and projects and much more. What would you like to know?"
            
        if first_load_state:
            return [[None, welcome_message]], False
        return [], first_load_state
    
    chat.load(init_chat, [first_load], [chatbot, first_load])
    
    submit_btn.click(user_input, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_response, chatbot, chatbot
    )
    
    clear_btn.click(lambda: None, None, chatbot, queue=False)
    
    
    logger.info("Starting Gradio chatbot interface")

if __name__ == "__main__":
    chat.launch()
    
    def chat(message, history):
    result = conversation_chain.invoke({"question": message})
    return result["answer"]
view = gr.ChatInterface(chat).launch()