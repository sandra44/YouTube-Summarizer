# YouTube MCP Server

A Model Context Protocol server that allows you to download subtitles from YouTube and connect them to a LLM.

## Features

- Download transcripts from YouTube videos
- Support for both video IDs and full YouTube URLs
- Timestamps included in transcript
- Works with any MCP-compatible client

## Usage

### In your MCP client configuration:

```json
"mcpServers": {
    "youtube": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/adhikasp/mcp-youtube", "mcp-youtube"]
    },
}
```

## Development

1. Clone the repository

2. Create and activate virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Unix/MacOS
# or .venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv sync
```

4. Run the server:
```bash
python -m youtube_mcp
```

## License

MIT