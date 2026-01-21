# Elpida Core - AI Research Framework

A Python-based framework for AI research and experimentation.

## Overview

This repository contains the Elpida Core framework, designed for conducting AI research experiments and analysis. See `wave1_comprehensive_synthesis.md` for detailed research documentation.

## Getting Started

### Using GitHub Codespaces

This repository is configured to work seamlessly with GitHub Codespaces. Simply:

1. Click the "Code" button
2. Select "Codespaces" tab
3. Click "Create codespace on main" (or your branch)

The development environment will be automatically configured with Python 3.11 and all necessary tools.

### Local Development

#### Prerequisites

- Python 3.8 or higher
- pip package manager

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/XOF-ops/python-elpida_core.py.git
cd python-elpida_core.py
```

2. Install in development mode:
```bash
pip install -e .[dev]
```

This installs the package in editable mode with all development dependencies (pytest, black, pylint, mypy).

#### Running Tests

```bash
pytest
```

#### Code Formatting

Format code with Black:
```bash
black elpida_core/ tests/
```

Lint code with Pylint:
```bash
pylint elpida_core/
```

## Project Structure

```
python-elpida_core.py/
├── elpida_core/          # Main package directory
│   └── __init__.py
├── tests/                 # Test suite
│   └── test_basic.py
├── .devcontainer/        # Codespaces configuration
│   └── devcontainer.json
├── pyproject.toml        # Project metadata and dependencies
├── .gitignore           # Git ignore patterns
├── README.md            # This file
└── wave1_comprehensive_synthesis.md  # Research documentation
```

## Development

### Adding New Features

1. Create a new module in the `elpida_core/` directory
2. Add corresponding tests in `tests/`
3. Update documentation as needed

### Running in Development Mode

The package is designed to be lightweight and run efficiently on low-end hardware. The devcontainer configuration uses a minimal Python 3.11 base image to ensure fast startup times.

## Troubleshooting

### Codespace Stops Immediately

If your codespace stops immediately after loading:

1. **Check devcontainer configuration**: Ensure `.devcontainer/devcontainer.json` exists
2. **Verify Python installation**: The postCreateCommand in devcontainer.json installs dependencies automatically
3. **Resource constraints**: On low-end PCs, initial setup might take 1-2 minutes. Wait for the "postCreateCommand" to complete
4. **Check logs**: View the creation logs in Codespaces to see if there were any errors

### Low-End PC Performance

The repository is configured to be lightweight:
- Uses minimal Python base image
- No heavy dependencies by default
- Optional development dependencies only installed when needed

If experiencing performance issues:
- Close other applications to free up memory
- Use Codespaces instead of local development (runs on GitHub's servers)
- Disable auto-save in your editor to reduce disk I/O

## Contributing

Contributions are welcome! Please ensure:
- Code is formatted with Black
- All tests pass
- New features include tests

## License

MIT License

## Research

For detailed research documentation, see `wave1_comprehensive_synthesis.md`.