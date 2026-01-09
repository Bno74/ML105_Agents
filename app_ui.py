import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration - Must be the first streamlt command
st.set_page_config(page_title="Gemini ChatBot", page_icon="🤖")

st.title("🤖 Chat with Gemini 3.0 Flash")

# Initialize Client
@st.cache_resource
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_client()

if not client:
    st.error("❌ GEMINI_API_KEY not found in .env file.")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What is up?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    try:
        with st.chat_message("assistant"):
            # Use the model requested by user
            model_id = "gemini-3-flash-preview"
            
            response = client.models.generate_content(
                model=model_id,
                contents=prompt
            )
            response_text = response.text
            st.markdown(response_text)
            
            # Add assistant message to state
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
    except Exception as e:
        st.error(f"Error: {e}")
