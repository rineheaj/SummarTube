import os
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
import httpx
import json
import shutil
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import sys
import requests
import platform

try:
    from elevenlabs import stream
    from elevenlabs.client import ElevenLabs
except ImportError:
    stream = None
    ElevenLabs = None

from rich.console import Console
from rich.markdown import Markdown
from deprecated import deprecated
import vlc
import warnings


console = Console()

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ELEVEN_LABS_API_KEY = st.secrets["ELEVEN_LABS_KEY"]
DEFAULT_VIDEO_ID = "XJC5WB2Bwrc"





if not GROQ_API_KEY and ELEVEN_LABS_API_KEY:
    raise RuntimeError("API key was not detected")



st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.preview-box {
    background: linear-gradient(to bottom right, #111827, #1f2937);
    color: #e5e7eb;
    text-color: rgb(255, 255, 255);
    padding: 1.25rem;
    border-radius: 0.75rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 1.2rem;
    line-height: 1.6;
    overflow-x: auto;
    transition: all 0.3s ease;
}

.preview-box h1, .preview-box h2, .preview-box h3 {
    color: #60a5fa;
    margin-top: 1rem;
}

.preview-box code {
    background-color: #374151;
    color: #fcd34d;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
}
</style>
""", unsafe_allow_html=True)


def resource_path(filename: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):  # running from a PyInstaller bundle
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent / filename



@deprecated(reason="Not in use")
def preview_in_terminal(markdown_txt: str):
    print(warnings.warn("preview_in_terminal is deprecated"))
    console.print(Markdown(markdown_txt))


def save_transcript(video_id: str, txt_path: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    with open(txt_path, "w", encoding="utf-8") as f:
        for e in transcript:
            f.write(f"{e['start']:.2f}s: {e['text']}\n")
    console.print(f"✅ Saved -> {txt_path}")



def display_lottie_url(url=None, height=300, key='lottie'):
    def load_lottie_url(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    lottie_animation = load_lottie_url(url=url)
    if lottie_animation:
        st_lottie(lottie_animation, height=height, key=key)
    else:
        st.error('Failed to load the Lottie animation')


def summarize_to_markdown(txt_path: str, md_path: str):
    client = httpx.AsyncClient(timeout=30)
    model = GroqModel(
        "llama-3.3-70b-versatile",
        provider=GroqProvider(api_key=GROQ_API_KEY, http_client=client),
    )
    instructions = """
    Please summarize the following transcript and format it as a fun, emoji-rich Markdown file that cannot have any rainbows under any circumstances.
    Make sure the emojis are not in the text but just the title headers.
    Remember to add to the summary by looking up something or multiple nice things about the subject if you determine the video to be sad.
    These nice things will add a little light to the darkness.
    Always include a section for fun likeable facts.
    Make it at least a 90-second read, industry-standard, no extra fluff—just the Markdown content.
    Remember to only have markdown no dashes or anything weird. Use emojis to express the idea you are getting across.
    """

    console.print(f"[yellow]Running Groq with instructions:[/]\n{instructions}")
    agent = Agent(model=model)
    text = Path(txt_path).read_text(encoding="utf-8")
    result = agent.run_sync(user_prompt=f"{instructions}\n\n\n{text}")

    md = result.output
    Path(md_path).write_text(md, encoding="utf-8")
    console.print(f"✅ Markdown saved -> {md_path}")
    preview_in_terminal(markdown_txt=md)


def talk_to_me(text: str, filename: str):
    ele_voice_id = "2EiwWnXFnvU5JabPnv8n"
    mpv_exists = shutil.which("mpv") is not None
    current_os = platform.system()

    if mpv_exists and stream and ElevenLabs:
        ele_labs_client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)

        audio_stream = ele_labs_client.text_to_speech.stream(
            text=text, voice_id=ele_voice_id, model_id="eleven_multilingual_v2"
        )
        stream(audio_stream)
    else:
        if not mpv_exists:
            st.info(
                "⚠️ mpv was not found - install and add to PATH if you want real time streaming functionality\n🍁Falling back to use vlc library"
            )

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ele_voice_id}"

        headers = {
            "xi-api-key": ELEVEN_LABS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.85},
        }

        with httpx.Client() as client:
            with client.stream("POST", url, headers=headers, json=payload) as resp:
                with open(filename, "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)


        if current_os == "Windows" and shutil.which("vlc"):
            player = vlc.MediaPlayer(filename)
            player.play()
        else:
            with open(filename, "rb") as f:
                audio_bytes = f.read()
            st.audio(data=audio_bytes, autoplay=True)

        # Path(filename).with_suffix(".txt").write_text(text, encoding="utf-8")





def run(basename: str, output_dir: str, video_id: str = DEFAULT_VIDEO_ID):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_path = Path(basename)
    base = base_path.stem
    ext = base_path.suffix.lower()

    txt_name = base_path.name if ext == ".txt" else f"{base}.txt"
    txt_path = out_dir / txt_name
    md_path = out_dir / f"{base}.md"

    save_transcript(video_id, str(txt_path))
    summarize_to_markdown(str(txt_path), str(md_path))


def main():
    st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
    st.title("📽️ YouTube Video Summarizer")
    st.write("Fetch a transcript, summarize it with Groq, then check out the Markdown.")

    if "welcome_msg" not in st.session_state:
        st.session_state.welcome_msg = talk_to_me(
            text="Welcome to Mr. Markdown.",
            filename="welcome.mp3"
        )



    # 1) User inputs
    story_name = st.text_input("🧾 Story Name ", "")
    out_folder = st.text_input("📂 Output folder", "place_holder")
    vid_id = st.text_input("🎥 YouTube video ID", DEFAULT_VIDEO_ID, placeholder="mB0EBW-vDSQ")

    # 2) Generate button
    if st.button("Generate & Preview"):
        if not story_name.strip():
            st.error("Enter a story basename.")
            return
        
        talk_to_me(
            text="Please wait while Groq works some magic",
            filename="wait_for_groq.mp3"
        )

        # ensure output dir exists
        os.makedirs(out_folder, exist_ok=True)
        md_path = Path(out_folder) / f"{Path(story_name).stem}.md"

        # 3) Summarizer 
        lottie_file = (r"lottie_thottie\Cat and Ball.json")
        with open(lottie_file, "r", encoding="utf-8") as infile:
            animation_json = json.load(infile)
        with st_lottie_spinner(animation_source=animation_json, key="spin_me_right_round"):
            try:
                run(story_name, out_folder, vid_id)
            except Exception as e:
                st.error(f"Summarization failed: {e}")
                return

        # 4) Read the markdown and render it
        if md_path.exists():
            talk_to_me(
                text="Markdown is ready for you sirrr.",
                filename="markdown_ready.mp3"
            )

            st.success(f"✅ Summary ready at `{md_path}`")
            md_text = md_path.read_text(encoding="utf-8")
            # clean_story = re.sub(r"^#{1,2}\s", "", md_text, flags=re.MULTILINE)
            st.markdown("---")
            st.subheader("📖 Preview")
            styled_md = f"""
            <div class='preview-box'>
            {md_text}
            </div>
            """

            tab1, tab2 = st.tabs(["✨ Styled", "🧾 Raw Markdown"])
            with tab1:
                st.markdown(styled_md, unsafe_allow_html=True)
            with tab2:
                st.code(md_text, language="markdown")
        else:
            st.error("Something went wrong: markdown file not found.")


if __name__ == "__main__":
    main()