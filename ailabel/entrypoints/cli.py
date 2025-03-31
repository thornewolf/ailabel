import os
import sys
from typing import Annotated
import typer
from pathlib import Path
from db.crud import (
    create_topic,
    get_all_topics,
    get_label_statistics,
    create_labeled_payload,
    topic_exists,
)
from predictions import label_payload
from lib.llms import Models


def print_debug_info():
    """Print debug information about the application configuration."""
    from db.database import data_dir, sqlite_url

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
    env_file = Path(".env.secret")
    env_exists = env_file.exists()
    typer.echo(f"  .env.secret file: {'Found' if env_exists else 'Not found'}")


def _ensure_stdin_exists():
    import sys

    if sys.stdin.isatty():
        typer.echo("Error: No input provided on stdin", err=True)
        raise typer.Exit(code=1)


def _display_topic_details(
    topic_name: str = typer.Argument(..., help="Name of the topic to show information for"),
    labels: bool = typer.Option(False, "--labels", help="Show label statistics"),
):
    """
    Show information about a specific topic.
    Usage: label topics info <topic_name> [--labels]
    """
    # Check if topic exists
    if not topic_exists(name=topic_name):
        typer.echo(f"Error: Topic '{topic_name}' does not exist.")
        raise typer.Exit(code=1)

    typer.echo(f'Topic: "{topic_name}"')

    if labels:
        stats = get_label_statistics(topic_name=topic_name)
        typer.echo("\nLabel statistics:")
        for label, count in stats.items():
            typer.echo(f"- {label}: {count}")
        typer.echo(f"Total labeled payloads: {sum(stats.values())}")


# ------------------------------------------------------
# Typer app setup
# ------------------------------------------------------
app = typer.Typer(help="CLI for categorizing topics, labeling payloads, and predicting labels.")


@app.command(no_args_is_help=True)
def main(
    payload: Annotated[str, typer.Argument(help="The payload to label. Use '-' to read from stdin.")] = "",
    topic: Annotated[str, typer.Option("--topic", "-t", help="The topic to use for labeling")] = "",
    label_value: Annotated[str, typer.Option("--as", "-a", help="Label to assign to the payload")] = "",
):
    """
    Label a payload under a given topic.

    Usage:
      label label "This product is amazing!" --topic=sentiment --as=positive
      echo "This product is amazing!" | label label - --topic=sentiment --as=positive
      label label --topic=sentiment --interactive
    """
    # Check if topic exists
    if not topic_exists(name=topic):
        create_topic(name=topic)

    # Handle stdin if payload is '-'
    if payload == "-":
        _ensure_stdin_exists()
        payload = sys.stdin.read().strip()

    match (payload, label_value):
        case ("", ""):
            _display_topic_details(topic)
        case ("", _):
            typer.echo("Error: No payload provided. Use a positional argument or pipe input with '-'", err=True)
            raise typer.Exit(code=1)
        case (_, ""):
            typer.echo(label_payload(topic, payload))
            raise typer.Exit(code=0)
        case (_, _):
            created = create_labeled_payload(payload=payload, label_name=label_value, topic_name=topic)
            typer.echo(
                f'Payload: "{payload}" | Label: "{label_value}" | Topic: "{topic}" | Created ID: "{created.id}" | Label successfully recorded.'
            )


if __name__ == "__main__":
    app()
