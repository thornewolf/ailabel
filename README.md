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

```bash
# Create a new topic
label topics new sentiment

# List all topics
label topics list

# Get information about a topic
label topics info sentiment --labels

# Label a payload
label label "This product is amazing!" --topic=sentiment --as=positive

# Label from stdin
echo "This product is amazing!" | label label - --topic=sentiment --as=positive

# Interactive labeling
label label --topic=sentiment --interactive

# JSON output format
label label "Product was great" --topic=sentiment --as=positive --json

# Predict a label for a new payload
label predict "I love this product" --topic=sentiment

# Predict from stdin and get JSON output
echo "I love this product" | label predict - --topic=sentiment --json

# Show debug information
label --debug
```

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