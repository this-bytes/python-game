"""
Layout Management System for UI components.

Provides grid-based, constraint-based, and responsive layout management
to replace absolute positioning chaos.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable, Any
from enum import Enum, IntEnum
import pygame
from collections import defaultdict


class LayoutMode(Enum):
    """Layout positioning modes."""
    GRID = "grid"           # Grid-based positioning
    ANCHORED = "anchored"   # Anchor to screen edges/corners
    FLOATING = "floating"   # Free-floating (draggable)
    FIXED = "fixed"         # Fixed absolute position (legacy)


class CollisionBehavior(Enum):
    """How to handle panel collisions."""
    OVERLAP = "overlap"   # Allow overlap
    PUSH = "push"         # Push other panels away
    BLOCK = "block"       # Block movement
    RESIZE = "resize"     # Resize to fit


class UILayer(IntEnum):
    """UI rendering layers (higher = on top)."""
    BACKGROUND = 0
    PANELS = 10
    FLOATING = 20
    OVERLAY = 30
    MODAL = 40
    NOTIFICATION = 50
    TOOLTIP = 60
    DEBUG = 100


@dataclass
class GridConstraints:
    """Grid-based layout constraints."""
    row: int = 0              # Grid row (0-based)
    col: int = 0              # Grid column (0-based)
    row_span: int = 1         # Number of rows
    col_span: int = 1         # Number of columns
    padding: int = 10         # Padding around cell
    alignment: str = "fill"   # fill, center, start, end
    min_width: int = 200      # Minimum width
    min_height: int = 100     # Minimum height


@dataclass
class AnchorConstraints:
    """Anchor-based layout constraints."""
    anchor_point: str = "top-left"  # Anchor position
    offset: Tuple[int, int] = (0, 0)  # Offset from anchor
    size_mode: str = "fixed"        # fixed, percentage, content
    size: Tuple[int, int] = (200, 100)  # Size if fixed
    percentage: Tuple[float, float] = (0.2, 0.2)  # Size if percentage


@dataclass
class FloatingConstraints:
    """Floating/draggable layout constraints."""
    initial_position: str = "center"  # center, top-left, etc.
    min_bounds: Tuple[int, int] = (0, 0)
    max_bounds: Optional[Tuple[int, int]] = None  # Auto-set to window
    snap_to_grid: bool = False
    collision_behavior: CollisionBehavior = CollisionBehavior.OVERLAP


@dataclass
class FixedConstraints:
    """Fixed absolute position (legacy support)."""
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (400, 500)


@dataclass
class GridConfig:
    """Grid layout configuration."""
    rows: int = 12
    cols: int = 12
    gutter: int = 10
    margin: int = 20
    reserved_zones: List[pygame.Rect] = field(default_factory=list)


class LayerManager:
    """Manages z-order/layer system for UI components."""
    
    def __init__(self):
        """Initialize layer manager."""
        self.layers: Dict[int, List] = defaultdict(list)
        self._render_order_cache: Optional[List] = None
        self._dirty = True
    
    def add_component(self, component, layer: int = UILayer.PANELS):
        """Add component to specific layer.
        
        Args:
            component: UI component to add
            layer: Layer number (higher = on top)
        """
        if component not in self.layers[layer]:
            self.layers[layer].append(component)
            self._dirty = True
    
    def remove_component(self, component):
        """Remove component from all layers.
        
        Args:
            component: UI component to remove
        """
        for layer_list in self.layers.values():
            if component in layer_list:
                layer_list.remove(component)
                self._dirty = True
    
    def bring_to_front(self, component):
        """Move component to front of its layer.
        
        Args:
            component: UI component to move
        """
        for layer_list in self.layers.values():
            if component in layer_list:
                layer_list.remove(component)
                layer_list.append(component)
                self._dirty = True
                break
    
    def get_render_order(self) -> List:
        """Get all components in render order (back to front).
        
        Returns:
            List of components sorted by layer and order
        """
        if self._dirty or self._render_order_cache is None:
            render_list = []
            for layer in sorted(self.layers.keys()):
                render_list.extend(self.layers[layer])
            self._render_order_cache = render_list
            self._dirty = False
        return self._render_order_cache
    
    def get_layer(self, component) -> Optional[int]:
        """Get layer number for component.
        
        Args:
            component: UI component
            
        Returns:
            Layer number or None if not found
        """
        for layer, components in self.layers.items():
            if component in components:
                return layer
        return None


class CollisionDetector:
    """Detect and resolve panel collisions."""
    
    @staticmethod
    def check_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """Check if two rectangles overlap.
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle
            
        Returns:
            True if rectangles overlap
        """
        return rect1.colliderect(rect2)
    
    @staticmethod
    def find_collisions(target_rect: pygame.Rect, other_rects: List[Tuple[pygame.Rect, Any]]) -> List:
        """Find all rectangles that collide with target.
        
        Args:
            target_rect: Rectangle to check
            other_rects: List of (rect, component) tuples
            
        Returns:
            List of colliding components
        """
        collisions = []
        for rect, component in other_rects:
            if CollisionDetector.check_collision(target_rect, rect):
                collisions.append(component)
        return collisions
    
    @staticmethod
    def resolve_push(mover_rect: pygame.Rect, blocker_rect: pygame.Rect) -> Tuple[int, int]:
        """Calculate push offset to resolve collision.
        
        Args:
            mover_rect: Rectangle being moved
            blocker_rect: Rectangle blocking movement
            
        Returns:
            (dx, dy) offset to resolve collision
        """
        # Calculate overlap on each axis
        left_overlap = mover_rect.right - blocker_rect.left
        right_overlap = blocker_rect.right - mover_rect.left
        top_overlap = mover_rect.bottom - blocker_rect.top
        bottom_overlap = blocker_rect.bottom - mover_rect.top
        
        # Find minimum overlap direction
        min_x = min(left_overlap, right_overlap)
        min_y = min(top_overlap, bottom_overlap)
        
        if min_x < min_y:
            # Push horizontally
            return (-left_overlap if left_overlap < right_overlap else right_overlap, 0)
        else:
            # Push vertically
            return (0, -top_overlap if top_overlap < bottom_overlap else bottom_overlap)


class LayoutManager:
    """Main layout manager coordinating all layout systems."""
    
    def __init__(self, screen_size: Tuple[int, int], grid_config: Optional[GridConfig] = None):
        """Initialize layout manager.
        
        Args:
            screen_size: Current screen dimensions (width, height)
            grid_config: Grid configuration (uses defaults if None)
        """
        self.screen_size = screen_size
        self.grid_config = grid_config or GridConfig()
        self.layer_manager = LayerManager()
        self.collision_detector = CollisionDetector()
        
        # Panel registry
        self.panels: Dict[str, Any] = {}  # name -> panel
        self.panel_constraints: Dict[str, Any] = {}  # name -> constraints
        self.panel_modes: Dict[str, LayoutMode] = {}  # name -> mode
        
        # Grid cache
        self._cell_width = 0
        self._cell_height = 0
        self._grid_origin = (0, 0)
        self._layout_dirty = True
        
        self._calculate_grid()
    
    def _calculate_grid(self):
        """Calculate grid cell dimensions based on screen and reserved zones."""
        # Calculate available space
        available_x = self.grid_config.margin
        available_y = self.grid_config.margin
        available_width = self.screen_size[0] - self.grid_config.margin * 2
        available_height = self.screen_size[1] - self.grid_config.margin * 2
        
        # Account for reserved zones
        for zone in self.grid_config.reserved_zones:
            # Adjust based on zone position
            if zone.left <= self.grid_config.margin:
                # Left-side reservation (e.g., nav menu)
                available_x = max(available_x, zone.right + self.grid_config.gutter)
                available_width -= zone.width
            if zone.top <= self.grid_config.margin:
                # Top reservation (e.g., HUD)
                available_y = max(available_y, zone.bottom + self.grid_config.gutter)
                available_height -= zone.height
        
        self._grid_origin = (available_x, available_y)
        
        # Calculate cell dimensions
        total_gutter_width = self.grid_config.gutter * (self.grid_config.cols - 1)
        total_gutter_height = self.grid_config.gutter * (self.grid_config.rows - 1)
        
        self._cell_width = (available_width - total_gutter_width) // self.grid_config.cols
        self._cell_height = (available_height - total_gutter_height) // self.grid_config.rows
        
        self._layout_dirty = True
    
    def add_panel(self, name: str, panel, mode: LayoutMode, constraints, layer: int = UILayer.PANELS):
        """Add panel to layout manager.
        
        Args:
            name: Unique panel identifier
            panel: Panel instance
            mode: Layout mode
            constraints: Layout constraints matching mode
            layer: Rendering layer
        """
        self.panels[name] = panel
        self.panel_constraints[name] = constraints
        self.panel_modes[name] = mode
        self.layer_manager.add_component(panel, layer)
        self._layout_dirty = True
    
    def remove_panel(self, name: str):
        """Remove panel from layout manager.
        
        Args:
            name: Panel identifier
        """
        if name in self.panels:
            panel = self.panels[name]
            self.layer_manager.remove_component(panel)
            del self.panels[name]
            del self.panel_constraints[name]
            del self.panel_modes[name]
            self._layout_dirty = True
    
    def layout(self):
        """Recalculate and apply layout to all panels."""
        if not self._layout_dirty:
            return
        
        for name, panel in self.panels.items():
            mode = self.panel_modes[name]
            constraints = self.panel_constraints[name]
            
            if mode == LayoutMode.GRID:
                bounds = self._calculate_grid_bounds(constraints)
            elif mode == LayoutMode.ANCHORED:
                bounds = self._calculate_anchored_bounds(constraints)
            elif mode == LayoutMode.FLOATING:
                bounds = self._calculate_floating_bounds(constraints)
            elif mode == LayoutMode.FIXED:
                bounds = pygame.Rect(constraints.position, constraints.size)
            else:
                continue
            
            # Apply bounds to panel
            if hasattr(panel, 'set_position'):
                panel.set_position(bounds.x, bounds.y)
            if hasattr(panel, 'set_size'):
                panel.set_size(bounds.width, bounds.height)
        
        self._layout_dirty = False
    
    def _calculate_grid_bounds(self, constraints: GridConstraints) -> pygame.Rect:
        """Calculate bounds for grid-based panel.
        
        Args:
            constraints: Grid constraints
            
        Returns:
            Calculated rectangle
        """
        # Calculate cell position
        x = self._grid_origin[0] + constraints.col * (self._cell_width + self.grid_config.gutter)
        y = self._grid_origin[1] + constraints.row * (self._cell_height + self.grid_config.gutter)
        
        # Calculate size including span
        width = constraints.col_span * self._cell_width + (constraints.col_span - 1) * self.grid_config.gutter
        height = constraints.row_span * self._cell_height + (constraints.row_span - 1) * self.grid_config.gutter
        
        # Apply padding
        x += constraints.padding
        y += constraints.padding
        width -= constraints.padding * 2
        height -= constraints.padding * 2
        
        # Apply minimum constraints
        width = max(width, constraints.min_width)
        height = max(height, constraints.min_height)
        
        return pygame.Rect(x, y, width, height)
    
    def _calculate_anchored_bounds(self, constraints: AnchorConstraints) -> pygame.Rect:
        """Calculate bounds for anchored panel.
        
        Args:
            constraints: Anchor constraints
            
        Returns:
            Calculated rectangle
        """
        # Calculate anchor position
        anchor_map = {
            "top-left": (0, 0),
            "top-center": (self.screen_size[0] // 2, 0),
            "top-right": (self.screen_size[0], 0),
            "center-left": (0, self.screen_size[1] // 2),
            "center": (self.screen_size[0] // 2, self.screen_size[1] // 2),
            "center-right": (self.screen_size[0], self.screen_size[1] // 2),
            "bottom-left": (0, self.screen_size[1]),
            "bottom-center": (self.screen_size[0] // 2, self.screen_size[1]),
            "bottom-right": (self.screen_size[0], self.screen_size[1]),
        }
        
        anchor_x, anchor_y = anchor_map.get(constraints.anchor_point, (0, 0))
        
        # Calculate size
        if constraints.size_mode == "fixed":
            width, height = constraints.size
        elif constraints.size_mode == "percentage":
            width = int(self.screen_size[0] * constraints.percentage[0])
            height = int(self.screen_size[1] * constraints.percentage[1])
        else:
            width, height = constraints.size  # Default to fixed
        
        # Apply offset
        x = anchor_x + constraints.offset[0]
        y = anchor_y + constraints.offset[1]
        
        return pygame.Rect(x, y, width, height)
    
    def _calculate_floating_bounds(self, constraints: FloatingConstraints) -> pygame.Rect:
        """Calculate bounds for floating panel.
        
        Args:
            constraints: Floating constraints
            
        Returns:
            Calculated rectangle
        """
        # For floating panels, we just enforce bounds
        # Initial position is set by panel itself
        # This method is called when panel moves
        # For now, return a centered position
        width, height = 400, 500  # Default size
        x = (self.screen_size[0] - width) // 2
        y = (self.screen_size[1] - height) // 2
        
        return pygame.Rect(x, y, width, height)
    
    def resize(self, new_screen_size: Tuple[int, int]):
        """Handle window resize.
        
        Args:
            new_screen_size: New screen dimensions
        """
        self.screen_size = new_screen_size
        self._calculate_grid()
        self.layout()
    
    def get_render_order(self) -> List:
        """Get panels in render order (back to front).
        
        Returns:
            List of panels sorted by layer
        """
        return self.layer_manager.get_render_order()
