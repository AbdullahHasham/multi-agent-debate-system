import json
import logging
from openai import OpenAI
from config import Config
from agents.prompts import AgentPrompts

logger = logging.getLogger("__name__")


class JudgeAgent:
    """
    An AI Judge that evaluates debates based on logic, evidence, and persuasion.
    """

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def evaluate_debate(self, topic: str, conversation_history: list) -> dict:
        """
        Analyzes the debate transcript and returns a structured Scorecard.
        """
        transcript = ""
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            transcript += f"{role.upper()}: {content}\n\n"

        system_prompt = AgentPrompts.JUDGE_SYSTEM

        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Topic: {topic}\n\nTranscript:\n{transcript}"}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            result = json.loads(content)

            # --- VALIDATION (Addressing Reviewer Feedback) ---
            required_keys = ['winner', 'reasoning', 'scores']
            if not all(key in result for key in required_keys):
                raise ValueError("Judge output missing required keys")

            scores = result.get('scores', {})
            if 'Pro' not in scores or 'Con' not in scores:
                raise ValueError("Judge output missing Pro/Con scores")

            logger.info("Judge evaluation completed successfully.")
            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Judge Validation Failed: {e}", exc_info=True)
            return {
                "winner": "Tie (Technical Error)",
                "reasoning": "The judge failed to output a valid scorecard.",
                "scores": {"Pro": {"logic": 0, "evidence": 0}, "Con": {"logic": 0, "evidence": 0}}
            }
        except Exception as e:
            logger.critical(f"Judge API Failed: {e}")
            return {
                "winner": "Tie",
                "reasoning": "Critical System Failure",
                "scores": {"Pro": {}, "Con": {}}
            }