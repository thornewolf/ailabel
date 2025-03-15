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


@topics_app.command("new")
def newtopic(
    topic_name: str = typer.Argument(..., help="Name of the new topic to create")
):
    """
    Create a new topic.
    Usage: label topics new <topic>
    """
    try:
        create_topic(name=topic_name)
        typer.echo(f'Topic "{topic_name}" created successfully.')
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


@topics_app.command("info")
def topic_info(
    topic_name: str = typer.Argument(..., help="Name of the topic to show information for"),
    labels: bool = typer.Option(False, "--labels", help="Show label statistics"),
):
    """
    Show information about a specific topic.
    Usage: label topics info <topic_name> [--labels]
    """
    try:
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
    except Exception as e:
        typer.echo(f"Error retrieving topic info: {e}")


@topics_app.callback(invoke_without_command=True)
def topics_callback(ctx: typer.Context):
    """
    Manage topics. If no subcommand is provided, lists all topics.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand was provided, so list all topics
        list_topics()


app.add_typer(topics_app, name="topics", help="Commands related to managing topics.")


@app.command()
def label(
    payload: str = typer.Argument(None, help="The payload to label. Use '-' to read from stdin."),
    topic: str = typer.Option(..., "--topic", "-t", help="The topic to use for labeling"),
    label_value: str = typer.Option(None, "--as", "-a", help="Label to assign to the payload"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Enter interactive labeling mode"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output the result in JSON format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output (except errors)"),
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
        typer.echo(f"Error: Topic '{topic}' does not exist.")
        raise typer.Exit(code=1)

    # Interactive mode
    if interactive:
        typer.echo(f"--- Interactive labeling for topic: '{topic}' ---")
        typer.echo("Press Ctrl+C to exit at any time.\n")

        try:
            while True:
                payload_input = typer.prompt("Enter payload")
                label_input = typer.prompt("Enter label")
                try:
                    create_labeled_payload(payload=payload_input, label_name=label_input, topic_name=topic)
                    if not quiet:
                        if json_output:
                            import json
                            result = {"payload": payload_input, "topic": topic, "label": label_input, "status": "success"}
                            typer.echo(json.dumps(result))
                        else:
                            typer.echo(f'Payload: "{payload_input}"')
                            typer.echo(f'Label: "{label_input}"')
                            typer.echo(f'Topic: "{topic}"')
                            typer.echo("Label successfully recorded.\n")
                except Exception as e:
                    typer.echo(f"Error storing label: {e}", err=True)
        except KeyboardInterrupt:
            typer.echo("\nExiting interactive mode.")
            return

    # Standard mode
    else:
        # Handle stdin if payload is '-'
        if payload == "-":
            import sys
            if sys.stdin.isatty():
                typer.echo("Error: No input provided on stdin", err=True)
                raise typer.Exit(code=1)
            payload = sys.stdin.read().strip()
        
        # Validate input
        if not payload:
            typer.echo("Error: No payload provided. Use a positional argument or pipe input with '-'", err=True)
            raise typer.Exit(code=1)
        
        if not label_value:
            typer.echo("Error: No label provided. Use --as=LABEL to specify a label", err=True)
            raise typer.Exit(code=1)
        
        # Create the labeled payload
        try:
            created = create_labeled_payload(payload=payload, label_name=label_value, topic_name=topic)
            
            if not quiet:
                if json_output:
                    import json
                    result = {"id": created.id, "payload": payload, "topic": topic, "label": label_value, "status": "success"}
                    typer.echo(json.dumps(result))
                else:
                    typer.echo(f'Payload: "{payload}"')
                    typer.echo(f'Label: "{label_value}"')
                    typer.echo(f'Topic: "{topic}"')
                    typer.echo("Label successfully recorded.")
        except Exception as e:
            typer.echo(f"Error storing label: {e}", err=True)
            raise typer.Exit(code=1)


@app.command()
def predict(
    payload: str = typer.Argument(None, help="The payload to predict a label for. Use '-' to read from stdin."),
    topic: str = typer.Option(..., "--topic", "-t", help="The topic to use for prediction"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output the result in JSON format"),
    batch: bool = typer.Option(False, "--batch", "-b", help="Process multi-line input as separate items (one per line)"),
):
    """
    Predict a label for a given payload in a topic.
    
    Usage: 
      label predict "I love this product" --topic=sentiment
      echo "I love this product" | label predict - --topic=sentiment
      cat items.txt | label predict - --topic=sentiment --batch
    """
    # Check if topic exists
    if not topic_exists(name=topic):
        typer.echo(f"Error: Topic '{topic}' does not exist.", err=True)
        raise typer.Exit(code=1)
    
    # Get input from stdin if payload is "-"
    if payload == "-":
        import sys
        if sys.stdin.isatty():
            typer.echo("Error: No input provided on stdin", err=True)
            raise typer.Exit(code=1)
        payload = sys.stdin.read().strip()
    elif payload is None:
        typer.echo("Error: No payload provided. Use a positional argument or pipe input with '-'", err=True)
        raise typer.Exit(code=1)

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
        
        # For multi-line input in batch mode, we need to adjust the system prompt
        history = get_examples_for_topic(topic)
        if batch and "\n" in payload:
            # For batch input, ask for an array of labels
            system_instruction = f"""Your task is to label each line of the input payload for topic "{topic}".
                    It is a classification task with the following possible labels: {distinct_labels}.
                    The input contains multiple items, one per line.
                    Classify each line separately and return an array of labels.
                    Your response should have the format:
                    {{ "label": ["label1", "label2", "label3", ...] }}
                    Where each item in the array corresponds to the label for that line in order.
                    Example for 2 lines:
                    {{ "label": ["{distinct_labels[0]}", "{distinct_labels[0]}"] }}"""
        else:
            # For single item input
            system_instruction = f"""Your task is to label incoming payloads for topic "{topic}".
                    It is a classification task with the following possible labels: {distinct_labels}.
                    Your response should have the format:
                    {{ "label": "your-label-here" }}
                    Where "your-label-here" is one of the possible labels for this topic.
                    Example:
                    {{ "label": "{distinct_labels[0]}" }}
                    {{ "label": "{distinct_labels[1]}" }}"""
        
        predicted_label = generate_json(
            payload,
            history=history,
            system_instruction=system_instruction,
        )
        return predicted_label["label"]

    # Process in batch mode if requested and the payload contains newlines
    if batch and "\n" in payload:
        lines = payload.strip().split("\n")
        # Get predictions for all lines at once
        labels = predict_label_for_payload(topic, payload)
        
        # Ensure we have the right number of labels
        if not isinstance(labels, list):
            labels = [labels]  # Handle case where model returns a single label
        
        # Extend or truncate the labels array to match input lines
        if len(labels) < len(lines):
            labels.extend([labels[-1]] * (len(lines) - len(labels)))
        elif len(labels) > len(lines):
            labels = labels[:len(lines)]
        
        # Output results
        import json
        for i, (line, label) in enumerate(zip(lines, labels)):
            if json_output:
                result = {"payload": line, "topic": topic, "label": label, "line": i+1}
                typer.echo(json.dumps(result))
            else:
                typer.echo(f"{label}")
    else:
        # Single prediction
        try:
            label = predict_label_for_payload(topic, payload)
            
            # Format output
            if json_output:
                import json
                result = {"payload": payload, "topic": topic, "label": label}
                typer.echo(json.dumps(result))
            else:
                typer.echo(label)
        except Exception as e:
            typer.echo(f"Error predicting label: {e}", err=True)
            raise typer.Exit(code=1)


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
