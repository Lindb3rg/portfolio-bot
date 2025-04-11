from anthropic import Anthropic
from tools.certification import CertificateTool
from api_config import API_KEY,API_MODEL
from config.config import IDENTITY,TOOLS
from utils.logger import log_event

import time

from dotenv import load_dotenv
load_dotenv()


class ChatBot:
    def __init__(self, session_state):
        self.anthropic = Anthropic(api_key=API_KEY)
        self.session_state = session_state
        self.max_tokens = 2048
        
    def generate_message(
        self,
        messages,
        max_tokens,
    ):
        try:
            response = self.anthropic.messages.create(
                model=API_MODEL,
                system=IDENTITY,
                max_tokens=max_tokens,
                messages=messages,
                tools=TOOLS,
            )
            return response
        except Exception as e:
            log_event("error", str(e))
            return {"error": str(e)}
    
    def process_user_input(self, user_input):
        
        typing_speed = 0.005
        
        self.session_state.messages.append({"role": "user", "content": user_input})
        
        
        response_message = self.generate_message(
            messages=self.session_state.messages,
            max_tokens=self.max_tokens,
        )
        

        if "error" in response_message:
            error_msg = f"An error occurred: {response_message['error']}"
            log_event("error",error_msg)
            return error_msg

        if response_message.content[-1].type == "tool_use":
            tool_use = response_message.content[-1]
            func_name = tool_use.name
            func_params = tool_use.input
            tool_use_id = tool_use.id

            result = self.handle_tool_use(func_name, func_params)
            self.session_state.messages.append(
                {"role": "assistant", "content": response_message.content}
            )
            self.session_state.messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": f"{result}",
                }],
            })

            follow_up_response = self.generate_message(
                messages=self.session_state.messages,
                max_tokens=self.max_tokens,
            )

            if "error" in follow_up_response:
                error_msg = f"An error occurred: {follow_up_response['error']}"
                log_event("error",error_msg)
                return error_msg

            response_text = follow_up_response.content[0].text
            self.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
            
            for char in response_text:
                time.sleep(typing_speed)
                yield char
        
        elif response_message.content[0].type == "text":
            response_text = response_message.content[0].text
            self.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
            for char in response_text:
                time.sleep(typing_speed)
                yield char
            
        
        else:
            raise Exception("An error occurred: Unexpected response type")

    def handle_tool_use(self, func_name, func_params):
        if func_name == "get_filtered_certificates":
            cert = CertificateTool()
            certificates = cert.get_filtered_certificates(**func_params)
            return f"Certificates: {certificates}"
        
        raise Exception("An unexpected tool was used")
