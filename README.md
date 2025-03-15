# AILabel

A tool for creating and managing labeled datasets for AI training.

## Features

- Create and manage topics (categories for classification)
- Label text payloads within topics
- Predict labels for new data using AI (Google Gemini)
- Access labeled data via a web interface

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ailabel.git
cd ailabel

# Install the package
pip install -e .

# For development, install test dependencies
pip install -e ".[test]"
```

## Usage

### CLI

```bash
# Create a new topic
label topics new sentiment

# List all topics
label topics list

# Get information about a topic
label topics info sentiment --labels

# Label a payload
label label sentiment "This product is amazing!" --label positive

# Interactive labeling
label label sentiment --interactive

# Predict a label for a new payload
label predict sentiment "I love this product"
```

### Web Interface

```bash
# Start the web server
python -m ailabel.server_main
```

Then open your browser to http://localhost:8000

## Environment Variables

Create a `.env.secret` file with the following variables:

```
GEMINI_API_KEY=your_gemini_api_key
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=ailabel
```

## License

MIT 