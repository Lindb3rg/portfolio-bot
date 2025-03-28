import gradio as gr
from api_config import api_key, system_message
from chatbot import ChatBot


new_chatbot = ChatBot(api_key=api_key,system_message=system_message)
new_chatbot.title = "Adam Lindberg Resumé Chatbot"
new_chatbot.welcome_message = "👋 Welcome to Adam Lindberg's resumé chatbot! I can tell you a little about Adam, his skills and projects. What would you like to know?"


with gr.Blocks(title=new_chatbot.title, analytics_enabled=False, theme=gr.themes.Origin(spacing_size="md", radius_size="lg")) as chat:
    
    first_load = gr.State(True)
    default_language = gr.State(new_chatbot.language)
    chatbot = gr.Chatbot(label="Adam Lindbergs Resumé Chatbot", layout="bubble")
    msg = gr.Textbox()
    
    with gr.Row():
        submit_btn = gr.Button("Submit")
        
    with gr.Row():
        language_dropdown = gr.Dropdown(
            choices=new_chatbot.get_supported_languages(), 
            value=new_chatbot.language,
            label="Select Language",
            interactive=True
        )
        set_language_btn = gr.Button("Set Language")
        translate_button = gr.Button("Translate Last Response")
        clear = gr.Button("Clear")
    
    def user(user_message, history):
        return "", history + [[user_message, None]]
    
    def init_chat(first_load_state, language):
        welcome_message = new_chatbot.welcome_message
        
        if language != new_chatbot.language:
            complete_translation = ""
            for chunk in new_chatbot.translate_text(welcome_message, language):
                complete_translation = chunk
            welcome_message = complete_translation
            
        if first_load_state:
            return [[None, welcome_message]], False
        return [], first_load_state
    
    
    def bot(history, language):
        user_message = history[-1][0]
        history[-1][1] = ""
        
        
        response_generator = new_chatbot.get_response(user_message)
        if language == new_chatbot.language:
            
            for chunk in response_generator:
                history[-1][1] = chunk
                yield history
            
        else:
            # For other languages, get the complete response first
            complete_response = ""
            for chunk in response_generator:
                complete_response = chunk  # Each chunk contains the full response so far
            
            # Then translate and stream the translation
            translation_generator = new_chatbot.translate_text(complete_response, language)
            for chunk in translation_generator:
                history[-1][1] = chunk
                yield history
            
            
    
    def translate_response(history, language):
        if not history or not history[-1][1]:
            return history
        
        original_response = history[-1][1]
        complete_response = ""
        translated_response = new_chatbot.translate_text(original_response,language)
        
        for chunk in translated_response:
            complete_response = chunk  # Each chunk contains the full response so far
        
        
        new_history = history.copy()
        new_history.append([f"Translate to {language}", complete_response])
        
        return new_history
    
    
    
    def update_language(language):
        new_chatbot.set_language(language=language)
        return language
    
    
    
    
    chat.load(init_chat, [first_load, default_language], [chatbot, first_load])
    
    submit_btn.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, [chatbot, default_language], chatbot
    )
    
    set_language_btn.click(update_language, language_dropdown, default_language).then(
        init_chat, [first_load, default_language], [chatbot, first_load]
    )
    
    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, [chatbot, default_language], chatbot
    )
    
    
    
    translate_button.click(
        translate_response, 
        [chatbot, language_dropdown], 
        [chatbot]
    )
    
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ =="__main__":
    chat.queue()
    chat.launch(server_name="0.0.0.0", debug=False)
    