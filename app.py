import time
import streamlit as st
from config import Config
from agents.topic_selector import TopicSelector
from agents.moderator import ModeratorAgent
from agents.debater import DebaterAgent
from agents.judge import JudgeAgent
from utils.logger import DebateLogger

# --- CONFIGURATION ---
st.set_page_config(
    page_title="AI Debate Arena",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Chat Bubbles & UI
st.markdown("""
<style>
    .stChatMessage { padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; }

    /* Blue Bubble for Pro */
    .pro-bubble { 
        background-color: #e3f2fd; 
        border-left: 5px solid #2196F3; 
        color: #0d47a1;
        padding: 15px;
        border-radius: 10px;
        font-size: 16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }

    /* Red Bubble for Con */
    .con-bubble { 
        background-color: #ffebee; 
        border-left: 5px solid #F44336; 
        color: #b71c1c;
        padding: 15px;
        border-radius: 10px;
        font-size: 16px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }

    /* Yellow Bubble for Moderator */
    .mod-bubble { 
        background-color: #fffde7; 
        border-left: 5px solid #FFEB3B; 
        color: #f57f17;
        padding: 15px;
        border-radius: 10px;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "history" not in st.session_state:
    st.session_state.history = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "topic" not in st.session_state:
    st.session_state.topic = ""


# --- LOAD AGENTS ---
@st.cache_resource
def load_agents():
    """Initialize agents once to save resources."""
    Config.validate()
    return {
        "moderator": ModeratorAgent(),
        "pro": DebaterAgent("Agent_Pro", "Pro", "philosophical"),
        "con": DebaterAgent("Agent_Con", "Con", "skeptical"),
        "judge": JudgeAgent(),
        "topic_gen": TopicSelector(),
        "logger": DebateLogger()
    }


agents = load_agents()


# --- HELPER FUNCTION: TYPEWRITER EFFECT ---
def stream_text(text, css_class, title, placeholder, speed=0.03):
    """
    Simulates typing effect for a given text inside a styled bubble.
    """
    full_response = ""
    # Create the HTML structure
    bubble_start = f"<div class='{css_class}'><b>{title}:</b><br>"
    bubble_end = "</div>"

    # Split by words to ensure HTML doesn't break mid-tag
    words = text.split()

    for word in words:
        full_response += word + " "
        # Add a blinking cursor effect
        placeholder.markdown(f"{bubble_start}{full_response}▌{bubble_end}", unsafe_allow_html=True)
        time.sleep(speed)

    # Final render without cursor
    placeholder.markdown(f"{bubble_start}{full_response}{bubble_end}", unsafe_allow_html=True)


# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("Configure your AI Debate settings below.")

    # Topic Controls
    if st.button("🎲 Generate Random Topic", use_container_width=True):
        with st.spinner("Generating topic..."):
            st.session_state.topic = agents["topic_gen"].generate_topic()

    user_topic = st.text_area("Current Topic:", value=st.session_state.topic, height=150)
    if user_topic != st.session_state.topic:
        st.session_state.topic = user_topic

    st.divider()

    # Settings
    rounds = st.slider("Number of Rounds", 1, 5, 3)

    # This slider controls how fast the "typing" happens
    typing_speed = st.select_slider(
        "Typing Speed",
        options=[0.05, 0.03, 0.01, 0.001],
        value=0.03,
        format_func=lambda x: "Slow" if x == 0.05 else ("Normal" if x == 0.03 else "Fast" if x == 0.01 else "Instant")
    )

    st.divider()

    if st.button("🚀 Start Live Debate", type="primary", use_container_width=True):
        st.session_state.history = []
        st.session_state.processing = True
        st.rerun()

# --- MAIN PAGE ---
st.title("🤖 Multi-Agent Debate Arena")

if not st.session_state.topic:
    st.info("👈 Please generate or enter a topic in the sidebar to begin.")
    st.stop()

st.markdown(f"### Topic: {st.session_state.topic}")
st.divider()

chat_container = st.container()

# --- THE DEBATE LOGIC ---
if st.session_state.processing:

    # 1. MODERATOR INTRO
    with chat_container:
        with st.chat_message("user", avatar="🎤"):
            intro_placeholder = st.empty()
            intro_text = agents["moderator"].start_debate(st.session_state.topic)

            # Stream the intro
            stream_text(intro_text, "mod-bubble", "Moderator", intro_placeholder, typing_speed)

            st.session_state.history.append({"role": "user", "name": "Moderator", "content": intro_text})
            time.sleep(0.5)

    # 2. DEBATE ROUNDS
    for i in range(1, rounds + 1):
        with chat_container:
            st.markdown(f"##### Round {i}/{rounds}")

            # --- PRO AGENT ---
            with st.chat_message("assistant", avatar="🟦"):
                message_placeholder = st.empty()
                with st.spinner(f"Agent Pro is thinking (Round {i})..."):
                    # Backend Call
                    pro_text = agents["pro"].speak(st.session_state.topic, st.session_state.history)

                # Frontend Streaming
                stream_text(pro_text, "pro-bubble", "Agent Pro", message_placeholder, typing_speed)

                # Save to History
                st.session_state.history.append({"role": "assistant", "name": "Agent_Pro", "content": pro_text})

            time.sleep(0.5)  # Pause between turns

            # --- CON AGENT ---
            with st.chat_message("assistant", avatar="🟥"):
                message_placeholder = st.empty()
                with st.spinner(f"Agent Con is thinking (Round {i})..."):
                    # Backend Call
                    con_text = agents["con"].speak(st.session_state.topic, st.session_state.history)

                # Frontend Streaming
                stream_text(con_text, "con-bubble", "Agent Con", message_placeholder, typing_speed)

                # Save to History
                st.session_state.history.append({"role": "assistant", "name": "Agent_Con", "content": con_text})

            time.sleep(0.5)

    # 3. JUDGE EVALUATION
    with chat_container:
        st.divider()
        st.markdown("### ⚖️ Final Verdict")

        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("The Judge is reviewing the transcript..."):
                verdict = agents["judge"].evaluate_debate(st.session_state.topic, st.session_state.history)

            # --- Display Scorecard (Visual) ---
            winner = verdict.get('winner', 'Tie')
            reasoning = verdict.get('reasoning', 'No reasoning provided.')

            scores_pro = verdict.get('scores', {}).get('Pro', {})
            scores_con = verdict.get('scores', {}).get('Con', {})

            # Color code the winner box
            if "Pro" in winner:
                st.success(f"🏆 Winner: {winner}")
            elif "Con" in winner:
                st.error(f"🏆 Winner: {winner}")
            else:
                st.warning(f"🤝 Result: {winner}")

            # Metric Columns
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🟦 Pro Scores")
                st.metric("Logic", f"{scores_pro.get('logic', 0)}/10")
                st.metric("Evidence", f"{scores_pro.get('evidence', 0)}/10")
            with col2:
                st.markdown("#### 🟥 Con Scores")
                st.metric("Logic", f"{scores_con.get('logic', 0)}/10")
                st.metric("Evidence", f"{scores_con.get('evidence', 0)}/10")

            st.info(f"**Judge's Reasoning:**\n\n{reasoning}")

            # MLOps: Save Log
            filename = agents["logger"].save_log(st.session_state.topic, st.session_state.history, verdict)
            st.toast("Debate transcript saved successfully!")

    st.session_state.processing = False