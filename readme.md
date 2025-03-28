# YouTube Summarize MCP Server & Client

## Overview
- Migrated the MCP Server from Flask to FastAPI for better performance and async support.
- MCP Client, built using Streamlit, for an interactive user interface.
- Improved API response times and scalability.

## Features
- **FastAPI-based MCP Server**: Handles transcript extraction from YouTube videos.
- **Streamlit-based MCP Client**: Provides an interactive UI for users to input YouTube URLs and receive summaries.
- **Summarization via GPT-4o**: Uses external API calls for generating concise summaries from extracted transcripts.

## MCP Server
- **Original MCP Server Repo**: https://github.com/adhikasp/mcp-youtube
- Converted from the original Flask-based to FastAPI (mcp_youtube.py).
**Functionality:**
- Accepts YouTube video URLs.
- Extracts the transcript using YouTube API.
- Sends the extracted transcript as JSON response.
Note: The MCP Server does not generate summaries; it only extracts transcripts.

## MCP Client
- Streamlit-based MCP Client which provides an easy-to-use UI for interacting with the MCP Server.
**Functionality:**
- Allows users to input YouTube URLs.
- Fetches the transcript from the MCP Server.
- Sends the transcript to Azure OpenAI GPT-4o for summarization.
- Displays the summarized text in the UI.

### How to Run
1. **Start the MCP Server:**
   ```bash
   uvicorn mcp_youtube:app --host 0.0.0.0 --port 8000
   ```
2. **Start the MCP Client:**
   ```bash
   streamlit run mcp_client.py
   ```
3. **Usage:**
Open the Streamlit UI in the browser to interact with the API visually.
- Enter a YouTube URL in the Streamlit UI.
- Click submit to extract transcript and generate a summary.

This setup ensures a smooth and efficient way to summarize YouTube videos using FastAPI and Streamlit!

