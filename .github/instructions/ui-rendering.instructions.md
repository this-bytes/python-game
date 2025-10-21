---
applyTo: "src/ui/**/*.py"

---

# UI Rendering Order - Instructions

This instruction file documents the required rendering contract for scrollable panels in the game UI and establishes a small regression test to ensure future agents and contributors keep the behavior.

Goal:
- Prevent scroll container backgrounds and scrollbars from over-drawing panel content (cards, lists, previews).
- Provide a concise, testable contract for rendering order used by all panels that embed a `ScrollContainer`.

Rendering contract (MANDATORY):

1. Panels must call `scroll_container.render_background(screen)` before rendering any content that should appear above the scroll background.
2. Panels must render their scrollable content while the Pygame clipping rect is set to the content area (use `screen.set_clip(content_rect)`), so the content clips correctly to the container.
3. After content is drawn and the clipping region reset (e.g. `screen.set_clip(None)`), panels must call `scroll_container.render_scrollbar(screen)` to draw the scrollbar and handle as an overlay on top of content.

Rationale:
- Separating background and scrollbar drawing prevents z-order issues where the scroll bar or background could be drawn on top of content, hiding it. This is particularly important for drag previews and semi-transparent overlays.

Code example:

```py
# In Panel.render_content(...):
self.scroll_container.position = (content_rect.x, content_rect.y)
self.scroll_container.size = (content_rect.width, content_rect.height)
self.scroll_container.set_content_height(total_content_height)

# 1) Draw background
self.scroll_container.render_background(screen)

# 2) Clip and draw content
screen.set_clip(content_rect)
# draw cards, lists, images ...
screen.set_clip(None)

# 3) Draw scrollbar overlay
self.scroll_container.render_scrollbar(screen)
```

Testing guidance (MANDATORY):
- Add unit tests that mock or spy on the `ScrollContainer` used by panels and verify that `render_background` is called before content rendering and `render_scrollbar` is called after.
- Integration tests should include a headless screenshot (if available) that asserts that the pixel area for cards is not fully identical to the background color (i.e., content is visible).

Acceptance criteria for changes:
- `SpecialistRosterPanel` and `IncidentQueuePanel` follow the contract (already updated in `src/ui/panels/`).
- A regression test exists under `tests/test_ui_render_order.py` and passes.

When you modify scroll behavior or panel drawing, update this instruction and add/adjust tests accordingly.
