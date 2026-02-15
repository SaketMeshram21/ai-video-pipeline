# AI Video Generation Pipeline 🎬

> **One-command automated YouTube video creation: Topic → Script → Voice → Visuals → Video**

Transform any topic into a complete, professional YouTube video with AI-generated script, voiceover, visuals, and subtitles - all in under 3 minutes.

## 🎯 Features

- ✅ **End-to-End Automation** - Single command execution
- 🤖 **AI Script Generation** - Google Gemini API
- 🎙️ **Natural Voiceover** - Microsoft Edge TTS (free)
- 🖼️ **Smart Visuals** - Pexels API with intelligent cropping
- 📝 **Auto Subtitles** - Whisper-powered transcription
- 🎨 **Dual Thumbnails** - Cinematic + Clean styles
- ⚡ **Fast Processing** - 2-3 minutes for 60s video

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export GEMINI_API_KEY="your_key"
export PEXELS_API_KEY="your_key"

# Run
python main.py
```

## 📋 Requirements

```txt
moviepy==2.0.0
openai-whisper==20231117
requests==2.31.0
Pillow==10.1.0
edge-tts==6.1.9
google-generativeai==0.3.2
```

## 🏗️ Architecture

```
Topic Input → Gemini (Script) → Edge-TTS (Voice) → Pexels (Images) 
→ MoviePy + Whisper (Assembly) → video.mp4
```

## 📁 Project Structure

```
ai-video-pipeline/
├── main.py                 # Main orchestrator
├── video_maker.py          # Video assembly
├── script_generator.py     # Gemini integration
├── voiceover.py           # Edge-TTS integration
├── visuals.py             # Pexels integration
└── output/                # Generated files
```

## 🎨 Customization

Change video settings in `video_maker.py`:
- Resolution, FPS, codec
- Subtitle style, position, size
- Thumbnail layout
