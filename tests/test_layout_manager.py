"""Tests for UI Layout Management System."""

import pytest
import pygame
from src.ui.layout_manager import (
    LayoutManager,
    GridConstraints,
    AnchorConstraints,
    FloatingConstraints,
    GridConfig,
    LayoutMode,
    UILayer,
    LayerManager,
    CollisionDetector,
)


class MockPanel:
    """Mock panel for testing."""
    
    def __init__(self):
        self.position = [0, 0]
        self.size = [200, 200]
        self.layer = UILayer.PANELS
        
    def set_position(self, x, y):
        self.position = [x, y]
        
    def set_size(self, width, height):
        self.size = [width, height]
        
    def get_bounds(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])


class TestGridConfig:
    """Test grid configuration."""
    
    def test_default_grid_config(self):
        """Test default grid configuration."""
        config = GridConfig()
        assert config.rows == 12
        assert config.cols == 12
        assert config.gutter == 10
        assert config.margin == 20
        assert len(config.reserved_zones) == 0
    
    def test_custom_grid_config(self):
        """Test custom grid configuration."""
        zones = [pygame.Rect(0, 0, 200, 720)]
        config = GridConfig(rows=10, cols=10, gutter=15, margin=30, reserved_zones=zones)
        assert config.rows == 10
        assert config.cols == 10
        assert config.gutter == 15
        assert config.margin == 30
        assert len(config.reserved_zones) == 1


class TestGridConstraints:
    """Test grid constraint dataclass."""
    
    def test_default_constraints(self):
        """Test default grid constraints."""
        constraints = GridConstraints()
        assert constraints.row == 0
        assert constraints.col == 0
        assert constraints.row_span == 1
        assert constraints.col_span == 1
        assert constraints.padding == 10
        assert constraints.alignment == "fill"
    
    def test_custom_constraints(self):
        """Test custom grid constraints."""
        constraints = GridConstraints(
            row=2,
            col=3,
            row_span=4,
            col_span=5,
            padding=20,
            alignment="center"
        )
        assert constraints.row == 2
        assert constraints.col == 3
        assert constraints.row_span == 4
        assert constraints.col_span == 5
        assert constraints.padding == 20
        assert constraints.alignment == "center"


class TestAnchorConstraints:
    """Test anchor constraint dataclass."""
    
    def test_default_anchor_constraints(self):
        """Test default anchor constraints."""
        constraints = AnchorConstraints()
        assert constraints.anchor_point == "top-left"
        assert constraints.offset == (0, 0)
        assert constraints.size_mode == "fixed"
        assert constraints.size == (200, 100)
    
    def test_custom_anchor_constraints(self):
        """Test custom anchor constraints."""
        constraints = AnchorConstraints(
            anchor_point="bottom-right",
            offset=(10, 20),
            size_mode="percentage",
            percentage=(0.3, 0.5)
        )
        assert constraints.anchor_point == "bottom-right"
        assert constraints.offset == (10, 20)
        assert constraints.size_mode == "percentage"
        assert constraints.percentage == (0.3, 0.5)


