"""
Test suite for Elpida Core
"""

import pytest
from elpida_core import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_import():
    """Test that package can be imported."""
    import elpida_core
    assert elpida_core is not None
