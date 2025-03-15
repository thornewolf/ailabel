import typer
from ailabel.db.crud import (
    create_topic,
    get_all_topics,
    get_label_statistics,
    create_labeled_payload,
    get_recent_labeled_payloads,
    topic_exists,
)
from ailabel.lib.llms import generate_json


# ------------------------------------------------------
# Typer app setup
# ------------------------------------------------------
app = typer.Typer(help="CLI for categorizing topics, labeling payloads, and predicting labels.")


topics_app = typer.Typer(help="Manage topics and labels.")


@topics_app.command("new")
def newtopic(topic: str):
    """
    Create a new topic.
    Usage: categorize topics create <topic>
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
    Usage: categorize topics list
    """
    try:
        all_topics = get_all_topics()
        typer.echo("Existing topics:")
        for idx, t in enumerate(all_topics, start=1):
            typer.echo(f"{idx}. {t.name}")
    except Exception as e:
        typer.echo(f"Error listing topics: {e}")


@topics_app.command("info")
def topic_info(
    topic_name: str,
    labels: bool = typer.Option(False, "--labels", help="Show label statistics"),
):
    """
    Show information about a specific topic.
    Usage: categorize topics info <topic_name> [--labels]
    """
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
      categorize label <topic> <payload> --label <correct label>\n
    Usage:
      categorize label <topic> --interactive
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
    Usage: categorize topics predict <topic> <payload>
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
def main():
    app()


if __name__ == "__main__":
    main()
