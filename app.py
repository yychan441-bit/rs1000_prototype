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
        "My chest hurts", "I fell down and can't get up", "Call for help", "I am dizzy and in pain"
    ]
    
    y_train = [
        "Normal", "Normal", "Normal", "Normal",
        "Normal", "Normal", "Normal", "Normal",
        "Normal", "Normal", "Normal",
        "Low Mood", "Low Mood", "Low Mood", "Low Mood",
        "Low Mood", "Low Mood", "Low Mood",
        "Distress", "Distress", "Distress", "Distress"
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
            reply = f"That is wonderful! Speaking of {random.choice(PERSONA['interests'])}, is there a song or kind of music you particularly enjoy?"
            alert_placeholder.success("✅ System Status: Normal. User state is stable.")
        
        # Simulate processing latency (looks more natural)
        time.sleep(1)
        response_placeholder.markdown(reply)
        
        # Save assistant message to memory
        st.session_state.messages.append({"role": "assistant", "content": reply})