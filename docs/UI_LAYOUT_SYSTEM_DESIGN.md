# UI Layout System Architecture Design

## 🚨 PROBLEM STATEMENT

### Current Issues
1. **Absolute positioning chaos** - Every panel has hardcoded (x, y) coordinates
2. **No bounds checking** - Components freely overlap each other
3. **No responsive design** - Window resize breaks everything
4. **Manual layout management** - Adding/moving panels requires recalculating all positions
5. **No z-order control** - Rendering order is based on list order, not priority
6. **No collision detection** - Panels can be dragged on top of each other

### Impact
- **User reports**: "UI overlap makes the game unusable"
- **Developer pain**: Every UI change requires manual position calculation
- **Scalability**: Can't add new panels without breaking layout
- **Professionalism**: Fixed layout = not production-ready

## 🎯 DESIGN GOALS

1. **Automatic layout** - Components position themselves based on constraints
2. **Bounds enforcement** - No overlaps, respect boundaries
3. **Responsive scaling** - Window resize = automatic reflow
4. **Z-order control** - Explicit layer system
5. **Developer-friendly** - Simple API, declarative positioning
6. **Performance** - Layout calculations cached, only recompute on change

## 🏗️ ARCHITECTURE

### Component Hierarchy
```
LayoutManager (Singleton)
├── GridLayout - Screen divided into grid cells
├── ResponsiveContainer - Handle window resize
├── LayerManager - Z-order/layer control
└── CollisionDetector - Bounds checking

Panel (Enhanced)
├── layout_mode: Enum (GRID, ANCHORED, FLOATING, FIXED)
├── grid_constraints: GridConstraints
├── anchor_constraints: AnchorConstraints
├── layer: int (0-100, higher = on top)
├── responsive: bool
└── bounds: Rect (computed automatically)

GameUI (Refactored)
├── layout_manager: LayoutManager
├── layout_config: LayoutConfig (per view)
└── panels: Dict[str, Panel] (managed by layout system)
```

## 📐 LAYOUT MODES

### 1. GridLayout Mode
**Use Case**: Main content panels that need structured positioning

```python
GridConstraints(
    row=0,           # Grid row (0-based)
    col=0,           # Grid column (0-based)
    row_span=1,      # Number of rows to occupy
    col_span=1,      # Number of columns to occupy
    padding=10,      # Padding around cell
    alignment="fill" # fill, center, start, end
)
```

**Example**: Operations view with 2-column layout
```
┌────────────────────────────────────────┐
│  Nav │  Specialists  │   Incidents    │
│ (200)│    (col 0)    │    (col 1)     │
│      │               │                 │
│      │   row 0       │    row 0        │
│      │   col_span=1  │    col_span=1   │
└────────────────────────────────────────┘
```

### 2. Anchored Mode
**Use Case**: HUD elements, overlays, tooltips

```python
AnchorConstraints(
    anchor_point="top-left",  # Where to anchor
    offset=(10, 10),          # Offset from anchor
    size_mode="fixed",        # fixed, percentage, content
    size=(200, 100)           # Size if fixed/percentage
)
```

**Anchor Points**: 
- `top-left`, `top-center`, `top-right`
- `center-left`, `center`, `center-right`  
- `bottom-left`, `bottom-center`, `bottom-right`

### 3. Floating Mode
**Use Case**: Draggable panels, modals, pop-ups

```python
FloatingConstraints(
    min_bounds=(0, 0),        # Minimum position
    max_bounds=(1280, 720),   # Maximum position (auto-set to window)
    snap_to_grid=True,        # Snap to grid when dragging
    collision_behavior="push" # push, overlap, block
)
```

### 4. Fixed Mode (Legacy)
**Use Case**: Backwards compatibility, special cases

```python
FixedConstraints(
    position=(100, 100),
    size=(400, 500)
)
```

## 🔢 GRID SYSTEM SPECIFICATION

### Grid Configuration
```python
@dataclass
class GridConfig:
    """Grid layout configuration."""
    rows: int = 12              # Number of rows
    cols: int = 12              # Number of columns
    gutter: int = 10            # Space between cells
    margin: int = 20            # Screen margin
    reserved_zones: List[Rect]  # Reserved for nav, HUD, etc.
```

### Default Grid (1280x720)
```
Screen: 1280x720
Reserved Zones:
  - Navigation Menu: (0, 60) → (200, 720)
  - HUD Overlay: (0, 0) → (1280, 60)

Available Grid Space: (220, 80) → (1260, 700)
Grid: 12 cols × 12 rows
Cell Size: ~86px × ~51px (auto-calculated)
```

