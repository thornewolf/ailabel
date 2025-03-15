# Contributing to AILabel

Thank you for your interest in contributing to AILabel! This document provides guidelines and instructions for contributing to this project.

## Development Environment

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ailabel.git
   cd ailabel
   ```

2. Install development dependencies
   ```bash
   uv pip install -e ".[test]"
   ```

3. Run tests to ensure everything is working
   ```bash
   uv run pytest
   ```

## Code Style

This project uses the [ruff](https://github.com/astral-sh/ruff) linter to maintain code quality. Please ensure your code passes all linting checks before submitting a pull request.

- All Python code should follow PEP 8 style guidelines
- Use type hints throughout the codebase
- Include docstrings for all modules, classes, and functions
- Maximum line length is 100 characters

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage of new code

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-new-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to your branch (`git push origin feature/my-new-feature`)
7. Create a new Pull Request

## Release Process

Releases are managed by the maintainers. The process involves:

1. Updating the version number in:
   - `pyproject.toml`
   - `ailabel/__init__.py`
2. Updating the CHANGELOG.md file
3. Creating a new release on GitHub
4. Publishing to PyPI

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.