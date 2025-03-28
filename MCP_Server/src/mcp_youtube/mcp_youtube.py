from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import uvicorn

# FastAPI instance
app = FastAPI()

class TranscriptRequest(BaseModel):
    video_url: str
    with_timestamps: bool = False
    language: str = "en"

def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed.path[1:]
    if parsed.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query)['v'][0]
        elif parsed.path.startswith('/v/'):
            return parsed.path[3:]
        elif parsed.path.startswith('/shorts/'):
            return parsed.path[8:]
    raise ValueError("Could not extract video ID from URL")

def get_transcript(video_id: str, with_timestamps: bool, language: str) -> str:
    """Fetch and format transcript"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    except NoTranscriptFound:
        return "No transcript found"

    if with_timestamps:
        return "\n".join(f"[{entry['start']:.2f}] {entry['text']}" for entry in transcript)
    else:
        return "\n".join(entry["text"] for entry in transcript)

@app.post("/get_transcript")
async def fetch_transcript(request: TranscriptRequest):
    try:
        video_id = extract_video_id(request.video_url)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    transcript = get_transcript(video_id, request.with_timestamps, request.language)
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not available")
    
    return {"text": transcript}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