### Grid Cell Calculation
```python
def calculate_cell_dimensions(self, screen_size: Tuple[int, int]) -> Tuple[int, int]:
    """Calculate grid cell size based on screen and reserved zones."""
    available_width = screen_size[0] - self.margin * 2
    available_height = screen_size[1] - self.margin * 2
    
    # Subtract reserved zones
    for zone in self.reserved_zones:
        available_width -= zone.width
        available_height -= zone.height
    
    # Calculate cell size
    cell_width = (available_width - self.gutter * (self.cols - 1)) // self.cols
    cell_height = (available_height - self.gutter * (self.rows - 1)) // self.rows
    
    return (cell_width, cell_height)
```

## 🎨 RESPONSIVE SCALING

### Size Modes
1. **Fixed** - Exact pixel size (e.g., 400×600)
2. **Percentage** - Relative to screen (e.g., 30% width, 80% height)
3. **Fill** - Fill available space in grid cell
4. **Content** - Size based on content (min/max constraints)

### Responsive Behavior
```python
@dataclass
class ResponsiveConfig:
    """Responsive behavior configuration."""
    min_width: int = 200        # Minimum width
    max_width: int = 9999       # Maximum width
    min_height: int = 100       # Minimum height
    max_height: int = 9999      # Maximum height
    aspect_ratio: Optional[float] = None  # Maintain aspect ratio
    scale_mode: str = "fit"     # fit, fill, stretch
```

### Window Resize Handling
```python
def on_window_resize(self, new_size: Tuple[int, int]):
    """Handle window resize event."""
    # 1. Recalculate grid cell dimensions
    self.update_grid_cells(new_size)
    
    # 2. Reposition all panels based on constraints
    for panel in self.panels:
        if panel.responsive:
            new_bounds = self.calculate_panel_bounds(panel)
            panel.set_bounds(new_bounds)
    
    # 3. Check for collisions and adjust
    self.resolve_collisions()
    
    # 4. Trigger repaint
    self.dirty = True
```

## 🔀 Z-ORDER / LAYER SYSTEM

### Layer Definitions
```python
class UILayer(IntEnum):
    """UI rendering layers (lower = behind, higher = on top)."""
    BACKGROUND = 0       # Background elements
    PANELS = 10          # Main content panels
    FLOATING = 20        # Floating panels (draggable)
    OVERLAY = 30         # Overlays (synergy, dopamine)
    MODAL = 40           # Modal dialogs
    NOTIFICATION = 50    # Notifications
    TOOLTIP = 60         # Tooltips (always on top)
    DEBUG = 100          # Debug overlays
```

### Layer Manager
```python
class LayerManager:
    """Manages z-order of UI components."""
    
    def __init__(self):
        self.layers: Dict[int, List[Panel]] = defaultdict(list)
    
    def add_component(self, component: Panel, layer: int = UILayer.PANELS):
        """Add component to specific layer."""
        self.layers[layer].append(component)
        self.sort_layer(layer)
    
    def get_render_order(self) -> List[Panel]:
        """Get all components in render order (back to front)."""
        render_list = []
        for layer in sorted(self.layers.keys()):
            render_list.extend(self.layers[layer])
        return render_list
    
    def bring_to_front(self, component: Panel):
        """Move component to front of its layer."""
        layer = component.layer
        if component in self.layers[layer]:
            self.layers[layer].remove(component)
            self.layers[layer].append(component)
```

## 🚧 COLLISION DETECTION & RESOLUTION

### Collision Behaviors
```python
class CollisionBehavior(Enum):
    """How to handle panel collisions."""
    OVERLAP = "overlap"   # Allow overlap (default for fixed panels)
    PUSH = "push"         # Push other panels away
    BLOCK = "block"       # Don't allow movement into collision
    RESIZE = "resize"     # Resize to fit available space
```

### Collision Detector
```python
class CollisionDetector:
    """Detect and resolve panel collisions."""
    
    def check_collision(self, panel1: Panel, panel2: Panel) -> bool:
        """Check if two panels overlap."""
        return panel1.bounds.colliderect(panel2.bounds)
    
    def find_collisions(self, panel: Panel, all_panels: List[Panel]) -> List[Panel]:
        """Find all panels that collide with given panel."""
        collisions = []
        for other in all_panels:
            if other != panel and self.check_collision(panel, other):
                collisions.append(other)
        return collisions
    
    def resolve_collision(self, panel: Panel, collision: Panel):
        """Resolve collision based on behavior."""
        if panel.collision_behavior == CollisionBehavior.PUSH:
            self._push_panel(collision, panel)
        elif panel.collision_behavior == CollisionBehavior.BLOCK:
            self._revert_position(panel)
        elif panel.collision_behavior == CollisionBehavior.RESIZE:
            self._resize_to_fit(panel, collision)
```

## 📝 API DESIGN

