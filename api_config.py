import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY').strip()
if not api_key.startswith('sk-ant-'):
    raise ValueError("API key appears to be in incorrect format. Should start with 'sk-ant-'")

with open('system_message.txt', 'r') as file:
    system_message = file.read()

if not system_message:
    raise ValueError(
        "system_message file could not be read"
    )