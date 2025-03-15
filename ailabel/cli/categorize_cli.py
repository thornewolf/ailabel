import os
import sys
import typer
from pathlib import Path
from ailabel.db.crud import (
    create_topic,
    get_all_topics,
    get_label_statistics,
    create_labeled_payload,
    get_recent_labeled_payloads,
    topic_exists,
)
from ailabel.db.database import data_dir, sqlite_url
from ailabel.lib.llms import generate_json, Models


def print_debug_info():
    """Print debug information about the application configuration."""
    # Get API key and mask it for security
    api_key = os.environ.get("GEMINI_API_KEY", "")
    masked_key = api_key[:4] + "*" * (len(api_key) - 4) if api_key else "Not set"
    
    typer.echo("=== AILabel Debug Information ===")
    typer.echo(f"Python version: {sys.version}")
    typer.echo(f"Database location: {data_dir}")
    typer.echo(f"Database URL: {sqlite_url}")
    typer.echo(f"Gemini API Key: {masked_key}")
    
    # Show configured models
    typer.echo("\nConfigured Gemini models:")
    for model in Models:
        typer.echo(f"  {model.name}: {model.value}")
    
    # Count existing database records
    try:
        topics_count = len(get_all_topics())
        typer.echo(f"\nDatabase status: {topics_count} topics defined")
    except Exception as e:
        typer.echo(f"\nDatabase status: Error accessing database - {e}")
    
    # Show environment and file paths
    typer.echo("\nEnvironment:")
    typer.echo(f"  Working directory: {os.getcwd()}")
    typer.echo(f"  Python executable: {sys.executable}")
    
    # Check for .env file
    env_file = Path('.env.secret')
    env_exists = env_file.exists()
    typer.echo(f"  .env.secret file: {'Found' if env_exists else 'Not found'}")


# ------------------------------------------------------
# Typer app setup
# ------------------------------------------------------
app = typer.Typer(help="CLI for categorizing topics, labeling payloads, and predicting labels.")


topics_app = typer.Typer(help="Manage topics and labels.")


# Create a separate topic-specific command group
topic_app = typer.Typer(help="Operations on a specific topic")


@topic_app.command("info")
def topic_info(
    labels: bool = typer.Option(False, "--labels", help="Show label statistics"),
):
    """
    Show information about this topic.
    Usage: label topics <topic_name> info [--labels]
    """
    # The topic_name is passed from the parent command
    topic_name = get_current_topic()
    try:
        typer.echo(f'Topic: "{topic_name}"')

        if labels:
            stats = get_label_statistics(topic_name=topic_name)
            typer.echo("\nLabel statistics:")
            for label, count in stats.items():
                typer.echo(f"- {label}: {count}")
            typer.echo(f"Total labeled payloads: {sum(stats.values())}")
    except Exception as e:
        typer.echo(f"Error retrieving topic info: {e}")


@topics_app.command("new")
def newtopic(topic: str):
    """
    Create a new topic.
    Usage: label topics new <topic>
    """
    try:
        create_topic(name=topic)
        typer.echo(f'Topic "{topic}" created successfully.')
    except Exception as e:
        typer.echo(f"Error creating topic: {e}")


@topics_app.command("list")
def list_topics():
    """
    List all existing topics.
    Usage: label topics list
    """
    try:
        all_topics = get_all_topics()
        typer.echo("Existing topics:")
        for idx, t in enumerate(all_topics, start=1):
            typer.echo(f"{idx}. {t.name}")
    except Exception as e:
        typer.echo(f"Error listing topics: {e}")


# Variable to store the current topic in the command chain
_current_topic = None

def get_current_topic():
    """Get the current topic in the command chain."""
    return _current_topic


@topics_app.callback(invoke_without_command=True)
def topic_router(
    ctx: typer.Context,
    topic: str = typer.Argument(None, help="The topic to operate on")
):
    """
    Manage topics. If no subcommand is provided, lists all topics.
    If a topic is provided, routes to topic-specific commands.
    """
    # If no command is provided at all, just list the topics
    if ctx.invoked_subcommand is None and topic is None:
        list_topics()
        raise typer.Exit()
    
    # If a topic is provided but no subcommand, show topic info
    elif topic and not ctx.resilient_parsing:
        # Check if topic exists
        if not topic_exists(name=topic):
            typer.echo(f"Error: Topic '{topic}' does not exist.")
            raise typer.Exit(code=1)
            
        # Store the topic
        global _current_topic
        _current_topic = topic
        
        # If no subcommand was provided after the topic, show topic info
        if len(ctx.args) == 0 or (len(ctx.args) == 1 and ctx.args[0] == topic):
            topic_info()
            raise typer.Exit()


