
import os
from dotenv import load_dotenv
from groq import Groq

# Load API keys from .env
load_dotenv()

# Supported languages
LANGUAGE_NAMES = {
    "English": "English",
    "Telugu": "Telugu",
    "Hindi": "Hindi"
}


def detect_question_language(question, selected_language="English"):
    """
    Give priority to the language selected by the student.

    If no valid language is selected, detect Telugu
    or Hindi from the question's Unicode script.
    """

    # Student's selected language has first priority
    if selected_language in LANGUAGE_NAMES:
        return selected_language

    # Automatic Telugu script detection
    for char in question:
        if "\u0C00" <= char <= "\u0C7F":
            return "Telugu"

    # Automatic Hindi (Devanagari) script detection
    for char in question:
        if "\u0900" <= char <= "\u097F":
            return "Hindi"

    # Default language
    return "English"


def generate_ai_answer(question, language="English"):
    """
    Generate an educational AI answer using Groq.

    The response language follows the student's
    selected language.
    """

    # Validate Groq API key
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file"
        )

    # Validate question
    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            "Please enter a valid question."
        )

    question = question.strip()

    # Determine response language
    detected_language = detect_question_language(
        question,
        language
    )

    selected_language = LANGUAGE_NAMES.get(
        detected_language,
        "English"
    )

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # System instructions
    system_prompt = f"""
You are Bharat Student AI, an intelligent multilingual
educational voice assistant designed for Indian students.

YOUR ROLE:
You are a friendly, knowledgeable, and helpful AI tutor.

YOUR RESPONSIBILITIES:

1. Explain academic concepts in simple language.
2. Help students understand programming and technology.
3. Explain Artificial Intelligence, Machine Learning,
   Data Science, and Computer Science concepts.
4. Provide general information about scholarships.
5. Help students explore career opportunities.
6. Provide practical examples whenever helpful.
7. Explain difficult topics step by step.
8. Give accurate and relevant information.
9. Admit uncertainty when information is unavailable.
10. Never invent scholarship deadlines or eligibility.

LANGUAGE INSTRUCTIONS:

The student has selected {selected_language}.

You MUST respond in {selected_language}, regardless of
the language or script used in the student's question.

If the selected language is Telugu:
- Write primarily in Telugu script.
- Use simple, natural Telugu.
- Keep technical English terms only when necessary.
- Do not answer entirely in English or Hindi.

If the selected language is Hindi:
- Write primarily in Hindi using Devanagari script.
- Use simple, natural Hindi.
- Keep technical English terms only when necessary.
- Do not answer entirely in Telugu or English.

If the selected language is English:
- Write in clear and simple English.
- Do not answer primarily in Telugu or Hindi.

EDUCATIONAL ANSWER FORMAT:

- Answer the student's question directly.
- Explain the concept in easy-to-understand language.
- Give practical examples when useful.
- Keep the response approximately 100 to 150 words.
- Use short paragraphs suitable for voice narration.
- Avoid unnecessary Markdown formatting.
- Avoid complex symbols and decorative characters.
- Do not begin with "As an AI language model".
- If the question requires current information,
  avoid claiming unverified facts are up to date.

IMPORTANT:
The response must be suitable for conversion into
natural speech using Gnani Timbre Text-to-Speech.
"""

    try:
        # Send request to Groq
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.4,
            max_completion_tokens=700
        )

        # Check response
        if not response.choices:
            raise RuntimeError(
                "Groq returned no response choices."
            )

        # Extract answer
        answer = (
            response.choices[0].message.content or ""
        ).strip()

        if not answer:
            raise RuntimeError(
                "Groq returned an empty answer."
            )

        return answer

    except Exception as error:
        raise RuntimeError(
            f"Groq answer generation failed: {error}"
        ) from error
