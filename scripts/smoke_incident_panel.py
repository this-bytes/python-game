"""Smoke test: draw IncidentQueuePanel with a single incident and verify rows created.

Run with: python3 scripts/smoke_incident_panel.py
"""
import sys
import os
import pygame
import time

# Ensure project root is on sys.path so 'src' package imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ui.panels.incident_queue_panel import IncidentQueuePanel
from src.models.incident import Incident


class DummyGameState:
    def __init__(self):
        self.game_time = time.time()


def main():
    pygame.init()
    pygame.font.init()

    surface = pygame.Surface((1280, 720))

    panel = IncidentQueuePanel(x=10, y=10, width=800, height=600)

    inc = Incident(
        id='smoke_inc_001',
        incident_type='Test Incident',
        specialty_required='Network Security',
        difficulty=2,
        sla_seconds=300,
        base_reward=500,
        xp_reward=100,
        client_id='client_test'
    )

    game_state = DummyGameState()

    try:
        panel.draw(surface, [inc], game_state)
        print(f"Panel rows after draw: {len(panel.rows)}")
        if panel.rows:
            print(f"First row id: {panel.rows[0].incident.id}")
        # Save a PNG to /tmp for manual inspection if desired
        try:
            pygame.image.save(surface, '/tmp/smoke_incident_panel.png')
            print('Saved surface to /tmp/smoke_incident_panel.png')
        except Exception as e:
            print(f'Failed to save surface: {e}')
    except Exception as e:
        print(f'Exception during panel.draw: {e}')
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
