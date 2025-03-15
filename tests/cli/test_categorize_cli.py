import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from ailabel.cli.categorize_cli import app, main
from ailabel.db.models import Topic, Label, LabeledPayload


runner = CliRunner()


@pytest.fixture
def mock_create_topic():
    with patch("ailabel.cli.categorize_cli.create_topic") as mock:
        mock.return_value = Topic(name="test_topic")
        yield mock


@pytest.fixture
def mock_get_all_topics():
    with patch("ailabel.cli.categorize_cli.get_all_topics") as mock:
        mock.return_value = [Topic(name="topic1"), Topic(name="topic2")]
        yield mock


@pytest.fixture
def mock_topic_exists():
    with patch("ailabel.cli.categorize_cli.topic_exists") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_get_label_statistics():
    with patch("ailabel.cli.categorize_cli.get_label_statistics") as mock:
        mock.return_value = {"positive": 5, "negative": 3, "neutral": 2}
        yield mock


@pytest.fixture
def mock_create_labeled_payload():
    with patch("ailabel.cli.categorize_cli.create_labeled_payload") as mock:
        mock.return_value = LabeledPayload(
            id="test-id",
            payload="test payload",
            label_name="test_label",
            topic_name="test_topic"
        )
        yield mock


@pytest.fixture
def mock_generate_json():
    with patch("ailabel.cli.categorize_cli.generate_json") as mock:
        mock.return_value = {"label": "test_label"}
        yield mock


@pytest.fixture
def mock_get_recent_labeled_payloads():
    with patch("ailabel.cli.categorize_cli.get_recent_labeled_payloads") as mock:
        mock.return_value = [
            LabeledPayload(
                id="id1",
                payload="payload1",
                label_name="label1",
                topic_name="topic1"
            ),
            LabeledPayload(
                id="id2",
                payload="payload2",
                label_name="label2",
                topic_name="topic1"
            )
        ]
        yield mock


def test_newtopic_command(mock_create_topic):
    """Test the 'newtopic' command."""
    result = runner.invoke(app, ["topics", "new", "test_topic"])
    assert result.exit_code == 0
    assert 'Topic "test_topic" created successfully' in result.stdout
    mock_create_topic.assert_called_once_with(name="test_topic")


def test_newtopic_command_error(mock_create_topic):
    """Test error handling in 'newtopic' command."""
    mock_create_topic.side_effect = ValueError("Topic already exists")
    result = runner.invoke(app, ["topics", "new", "test_topic"])
    assert result.exit_code == 0
    assert "Error creating topic: Topic already exists" in result.stdout


def test_list_topics_command(mock_get_all_topics):
    """Test the 'list_topics' command."""
    result = runner.invoke(app, ["topics", "list"])
    assert result.exit_code == 0
    assert "Existing topics:" in result.stdout
    assert "1. topic1" in result.stdout
    assert "2. topic2" in result.stdout
    mock_get_all_topics.assert_called_once()


def test_list_topics_command_error(mock_get_all_topics):
    """Test error handling in 'list_topics' command."""
    mock_get_all_topics.side_effect = ValueError("Database error")
    result = runner.invoke(app, ["topics", "list"])
    assert result.exit_code == 0
    assert "Error listing topics: Database error" in result.stdout


def test_topic_info_command(mock_get_label_statistics):
    """Test the 'topic_info' command."""
    result = runner.invoke(app, ["topics", "info", "test_topic", "--labels"])
    assert result.exit_code == 0
    assert 'Topic: "test_topic"' in result.stdout
    assert "Label statistics:" in result.stdout
    assert "- positive: 5" in result.stdout
    assert "- negative: 3" in result.stdout
    assert "- neutral: 2" in result.stdout
    assert "Total labeled payloads: 10" in result.stdout
    mock_get_label_statistics.assert_called_once_with(topic_name="test_topic")


def test_topic_info_command_no_labels():
    """Test the 'topic_info' command without the --labels flag."""
    result = runner.invoke(app, ["topics", "info", "test_topic"])
    assert result.exit_code == 0
    assert 'Topic: "test_topic"' in result.stdout


def test_topic_info_command_error(mock_get_label_statistics):
    """Test error handling in 'topic_info' command."""
    mock_get_label_statistics.side_effect = ValueError("Topic not found")
    result = runner.invoke(app, ["topics", "info", "test_topic", "--labels"])
    assert result.exit_code == 0
    assert "Error retrieving topic info: Topic not found" in result.stdout


