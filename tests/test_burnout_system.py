"""Test Suite for Burnout System.

Note: BurnoutSystem was refactored into BurnoutPlugin.
These tests are DISABLED until plugin testing is implemented.
"""

import pytest

# Skip all tests in this module since BurnoutSystem no longer exists
# Functionality now in src/core/plugins/burnout_plugin.py
pytestmark = pytest.mark.skip(reason="BurnoutSystem refactored into BurnoutPlugin")


def test_placeholder():
    """Placeholder test - actual burnout tests need to be rewritten for BurnoutPlugin."""
    pass
