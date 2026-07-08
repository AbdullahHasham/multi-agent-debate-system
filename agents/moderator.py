import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class ModeratorAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def start_debate(self, topic: str) -> str:
        """
        Introduces the topic and sets the rules.
        """
        system_prompt = """
        You are the Moderator of a formal debate. 
        Your goal is to briefly introduce the topic and welcome the two debaters (Pro and Con).
        Keep it under 50 words. Be neutral, formal, and commanding.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"The topic is: {topic}. Please start the debate."}
            ]
        )
        return response.choices[0].message.content