# Add the topic-specific commands to be accessible via 'label topics <topic> <command>'
topics_app.add_typer(topic_app, name="{topic}")


app.add_typer(topics_app, name="topics", help="Commands related to managing topics.")


@app.command()
def label(
    topic: str,
    payload: str = typer.Argument(None, help="The payload to label."),
    correct_label: str = typer.Option(None, "--label", help="Label for the payload."),
    interactive: bool = typer.Option(False, "--interactive", help="Enter interactive labeling mode."),
):
    """
    Label a payload under a given topic.

    Usage:
      label label <topic> <payload> --label <correct label>\n
    Usage:
      label label <topic> --interactive
    """
    if interactive:
        if not topic_exists(name=topic):
            typer.echo(f"Topic '{topic}' does not exist.")
            raise typer.Exit(code=1)

        typer.echo(f"--- Interactive labeling for topic: '{topic}' ---")
        typer.echo("Press Ctrl+C to exit at any time.\n")

        while True:
            payload_input = typer.prompt("Enter payload")
            label_input = typer.prompt("Enter label")
            try:
                create_labeled_payload(payload=payload_input, label_name=label_input, topic_name=topic)
                typer.echo(f'Payload: "{payload_input}"')
                typer.echo(f'Label: "{label_input}"')
                typer.echo(f'Topic: "{topic}"')
                typer.echo("Label successfully recorded.\n")
            except Exception as e:
                typer.echo(f"Error storing label: {e}")
    else:
        if not payload or not correct_label:
            typer.echo(
                "Error: You must provide both <payload> and --label <correct-label> unless in --interactive mode."
            )
            raise typer.Exit(code=1)
        try:
            create_labeled_payload(payload=payload, label_name=correct_label, topic_name=topic)
            typer.echo(f'Payload: "{payload}"')
            typer.echo(f'Label: "{correct_label}"')
            typer.echo(f'Topic: "{topic}"')
            typer.echo("Label successfully recorded.\n")
        except Exception as e:
            typer.echo(f"Error storing label: {e}")


@app.command()
def predict(topic: str, payload: str):
    """
    Predict a label for a given payload in a topic.
    Usage: label predict <topic> <payload>
    """

    def get_examples_for_topic(topic: str):
        topic_actual_labels = get_recent_labeled_payloads(topic)
        history = []
        for label in topic_actual_labels:
            history += [
                {"role": "user", "parts": [label.payload]},
                {"role": "assistant", "parts": [f'{{ "label": "{label.label_name}" }}']},
            ]
        return history

    def predict_label_for_payload(topic: str, payload: str):
        labels_for_topic = get_label_statistics(topic)
        distinct_labels = list(labels_for_topic.keys())
        if not distinct_labels:
            raise ValueError(f"Topic '{topic}' has no labels. Please label some payloads first.")
        predicted_label = generate_json(
            payload,
            history=get_examples_for_topic(topic),
            system_instruction=f"""Your task is to label incoming payloads for topic "{topic}".
                    It is a classification task with the following possible labels: {distinct_labels}.
                    Your response should have the format:
                    {{ "label": "your-label-here" }}
                    Where "your-label-here" is one of the possible labels for this topic.
                    Example:
                    {{ "label": "{distinct_labels[0]}" }}
                    {{ "label": "{distinct_labels[1]}" }}""",
        )
        return predicted_label["label"]

    typer.echo(predict_label_for_payload(topic, payload))


# ------------------------------------------------------
# Entry point
# ------------------------------------------------------
@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Print debug information about the current configuration."),
):
    """
    CLI for labeling data with AI assistance.
    """
    if debug:
        print_debug_info()
        raise typer.Exit()
    elif ctx.invoked_subcommand is None:
        # Display help if no subcommand provided
        typer.echo(ctx.get_help())
        raise typer.Exit()


def main():
    app()


if __name__ == "__main__":
    main()
