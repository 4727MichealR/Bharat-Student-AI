
import streamlit as st
from datetime import datetime
from html import escape

from gnani_api import transcribe_audio
from smart_ai import generate_smart_answer
from tts_engine import generate_speech


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Bharat Student AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# LANGUAGE SETTINGS
# ==================================================

SUPPORTED_LANGUAGES = (
    "English",
    "Telugu",
    "Hindi"
)

LANGUAGE_OPTIONS = [
    "Auto Detect",
    "English",
    "Telugu",
    "Hindi"
]

LANGUAGE_CODES = {
    "en": "English",
    "en-IN": "English",
    "te": "Telugu",
    "te-IN": "Telugu",
    "hi": "Hindi",
    "hi-IN": "Hindi"
}


def detect_script_language(text):
    """
    Detect Telugu or Hindi using Unicode characters.
    Returns None when the script is inconclusive.
    """

    telugu_count = sum(
        "\u0C00" <= char <= "\u0C7F"
        for char in text
    )

    hindi_count = sum(
        "\u0900" <= char <= "\u097F"
        for char in text
    )

    if telugu_count > hindi_count and telugu_count > 0:
        return "Telugu"

    if hindi_count > telugu_count and hindi_count > 0:
        return "Hindi"

    return None


def get_audio_language(detected_code, transcript):
    """
    Determine language using Gnani's detection
    and the recognized transcript.
    """

    script_language = detect_script_language(
        transcript
    )

    if script_language:
        return script_language

    code = str(
        detected_code or ""
    ).strip()

    if code in LANGUAGE_CODES:
        return LANGUAGE_CODES[code]

    # Support variants such as en-US.
    prefix = code.split("-")[0].lower()

    return LANGUAGE_CODES.get(prefix)


def resolve_answer_language(question, mode):
    """
    Manual selection always takes priority.

    In Auto Detect mode:
    1. Detect Telugu/Hindi from the question script.
    2. Use Gnani audio language only if the question
       still matches the recognized transcript.
    3. Return None when language is uncertain.
    """

    if mode in SUPPORTED_LANGUAGES:
        return mode

    script_language = detect_script_language(
        question
    )

    if script_language:
        return script_language

    recognized_question = (
        st.session_state.recognized_question
    ).strip()

    audio_language = (
        st.session_state.audio_language
    )

    if (
        recognized_question
        and question.strip() == recognized_question
        and audio_language in SUPPORTED_LANGUAGES
    ):
        return audio_language

    return None