class TestLayerManager:
    """Test layer manager."""
    
    def test_add_component(self):
        """Test adding components to layers."""
        manager = LayerManager()
        panel1 = MockPanel()
        panel2 = MockPanel()
        
        manager.add_component(panel1, UILayer.PANELS)
        manager.add_component(panel2, UILayer.OVERLAY)
        
        assert panel1 in manager.layers[UILayer.PANELS]
        assert panel2 in manager.layers[UILayer.OVERLAY]
    
    def test_remove_component(self):
        """Test removing components."""
        manager = LayerManager()
        panel = MockPanel()
        
        manager.add_component(panel, UILayer.PANELS)
        assert panel in manager.layers[UILayer.PANELS]
        
        manager.remove_component(panel)
        assert panel not in manager.layers[UILayer.PANELS]
    
    def test_render_order(self):
        """Test render order by layer."""
        manager = LayerManager()
        panel1 = MockPanel()
        panel2 = MockPanel()
        panel3 = MockPanel()
        
        # Add in non-sequential order
        manager.add_component(panel2, UILayer.OVERLAY)
        manager.add_component(panel1, UILayer.PANELS)
        manager.add_component(panel3, UILayer.NOTIFICATION)
        
        render_order = manager.get_render_order()
        
        # Should be ordered: PANELS (10), OVERLAY (30), NOTIFICATION (50)
        assert render_order[0] == panel1
        assert render_order[1] == panel2
        assert render_order[2] == panel3
    
    def test_bring_to_front(self):
        """Test bringing component to front of layer."""
        manager = LayerManager()
        panel1 = MockPanel()
        panel2 = MockPanel()
        panel3 = MockPanel()
        
        manager.add_component(panel1, UILayer.PANELS)
        manager.add_component(panel2, UILayer.PANELS)
        manager.add_component(panel3, UILayer.PANELS)
        
        # Bring panel1 to front
        manager.bring_to_front(panel1)
        
        panels_layer = manager.layers[UILayer.PANELS]
        assert panels_layer[-1] == panel1  # Should be last (on top)


class TestCollisionDetector:
    """Test collision detection."""
    
    def test_check_collision_overlap(self):
        """Test collision detection with overlapping rects."""
        rect1 = pygame.Rect(0, 0, 100, 100)
        rect2 = pygame.Rect(50, 50, 100, 100)
        
        assert CollisionDetector.check_collision(rect1, rect2)
    
    def test_check_collision_no_overlap(self):
        """Test collision detection with non-overlapping rects."""
        rect1 = pygame.Rect(0, 0, 100, 100)
        rect2 = pygame.Rect(200, 200, 100, 100)
        
        assert not CollisionDetector.check_collision(rect1, rect2)
    
    def test_find_collisions(self):
        """Test finding all collisions."""
        target = pygame.Rect(50, 50, 100, 100)
        
        other1 = pygame.Rect(0, 0, 100, 100)
        other2 = pygame.Rect(200, 200, 100, 100)
        other3 = pygame.Rect(100, 100, 100, 100)
        
        panel1 = MockPanel()
        panel2 = MockPanel()
        panel3 = MockPanel()
        
        other_rects = [
            (other1, panel1),
            (other2, panel2),
            (other3, panel3),
        ]
        
        collisions = CollisionDetector.find_collisions(target, other_rects)
        
        # Should collide with panel1 and panel3, not panel2
        assert panel1 in collisions
        assert panel3 in collisions
        assert panel2 not in collisions
    
    def test_resolve_push_horizontal(self):
        """Test push resolution horizontally."""
        mover = pygame.Rect(90, 50, 50, 50)
        blocker = pygame.Rect(50, 50, 50, 50)
        
        dx, dy = CollisionDetector.resolve_push(mover, blocker)
        
        # Should push horizontally (smaller overlap)
        assert dy == 0
        assert dx != 0
    
    def test_resolve_push_vertical(self):
        """Test push resolution vertically."""
        mover = pygame.Rect(50, 90, 50, 50)
        blocker = pygame.Rect(50, 50, 50, 50)
        
        dx, dy = CollisionDetector.resolve_push(mover, blocker)
        
        # Should push vertically (smaller overlap)
        assert dx == 0
        assert dy != 0


