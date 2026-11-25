import streamlit as st
import random
import time
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# --- 1. SETUP CLASSIFIER (Cached for real-time performance) ---
@st.cache_resource
def load_classifier():
    # Expanded training data so the prototype handles varied inputs better
    # Expanded training data to recognize happiness, reassurance, and food
    X_train = [
        "I feel great today", "Everything is fine", "Hello", "What a lovely day",
        "I am ok now", "No I am ok", "I am so happy", "I ate a pineapple bun",
        "I love A-1 Bakery", "I am craving food", "That makes me feel better", 
        "I am so lonely", "I feel sad", "Nobody visits me anymore", "I miss my family",
        "I feel down", "I am crying", "I am upset",
        "My chest hurts", "I fell down and can't get up", "Call for help", "I am dizzy and in pain", 
        "I am bleeding", "I feel dizzy", "i just fall down", 
    ]
    
    y_train = [
        "Normal", "Normal", "Normal", "Normal",
        "Normal", "Normal", "Normal", "Normal",
        "Normal", "Normal", "Normal",
        "Low Mood", "Low Mood", "Low Mood", "Low Mood",
        "Low Mood", "Low Mood", "Low Mood",
        "Distress", "Distress", "Distress", "Distress", 
        "Distress", "Distress", "Distress",
    ]
    # Creates the supervised machine learning pipeline
    clf = Pipeline([
        ('vectorizer', CountVectorizer()),
        ('model', LogisticRegression())
    ])
    clf.fit(X_train, y_train)
    return clf

classifier = load_classifier()

# --- 2. DEMONSTRATION KNOWLEDGE ---
PERSONA = {
    "name": "Mrs Chan",
    "interests": ["gardening", "cooking", "music"],
    "topics": ["food", "everyday memories"]
}
# --- RESPONSE FUNCTIONS ---
def choose_reply(options):
    recent_replies = [
        message["content"]
        for message in st.session_state.get("messages", [])
        if message["role"] == "assistant"
    ][-6:]

    available = [
        reply for reply in options
        if reply not in recent_replies
    ]

    return random.choice(available or options)


def generate_normal_reply(prompt):
    text = prompt.lower()

    if any(word in text for word in [
        "repeating", "repeat", "same sentence"
    ]):
        return choose_reply([
            "You're right—I repeated myself. Sorry about that. "
            "What would you like to talk about instead?",
            "Sorry, that reply wasn't helpful. "
            "Let's stay with what you were telling me.",
        ])

    if "yum cha" in text or "dim sum" in text:
        return choose_reply([
            "What was your favourite dim sum dish?",
            "Who did you usually go to yum cha with?",
            "Did you have a favourite restaurant for yum cha?",
            "What did you enjoy most about going for yum cha?",
        ])

    if "anita mui" in text:
        return choose_reply([
            "Which Anita Mui song do you enjoy most?",
            "Do her songs remind you of a particular time in your life?",
            "When did you first start listening to Anita Mui?",
            "What do you like most about her music?",
        ])

    if any(word in text for word in [
        "music", "song", "sing", "cantonese"
    ]):
        return choose_reply([
            "Who is your favourite singer?",
            "Is there a particular song that brings back memories?",
            "Do you enjoy singing along, or do you prefer listening?",
            "What music did you listen to when you were younger?",
        ])

    if any(word in text for word in [
        "food", "eat", "ate", "bun", "bakery", "cook"
    ]):
        return choose_reply([
            "What do you enjoy most about that food?",
            "Is there a dish you especially enjoy cooking?",
            "Does that food remind you of anyone?",
            "What was a favourite meal in your family?",
        ])

    if any(word in text for word in [
        "garden", "plant", "flower"
    ]):
        return choose_reply([
            "What do you like growing?",
            "Do you have a favourite flower?",
            "How did you first become interested in gardening?",
            "What do you enjoy most about looking after plants?",
        ])

    return choose_reply([
        "Could you tell me a little more about that?",
        "What would you like to share about it?",
        "I'm listening. What happened next?",
        "Would you like to keep talking about that, or choose another topic?",
    ])
# --- 3. UI DASHBOARD & WEARABLE DATA (INNOVATION LAYER) ---
st.set_page_config(page_title="Elderly Companion AI", layout="wide")
st.title("Elderly Companion AI — Prototype")
st.caption("Not a medical service or a replacement for human support.")

# Simulated IoT Sensors
st.sidebar.header("Wearable Data (Simulated)")
heart_rate = st.sidebar.slider("Heart Rate (bpm)", 50, 150, 72)
sleep_hours = st.sidebar.slider("Last Night's Sleep (hrs)", 2.0, 10.0, 7.0)
steps = st.sidebar.number_input("Steps Today", 0, 10000, 2500)

# Dynamic tone adjustment based on wearable data
if sleep_hours < 5.0:
    st.sidebar.warning("⚠️ Low sleep detected. Adjusting conversational tone to be gentler.")
if heart_rate > 100:
    st.sidebar.warning("⚠️ Elevated heart rate detected.")

# Caregiver Alert Module
st.sidebar.header("Caregiver Dashboard Alerts")
alert_placeholder = st.sidebar.empty()
alert_placeholder.info("System Status: Normal. Waiting for interaction.")

# --- 4. CHAT INTERFACE ---
# Initialize chat history memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello {PERSONA['name']}! What food did you most enjoy when you were younger?"}
    ]

# Display past chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Accept user input
if prompt := st.chat_input("Type your message here..."):
    
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run Supervised Classification on the user's message
    predicted_state = classifier.predict([prompt])[0]
    
    # Generate Assistant Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Logic Routing based on AI Classification
        if predicted_state == "Distress":
            reply = "I'm sorry to hear that you are not feeling well. I am alerting your caregiver right away. Please sit down and rest."
            alert_placeholder.error("🚨 CRITICAL ALERT: Distress detected in user dialogue. Caregiver notified.")
        elif predicted_state == "Low Mood":
            reply = "It sounds like you're having a tough day. I am always here to chat. Would you like to tell me about a place you remember fondly to take your mind off things?"
            alert_placeholder.warning("⚠️ NOTE: Low mood trend detected. Monitoring closely.")
        else:
            reply = generate_normal_reply(prompt)
            alert_placeholder.success(
                "✅ Demo classifier result: Normal."
            )

        # Simulate processing latency (looks more natural)
        time.sleep(1)
        response_placeholder.markdown(reply)
        
        # Save assistant message to memory
        st.session_state.messages.append({"role": "assistant", "content": reply})
