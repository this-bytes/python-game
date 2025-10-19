"""
Layout Validator - checks for overlapping panels and constraint issues.

This is intentionally small and non-invasive: it inspects the layout_manager
state and returns a list of human-readable issues.
"""

from typing import List


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

    return issues
