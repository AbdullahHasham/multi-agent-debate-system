import time
import logging
from rich.console import Console
from rich.panel import Panel

from config import Config
from agents.moderator import ModeratorAgent
from agents.debater import DebaterAgent
from agents.judge import JudgeAgent
from agents.topic_selector import TopicSelector
from utils.logger import DebateLogger

# Initialize Rich Console
console = Console()


def main():
    # --- 1. SYSTEM SETUP ---
    console.clear()
    Config.validate()  # Check API keys
    Config.setup_logging()  # Start the professional logger

    # Get the logger instance for Main
    logger = logging.getLogger("Main")
    logger.info("Debate System Starting...")

    # --- 2. TOPIC GENERATION ---
    with console.status("[bold cyan]System is selecting a debate topic...[/bold cyan]"):
        topic_selector = TopicSelector()
        TOPIC = topic_selector.generate_topic()
        logger.info(f"Topic Selected: {TOPIC}")

    console.print(Panel.fit(
        f"[bold blue]MULTI-AGENT DEBATE SYSTEM[/bold blue]\n\n[bold white]Selected Topic:[/bold white] {TOPIC}",
        border_style="blue"))

    ROUNDS = Config.ROUNDS

    # --- 3. AGENT INITIALIZATION ---
    moderator = ModeratorAgent()
    debater_a = DebaterAgent(name="Agent_A", position="Pro", style="philosophical and academic")
    debater_b = DebaterAgent(name="Agent_B", position="Con", style="pragmatic and skeptical")
    judge = JudgeAgent()
    file_logger = DebateLogger()  # Keeps the pretty text log as well

    conversation_history = []

    # --- 4. DEBATE START ---
    with console.status("[bold yellow]Moderator is starting...[/bold yellow]"):
        intro = moderator.start_debate(TOPIC)

    console.print(Panel(intro, title="[bold yellow]Moderator[/bold yellow]", border_style="yellow"))
    conversation_history.append({"role": "user", "content": intro})
    time.sleep(1)

    # --- 5. DEBATE LOOP ---
    for i in range(1, ROUNDS + 1):
        console.rule(f"[bold]Round {i}/{ROUNDS}[/bold]")
        logger.info(f"Starting Round {i}")

        # Agent A (Pro)
        with console.status(f"[bold green]{debater_a.name} is researching...[/bold green]"):
            response_a = debater_a.speak(TOPIC, conversation_history)

        console.print(Panel(response_a, title=f"[bold green]{debater_a.name} (Pro)[/bold green]", border_style="green"))
        conversation_history.append({"role": "assistant", "name": debater_a.name, "content": response_a})

        # Agent B (Con)
        with console.status(f"[bold red]{debater_b.name} is researching...[/bold red]"):
            response_b = debater_b.speak(TOPIC, conversation_history)

        console.print(Panel(response_b, title=f"[bold red]{debater_b.name} (Con)[/bold red]", border_style="red"))
        conversation_history.append({"role": "assistant", "name": debater_b.name, "content": response_b})

    # --- 6. JUDGEMENT ---
    console.rule("[bold purple]JUDGE EVALUATING[/bold purple]")
    with console.status("[bold purple]Judge is filling the scorecard...[/bold purple]"):
        verdict = judge.evaluate_debate(TOPIC, conversation_history)

    # Safe score parsing (thanks to validation in Judge class)
    scores_pro = verdict.get('scores', {}).get('Pro', {})
    scores_con = verdict.get('scores', {}).get('Con', {})

    console.print(Panel(
        f"[bold]Winner:[/bold] {verdict.get('winner')}\n\n"
        f"[bold blue]PRO Scores:[/bold blue] Logic: {scores_pro.get('logic')}/10 | Evidence: {scores_pro.get('evidence')}/10\n"
        f"[bold red]CON Scores:[/bold red] Logic: {scores_con.get('logic')}/10 | Evidence: {scores_con.get('evidence')}/10\n\n"
        f"[bold]Reasoning:[/bold] {verdict.get('reasoning')}",
        title="[bold purple]FINAL VERDICT[/bold purple]",
        border_style="purple"
    ))

    # Save logs
    file_logger.save_log(TOPIC, conversation_history, verdict)
    logger.info("Debate finished successfully.")


if __name__ == "__main__":
    main()