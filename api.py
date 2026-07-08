from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from config import Config
from agents.topic_selector import TopicSelector
from agents.moderator import ModeratorAgent
from agents.debater import DebaterAgent
from agents.judge import JudgeAgent
from utils.logger import DebateLogger

# Initialize FastAPI app with metadata
app = FastAPI(
    title="AI Debate API",
    description="Enterprise-grade Multi-Agent Debate System API",
    version="1.0"
)


# --- DATA MODELS ---

class DebateRequest(BaseModel):
    """
    Defines what the user can send to the API.
    """
    topic: Optional[str] = None  # If null, the system generates one
    rounds: int = 3  # Default to 3 rounds


class DebateResponse(BaseModel):
    """
    Defines what the API returns.
    """
    topic: str
    transcript: List[dict]  # The full chat history
    verdict: dict  # The Judge's scorecard


# --- ENDPOINTS ---

@app.post("/run_debate", response_model=DebateResponse)
def run_debate(request: DebateRequest):
    """
    Orchestrates a full debate:
    1. Generates/Validates Topic
    2. Runs the Moderator -> Pro -> Con loop
    3. Runs the Judge
    4. Saves logs (MLOps)
    5. Returns the JSON result
    """
    try:
        # 1. System Validation & Setup
        Config.validate()
        logger = DebateLogger()

        # Initialize Agents (Stateless execution for API)
        moderator = ModeratorAgent()
        pro_agent = DebaterAgent("Agent_Pro", "Pro", "philosophical")
        con_agent = DebaterAgent("Agent_Con", "Con", "skeptical")
        judge = JudgeAgent()

        # 2. Determine Topic
        topic = request.topic
        if not topic:
            # If user didn't provide one, use the AI generator
            topic = TopicSelector().generate_topic()

        history = []

        # 3. Moderator Intro
        intro = moderator.start_debate(topic)
        history.append({"role": "user", "name": "Moderator", "content": intro})

        # 4. The Debate Loop
        for _ in range(request.rounds):
            # Pro Agent Speaks
            msg_pro = pro_agent.speak(topic, history)
            history.append({"role": "assistant", "name": "Agent_Pro", "content": msg_pro})

            # Con Agent Speaks
            msg_con = con_agent.speak(topic, history)
            history.append({"role": "assistant", "name": "Agent_Con", "content": msg_con})

        # 5. Judge's Evaluation
        verdict = judge.evaluate_debate(topic, history)

        # 6. MLOps Logging (Save to file)
        logger.save_log(topic, history, verdict)

        # 7. Return Response
        return {
            "topic": topic,
            "transcript": history,
            "verdict": verdict
        }

    except Exception as e:
        # Return a clean 500 error if something crashes
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """
    Simple endpoint for Docker health checks.
    """
    return {"status": "healthy", "service": "debate-system"}