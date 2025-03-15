# Publishing AILabel to PyPI

This document describes the steps to publish AILabel to PyPI.

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Install Twine if you don't have it already:
   ```bash
   uv pip install twine
   ```

## Steps to Publish

1. **Build the distribution packages**:
   ```bash
   cd /path/to/ailabel
   uv build
   ```
   This will create both `.tar.gz` and `.whl` files in the `dist/` directory.

2. **Upload to PyPI using Twine**:
   ```bash
   twine upload dist/*
   ```
   You'll be prompted for your PyPI username and password.

3. **Upload to TestPyPI (optional, for testing)**:
   ```bash
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```
   This uploads to TestPyPI first so you can test the installation before making it publicly available.

## Updating the Package

1. Update the version number in:
   - `pyproject.toml`
   - `ailabel/__init__.py`

2. Update the CHANGELOG.md with the new version information

3. Rebuild and upload as described above

## After Publishing

1. Verify the package can be installed:
   ```bash
   uv pip install ailabel
   # or from TestPyPI:
   uv pip install --index-url https://test.pypi.org/simple/ ailabel
   ```

2. Create a GitHub release with the same version number

3. Tag the release in Git:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```