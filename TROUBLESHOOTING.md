# Troubleshooting Codespace Issues

This document provides detailed troubleshooting steps for resolving GitHub Codespace issues with this repository.

## Issue: Codespace Stops Immediately After Loading

### Root Cause Analysis

The original issue was caused by:

1. **Missing devcontainer configuration**: Without `.devcontainer/devcontainer.json`, GitHub Codespaces uses a default generic container
2. **No Python project structure**: The repository only contained markdown files with no Python code
3. **No package configuration**: Without `pyproject.toml` or `setup.py`, there was no installable Python package

This combination caused the codespace to:
- Load with a generic environment
- Have no clear entry point or development workflow
- Appear to "stop" or "do nothing" after loading

### Solution

The repository now includes:

1. **`.devcontainer/devcontainer.json`**: Specifies Python 3.11 environment with necessary tools
2. **`pyproject.toml`**: Modern Python package configuration
3. **`elpida_core/`**: Python package with basic structure
4. **`tests/`**: Test suite to validate functionality
5. **`.gitignore`**: Prevents committing unwanted files

## Post-Setup Verification

After the codespace loads, verify everything works:

### 1. Check Python Installation

```bash
python --version
# Should show Python 3.11.x or higher
```

### 2. Verify Package Installation

The `postCreateCommand` in `.devcontainer/devcontainer.json` automatically runs:
```bash
pip install --user -e .[dev]
```

Check if it completed successfully:
```bash
pip show elpida-core
```

If not installed, run manually:
```bash
pip install --user -e .[dev]
```

### 3. Run Tests

```bash
pytest -v
```

Expected output:
```
tests/test_basic.py::test_version PASSED
tests/test_basic.py::test_import PASSED

2 passed in 0.01s
```

### 4. Verify Package Import

```bash
python -c "import elpida_core; print(elpida_core.__version__)"
```

Should print: `0.1.0`

## Common Issues and Solutions

### Issue: "postCreateCommand" Still Running

**Symptom**: Codespace loads but terminal shows pip installing packages

**Solution**: 
- Wait for the installation to complete (usually 1-2 minutes)
- This is normal on first load
- The codespace is ready when you see the command prompt

**For low-end PCs**:
- Initial setup may take longer
- This happens in GitHub's cloud, not on your PC
- Your PC only needs to run VS Code Web interface

### Issue: Cannot Find Module 'elpida_core'

**Symptom**: ImportError when trying to import the package

**Solution**:
```bash
# Reinstall in development mode
pip install --user -e .[dev]

# Verify installation
pip show elpida-core
```

### Issue: Codespace Feels Slow

**Possible Causes**:
1. **Network latency**: Codespace runs remotely, keyboard input goes over network
2. **Extensions loading**: VS Code extensions take time to activate
3. **Initial indexing**: Python language server indexes code on first load

**Solutions**:
- Wait 1-2 minutes after codespace starts for all services to load
- Disable unused VS Code extensions
- Close other browser tabs to free up local resources
- Use a wired internet connection if possible

### Issue: Codespace Stops After 30 Minutes

**This is normal behavior**:
- Codespaces auto-stop after 30 minutes of inactivity to save resources
- Your work is saved automatically
- Simply restart the codespace to continue

**To keep codespace running**:
- Interact with the terminal or editor periodically
- Increase timeout in GitHub Codespaces settings (if available)

### Issue: Out of Codespace Hours

**Free tier limits**:
- GitHub Free: 120 core-hours/month
- This repository uses a 2-core machine = 60 hours/month usage

**Solutions**:
- Use local development instead (see README.md)
- Upgrade to GitHub Pro for more hours
- Stop codespace when not actively using it

## Local Development Alternative

If codespaces don't work well on your PC, develop locally:

### Requirements
- Python 3.8 or higher
- Git

### Setup Steps

1. Clone repository:
```bash
git clone https://github.com/XOF-ops/python-elpida_core.py.git
cd python-elpida_core.py
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install package:
```bash
pip install -e .[dev]
```

4. Run tests:
```bash
pytest -v
```

## Performance Considerations for Low-End PCs

### Codespace (Recommended for Low-End PCs)
**Pros**:
- Runs on GitHub's servers (not your PC)
- Your PC only needs to run a web browser
- Consistent environment regardless of PC specs
- No local disk space used

**Cons**:
- Requires stable internet connection
- May have network latency
- Limited by free tier hours

### Local Development
**Pros**:
- No internet required after setup
- No hour limits
- Potentially faster for good PCs

**Cons**:
- Uses local CPU, RAM, and disk
- May be slow on low-end PCs
- Requires managing Python environment

## Getting Help

If you continue to experience issues:

1. Check GitHub Codespaces status: https://www.githubstatus.com/
2. Review codespace creation logs in GitHub UI
3. Try rebuilding the container: Command Palette → "Codespaces: Rebuild Container"
4. Delete and recreate the codespace if corruption suspected
5. File an issue in this repository with details:
   - PC specifications
   - Browser and version
   - Internet connection type
   - Exact error messages
   - Screenshots if applicable

## Additional Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Python Packaging Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