### Panel Creation (New Way)
```python
# Grid-based panel
specialist_panel = SpecialistRosterPanel(
    game_state=game_state,
    layout_mode=LayoutMode.GRID,
    grid_constraints=GridConstraints(
        row=0,
        col=0,
        row_span=12,  # Full height
        col_span=4,   # 4 columns wide
        padding=10
    ),
    layer=UILayer.PANELS,
    responsive=True
)

# Anchored overlay
notification_panel = NotificationPanel(
    layout_mode=LayoutMode.ANCHORED,
    anchor_constraints=AnchorConstraints(
        anchor_point="top-right",
        offset=(-20, 20),
        size_mode="fixed",
        size=(300, 400)
    ),
    layer=UILayer.NOTIFICATION,
    responsive=True
)

# Floating modal
settings_modal = SettingsModal(
    layout_mode=LayoutMode.FLOATING,
    floating_constraints=FloatingConstraints(
        initial_position="center",
        snap_to_grid=False,
        collision_behavior=CollisionBehavior.OVERLAP
    ),
    layer=UILayer.MODAL,
    responsive=True
)
```

### Layout Manager Usage
```python
# In GameUI.__init__
self.layout_manager = LayoutManager(
    grid_config=GridConfig(
        rows=12,
        cols=12,
        gutter=10,
        margin=20,
        reserved_zones=[
            Rect(0, 0, 200, 720),   # Nav menu
            Rect(0, 0, 1280, 60)    # HUD
        ]
    )
)

# Register panels with layout manager
self.layout_manager.add_panel(specialist_panel, "specialist_roster")
self.layout_manager.add_panel(incident_panel, "incident_queue")

# Layout manager handles positioning automatically
self.layout_manager.layout()

# On window resize
def on_resize(self, new_size):
    self.layout_manager.resize(new_size)
```

## 🔄 MIGRATION STRATEGY

### Phase 1: Core Infrastructure (This Session)
1. ✅ Create `LayoutManager` base class
2. ✅ Implement `GridLayout` system
3. ✅ Add `LayerManager` for z-order
4. ✅ Create `CollisionDetector`
5. ✅ Add `ResponsiveContainer`

### Phase 2: Panel Enhancement (This Session)
1. ✅ Add layout constraints to `Panel` base class
2. ✅ Implement collision detection in panels
3. ✅ Add responsive behavior

### Phase 3: GameUI Refactor (This Session)
1. ✅ Integrate `LayoutManager` into `GameUI`
2. ✅ Define grid layouts for each view
3. ✅ Remove hardcoded positions

### Phase 4: Panel Migration (This Session)
1. ✅ Update `SpecialistRosterPanel` to use grid
2. ✅ Update `IncidentQueuePanel` to use grid
3. ✅ Update other panels
4. ✅ Test each panel individually

### Phase 5: Testing & Validation (This Session)
1. ✅ Test window resize
2. ✅ Test collision detection
3. ✅ Test z-order rendering
4. ✅ Integration tests

## 📊 PERFORMANCE CONSIDERATIONS

### Optimization Strategies
1. **Lazy layout calculation** - Only recalculate when needed
2. **Dirty flag system** - Track which panels need repositioning
3. **Batch updates** - Group layout changes together
4. **Cached cell dimensions** - Don't recalculate every frame
5. **Spatial partitioning** - Only check nearby panels for collisions

### Performance Targets
- Layout calculation: < 1ms for 10 panels
- Collision detection: < 0.5ms per frame
- Window resize: < 5ms to reflow
- No frame drops during resize

## 🧪 TESTING STRATEGY

### Unit Tests
- `test_grid_cell_calculation()`
- `test_collision_detection()`
- `test_anchor_point_positioning()`
- `test_responsive_scaling()`
- `test_layer_ordering()`

### Integration Tests
- `test_full_layout_system()`
- `test_window_resize_reflow()`
- `test_panel_drag_collision()`
- `test_view_switching_layout()`

### Visual Tests
- Screenshot comparison for layout consistency
- Manual testing of drag-and-drop
- Window resize visual validation

## 📚 REFERENCE IMPLEMENTATIONS

### Similar Systems
- **CSS Grid/Flexbox** - Web layout inspiration
- **Unity UI Layout Groups** - Game engine layout system
- **Qt Layouts** - Desktop app layout managers
- **Android ConstraintLayout** - Mobile layout system

### Key Learnings
- Declarative > Imperative for layouts
- Constraints > Absolute positions
- Caching is critical for performance
- Simple API = better adoption

## 🎯 SUCCESS CRITERIA

1. ✅ No hardcoded positions in panel constructors
2. ✅ Window resize works without breaking layout
3. ✅ No panel overlaps (unless intentional)
4. ✅ Z-order rendering correct
5. ✅ Easy to add new panels (< 5 lines of code)
6. ✅ All tests pass
7. ✅ No performance regression
8. ✅ Developer-friendly API

---

**This is a foundational refactor that will make the UI system scalable and professional.**
