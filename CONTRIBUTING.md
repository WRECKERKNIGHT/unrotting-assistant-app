# Contributing to Unrotting

Thanks for your interest in contributing!

## Development Setup
```bash
# Clone the repo
git clone https://github.com/WRECKERKNIGHT/unrotting-assistant-app.git
cd unrotting-assistant-app

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if exists

# Run tests
python -m pytest tests/

# Run the app
python -m unrotting.app.main run
```

## Code Style
- Use 4 spaces for indentation
- Follow PEP 8 for Python code
- Use descriptive commit messages
- Add tests for new features

## Pull Request Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Reporting Issues
- Use the GitHub issue tracker
- Include steps to reproduce
- Add your OS and Python version
- Attach relevant logs from `unrotting.log`

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
