#!/usr/bin/env python3
"""Diagnose incident lifecycle: generation -> (auto-assign) -> UI snapshot
"""
import sys
import os
import time

# Ensure project root on sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models.game_state import GameState
from src.ui.panels.incident_queue_panel import IncidentQueuePanel
from src.utils.logger import GameLogger

logger = GameLogger("diagnose")

def main():
    logger.info("Starting incident lifecycle diagnostic")
    gs = GameState()

    # Log initial incidents
    incidents = gs.incidents
    logger.info(f"Initial incidents count: {len(incidents)}")
    for inc in incidents:
        logger.info(f"INCIDENT BEFORE AUTO-ASSIGN: id={inc.id} status={getattr(inc,'status',None)} assigned={getattr(inc,'assigned_specialist_id',None)} spawn={getattr(inc,'spawn_time',None)}")

    # Trigger auto-assignment explicitly
    try:
        gs._auto_assign_incidents()
        logger.info("Called _auto_assign_incidents()")
    except Exception as e:
        logger.warning(f"_auto_assign_incidents() failed: {e}")

    # Log after auto-assign
    incidents2 = gs.incidents
    logger.info(f"Incidents count after auto-assign: {len(incidents2)}")
    for inc in incidents2:
        logger.info(f"INCIDENT AFTER AUTO-ASSIGN: id={inc.id} status={getattr(inc,'status',None)} assigned={getattr(inc,'assigned_specialist_id',None)}")

    # Create a headless pygame surface to draw panel (will open display as in smoke test)
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        panel = IncidentQueuePanel(x=0, y=0, width=800, height=600)
        # Prepare snapshot: unassigned incidents
        unassigned = [inc for inc in incidents2 if not getattr(inc, 'assigned_specialist_id', None)]
        logger.info(f"Preparing to draw panel with {len(unassigned)} unassigned incidents")
        panel.draw(screen, unassigned, gs)
        pygame.image.save(screen, "/tmp/diagnose_incident_panel.png")
        logger.info("Saved /tmp/diagnose_incident_panel.png")
    except Exception as e:
        logger.warning(f"Failed to draw panel: {e}")

    logger.info("Diagnostic complete")

if __name__ == '__main__':
    main()