class TestLayoutManager:
    """Test layout manager."""
    
    @pytest.fixture
    def layout_manager(self):
        """Create layout manager for testing."""
        return LayoutManager(
            screen_size=(1280, 720),
            grid_config=GridConfig(
                rows=12,
                cols=12,
                gutter=10,
                margin=20
            )
        )
    
    def test_initialization(self, layout_manager):
        """Test layout manager initialization."""
        assert layout_manager.screen_size == (1280, 720)
        assert layout_manager.grid_config.rows == 12
        assert layout_manager.grid_config.cols == 12
        assert layout_manager._cell_width > 0
        assert layout_manager._cell_height > 0
    
    def test_grid_calculation(self, layout_manager):
        """Test grid cell calculation."""
        # With 1280x720 screen, 20px margin, 12x12 grid
        # Available: 1240x680 (after margins)
        # Gutter: 11*10 = 110px width, 11*10 = 110px height
        # Cell size: (1240-110)/12 = ~94px width, (680-110)/12 = ~47px height
        
        assert layout_manager._cell_width > 0
        assert layout_manager._cell_height > 0
        assert layout_manager._grid_origin == (20, 20)
    
    def test_grid_calculation_with_reserved_zones(self):
        """Test grid calculation with reserved zones."""
        nav_menu = pygame.Rect(0, 60, 200, 660)
        hud = pygame.Rect(0, 0, 1280, 60)
        
        manager = LayoutManager(
            screen_size=(1280, 720),
            grid_config=GridConfig(
                rows=12,
                cols=12,
                reserved_zones=[nav_menu, hud]
            )
        )
        
        # Grid origin should be after nav menu and HUD
        assert manager._grid_origin[0] >= nav_menu.right
        assert manager._grid_origin[1] >= hud.bottom
    
    def test_add_panel_grid_mode(self, layout_manager):
        """Test adding panel in grid mode."""
        panel = MockPanel()
        constraints = GridConstraints(row=0, col=0, row_span=6, col_span=4)
        
        layout_manager.add_panel(
            "test_panel",
            panel,
            LayoutMode.GRID,
            constraints,
            UILayer.PANELS
        )
        
        assert "test_panel" in layout_manager.panels
        assert layout_manager.panel_modes["test_panel"] == LayoutMode.GRID
        assert layout_manager.panel_constraints["test_panel"] == constraints
    
    def test_remove_panel(self, layout_manager):
        """Test removing panel."""
        panel = MockPanel()
        constraints = GridConstraints()
        
        layout_manager.add_panel("test_panel", panel, LayoutMode.GRID, constraints)
        assert "test_panel" in layout_manager.panels
        
        layout_manager.remove_panel("test_panel")
        assert "test_panel" not in layout_manager.panels
    
    def test_layout_grid_mode(self, layout_manager):
        """Test layout calculation for grid mode."""
        panel = MockPanel()
        constraints = GridConstraints(
            row=0,
            col=0,
            row_span=1,
            col_span=1,
            padding=10
        )
        
        layout_manager.add_panel("test_panel", panel, LayoutMode.GRID, constraints)
        layout_manager.layout()
        
        # Panel should be positioned at grid origin + padding
        expected_x = layout_manager._grid_origin[0] + constraints.padding
        expected_y = layout_manager._grid_origin[1] + constraints.padding
        
        assert panel.position[0] == expected_x
        assert panel.position[1] == expected_y
    
    def test_layout_anchored_mode(self, layout_manager):
        """Test layout calculation for anchored mode."""
        panel = MockPanel()
        constraints = AnchorConstraints(
            anchor_point="top-right",
            offset=(-10, 10),
            size_mode="fixed",
            size=(200, 100)
        )
        
        layout_manager.add_panel("test_panel", panel, LayoutMode.ANCHORED, constraints)
        layout_manager.layout()
        
        # Panel should be at top-right with offset
        expected_x = 1280 - 10  # screen width + offset
        expected_y = 0 + 10     # top + offset
        
        assert panel.position[0] == expected_x
        assert panel.position[1] == expected_y
        assert panel.size[0] == 200
        assert panel.size[1] == 100
    
    def test_window_resize(self, layout_manager):
        """Test window resize recalculation."""
        panel = MockPanel()
        constraints = GridConstraints(row=0, col=0)
        
        layout_manager.add_panel("test_panel", panel, LayoutMode.GRID, constraints)
        layout_manager.layout()
        
        initial_pos = panel.position.copy()
        
        # Resize window
        layout_manager.resize((1920, 1080))
        
        assert layout_manager.screen_size == (1920, 1080)
        # Grid cells should be recalculated
        # Panel position should update (may or may not be same depending on grid)
    
    def test_get_render_order(self, layout_manager):
        """Test getting panels in render order."""
        panel1 = MockPanel()
        panel2 = MockPanel()
        panel3 = MockPanel()
        
        layout_manager.add_panel("panel1", panel1, LayoutMode.GRID, GridConstraints(), UILayer.PANELS)
        layout_manager.add_panel("panel2", panel2, LayoutMode.GRID, GridConstraints(), UILayer.OVERLAY)
        layout_manager.add_panel("panel3", panel3, LayoutMode.GRID, GridConstraints(), UILayer.NOTIFICATION)
        
        render_order = layout_manager.get_render_order()
        
        # Should be ordered by layer: PANELS < OVERLAY < NOTIFICATION
        assert render_order.index(panel1) < render_order.index(panel2)
        assert render_order.index(panel2) < render_order.index(panel3)


