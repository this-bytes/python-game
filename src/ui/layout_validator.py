"""
Layout Validator - checks for overlapping panels and constraint issues.

This is intentionally small and non-invasive: it inspects the layout_manager
state and returns a list of human-readable issues.
"""

from typing import List
import pygame




def validate_layout(layout_manager) -> List[str]:
    """Validate layout and return list of issues found.

    Args:
        layout_manager: LayoutManager instance

    Returns:
        List of issue strings
    """
    issues = []

    # Check for overlapping panels
    panels = list(layout_manager.panels.items())
    for i, (name1, p1) in enumerate(panels):
        if not hasattr(p1, 'rect'):
            issues.append(f"Panel '{name1}' missing rect")
            continue
        for name2, p2 in panels[i+1:]:
            if not hasattr(p2, 'rect'):
                issues.append(f"Panel '{name2}' missing rect")
                continue
            if p1.rect.colliderect(p2.rect):
                issues.append(f"Overlap: '{name1}' <-> '{name2}'")

    # Detect panels with zero size
    for name, panel in layout_manager.panels.items():
        if hasattr(panel, 'rect'):
            if panel.rect.width <= 0 or panel.rect.height <= 0:
                issues.append(f"Zero-size panel: '{name}' {panel.rect.size}")

    # Check panels against reserved zones (they should not overlap)
    try:
        reserved = getattr(layout_manager.grid_config, 'reserved_zones', []) or []
        for name, panel in layout_manager.panels.items():
            if not hasattr(panel, 'rect'):
                continue
            for zone in reserved:
                if panel.rect.colliderect(zone):
                    issues.append(f"Panel '{name}' overlaps reserved zone {zone}")
    except Exception:
        # Be defensive: don't fail validation if layout_manager lacks attributes
        pass

    # Check for constraint mismatch for grid-mode panels
    try:
        for name, mode in getattr(layout_manager, 'panel_modes', {}).items():
            if mode == getattr(layout_manager, 'LayoutMode', None) or str(mode).endswith('GRID'):
                # get constraints and expected bounds if possible
                constraints = layout_manager.panel_constraints.get(name)
                panel = layout_manager.panels.get(name)
                if not constraints or not panel or not hasattr(panel, 'rect'):
                    continue
                # Use internal calculation when available
                try:
                    expected = layout_manager._calculate_grid_bounds(constraints)
                    # Allow small tolerance for padding math
                    if (abs(panel.rect.x - expected.x) > 2 or abs(panel.rect.y - expected.y) > 2
                            or abs(panel.rect.width - expected.width) > 2 or abs(panel.rect.height - expected.height) > 2):
                        issues.append(f"Constraint mismatch for '{name}': expected {expected}, actual {panel.rect}")
                except Exception:
                    # ignore if calculation method not available
                    pass
    except Exception:
        pass

    # Panels outside screen bounds
    try:
        screen_w, screen_h = layout_manager.screen_size
        for name, panel in layout_manager.panels.items():
            if not hasattr(panel, 'rect'):
                continue
            if panel.rect.right > screen_w or panel.rect.bottom > screen_h or panel.rect.left < 0 or panel.rect.top < 0:
                issues.append(f"Panel '{name}' outside screen bounds: {panel.rect}")
    except Exception:
        pass

    return issues
