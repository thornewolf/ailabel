import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from typer import Exit

from ailabel.entrypoints.cli import app
from ailabel.db.models import Topic, LabeledPayload


runner = CliRunner()


def test_main_no_args():
    """Test the main command with no arguments."""
    result = runner.invoke(app)
    assert "Usage" in result.stdout
    assert result.exit_code == 0


def test_display_topic_details():
    """Test displaying topic details."""
    with patch("ailabel.entrypoints.cli._display_topic_details") as mock_display:
        # Mock this function to avoid DB calls
        mock_display.return_value = None
        
        # Call the CLI with just a topic
        result = runner.invoke(app, ["--topic", "test_topic"])
        
        # Verify _display_topic_details was called
        mock_display.assert_called_once_with("test_topic")


def test_topic_info_with_labels():
    """Test topic info with labels."""
    with patch("ailabel.entrypoints.cli.topic_exists") as mock_exists, \
         patch("ailabel.entrypoints.cli.get_label_statistics") as mock_stats:
        
        mock_exists.return_value = True
        mock_stats.return_value = {"positive": 5, "negative": 3}
        
        result = runner.invoke(app, ["--topic", "test_topic"])
        
        assert 'Topic: "test_topic"' in result.stdout
        assert "Label statistics:" in result.stdout
        assert "Total labeled payloads: 8" in result.stdout


@patch("ailabel.entrypoints.cli.create_labeled_payload")
@patch("ailabel.entrypoints.cli.topic_exists")
def test_label_payload(mock_exists, mock_create):
    """Test labeling a payload."""
    mock_exists.return_value = True
    mock_create.return_value = MagicMock(id="test-id")
    
    result = runner.invoke(app, ["test payload", "--topic", "test_topic", "--as", "test_label"])
    
    assert result.exit_code == 0
    assert 'Label successfully recorded' in result.stdout
    mock_create.assert_called_once()


@patch("ailabel.entrypoints.cli.label_payload")
@patch("ailabel.entrypoints.cli.topic_exists")
def test_predict_label(mock_exists, mock_predict):
    """Test predicting a label."""
    mock_exists.return_value = True
    mock_predict.return_value = "predicted_label"
    
    result = runner.invoke(app, ["test payload", "--topic", "test_topic"])
    
    assert result.exit_code == 0
    assert "predicted_label" in result.stdout
    mock_predict.assert_called_once_with("test_topic", "test payload")


@patch("ailabel.entrypoints.cli.topic_exists")
def test_error_no_payload_with_label(mock_exists):
    """Test error when no payload is provided but label is."""
    mock_exists.return_value = True
    
    result = runner.invoke(app, ["--topic", "test_topic", "--as", "test_label"])
    
    assert result.exit_code == 1
    assert "Error: No payload provided" in result.stdout