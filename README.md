# Personalized Chatbot

This is a lightweight chatbot that can provide relevant information about you, for the customer.

## Description

This project consists of a custom Chatbot class which uses Anthropic's Claude 3.7 Sonnet API to create a personalized assistant that can answer questions about your skills, experience, and portfolio projects. The chatbot features multilingual support and a clean interface built with Gradio.

## Getting Started

### Dependencies

* Python 3.8 or higher
* Anthropic API key for Claude 3.7 Sonnet
* Required Python packages:
  * anthropic
  * gradio
  * python-dotenv

### Installing


```bash

1. Clone the repository:

git clone https://github.com/yourusername/portfolio-chatbot.git

cd portfolio-chatbot

2. Install required packages

pip install anthropic gradio python-dotenv

3. Create an .env file in your project root with your API key

ANTHROPIC_API_KEY=your_api_key_here

4. Rename the existing system_message.txt file or create a new file. The class expects a file called system_message.py

5. Executing program

To run the chatbot:
  1. Make sure your .env file and system_message.txt are properly configured
  2. Run the main script:
    python main.py
  3. Open the provided URL in your browser (typically http://127.0.0.1:7860)

Help
Common issues and solutions:

API Key Issues: Ensure your API key starts with "sk-ant-" and is correctly set in the .env file
Missing Libraries: Run pip install -r requirements.txt if provided, or install packages individually
Language Support: If you need to modify supported languages, edit the SUPPORTED_LANGUAGES list in chatbot.py

Authors
Adam Lindberg
@Lindb3rg
Version History

0.1

Initial Release with multilingual support and streaming responses

License
This project is licensed under the MIT License - see the LICENSE.md file for details
Acknowledgments

Anthropic for the Claude API
Gradio team for the interface framework
Python community for supporting libraries