# ==================================================
# CUSTOM STYLING
# ==================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(
            120deg,
            #172554,
            #0F172A
        );
        color: white;
        padding: 30px;
        border-radius: 18px;
        margin-bottom: 24px;
        border-top: 4px solid #FF9933;
        border-bottom: 4px solid #138808;
    }

    .hero h1 {
        color: white !important;
        margin: 0;
        font-size: 36px;
    }

    .hero p {
        color: #CBD5E1;
        margin-top: 12px;
        font-size: 16px;
    }

    .feature-card {
        background: #172554;
        color: white;
        border-radius: 14px;
        padding: 20px;
        min-height: 120px;
        margin-bottom: 12px;
    }

    .feature-card strong {
        font-size: 17px;
    }

    .feature-card p {
        font-size: 13px;
        color: #CBD5E1;
    }

    .answer-box {
        border-left: 4px solid #138808;
        border-radius: 10px;
        padding: 16px;
        background: rgba(100, 116, 139, 0.08);
    }

    .footer {
        text-align: center;
        padding: 18px;
        font-size: 13px;
        color: #94A3B8;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SESSION STATE
# ==================================================

DEFAULTS = {
    "selected_language": "Auto Detect",
    "question_input": "",
    "recognized_question": "",
    "detected_language": "",
    "audio_language": None,
    "ai_answer": "",
    "answer_language": "",
    "answer_mode": "",
    "answer_sources": [],
    "voice_audio": None,
    "history": []
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def clear_answer():
    """
    Remove previous AI answer and generated audio.
    """

    st.session_state.ai_answer = ""
    st.session_state.answer_language = ""
    st.session_state.answer_mode = ""
    st.session_state.answer_sources = []
    st.session_state.voice_audio = None


def question_changed():
    """
    Clear old answer when question changes.
    """

    clear_answer()


def language_changed():
    """
    Clear old answer when language changes.
    """

    clear_answer()


def clear_history():
    """
    Clear stored conversation history.
    """

    st.session_state.history = []
    clear_answer()


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🇮🇳 Bharat Student AI")

    st.caption(
        "Your Multilingual AI Learning Companion"
    )

    st.divider()

    st.subheader("🌐 Language Settings")

    mode = st.selectbox(
        "Choose response language",
        LANGUAGE_OPTIONS,
        key="selected_language",
        on_change=language_changed
    )

    if mode == "Auto Detect":
        st.info(
            "Automatically detect Telugu, Hindi "
            "or English from your voice or text."
        )
    else:
        st.info(
            f"AI answers and speech will use {mode}."
        )

    st.divider()

    st.subheader("🧠 Intelligent Answer System")

    st.write("📚 Academic AI")
    st.write("🌍 Automatic Live Web Search")
    st.write("🎤 Multilingual Voice Input")
    st.write("🔊 Natural AI Voice Output")

    st.caption(
        "Current questions use Tavily search. "
        "Academic questions use Groq directly."
    )

    st.divider()

    st.subheader("📖 Learning Categories")

    st.write("🎓 Academic Assistance")
    st.write("💻 Programming Help")
    st.write("🤖 Artificial Intelligence")
    st.write("🏆 Scholarships")
    st.write("🚀 Career Guidance")
    st.write("📰 Current Affairs")

    st.divider()

    st.subheader("🕘 Conversation History")

    if st.session_state.history:

        for item in reversed(
            st.session_state.history[-10:]
        ):

            title = item["question"][:40]

            with st.expander(title):

                st.caption(
                    f'{item["language"]} | '
                    f'{item["mode"]} | '
                    f'{item["time"]}'
                )

                st.write(item["answer"])

    else:
        st.caption(
            "Your questions will appear here."
        )

    st.button(
        "🗑️ Clear History",
        on_click=clear_history,
        use_container_width=True
    )


# ==================================================
# HERO SECTION
# ==================================================

st.markdown(
    """
    <div class="hero">
        <h1>🎓 Bharat Student AI</h1>
        <p>
            Your intelligent multilingual learning
            companion with automatic language detection
            and live information search.
            <br><br>
            Speak. Ask. Learn. Explore.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==================================================
# FEATURE CARDS
# ==================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        """
        <div class="feature-card">
            <strong>🎤 Voice Assistant</strong>
            <p>
                Ask questions naturally in
                Telugu, Hindi or English.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        """
        <div class="feature-card">
            <strong>🌐 Smart Live Search</strong>
            <p>
                Automatically retrieve recent
                information when needed.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        """
        <div class="feature-card">
            <strong>🤖 AI Learning Tutor</strong>
            <p>
                Get clear educational answers
                with natural voice output.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ==================================================
# VOICE INPUT
# ==================================================

st.header("🎤 Ask Using Your Voice")

audio = st.audio_input(
    "Record your question",
    sample_rate=16000
)

if audio is not None:

    st.audio(
        audio,
        format="audio/wav"
    )

    if st.button(
        "🎙️ Convert Speech to Text",
        type="primary"
    ):

        with st.spinner(
            "Recognizing speech with Gnani Prisma..."
        ):

            try:

                result = transcribe_audio(
                    audio.getvalue()
                )

                if not result.get("success"):

                    st.error(
                        result.get(
                            "error",
                            "Speech recognition failed."
                        )
                    )

                else:

                    transcript = (
                        result.get("transcript") or ""
                    ).strip()

                    detected_code = (
                        result.get("detected_language_code")
                        or "Unknown"
                    )

                    if not transcript:

                        st.warning(
                            "No speech was recognized. "
                            "Please record again."
                        )

                    else:

                        audio_language = (
                            get_audio_language(
                                detected_code,
                                transcript
                            )
                        )

                        st.session_state.recognized_question = (
                            transcript
                        )

                        st.session_state.question_input = (
                            transcript
                        )

                        st.session_state.detected_language = (
                            detected_code
                        )

                        st.session_state.audio_language = (
                            audio_language
                        )

                        clear_answer()

                        st.success(
                            "Speech recognized successfully!"
                        )

            except Exception as error:

                st.error(
                    f"Speech recognition failed: {error}"
                )


# ==================================================
# RECOGNIZED SPEECH
# ==================================================

if st.session_state.recognized_question:

    st.subheader("📝 Recognized Speech")

    st.info(
        st.session_state.recognized_question
    )

    st.caption(
        "Gnani detected code: "
        + st.session_state.detected_language
    )

    if st.session_state.audio_language:

        st.success(
            "🌐 Detected language: "
            + st.session_state.audio_language
        )

    else:

        st.warning(
            "Automatic language detection was "
            "inconclusive. Select a language "
            "manually if necessary."
        )


st.divider()


# ==================================================
# QUESTION INPUT
# ==================================================

st.header("💬 Ask Bharat Student AI")

question = st.text_area(
    "Type your question or use recognized speech",
    key="question_input",
    on_change=question_changed,
    height=110,
    placeholder=(
        "Ask about AI, programming, scholarships, "
        "current affairs, exams or careers..."
    )
)


# ==================================================
# GENERATE SMART AI ANSWER
# ==================================================

if st.button(
    "✨ Generate AI Answer",
    type="primary",
    use_container_width=True
):

    question_text = question.strip()

    if not question_text:

        st.warning(
            "Please speak or type a question."
        )

    else:

        answer_language = resolve_answer_language(
            question_text,
            mode
        )

        if answer_language is None:

            st.warning(
                "The response language could not "
                "be determined. Please select "
                "English, Telugu or Hindi "
                "from the sidebar."
            )

        else:

            with st.spinner(
                "Analyzing question and checking "
                "whether live search is needed..."
            ):

                try:

                    clear_answer()

                    result = generate_smart_answer(
                        question=question_text,
                        language=answer_language
                    )

                    answer = result["answer"]

                    answer_mode = result["mode"]

                    sources = result.get(
                        "sources",
                        []
                    )

                    st.session_state.ai_answer = (
                        answer
                    )

                    st.session_state.answer_language = (
                        answer_language
                    )

                    st.session_state.answer_mode = (
                        answer_mode
                    )

                    st.session_state.answer_sources = (
                        sources
                    )

                    st.session_state.history.append({
                        "question": question_text,
                        "answer": answer,
                        "language": answer_language,
                        "mode": answer_mode,
                        "time": datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )
                    })

                    st.success(
                        "AI answer generated successfully!"
                    )

                except Exception as error:

                    st.error(
                        f"AI generation failed: {error}"
                    )


# ==================================================
# AI ANSWER
# ==================================================

if st.session_state.ai_answer:

    st.divider()

    st.header("🤖 Your AI Answer")

    col_lang, col_mode = st.columns(2)

    with col_lang:

        st.caption(
            "🌐 Answer language: "
            + st.session_state.answer_language
        )

    with col_mode:

        st.caption(
            "🧠 Answer mode: "
            + st.session_state.answer_mode
        )

    st.markdown(
        '<div class="answer-box">',
        unsafe_allow_html=True
    )

    st.write(
        st.session_state.ai_answer
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # ==============================================
    # LIVE SEARCH SOURCES
    # ==============================================

    if st.session_state.answer_sources:

        st.subheader(
            "🌍 Live Information Sources"
        )

        st.caption(
            "The following web results were used "
            "to generate this answer. Verify "
            "important details on official websites."
        )

        for index, source in enumerate(
            st.session_state.answer_sources,
            start=1
        ):

            title = source.get(
                "title",
                f"Source {index}"
            )

            url = source.get("url", "")

            if url.startswith(
                ("https://", "http://")
            ):

                st.markdown(
                    f"**{index}.** "
                    f"[{escape(title)}]({url})"
                )


    # ==============================================
    # TEXT TO SPEECH
    # ==============================================

    st.divider()

    st.subheader("🔊 Listen to Your Answer")

    if st.button(
        "🎧 Generate Voice Answer",
        use_container_width=True
    ):

        if st.session_state.voice_audio is None:

            with st.spinner(
                "Generating speech using "
                "Gnani Timbre v3.0..."
            ):

                try:

                    audio_bytes = generate_speech(
                        text=st.session_state.ai_answer,
                        language=(
                            st.session_state.answer_language
                        )
                    )

                    if not audio_bytes:
                        raise RuntimeError(
                            "No audio was returned."
                        )

                    st.session_state.voice_audio = (
                        audio_bytes
                    )

                    st.success(
                        "Voice generated successfully!"
                    )

                except Exception as error:

                    st.session_state.voice_audio = None

                    st.error(
                        f"Voice generation failed: {error}"
                    )

        else:

            st.info(
                "Voice is already generated. "
                "Use the audio player below."
            )


    # ==============================================
    # AUDIO PLAYER AND DOWNLOAD
    # ==============================================

    if st.session_state.voice_audio is not None:

        st.audio(
            st.session_state.voice_audio,
            format="audio/wav"
        )

        st.download_button(
            label="⬇️ Download Voice Answer",
            data=st.session_state.voice_audio,
            file_name="bharat_student_ai_voice.wav",
            mime="audio/wav",
            use_container_width=True
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        🇮🇳 Bharat Student AI
        <br>
        Speech Recognition: Gnani Prisma v3.0
        <br>
        AI Engine: Groq GPT-OSS 20B
        <br>
        Live Search: Tavily
        <br>
        Voice Generation: Gnani Timbre v3.0
    </div>
    """,
    unsafe_allow_html=True
)
