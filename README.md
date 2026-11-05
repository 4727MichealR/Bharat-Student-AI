
# 🇮🇳 Bharat Student AI

A multilingual AI-powered educational voice assistant
designed for Indian students.

## Overview

Bharat Student AI helps students ask educational questions
through voice or text in Telugu, Hindi and English.

The application supports automatic language detection,
AI-generated explanations, live web search and
natural voice responses.

## Features

- Telugu, Hindi and English support
- Automatic speech language detection
- Voice-to-text transcription
- AI-powered educational explanations
- Automatic real-time web search
- Text-to-speech voice answers
- Audio playback and WAV download
- Conversation history
- Streamlit web interface

## Technologies

- Python
- Streamlit
- Gnani Prisma v3.0
- Gnani Timbre v3.0
- Groq GPT-OSS 20B
- Tavily Search API

## Installation

1. Clone the repository.
2. Create a Python virtual environment.
3. Install dependencies:

   pip install -r requirements.txt

4. Create a .env file containing:

   GNANI_API_KEY=your_key
   GROQ_API_KEY=your_key
   TAVILY_API_KEY=your_key

5. Run the application:

   python -m streamlit run app.py

## How It Works

1. The student records or types a question.
2. Gnani Prisma transcribes recorded speech.
3. The application determines the response language.
4. The AI system decides whether live search is needed.
5. Groq generates an educational answer.
6. Gnani Timbre converts the answer into speech.

## Supported Languages

- English
- Telugu
- Hindi

## Security

API credentials are stored in environment variables
and must not be committed to GitHub.

## Purpose

Developed as a multilingual educational AI assistant
project for an internship challenge.
