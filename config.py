import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class Config:
    # System Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4o-mini"

    # Debate Settings
    ROUNDS = 5
    WORD_LIMIT = 150

    # Logging Settings
    LOG_DIR = "logs"

    @classmethod
    def validate(cls):
        """Validate configuration at startup."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("CRITICAL ERROR: OPENAI_API_KEY is missing in .env file!")

    @classmethod
    def setup_logging(cls):
        """Configure professional logging with timestamps."""
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{cls.LOG_DIR}/system_{timestamp}.log"

        # Configure the Root Logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(log_file),  # Save to file
                logging.StreamHandler()  # Print to console
            ]
        )
        logging.info("System logging initialized.")