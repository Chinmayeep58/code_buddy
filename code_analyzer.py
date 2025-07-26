import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_code_with_gpt(question: str, code: str, file_type: str) -> str:
    """Use OpenAI GPT to analyze code and answer questions"""
    try:
        prompt = f"""You are an expert code assistant. Analyze this {file_type} code and answer the user's question.

Code:
```{file_type}
{code}