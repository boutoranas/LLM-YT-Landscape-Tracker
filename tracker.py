import os
import json
import yt_dlp
import traceback
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Load channel list from dataset/channels.json if available, otherwise fall back to defaults.
DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")
DATASET_CHANNELS_PATH = os.path.join(DATASET_DIR, "channels.json")
try:
    with open(DATASET_CHANNELS_PATH, "r", encoding="utf-8") as f:
        CHANNELS = json.load(f)
        if not isinstance(CHANNELS, list):
            raise ValueError("channels.json must contain a JSON array of URLs")
except Exception as e:
    print(f"Warning: could not load dataset/channels.json ({e}), using built-in channel list")
    CHANNELS = [
        "https://www.youtube.com/@AndrejKarpathy",
        "https://www.youtube.com/@TwoMinutePapers",
        "https://www.youtube.com/@YannicKilcher",
        "https://www.youtube.com/@MatthewBerman"
    ]
DB_FILE = "data.json"
client = None

# Default model name; override with GEMINI_MODEL env var if needed.
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PROJECT_ID = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("SERVICE_ACCOUNT")

if SERVICE_ACCOUNT_PATH and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.path.exists(SERVICE_ACCOUNT_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH

def get_recent_videos(channel_url, limit=2):
    ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_ext': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        dict_meta = ydl.extract_info(f"{channel_url}/videos", download=False)
        return dict_meta['entries'][:limit]


def get_video_speaker(video, channel_url):
    return video.get('uploader') or video.get('channel') or channel_url.rsplit('/', 1)[-1]

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=("en",))
        return " ".join(snippet.text for snippet in transcript)
    except:
        return "No transcript available."

def analyze_content(speaker, title, transcript, context_summary):
    global client

    if client is None:
        client = genai.Client(
				vertexai=True,
				project=PROJECT_ID,
				location=VERTEX_LOCATION,
			)

    prompt = f"""
    You are a technical AI researcher. Analyze this YouTube video transcript.
    Speaker: {speaker}
    Title: {title}
    Transcript snippet: {transcript[:2000]}
    
    Context of other recent LLM videos: {context_summary}

    Return a JSON object with (respond with JSON only, no extra text):
    1. topics: List of technical themes (e.g., RAG, Quantization).
    2. summary: 2-sentence breakdown of what the creator actually says.
    3. relationship: How this connects to the recent LLM landscape (e.g. "Contradicts Karpathy's view on X" or "Builds on the Llama 3 release").
    """
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={"temperature": 0.0, "response_mime_type": "application/json"},
        )
        response_text = getattr(response, "text", None)
        if not response_text and getattr(response, "candidates", None):
            parts = response.candidates[0].content.parts
            response_text = "".join(getattr(part, "text", "") for part in parts)
        return json.loads(response_text)
    except Exception as e:
        # Log the underlying error so it's visible in the terminal
        print("Gemini API error:", type(e).__name__, str(e))
        traceback.print_exc()
        # If the response object exists, try to print it for debugging
        try:
            if 'response' in locals() and getattr(response, 'text', None):
                print('Raw response.text:', response.text)
        except Exception:
            pass
        # If parsing fails or the API errored, return a safe fallback
        return {
            "topics": [],
            "summary": "Analysis unavailable.",
            "relationship": "Unknown"
        }


def load_existing_data():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return []

def main():
    data = load_existing_data()
    records_by_id = {v['id']: v for v in data}

    context_str = ", ".join([v['title'] for v in data[-5:]])

    for channel in CHANNELS:
        videos = get_recent_videos(channel)
        for v in videos:
            speaker = get_video_speaker(v, channel)
            existing = records_by_id.get(v['id'])
            needs_refresh = (
                existing is None
                or not existing.get('speaker')
                or not existing.get('transcript')
                or not existing.get('topics')
                or existing.get('summary') == 'Analysis unavailable.'
                or existing.get('relationship') == 'Unknown'
            )

            if needs_refresh:
                print(f"Processing: {v['title']}")
                transcript = get_transcript(v['id'])
                analysis = analyze_content(speaker, v['title'], transcript, context_str)

                record = {
                    "id": v['id'],
                    "speaker": speaker,
                    "title": v['title'],
                    "url": f"https://youtu.be/{v['id']}",
                    "transcript": transcript,
                    "topics": analysis['topics'],
                    "summary": analysis['summary'],
                    "relationship": analysis['relationship']
                }

                if existing is None:
                    data.append(record)
                else:
                    existing.update(record)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()