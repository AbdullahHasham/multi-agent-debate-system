import json
import random
import logging
from openai import OpenAI
from config import Config
from agents.prompts import AgentPrompts
from utils.tools import search_web

# Initialize Logger
logger = logging.getLogger("__name__")


class DebaterAgent:
    """
    An AI agent that participates in structured debates using a ReAct (Reason+Act) flow.
    """

    def __init__(self, name: str, position: str, style: str = "logical"):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.name = name
        self.position = position
        self.style = style

    def speak(self, topic: str, conversation_history: list) -> str:
        """
        Generates a debate argument by planning, researching, and speaking.

        Args:
            topic (str): The debate resolution.
            conversation_history (list): Previous messages in the debate.

        Returns:
            str: The agent's argument.
        """
        # --- 0. ANALYZE CONTEXT ---
        if not topic:
            raise ValueError("Topic cannot be empty.")

        opponent_argument = "This is the opening statement. You speak first."
        if conversation_history:
            last_msg = conversation_history[-1]
            if last_msg.get("role") == "assistant":
                opponent_argument = f"OPPONENT SAID: '{last_msg['content'][:300]}...'"

        turns = len(conversation_history)
        round_lens = "General Overview"
        if turns > 2: round_lens = "Economic & Societal Impact"
        if turns > 4: round_lens = "Ethics & Human Rights"
        if turns > 6: round_lens = "Future Implications & Safety"

        # --- 1. THE PLANNING STEP ---
        side_goal = "Support the resolution" if self.position == "Pro" else "OPPOSE the resolution"

        plan_system_msg = AgentPrompts.DEBATER_PLAN.format(
            name=self.name,
            position=self.position,
            topic=topic,
            side_goal=side_goal,
            opponent_argument=opponent_argument
        )

        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[{"role": "system", "content": plan_system_msg}],
                response_format={"type": "json_object"}
            )
            plan = json.loads(response.choices[0].message.content)
            logger.info(f"{self.name} Plan: {plan}")  # Log the plan
        except Exception as e:
            logger.error(f"{self.name} Planning Failed: {e}", exc_info=True)
            plan = {"needs_search": False}

        # --- 2. THE TOOL EXECUTION ---
        context_knowledge = ""
        if plan.get("needs_search"):
            query = plan.get("search_query")
            try:
                search_results = search_web(query)
                context_knowledge = f"\n[RAW RESEARCH NOTES]:\n{search_results}\n"
                logger.info(f"{self.name} found {len(search_results)} chars of research.")
            except Exception as e:
                logger.error(f"Search tool failed: {e}")

        # --- 3. DYNAMIC OPENINGS ---
        openings = [
            f"I must strongly disagree with the notion that...",
            f"My opponent fails to consider the critical reality that...",
            f"Let's look at the hard data regarding...",
            f"The logic provided by the opposition is fundamentally flawed because...",
            f"It is imperative we look at the {round_lens} of this issue..."
        ]
        opening_phrase = random.choice(openings)

        # --- 4. THE SPEAKING STEP ---
        speak_system_msg = AgentPrompts.DEBATER_SPEAK.format(
            name=self.name,
            topic=topic,
            position=self.position,
            round_lens=round_lens,
            opponent_argument=opponent_argument,
            opening_phrase=opening_phrase,
            word_limit=Config.WORD_LIMIT,
            style=self.style
        )

        final_messages = [{"role": "system", "content": speak_system_msg}]
        if context_knowledge:
            final_messages.append({"role": "system", "content": context_knowledge})
        final_messages.extend(conversation_history)

        try:
            final_response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=final_messages
            )
            return final_response.choices[0].message.content
        except Exception as e:
            logger.critical(f"OpenAI API Call Failed: {e}")
            return "I apologize, but I am unable to formulate an argument due to a system error."