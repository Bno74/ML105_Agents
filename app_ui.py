import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration - Must be the first streamlt command
st.set_page_config(page_title="n7ob4", page_icon="🤖")

st.title("🤖 n7ob4")

# Hide Streamlit Style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            [data-testid="stDecoration"] {visibility: hidden !important;}
            [data-testid="stStatusWidget"] {visibility: hidden !important;}
            [data-testid="stHeader"] {display: none !important;}
            header {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    system_prompt = st.text_area("System Persona", value="You are a helpful AI assistant.")
    
    with st.expander("Advanced"):
        temperature = st.slider("Temperature", 0.0, 2.0, 1.0, 0.1)
        max_tokens = st.slider("Max Tokens", 100, 8192, 2048, 100)

    st.divider()
    
    # Download Chat History
    import json
    chat_json = json.dumps(st.session_state.get("messages", []), indent=2)
    st.download_button("📥 Download History", chat_json, "chat_history.json", "application/json")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

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

# File Uploader (Chat Integration)
with st.popover("📎 Attach"):
    uploaded_file = st.file_uploader(
        "Upload Image/PDF", 
        type=["png", "jpg", "jpeg", "pdf"],
        key="chat_uploader" 
    )

# User Input
if prompt := st.chat_input("What is up?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_file:
            st.info(f"📎 Attached: {uploaded_file.name}")

    # Generate Response
    try:
        with st.chat_message("assistant"):
            # Use the model requested by user
            model_id = "gemini-3-flash-preview"
            
            response = None
            retry_count = 0
            max_retries = 3
            
            # Prepare Content
            generation_content = [prompt]
            if uploaded_file:
                # Reset file pointer
                uploaded_file.seek(0)
                if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                    img = Image.open(uploaded_file)
                    generation_content.append(img)
                elif uploaded_file.type == "application/pdf":
                    generation_content.append(types.Part.from_bytes(
                        data=uploaded_file.getvalue(),
                        mime_type="application/pdf"
                    ))
            
            # Load Knowledge Base (Billboards)
            try:
                with open("billboards.csv", "r") as f:
                    kb_data = f.read()
                full_system_prompt = f"{system_prompt}\n\nKnowledge Base (Billboards):\n{kb_data}"
            except Exception as e:
                # Fallback if file missing
                full_system_prompt = system_prompt
            
            placeholder = st.empty()
            
            while retry_count < max_retries:
                try:
                    response = client.models.generate_content(
                        model=model_id,
                        contents=generation_content,
                        config=types.GenerateContentConfig(
                            system_instruction=full_system_prompt,
                            temperature=temperature,
                            max_output_tokens=max_tokens
                        )
                    )
                    break 
                except Exception as e:
                    # Check for Rate Limit (429) or Quota issues
                    error_str = str(e)
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                        retry_count += 1
                        if retry_count == max_retries:
                            raise e
                        
                        # Increase wait time: 20s, 40s, 60s
                        wait_time = retry_count * 20 
                        placeholder.warning(f"⚠️ Rate limit hit. Waiting {wait_time} seconds before retrying... (Attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        placeholder.empty()
                    else:
                        raise e

            try:
                response_text = response.text
                st.markdown(response_text)
                # Add assistant message to state
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                # Often happens if response is blocked by safety filters
                st.warning("⚠️ The model refused to answer (Safety Filter Triggered).")
                st.write(f"Debug details: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
            
    except Exception as e:
        st.error(f"Error: {e}")
