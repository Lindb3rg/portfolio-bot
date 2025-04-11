import anthropic




class ChatBot:
    
    SUPPORTED_LANGUAGES = ["English", "Swedish", "Norwegian", "French", "German", "Danish", "Finnish"]
    
    def __init__(self, api_key: str, system_message: str):
        self.title = "Title not defined"
        self.welcome_message  = "Welcome message not defined"
        self.api_key = api_key
        self.system_message = system_message
        self.client = None
        self.language = "English"
        self._setup_client()
    
    def __str__(self):
        return self.title

    
    def _setup_client(self):
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
    
    def set_title(self, title:str):
        self.title = title
    
    def set_welcome_message(self, welcome_message:str):
        self.welcome_message = welcome_message
    
    def get_response(self, prompt: str):
        result = self.client.messages.stream(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=0.7,
        system=self.system_message,
        messages=[
            {"role": "user", "content": prompt},
        ])
        return self.stream_response(result)
    
    def get_supported_languages(self):
        return self.SUPPORTED_LANGUAGES.copy()
    
    def set_language(self, language):
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{language}' not supported. Choose from: {', '.join(self.SUPPORTED_LANGUAGES)}")
        self.language = language
        print(f"**** Language has been set to {self.language} ****")
        return self.language
    
    
    def translate_text(self, text, target_language):
        translate_prompt = f"Translate the following text to {target_language}. Only provide the translation, nothing else: {text}"
        result =  self.get_response(translate_prompt)
        return result
    
    def stream_response(self, result:anthropic.MessageStreamManager):
        response = ""
        
        with result as stream:
            for text in stream.text_stream:
                response += text or ""
                yield response
        
    
