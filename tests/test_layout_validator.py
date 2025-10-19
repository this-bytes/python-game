import pytest
import pygame
from src.ui.layout_manager import LayoutManager, GridConfig, GridConstraints, LayoutMode
from src.ui.layout_validator import validate_layout


def create_test_layout():
    pygame.init()
    lm = LayoutManager((800, 600), GridConfig(rows=4, cols=4, gutter=5, margin=10))

    # create simple panels as objects with set_position/set_size and rect
    class DummyPanel:
        def __init__(self):
            self.rect = pygame.Rect(0,0,0,0)
            self.visible = True
        def set_position(self, x, y):
            self.rect.x = x
            self.rect.y = y
        def set_size(self, w, h):
            self.rect.width = w
            self.rect.height = h

    p1 = DummyPanel()
    p2 = DummyPanel()
    p3 = DummyPanel()

    lm.add_panel('p1', p1, LayoutMode.GRID, GridConstraints(row=0, col=0, row_span=2, col_span=2))
    lm.add_panel('p2', p2, LayoutMode.GRID, GridConstraints(row=1, col=1, row_span=2, col_span=2))
    lm.add_panel('p3', p3, LayoutMode.GRID, GridConstraints(row=3, col=3, row_span=1, col_span=1))

    lm.layout()
    return lm


def test_validate_overlap_detected():
    lm = create_test_layout()
    issues = validate_layout(lm)
    assert any('Overlap' in i for i in issues), f"Expected overlap issues, got {issues}"


def test_validate_no_issues_when_separated():
    lm = create_test_layout()
    # move p2 out of overlap manually
    p2 = lm.panels['p2']
    # place well outside typical grid area to avoid overlap
    p2.set_position(50, 450)
    p2.set_size(40, 40)
    issues = validate_layout(lm)
    assert not any('Overlap' in i for i in issues), f"Did not expect overlaps, got {issues}"


def test_validate_reserved_zone_detection():
    lm = create_test_layout()
    # Add reserved zone that overlaps first panel
    reserved = pygame.Rect(5,5,200,200)
    lm.grid_config.reserved_zones = [reserved]
    issues = validate_layout(lm)
    assert any('overlaps reserved zone' in i for i in issues)
