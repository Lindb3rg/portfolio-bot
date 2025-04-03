import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY').strip()
if not api_key.startswith('sk-ant-'):
    raise ValueError("API key appears to be in incorrect format. Should start with 'sk-ant-'")

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to system_message.txt
system_message_path = os.path.join(current_dir, 'system_message.txt')

with open(system_message_path, 'r') as file:
    system_message = file.read()

if not system_message:
    raise ValueError(
        "system_message file could not be read"
    )