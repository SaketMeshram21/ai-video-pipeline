import asyncio
import edge_tts
import os
import re  # Added for text cleaning

def clean_text_for_tts(text):
    """Removes stage directions and labels like **Host:** or [Music]."""
    # 1. Remove anything in brackets like [Intro Music] or (Exciting clips)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    
    # 2. Remove labels like **Host:**, **Narrator:**, or **Person:**
    text = re.sub(r'\*\*.*?:', '', text)
    
    # 3. Strip remaining double asterisks (bolding)
    text = text.replace("**", "")
    
    # 4. Clean up extra whitespace and newlines
    text = " ".join(text.split())
    
    return text

async def generate_voice(text, output_file="output/voice.mp3"):
    os.makedirs("output", exist_ok=True)
    
    # Clean the script before it reaches the AI voice
    cleaned_script = clean_text_for_tts(text)
    
    voice = "en-US-AriaNeural"  # natural female voice
    communicate = edge_tts.Communicate(cleaned_script, voice=voice)
    await communicate.save(output_file)

def run_voice(text):
    asyncio.run(generate_voice(text))

if __name__ == "__main__":
    sample_text = "**Host:** [Intro Music] This is a test. (Wait for it) Success!"
    run_voice(sample_text)
    print("Voiceover generated: output/voice.mp3")