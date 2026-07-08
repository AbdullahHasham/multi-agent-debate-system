import os
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TopicSelector:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_topic(self) -> str:
        # We pick a random domain first to force variety
        domains = [
            "Bioethics & Genetic Engineering",
            "Interplanetary Law & Space Colonization",
            "Advanced Economics (Post-Capitalism)",
            "Transhumanism & Cybernetics",
            "Global Geopolitics & Borders",
            "AI Sentience & Rights",
            "Climate Engineering & Geo-Intervention"
        ]
        selected_domain = random.choice(domains)

        prompt = f"""
        You are a Debate Commissioner for a PhD-level competition.

        Task: Generate a specific, controversial, and high-stakes resolution for a debate.
        Domain: {selected_domain}

        Rules:
        1. It must be a clear statement (e.g., "Resolved: That...").
        2. It must be specific (No generic "AI is bad").
        3. It must be balanced (both sides have strong arguments).

        Output ONLY the topic string. No quotes, no intro.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0  # High creativity
        )
        return response.choices[0].message.content.strip()