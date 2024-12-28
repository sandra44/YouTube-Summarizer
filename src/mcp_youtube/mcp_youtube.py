from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound
from youtube_transcript_api._transcripts import Transcript
from urllib.parse import urlparse, parse_qs
import asyncio
import pydantic

# Create server instance
server = Server("youtube-transcript")

class YoutubeTranscript(pydantic.BaseModel):
    video_url: str
    with_timestamps: bool = False
    language: str = "en"

def extract_video_id(url: str) -> str:
    """Extract video ID from various forms of YouTube URLs."""
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed.path[1:]
    if parsed.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query)['v'][0]
        elif parsed.path.startswith('/v/'):
            return parsed.path[3:]
    raise ValueError("Could not extract video ID from URL")

def get_transcript(video_id: str, with_timestamps: bool = False, language: str = "en") -> str:
    """Get transcript for a video ID and format it as readable text."""
    transcript: Transcript = None
    available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    try:
        transcript = available_transcripts.find_transcript([language])
    except NoTranscriptFound:
        for t in available_transcripts:
            transcript = t
            break
        else:
            return f"No transcript found for video {video_id}"
    transcript = transcript.fetch()
    if with_timestamps:
        def format_timestamp(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if hours > 0:
                return f"[{hours}:{minutes:02d}:{secs:02d}]"
            return f"[{minutes}:{secs:02d}]"
            
        return "\n".join(f"{format_timestamp(entry['start'])} {entry['text']}" for entry in transcript)
    else:
        return "\n".join(entry['text'] for entry in transcript)

@server.list_tools()
async def handle_list_tools() -> types.ListToolsResult:
    return [
        types.Tool(
            name="youtube-transcript",
            description="Get transcript from YouTube videos",
            inputSchema=YoutubeTranscript.model_json_schema()
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, str]) -> list[types.TextContent]:
    # Handle both video IDs and full URLs
    video_param = arguments["video_url"]
    language = arguments.get("language", "en")
    with_timestamps = arguments.get("with_timestamps", False)
    try:
        video_id = extract_video_id(video_param)
    except ValueError:
        video_id = video_param  # Assume it's already a video ID

    transcript_text = get_transcript(video_id, with_timestamps, language)
    
    return [
        types.TextContent(
                type="text",
                text=transcript_text
        )
    ]

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="youtube-transcript",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
