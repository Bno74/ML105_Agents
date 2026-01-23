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
            
            /* Mobile Optimization */
            @media (max-width: 768px) {
                .block-container {
                    padding-top: 1rem !important;
                    padding-bottom: 5rem !important;
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                }
                .element-container {
                    width: 100% !important;
                }
                [data-testid="stChatInput"] {
                    padding-bottom: 20px;
                }
                h1 {
                    font-size: 1.8rem !important;
                }
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    default_persona = """You are an expert Billboard & Advertising Consultant for 'n7ob4'. 
Your goal is to provide deep, strategic insights. DON'T just list data; analyze it.

Guidelines:
1. **Categorize Recommendations**: Group options by strategy (e.g., "Top Priority", "High Visibility", "Budget-Friendly").
2. **Provide Reasoning**: For each location, explain WHY it fits the user's need (e.g., "Perfect for students due to proximity to City College").
3. **Data-Driven Insights**: Use the KB data (Price, Dimension, Hours) to back up your claims.
   - High Price (>150) = Premium/Luxury.
   - Low Price (<100) = Cost-Effective/Mass Reach.
4. **Comparison Table**: IF providing multiple options (3+), ALWAYS end with a **Markdown Summary Table** matching locations to Price, Size, and Strategy.
5. **Formatting**: For detailed sections, use Bold headers and bullet points. For the summary, use a clear Table."""

    system_prompt = st.text_area("System Persona", value=default_persona, height=250)
    
    # Ensure system_prompt is available globally if needed (redundant but safe)
    if "system_prompt" not in locals() or not system_prompt:
        system_prompt = default_persona
    
    with st.expander("Advanced"):
        temperature = st.slider("Temperature", 0.0, 2.0, 0.4, 0.1) # Lowered to 0.4 for accuracy
        max_tokens = st.slider("Max Tokens", 100, 8192, 4096, 100)

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

# Suggested Questions
suggested_prompt = None
sq_cols = st.columns(3)
if sq_cols[0].button("💎 Best for Luxury?"):
    suggested_prompt = "Provide a strategic analysis of the best billboard locations for a Luxury Brand, including reasoning."
if sq_cols[1].button("💰 Cheap Options?"):
    suggested_prompt = "Identify cost-effective billboard locations and explain their value proposition for low budgets."
if sq_cols[2].button("🆚 Gulshan vs Dhanmondi"):
    suggested_prompt = "Compare Gulshan vs Dhanmondi billboards with a strategic focus on audience and return on investment."

sq_cols_2 = st.columns(3)
if sq_cols_2[0].button("🎓 Student Target?"):
    suggested_prompt = "Recommend the top locations to target university students, explaining why each spot works."
if sq_cols_2[1].button("📈 High Traffic?"):
    suggested_prompt = "Identify high-visibility locations and analyze their traffic potential for brand awareness."
if sq_cols_2[2].button("🗺️ Chittagong Spots?"):
    suggested_prompt = "Provide a strategic overview of billboard options in Chittagong and their best use cases."

sq_cols_3 = st.columns(3)
if sq_cols_3[0].button("🌊 Cox's Bazar?"):
    suggested_prompt = "Analyze the advertising potential in Cox's Bazar, specifically targeting tourists."
if sq_cols_3[1].button("🍃 Sylhet Options?"):
    suggested_prompt = "Recommend the best billboard spots in Sylhet based on location value and audience."
if sq_cols_3[2].button("💡 Best LED Screens?"):
    suggested_prompt = "Evaluate the best LED/Digital screens available, focusing on display quality and impact."

sq_cols_4 = st.columns(3)
if sq_cols_4[0].button("🏰 Rajshahi & Rangpur?"):
    suggested_prompt = "Analyze the billboard landscape in Rajshahi and Rangpur, offering key recommendations."
if sq_cols_4[1].button("🛣️ Comilla & Feni?"):
    suggested_prompt = "Provide a strategic breakdown of billboard opportunities in Comilla and Feni."
if sq_cols_4[2].button("🏙️ Bogura & Narayanganj?"):
    suggested_prompt = "Evaluate billboard advertising availability in Bogura and Narayanganj."

# User Input
if prompt := (st.chat_input("What is up?") or suggested_prompt):
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
            # Use a more stable model to avoid Rate Limits
            # Fallback Strategy for Rate Limits
            fallback_models = [
                "gemini-2.5-flash",                  # Newest, likely good quota
                "gemini-2.0-flash",                  # Stable workhorse
                "gemini-2.0-flash-lite-preview-02-05", # Fast/Lite
                "gemini-1.5-flash",                  # Reliable previous generation
                "gemini-2.0-flash-001",              # Older stable 2.0
                "gemini-flash-latest",               # Alias for latest flash
                "gemini-1.5-pro-latest"              # Heavy duty fallback
            ]
            
            # Prepare Content (Restored)
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
            
            # Load Knowledge Base (Billboards) (Restored)
            try:
                with open("billboards.csv", "r") as f:
                    kb_data = f.read()
                full_system_prompt = f"{system_prompt}\n\nKnowledge Base (Billboards):\n{kb_data}"
                st.toast(f"✅ Knowledge Base Loaded ({len(kb_data)} chars)", icon="📚") 
                # st.write(f"Debug: Loaded {len(kb_data)} chars of billboard data.")
            except Exception as e:
                # Fallback if file missing
                full_system_prompt = system_prompt
                st.error(f"⚠️ Failed to load Knowledge Base: {e}")
            
            response = None
            successful_model = None
            error_stats = []
            
            for model_id in fallback_models:
                retry_count = 0
                max_retries = 2
                
                # Check for uploaded file compatibility (some models might not support PDF/Images well, but these Flash ones do)
                
                try:
                     while retry_count < max_retries:
                        try:
                            # Placeholder for status update
                            status_msg = f"Generating with {model_id}..." if retry_count == 0 else f"Retrying with {model_id} (Attempt {retry_count+1})..."
                            placeholder = st.empty()
                            # placeholder.info(status_msg) 

                            response = client.models.generate_content(
                                model=model_id,
                                contents=generation_content,
                                config=types.GenerateContentConfig(
                                    system_instruction=full_system_prompt,
                                    temperature=temperature,
                                    max_output_tokens=max_tokens
                                )
                            )
                            successful_model = model_id
                            placeholder.empty()
                            break # Success! Break retry loop
                        
                        except Exception as e:
                            error_str = str(e)
                            # Handle Rate Limits
                            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                                retry_count += 1
                                if retry_count == max_retries:
                                    # This model failed completely, let's try the next one in the list
                                    placeholder.warning(f"⚠️ {model_id} is busy. Switching model...")
                                    time.sleep(2) # Increased from 1s to 2s to let quota cool down
                                    placeholder.empty()
                                    raise e # Trigger outer loop to continue to next model
                                else:
                                    wait_time = retry_count * 5 # Short wait before retry same model
                                    time.sleep(wait_time)
                            else:
                                raise e # Fatal error (not rate limit), stop everything
                    
                     if response:
                        break # Success! Break model loop
                        
                except Exception as e:
                    # Capture the error to debug why this model failed
                    error_stats.append(f"{model_id}: {str(e)}")
                    continue # Try next model
            
            if not response:
                st.error("⚠️ All available models are currently overloaded (or incompatible).")
                with st.expander("🔍 Debug: Why did they fail?"):
                    for err in error_stats:
                        st.write(err)
            else:
                try:
                    response_text = response.text
                    st.markdown(response_text)
                    # Add assistant message to state
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Debug Info: Why did it stop?
                    if response.candidates:
                         finish_reason = response.candidates[0].finish_reason
                         # Check if it finished naturally (STOP)
                         # finish_reason might be an Enum or Int depending on version, convert to str to be safe
                         if str(finish_reason) != "FinishReason.STOP" and str(finish_reason) != "1":
                             st.warning(f"⚠️ Response stopped due to: {finish_reason}")
                         
                         # Usage Metadata (Optional)
                         try:
                             usage = response.usage_metadata
                             st.caption(f"Tokens: {usage.prompt_token_count} query + {usage.candidates_token_count} response")
                         except:
                             pass
                except Exception as e:
                    # Often happens if response is blocked by safety filters
                    st.warning("⚠️ The model refused to answer (Safety Filter Triggered).")
                    try:
                        st.write(f"Debug details: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
                    except:
                        pass

    except Exception as e:
        st.error(f"Error: {e}")
