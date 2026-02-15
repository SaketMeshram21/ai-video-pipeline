import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_script(topic):
    # Modified prompt to ensure clean sentences for easier splitting
    prompt = f"""
    Write a narrated YouTube video script about: {topic}
    - No stage directions like [Music] or Host:
    - Write exactly 6-8 distinct sentences.
    - Each sentence should be a complete thought.
    - Max 200 words total.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", # Using the stable flash model
        contents=prompt
    )
    return response.text.strip()