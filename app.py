import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Elderly Companion AI",
    layout="wide",
)

st.title("Elderly Companion AI — Student Prototype")

st.caption(
    "This is an AI prototype, not a medical service. "
    "Please use fictional information when testing."
)

SYSTEM_INSTRUCTIONS = """
You are an AI companion for a student demonstration.

Have warm, respectful conversations about everyday life,
food, music, gardening, and memories.

Follow these rules:
- Respond directly to what the user says.
- Use earlier messages to understand the conversation.
- Do not randomly change the topic.
- Do not ask questions the user has already answered.
- Keep most replies to 2–4 short sentences.
- Ask no more than one follow-up question at a time.
- Do not repeatedly say "That is wonderful."
- If a message is unclear, ask for clarification.
- Be honest that you are an AI, not a human caregiver.
- Encourage human contact when appropriate.
- Do not diagnose illnesses or claim someone is medically stable.
- Never claim you notified a caregiver or called emergency services.
- For a possible emergency, encourage the user to contact local
  emergency services or someone nearby immediately.
"""

if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "Your API key is missing. "
        "Add GEMINI_API_KEY in Streamlit Settings → Secrets."
    )
    st.stop()

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model_name = st.secrets.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

# Demonstration dashboard only.
st.sidebar.header("Wearable Data — Simulated")

st.sidebar.slider(
    "Heart Rate (bpm)",
    min_value=50,
    max_value=150,
    value=72,
)

st.sidebar.slider(
    "Last Night's Sleep (hrs)",
    min_value=2.0,
    max_value=10.0,
    value=7.0,
)

st.sidebar.number_input(
    "Steps Today",
    min_value=0,
    max_value=10000,
    value=2500,
)

st.sidebar.info(
    "These readings are simulated. "
    "No health assessment or caregiver notification is performed."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm an AI companion prototype. "
                "What would you like to talk about today?"
            ),
        }
    ]

if st.sidebar.button("Start a new conversation"):
    del st.session_state["messages"]
    st.rerun()

# Display the conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new message.
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the conversation to the model.
    contents = [
        types.Content(
            role=(
                "user"
                if message["role"] == "user"
                else "model"
            ),
            parts=[
                types.Part.from_text(
                    text=message["content"]
                )
            ],
        )
        for message in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        try:
            with st.spinner("Preparing a reply..."):
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTIONS,
                    ),
                )

            if response.text:
                reply = response.text
                st.markdown(reply)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply,
                    }
                )
            else:
                st.warning(
                    "No reply was returned. "
                    "Please try rephrasing your message."
                )

                except Exception as error:
            # Hide the API key if it appears in the error.
            error_text = str(error).replace(
                st.secrets["GEMINI_API_KEY"],
                "[API KEY HIDDEN]",
            )

            st.error("The AI service returned this error:")
            st.code(error_text)