def test_label_command(mock_create_labeled_payload):
    """Test the 'label' command."""
    result = runner.invoke(app, [
        "label", "test_topic", "test payload", "--label", "test_label"
    ])
    assert result.exit_code == 0
    assert 'Payload: "test payload"' in result.stdout
    assert 'Label: "test_label"' in result.stdout
    assert 'Topic: "test_topic"' in result.stdout
    assert "Label successfully recorded" in result.stdout
    mock_create_labeled_payload.assert_called_once_with(
        payload="test payload",
        label_name="test_label",
        topic_name="test_topic"
    )


def test_label_command_missing_arguments():
    """Test the 'label' command with missing arguments."""
    # Missing payload
    result = runner.invoke(app, ["label", "test_topic"])
    assert result.exit_code == 1
    assert "Error: You must provide both <payload> and --label" in result.stdout
    
    # Missing label
    result = runner.invoke(app, ["label", "test_topic", "test payload"])
    assert result.exit_code == 1
    assert "Error: You must provide both <payload> and --label" in result.stdout


def test_label_command_error(mock_create_labeled_payload):
    """Test error handling in 'label' command."""
    mock_create_labeled_payload.side_effect = ValueError("Invalid label")
    result = runner.invoke(app, [
        "label", "test_topic", "test payload", "--label", "test_label"
    ])
    assert result.exit_code == 0
    assert "Error storing label: Invalid label" in result.stdout


@patch("typer.prompt")
def test_label_interactive_mode(mock_prompt, mock_topic_exists, mock_create_labeled_payload):
    """Test the 'label' command in interactive mode."""
    # Set up mock for prompt to return values once then raise KeyboardInterrupt
    mock_prompt.side_effect = ["interactive payload", "interactive label", KeyboardInterrupt]
    
    result = runner.invoke(app, ["label", "test_topic", "--interactive"])
    # KeyboardInterrupt causes exit code 130, which is expected
    assert result.exit_code == 130
    assert "--- Interactive labeling for topic: 'test_topic' ---" in result.stdout
    assert "Press Ctrl+C to exit at any time" in result.stdout
    mock_topic_exists.assert_called_once_with(name="test_topic")
    mock_create_labeled_payload.assert_called_once_with(
        payload="interactive payload",
        label_name="interactive label",
        topic_name="test_topic"
    )


def test_label_interactive_nonexistent_topic(mock_topic_exists):
    """Test the 'label' command in interactive mode with nonexistent topic."""
    mock_topic_exists.return_value = False
    result = runner.invoke(app, ["label", "nonexistent_topic", "--interactive"])
    assert result.exit_code == 1
    assert "Topic 'nonexistent_topic' does not exist" in result.stdout


@patch("typer.prompt")
def test_label_interactive_error(mock_prompt, mock_topic_exists, mock_create_labeled_payload):
    """Test error handling in 'label' command in interactive mode."""
    mock_prompt.side_effect = ["interactive payload", "interactive label", KeyboardInterrupt]
    mock_create_labeled_payload.side_effect = ValueError("Invalid label")
    
    result = runner.invoke(app, ["label", "test_topic", "--interactive"])
    # KeyboardInterrupt causes exit code 130, which is expected
    assert result.exit_code == 130
    assert "Error storing label: Invalid label" in result.stdout


def test_predict_command(mock_get_recent_labeled_payloads, mock_get_label_statistics, mock_generate_json):
    """Test the 'predict' command."""
    mock_get_label_statistics.return_value = {"label1": 3, "label2": 2}
    
    result = runner.invoke(app, ["predict", "test_topic", "test payload"])
    assert result.exit_code == 0
    assert "test_label" in result.stdout
    
    # Verify the call to generate_json
    mock_generate_json.assert_called_once()
    args, kwargs = mock_generate_json.call_args
    
    # First argument should be the payload
    assert args[0] == "test payload"
    
    # Check that history and system_instruction are provided
    assert "history" in kwargs
    assert "system_instruction" in kwargs
    assert "test_topic" in kwargs["system_instruction"]
    assert "label1" in kwargs["system_instruction"]
    assert "label2" in kwargs["system_instruction"]


def test_predict_command_no_labels(mock_get_label_statistics, mock_get_recent_labeled_payloads):
    """Test the 'predict' command when there are no labels."""
    mock_get_label_statistics.return_value = {}
    
    result = runner.invoke(app, ["predict", "test_topic", "test payload"])
    # The CLI raises a ValueError that exits with code 1, which is expected
    assert result.exit_code == 1
    # Check the exception message directly since it's not in stdout
    assert "Topic 'test_topic' has no labels" in str(result.exception)


def test_main_function():
    """Test the main function."""
    with patch("ailabel.cli.categorize_cli.app") as mock_app:
        main()
        mock_app.assert_called_once()