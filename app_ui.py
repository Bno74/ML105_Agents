import streamlit as st
from google import genai
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration - Must be the first streamlt command
st.set_page_config(page_title="n7ob4", page_icon="🤖")

st.title("🤖 n7ob4")

# Initialize Client
@st.cache_resource
def get_client():
    # Try getting key from environment (Local .env)
    api_key = os.getenv("GEMINI_API_KEY")
    
    # If not found, try getting from Streamlit Secrets (Cloud)
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
            
    if not api_key:
        return None
    
    # Sanitize key (remove whitespaces and potential accidental quotes)
    api_key = api_key.strip().strip('"').strip("'")
            
    return genai.Client(api_key=api_key)

client = get_client()

if not client:
    st.error("❌ GEMINI_API_KEY not found.")
    st.stop()
    
# Test validity immediately
try:
    # Just check if we can list models or do a dummy call (lightweight)
    pass
except Exception as e:
    st.error(f"Error initializing client: {e}")

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
            
            response = None
            retry_count = 0
            max_retries = 3
            
            placeholder = st.empty()
            
            while retry_count < max_retries:
                try:
                    response = client.models.generate_content(
                        model=model_id,
                        contents=prompt
                    )
                    break 
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        retry_count += 1
                        if retry_count == max_retries:
                            raise e
                        
                        wait_time = retry_count * 15 # Wait 15s, 30s...
                        placeholder.warning(f"Rate limit hit. Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        placeholder.empty()
                    else:
                        raise e

            response_text = response.text
            st.markdown(response_text)
            
            # Add assistant message to state
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
    except Exception as e:
        st.error(f"Error: {e}")
