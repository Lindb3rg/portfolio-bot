import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv('ANTHROPIC_API_KEY').strip()
API_MODEL = os.getenv('ANTHROPIC_HAIKU').strip()

if not API_KEY.startswith('sk-ant-'):
    raise ValueError("API key appears to be in incorrect format. Should start with 'sk-ant-'")

with open('config/system_message.txt', 'r') as file:
    system_message = file.read()

if not system_message:
    raise ValueError(
        "system_message file could not be read"
    )