import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Elderly Companion AI",
    layout="wide",
)

st.title("Elderly Companion AI — Student Prototype")
st.caption(
    "Use fictional information for testing. "
    "This AI is not a medical or emergency service."
)

SYSTEM_INSTRUCTIONS = """
You are an AI companion for a student demonstration.

Have warm, respectful conversations about everyday life,
food, music, gardening, and memories.

Rules:
- Respond directly to what the user says.
- Use earlier messages to follow the conversation.
- Do not randomly change topics or repeat answered questions.
- Keep most replies to 2–4 short sentences.
- Ask at most one follow-up question.
- If something is unclear, ask for clarification.
- Be honest that you are an AI, not a human caregiver.
- Encourage contact with family, friends, or caregivers when useful.
- Do not diagnose illnesses.
- Never claim you contacted a caregiver or emergency services.
- For a possible emergency, encourage immediate contact with
  local emergency services or someone nearby.
"""


def get_ai_reply(messages):
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    contents = [
        types.Content(
            role="user" if item["role"] == "user" else "model",
            parts=[
                types.Part.from_text(text=item["content"])
            ],
        )
        for item in messages
    ]

    response = client.models.generate_content(
        model=st.secrets.get(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        ),
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
        ),
    )

    return response.text


if "GEMINI_API_KEY" not in st.secrets:
    st.error(
        "Add GEMINI_API_KEY in Streamlit Settings → Secrets."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("Start a new conversation"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.info(
    "Student demonstration only. "
    "No caregiver notifications are sent."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your message here...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Preparing a reply..."):
                reply = get_ai_reply(
                    st.session_state.messages
                )

            if reply:
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )
            else:
                st.warning(
                    "No reply was returned. Please try again."
                )

        except Exception as error:
            error_text = str(error).replace(
                st.secrets["GEMINI_API_KEY"],
                "[API KEY HIDDEN]",
            )
            st.error("The AI service returned this error:")
            st.code(error_text)
# Demo caregiver alert — no external notification is sent.
st.sidebar.divider()
st.sidebar.header("Caregiver Alert — Demo")

if "caregiver_help_requested" not in st.session_state:
    st.session_state.caregiver_help_requested = False

if st.sidebar.button("Request caregiver help"):
    st.session_state.caregiver_help_requested = True

if st.session_state.caregiver_help_requested:
    st.sidebar.warning(
        "DEMO ALERT: Caregiver help requested. "
        "This alert is displayed in the app only. "
        "No caregiver has been contacted."
    )

    if st.sidebar.button("Clear demo alert"):
        st.session_state.caregiver_help_requested = False
        st.rerun()

st.sidebar.caption(
    "For an emergency, contact local emergency services "
    "or someone nearby directly."
)
# Simulated readings — not connected to a real device.
st.sidebar.divider()
st.sidebar.header("Remote Monitoring — Demo")

st.sidebar.caption(
    "SIMULATED DATA: Adjust these values to demonstrate "
    "the dashboard. No real person is being monitored."
)

demo_heart_rate = st.sidebar.slider(
    "Heart rate (bpm)",
    min_value=40,
    max_value=160,
    value=72,
    key="demo_heart_rate",
)

demo_oxygen = st.sidebar.slider(
    "Oxygen saturation (%)",
    min_value=80,
    max_value=100,
    value=98,
    key="demo_oxygen",
)

demo_sleep = st.sidebar.slider(
    "Last night's sleep (hours)",
    min_value=0.0,
    max_value=12.0,
    value=7.0,
    step=0.5,
    key="demo_sleep",
)

demo_steps = st.sidebar.number_input(
    "Steps today",
    min_value=0,
    max_value=50000,
    value=2500,
    step=100,
    key="demo_steps",
)

st.sidebar.subheader("Simulated Readings")

st.sidebar.metric(
    "Heart rate",
    f"{demo_heart_rate} bpm",
)

st.sidebar.metric(
    "Oxygen saturation",
    f"{demo_oxygen}%",
)

st.sidebar.metric(
    "Sleep",
    f"{demo_sleep:.1f} hours",
)

st.sidebar.metric(
    "Steps",
    f"{demo_steps:,}",
)

st.sidebar.info(
    "Demo only: these values are entered manually. "
    "No medical assessment or automatic caregiver "
    "notification is performed."
)
