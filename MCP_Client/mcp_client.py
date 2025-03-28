import streamlit as st
import requests
import openai
import tempfile
import base64

# Azure OpenAI API credentials
AZURE_OPENAI_ENDPOINT = "https://sandr-m8rotipa-eastus2.cognitiveservices.azure.com"
AZURE_OPENAI_KEY = "1wRkUmrtNcacZiSpb9I9sR0kZ8diEc4j0SePv6bwLHWmf31jtpHaJQQJ99BCACHYHv6XJ3w3AAAAACOGvhYZ"
AZURE_DEPLOYMENT_NAME = "gpt-4o"  

# OpenAI API client setup
client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2023-03-15-preview",  # Adjust based on Azure's latest version
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

st.title("YouTube Transcript & Summarization 🎬")

video_url = st.text_input("Enter YouTube Video URL")
with_timestamps = st.checkbox("Include timestamps")
language = st.selectbox("Select Language", ["en", "es", "fr", "de", "hi"])

# Store transcript in session state
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""
if "transcript_generated" not in st.session_state:
    st.session_state.transcript_generated = False  # Track if transcript is generated

col1, col2 = st.columns([1, 1])

transcript_file = None  

if video_url.strip():
    response = requests.post(
        "http://localhost:8080/get_transcript",
        json={"video_url": video_url, "with_timestamps": with_timestamps, "language": language}
    )

    if response.status_code == 200:
        transcript_text = response.json()["text"]
        st.session_state.transcript_text = transcript_text  
        st.session_state.transcript_generated = True  

        transcript_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        transcript_file.write(transcript_text.encode("utf-8"))
        transcript_file.close()

with col1:
    if transcript_file:
        with open(transcript_file.name, "rb") as f:
            st.download_button(
                label="Generate Transcript 📄",
                data=f,
                file_name="transcript.txt",
                mime="text/plain",
            )
    else:
        st.download_button(
            label="Generate Transcript 📄",
            data="",
            file_name="transcript.txt",
            mime="text/plain",
            disabled=True
        )

with col2:
    summarize_btn = st.button("Summarize 📝", disabled=not st.session_state.transcript_generated)

if summarize_btn:
    with st.spinner("Generating summary..."):
        try:
            response = client.chat.completions.create(
                model=AZURE_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that summarizes YouTube transcripts and extracts key takeaways."},
                    {"role": "user", "content": f"Provide a one-line summary of the video and then list three key takeaways from the transcript. Do not add any formatting such as making the headers bold and do not start the summary section with Summary:\n{st.session_state.transcript_text}"}
                ],
                max_tokens=350
            )
            summary_response = response.choices[0].message.content.strip()

            # Extract summary and takeaways
            parts = summary_response.split("\n\n")
            summary = parts[0].strip() if len(parts) > 0 else "No summary available."
            raw_takeaways = "\n".join(parts[1:]).strip() if len(parts) > 1 else "No takeaways available."

            takeaway_list = [
                point.lstrip("-*0123456789. ").strip()  
                for point in raw_takeaways.split("\n") if point.strip()
            ]
            last_three_takeaways = takeaway_list[-3:]  

            st.subheader("📜 Summary")
            st.markdown(
                f"""
                <div style="padding: 10px; background-color: #f9f9f9; border-radius: 10px; border-left: 5px solid #4CAF50;">
                    <p style="font-size: 16px; color: #333; margin-bottom: 0;">{summary}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.subheader("📌 Key Takeaways")
            st.markdown("<ul style='padding-left: 20px;'>", unsafe_allow_html=True)
            for point in last_three_takeaways:
                st.markdown(
                    f"<li style='font-size: 16px; color: #555; margin-bottom: 5px;'>{point}</li>",
                    unsafe_allow_html=True
                )
            st.markdown("</ul>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error generating summary: {e}")