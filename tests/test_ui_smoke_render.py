import os
import subprocess
import sys

import pytest

# This smoke test runs a headless one-frame render of the GameUI to ensure
# there are no immediate crashes when constructing UI components.

def test_headless_render_runs():
    # Run a small script in a subprocess to avoid side-effects in test runner
    script = r"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
from src.models.game_state import GameState
from src.ui.game_ui import GameUI

# Minimal GameState
gs = GameState()
setattr(gs, 'current_money', 54321.0)
setattr(gs, 'clients', [])
setattr(gs, 'specialists', [])
setattr(gs, 'incidents', [])

ui = GameUI(gs, system_manager=None)
ui.update(0.016)
ui.render()
print('RENDER_OK')
"""
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=10)
    assert 'RENDER_OK' in result.stdout
