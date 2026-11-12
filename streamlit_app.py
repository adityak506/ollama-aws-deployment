import streamlit as st
import requests

# Change this to your EC2 Public IP
API_URL = "http://16.16.219.247:8000"

st.set_page_config(page_title="Ollama Chat")

st.title("Ollama Chatbot")
st.caption("Testing a self-hosted LLM deployed on AWS EC2 using Ollama")

# ---------------------------------------------------------
# Check API Health
# ---------------------------------------------------------
try:
    health = requests.get(f"{API_URL}/health", timeout=5)

    if health.status_code == 200:
        st.success("Connected to the deployed LLM API")
    else:
        st.error("Unable to connect to the API")
        st.stop()

except Exception as e:
    st.error(f"Connection failed.\n\n{e}")
    st.stop()

# ---------------------------------------------------------
# Load Available Models
# ---------------------------------------------------------
try:
    response = requests.get(f"{API_URL}/models", timeout=10)
    response.raise_for_status()

    models = response.json().get("models", [])
    model_names = [model["name"] for model in models]

except Exception as e:
    st.error(f"Unable to load models.\n\n{e}")
    st.stop()

if not model_names:
    st.warning("No Ollama models found.")
    st.stop()

# ---------------------------------------------------------
# User Input
# ---------------------------------------------------------
selected_model = st.selectbox("Select Model",model_names)

prompt = st.text_area("Enter your prompt",height=150)

# ---------------------------------------------------------
# Generate Response / hit the locally deployed LLM
# ---------------------------------------------------------
if st.button("Generate Response"):

    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    with st.spinner("Generating response..."):

        try:

            response = requests.post(
                f"{API_URL}/generate",
                json={
                    "model": selected_model,
                    "prompt": prompt
                },
                timeout=180
            )

            response.raise_for_status()

            result = response.json()
            
            # # for debugging
            # st.json(result)

            st.subheader("Response")
            st.write(result.get("response", "No response returned."))

        except Exception as e:
            st.error(f"Request failed.\n\n{e}")