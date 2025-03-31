import dotenv

# Load API key from environment variables
dotenv.load_dotenv()
dotenv.load_dotenv(".env.secret")

import sys
from typing import Annotated
import typer
from ailabel.db.crud import (
    create_topic,
    get_label_statistics,
    create_labeled_payload,
    topic_exists,
)
from ailabel.label_prediction import label_payload


def _ensure_stdin_passed():
    import sys

    if sys.stdin.isatty():
        typer.echo("Error: No input provided on stdin", err=True)
        raise typer.Exit(code=1)


def _display_topic_details(topic_name: str):
    """
    Show information about a specific topic.
    Usage: label topics info <topic_name> [--labels]
    """
    # Check if topic exists
    if not topic_exists(name=topic_name):
        typer.echo(f"Error: Topic '{topic_name}' does not exist.")
        raise typer.Exit(code=1)

    typer.echo(f'Topic: "{topic_name}"')

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
        _ensure_stdin_passed()
        payload = sys.stdin.read().strip()

    match (payload, label_value):
        case ("", ""):
            _display_topic_details(topic)
        case ("", _):
            typer.echo("Error: No payload provided. Use a positional argument or pipe input with '-'", err=True)
            raise typer.Exit(code=1)
        case (_, ""):
            try:
                typer.echo(label_payload(topic, payload))
                raise typer.Exit(code=0)
            except ValueError as e:
                if "API key not found" in str(e):
                    typer.echo(f"Error: {e}", err=True)
                    typer.echo("\nPlease set your API key as described in the README:\n  export GOOGLE_API_KEY=\"AIz...\"", err=True)
                    raise typer.Exit(code=1)
                raise
        case (_, _):
            created = create_labeled_payload(payload=payload, label_name=label_value, topic_name=topic)
            typer.echo(
                f'Payload: "{payload}" | Label: "{label_value}" | Topic: "{topic}" | Created ID: "{created.id}" | Label successfully recorded.'
            )


if __name__ == "__main__":
    app()