class TestLayoutModes:
    """Test different layout modes."""
    
    @pytest.fixture
    def layout_manager(self):
        """Create layout manager."""
        return LayoutManager((1280, 720))
    
    def test_grid_multi_span(self, layout_manager):
        """Test grid with multiple row/col spans."""
        panel = MockPanel()
        constraints = GridConstraints(
            row=0,
            col=0,
            row_span=3,
            col_span=4,
            padding=5
        )
        
        layout_manager.add_panel("panel", panel, LayoutMode.GRID, constraints)
        layout_manager.layout()
        
        # Panel should span multiple cells
        cell_w = layout_manager._cell_width
        cell_h = layout_manager._cell_height
        gutter = layout_manager.grid_config.gutter
        
        expected_width = 4 * cell_w + 3 * gutter - 2 * constraints.padding
        expected_height = 3 * cell_h + 2 * gutter - 2 * constraints.padding
        
        assert panel.size[0] == expected_width
        assert panel.size[1] == expected_height
    
    def test_anchored_percentage_size(self, layout_manager):
        """Test anchored mode with percentage sizing."""
        panel = MockPanel()
        constraints = AnchorConstraints(
            anchor_point="center",
            size_mode="percentage",
            percentage=(0.5, 0.5)
        )
        
        layout_manager.add_panel("panel", panel, LayoutMode.ANCHORED, constraints)
        layout_manager.layout()
        
        # Panel should be 50% of screen size
        assert panel.size[0] == 1280 * 0.5
        assert panel.size[1] == 720 * 0.5


class TestResponsiveScaling:
    """Test responsive scaling behavior."""
    
    def test_responsive_grid_resize(self):
        """Test grid cells resize with window."""
        manager1 = LayoutManager((1280, 720))
        initial_cell_width = manager1._cell_width
        initial_cell_height = manager1._cell_height
        
        # Resize to larger window
        manager1.resize((1920, 1080))
        
        # Cells should be larger
        assert manager1._cell_width > initial_cell_width
        assert manager1._cell_height > initial_cell_height
    
    def test_responsive_anchored_resize(self):
        """Test anchored panels reposition on resize."""
        manager = LayoutManager((1280, 720))
        panel = MockPanel()
        constraints = AnchorConstraints(
            anchor_point="bottom-right",
            offset=(-20, -20),
            size_mode="fixed",
            size=(200, 100)
        )
        
        manager.add_panel("panel", panel, LayoutMode.ANCHORED, constraints)
        manager.layout()
        
        initial_x = panel.position[0]
        
        # Resize window
        manager.resize((1920, 1080))
        
        # Panel should move with anchor point
        assert panel.position[0] > initial_x  # Moved right
