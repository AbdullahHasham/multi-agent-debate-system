import os
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DebateLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def save_log(self, topic: str, history: List[Dict[str, str]], evaluation: Dict[str, Any]):
        """
        Saves the debate transcript and judge's score to a timestamped file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        readable_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{self.log_dir}/debate_{timestamp}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                # --- PROFESSIONAL HEADER ---
                f.write("=" * 60 + "\n")
                f.write("MULTI-AGENT DEBATE SYSTEM - TRANSCRIPT\n")
                f.write("=" * 60 + "\n")
                f.write(f"Timestamp: {readable_time}\n")
                f.write(f"Topic:     {topic}\n")
                f.write("=" * 60 + "\n\n")

                # Write the transcript
                for msg in history:
                    role = msg.get("role", "unknown")
                    name = msg.get("name", role.upper())
                    content = msg.get("content", "")

                    f.write(f"[{name}]:\n")
                    f.write(f"{content}\n")
                    f.write("-" * 40 + "\n\n")

                # Write the Judge's decision
                f.write("=" * 60 + "\n")
                f.write("JUDGE'S EVALUATION:\n")
                f.write(f"Winner: {evaluation.get('winner')}\n")

                # Handle scores safely
                scores_pro = evaluation.get('scores', {}).get('Pro', {})
                scores_con = evaluation.get('scores', {}).get('Con', {})

                f.write(f"Pro Scores: {scores_pro}\n")
                f.write(f"Con Scores: {scores_con}\n")
                f.write(f"Reasoning: {evaluation.get('reasoning')}\n")
                f.write("=" * 60 + "\n")

            logger.info(f"Debate log saved successfully to: {filename}")

        except Exception as e:
            logger.error(f"Failed to save debate log: {e}")