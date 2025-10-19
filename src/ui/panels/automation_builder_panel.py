"""Automation Script Builder Panel for creating custom automation rules.

Provides a visual drag-and-drop interface for building automation scripts
with nodes representing conditions, actions, and logic operators.
"""

import pygame
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.ui.components.panel import Panel
from src.models.automation_script import AutomationScript, TriggerConditions
from src.models.game_state import GameState


class NodeType(Enum):
    """Types of nodes in the automation builder."""
    CONDITION = "condition"
    ACTION = "action"
    LOGIC = "logic"
    OUTPUT = "output"


class ConnectionType(Enum):
    """Types of connections between nodes."""
    FLOW = "flow"  # Execution flow
    DATA = "data"  # Data flow


@dataclass
class NodeConnection:
    """Represents a connection between two nodes."""
    from_node_id: str
    from_output_index: int
    to_node_id: str
    to_input_index: int
    connection_type: ConnectionType = ConnectionType.FLOW

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "from_node_id": self.from_node_id,
            "from_output_index": self.from_output_index,
            "to_node_id": self.to_node_id,
            "to_input_index": self.to_input_index,
            "connection_type": self.connection_type.value
        }


@dataclass
class NodePort:
    """Input or output port on a node."""
    name: str
    data_type: str
    is_input: bool
    position: Tuple[int, int] = (0, 0)

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within this port."""
        px, py = point
        port_x, port_y = self.position
        return (port_x - 5 <= px <= port_x + 5) and (port_y - 5 <= py <= port_y + 5)


@dataclass
class AutomationNode:
    """A node in the automation builder graph."""
    id: str
    node_type: NodeType
    title: str
    position: Tuple[int, int]
    size: Tuple[int, int] = (120, 80)
    inputs: List[NodePort] = field(default_factory=list)
    outputs: List[NodePort] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    is_selected: bool = False
    is_dragging: bool = False

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within this node."""
        px, py = point
        nx, ny = self.position
        nw, nh = self.size
        return (nx <= px <= nx + nw) and (ny <= py <= ny + nh)

    def get_port_at_point(self, point: Tuple[int, int]) -> Optional[Tuple[NodePort, int]]:
        """Get port at the given point, returns (port, index)."""
        for i, port in enumerate(self.inputs):
            if port.contains_point(point):
                return (port, i)
        for i, port in enumerate(self.outputs):
            if port.contains_point(point):
                return (port, i)
        return None

    def update_port_positions(self) -> None:
        """Update port positions based on node position."""
        x, y = self.position
        w, h = self.size

        # Input ports on left side
        for i, port in enumerate(self.inputs):
            port.position = (x, y + 20 + i * 20)

        # Output ports on right side
        for i, port in enumerate(self.outputs):
            port.position = (x + w, y + 20 + i * 20)


class AutomationBuilderPanel(Panel):
    """Visual drag-and-drop automation script builder."""

    def __init__(self, game_state: GameState):
        """Initialize automation builder panel.

        Args:
            game_state: Game state reference
        """
        super().__init__(
            title="Automation Script Builder",
            position=(200, 100),
            size=(1000, 700),
            closeable=True,
            minimizable=True,
            draggable=True,
        )

        self.game_state = game_state
        self.nodes: List[AutomationNode] = []
        self.connections: List[NodeConnection] = []
        self.selected_nodes: List[str] = []
        self.dragged_connection: Optional[Tuple[str, int]] = None  # (node_id, output_index)
        self.connection_start_pos: Optional[Tuple[int, int]] = None

        # Node creation palette
        self.palette_nodes = self._create_palette_nodes()

        # Colors
        self.node_colors = {
            NodeType.CONDITION: (100, 150, 255),
            NodeType.ACTION: (255, 150, 100),
            NodeType.LOGIC: (150, 255, 100),
            NodeType.OUTPUT: (255, 255, 100)
        }

        self.connection_color = (200, 200, 200)
        self.selected_color = (255, 255, 255)

        # Initialize with a basic template
        self._create_basic_template()

    def _create_palette_nodes(self) -> List[AutomationNode]:
        """Create the palette of available node types."""
        palette = []

        # Condition nodes
        palette.append(AutomationNode(
            id="palette_condition_difficulty",
            node_type=NodeType.CONDITION,
            title="Difficulty ≤",
            position=(10, 50),
            config={"condition_type": "max_difficulty", "value": 2}
        ))

        palette.append(AutomationNode(
            id="palette_condition_specialty",
            node_type=NodeType.CONDITION,
            title="Specialty Match",
            position=(10, 140),
            config={"condition_type": "specialty_match", "value": True}
        ))

        palette.append(AutomationNode(
            id="palette_condition_available",
            node_type=NodeType.CONDITION,
            title="Specialist Available",
            position=(10, 230),
            config={"condition_type": "specialist_available", "value": True}
        ))

        # Action nodes
        palette.append(AutomationNode(
            id="palette_action_assign",
            node_type=NodeType.ACTION,
            title="Auto Assign",
            position=(10, 350),
            config={"action_type": "auto_assign"}
        ))

        palette.append(AutomationNode(
            id="palette_action_boost",
            node_type=NodeType.ACTION,
            title="Speed Boost",
            position=(10, 440),
            config={"action_type": "speed_boost", "magnitude": 1.5}
        ))

        # Logic nodes
        palette.append(AutomationNode(
            id="palette_logic_and",
            node_type=NodeType.LOGIC,
            title="AND",
            position=(10, 560),
            config={"logic_type": "AND"}
        ))

        # Output node
        palette.append(AutomationNode(
            id="palette_output",
            node_type=NodeType.OUTPUT,
            title="Execute Script",
            position=(10, 650),
            config={"output_type": "execute"}
        ))

        # Set up ports for palette nodes
        for node in palette:
            self._setup_node_ports(node)

        return palette

    def _setup_node_ports(self, node: AutomationNode) -> None:
        """Set up input and output ports for a node based on its type."""
        if node.node_type == NodeType.CONDITION:
            node.outputs.append(NodePort("Result", "bool", False))
        elif node.node_type == NodeType.ACTION:
            node.inputs.append(NodePort("Trigger", "flow", True))
            node.outputs.append(NodePort("Done", "flow", False))
        elif node.node_type == NodeType.LOGIC:
            node.inputs.append(NodePort("Input A", "bool", True))
            node.inputs.append(NodePort("Input B", "bool", True))
            node.outputs.append(NodePort("Result", "bool", False))
        elif node.node_type == NodeType.OUTPUT:
            node.inputs.append(NodePort("Execute", "flow", True))

        node.update_port_positions()

    def _create_basic_template(self) -> None:
        """Create a basic automation script template."""
        # Create nodes for a simple auto-assign script
        condition_node = AutomationNode(
            id="condition_1",
            node_type=NodeType.CONDITION,
            title="Difficulty ≤ 2",
            position=(300, 200),
            config={"condition_type": "max_difficulty", "value": 2}
        )

        specialty_node = AutomationNode(
            id="condition_2",
            node_type=NodeType.CONDITION,
            title="Network Specialty",
            position=(300, 300),
            config={"condition_type": "specialty_match", "value": True}
        )

        and_node = AutomationNode(
            id="logic_1",
            node_type=NodeType.LOGIC,
            title="AND",
            position=(500, 250),
            config={"logic_type": "AND"}
        )

        action_node = AutomationNode(
            id="action_1",
            node_type=NodeType.ACTION,
            title="Auto Assign",
            position=(700, 250),
            config={"action_type": "auto_assign"}
        )

        output_node = AutomationNode(
            id="output_1",
            node_type=NodeType.OUTPUT,
            title="Execute",
            position=(900, 250),
            config={"output_type": "execute"}
        )

        # Set up ports
        for node in [condition_node, specialty_node, and_node, action_node, output_node]:
            self._setup_node_ports(node)

        self.nodes.extend([condition_node, specialty_node, and_node, action_node, output_node])

        # Create connections
        self.connections.extend([
            NodeConnection("condition_1", 0, "logic_1", 0),
            NodeConnection("condition_2", 0, "logic_1", 1),
            NodeConnection("logic_1", 0, "action_1", 0),
            NodeConnection("action_1", 0, "output_1", 0)
        ])

    def render(self, screen: pygame.Surface) -> None:
        """Render the automation builder."""
        # Render panel background
        super().render(screen)

        if not self.visible:
            return

        # Get content area
        content_rect = pygame.Rect(
            self.position[0] + self.BORDER_WIDTH,
            self.position[1] + self.TITLE_BAR_HEIGHT + self.BORDER_WIDTH,
            self.size[0] - 2 * self.BORDER_WIDTH,
            self.size[1] - self.TITLE_BAR_HEIGHT - 2 * self.BORDER_WIDTH
        )

        # Render palette area
        palette_rect = pygame.Rect(content_rect.x, content_rect.y, 140, content_rect.height)
        pygame.draw.rect(screen, (30, 30, 50), palette_rect)

        # Render palette title
        font = pygame.font.SysFont("Arial", 14, bold=True)
        title_text = font.render("Node Palette", True, (255, 255, 255))
        screen.blit(title_text, (palette_rect.x + 10, palette_rect.y + 10))

        # Render palette nodes
        for node in self.palette_nodes:
            self._render_node(screen, node, is_palette=True)

        # Render canvas area
        canvas_rect = pygame.Rect(
            palette_rect.right + 10,
            content_rect.y,
            content_rect.width - palette_rect.width - 10,
            content_rect.height
        )
        pygame.draw.rect(screen, (20, 20, 30), canvas_rect)

        # Render canvas nodes
        for node in self.nodes:
            self._render_node(screen, node, is_palette=False)

        # Render connections
        for connection in self.connections:
            self._render_connection(screen, connection)

        # Render dragged connection
        if self.dragged_connection and self.connection_start_pos:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.line(screen, self.connection_color,
                           self.connection_start_pos, mouse_pos, 2)

    def _render_node(self, screen: pygame.Surface, node: AutomationNode, is_palette: bool = False) -> None:
        """Render a single node."""
        x, y = node.position
        w, h = node.size

        # Node background
        color = self.node_colors[node.node_type]
        if node.is_selected and not is_palette:
            color = self.selected_color

        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), width=2, border_radius=5)

        # Node title
        font = pygame.font.SysFont("Arial", 12, bold=True)
        title_text = font.render(node.title, True, (0, 0, 0))
        screen.blit(title_text, (x + 5, y + 5))

        # Render ports
        for port in node.inputs + node.outputs:
            port_color = (0, 255, 0) if port.is_input else (255, 0, 0)
            pygame.draw.circle(screen, port_color, port.position, 5)

    def _render_connection(self, screen: pygame.Surface, connection: NodeConnection) -> None:
        """Render a connection between nodes."""
        from_node = next((n for n in self.nodes if n.id == connection.from_node_id), None)
        to_node = next((n for n in self.nodes if n.id == connection.to_node_id), None)

        if not from_node or not to_node:
            return

        if connection.from_output_index < len(from_node.outputs):
            start_pos = from_node.outputs[connection.from_output_index].position
        else:
            return

        if connection.to_input_index < len(to_node.inputs):
            end_pos = to_node.inputs[connection.to_input_index].position
        else:
            return

        pygame.draw.line(screen, self.connection_color, start_pos, end_pos, 2)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the automation builder."""
        if not self.visible:
            return False

        # Handle panel events first
        if super().handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)

        return False

    def _handle_mouse_down(self, event: pygame.event.Event) -> bool:
        """Handle mouse button down events."""
        mouse_pos = event.pos

        # Check palette nodes for dragging to canvas
        for palette_node in self.palette_nodes:
            if palette_node.contains_point(mouse_pos):
                # Create a copy of the palette node on the canvas
                new_node = AutomationNode(
                    id=f"{palette_node.id}_{len(self.nodes)}",
                    node_type=palette_node.node_type,
                    title=palette_node.title,
                    position=(mouse_pos[0] - 60, mouse_pos[1] - 40),
                    config=palette_node.config.copy()
                )
                self._setup_node_ports(new_node)
                self.nodes.append(new_node)
                new_node.is_dragging = True
                return True

        # Check canvas nodes
        for node in self.nodes:
            port_info = node.get_port_at_point(mouse_pos)
            if port_info:
                port, port_index = port_info
                if not port.is_input:
                    # Start dragging connection from output
                    self.dragged_connection = (node.id, port_index)
                    self.connection_start_pos = port.position
                    return True
            elif node.contains_point(mouse_pos):
                # Start dragging node
                node.is_dragging = True
                node.is_selected = True
                # Clear other selections
                for other_node in self.nodes:
                    if other_node != node:
                        other_node.is_selected = False
                return True

        # Clear selections if clicking empty space
        for node in self.nodes:
            node.is_selected = False

        return False

    def _handle_mouse_up(self, event: pygame.event.Event) -> bool:
        """Handle mouse button up events."""
        mouse_pos = event.pos

        # Finish dragging connection
        if self.dragged_connection:
            from_node_id, from_output_index = self.dragged_connection

            # Check if dropped on an input port
            for node in self.nodes:
                port_info = node.get_port_at_point(mouse_pos)
                if port_info:
                    port, port_index = port_info
                    if port.is_input:
                        # Create connection
                        connection = NodeConnection(
                            from_node_id, from_output_index,
                            node.id, port_index
                        )
                        self.connections.append(connection)
                        break

            self.dragged_connection = None
            self.connection_start_pos = None
            return True

        # Stop dragging nodes
        for node in self.nodes:
            node.is_dragging = False

        return False

    def _handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion events."""
        # Update dragged nodes
        for node in self.nodes:
            if node.is_dragging:
                node.position = (
                    node.position[0] + event.rel[0],
                    node.position[1] + event.rel[1]
                )
                node.update_port_positions()
                return True

        return False

    def build_automation_script(self) -> Optional[AutomationScript]:
        """Build an AutomationScript from the current node graph.

        Returns:
            AutomationScript if valid, None if invalid
        """
        # Find output node
        output_nodes = [n for n in self.nodes if n.node_type == NodeType.OUTPUT]
        if not output_nodes:
            return None

        output_node = output_nodes[0]

        # Trace back from output to build conditions and actions
        trigger_conditions = TriggerConditions()
        effect = "auto_assign"  # Default
        effect_magnitude = 1.0

        # Simple implementation: collect all condition nodes connected to output
        connected_conditions = self._get_connected_conditions(output_node)

        for condition_node in connected_conditions:
            config = condition_node.config
            if config["condition_type"] == "max_difficulty":
                trigger_conditions.max_difficulty = config["value"]
            elif config["condition_type"] == "specialty_match":
                trigger_conditions.specialty_match = config["value"]
            elif config["condition_type"] == "specialist_available":
                trigger_conditions.specialist_available = config["value"]

        # Find action node
        action_nodes = [n for n in self.nodes if n.node_type == NodeType.ACTION]
        if action_nodes:
            action_config = action_nodes[0].config
            effect = action_config["action_type"]
            effect_magnitude = action_config.get("magnitude", 1.0)

        return AutomationScript(
            id=f"custom_script_{int(pygame.time.get_ticks())}",
            name="Custom Automation Script",
            description="Built with visual automation builder",
            required_level=1,
            specialty="General",  # Could be made configurable
            trigger_conditions=trigger_conditions,
            effect=effect,
            effect_magnitude=effect_magnitude
        )

    def _get_connected_conditions(self, output_node: AutomationNode) -> List[AutomationNode]:
        """Get all condition nodes connected to the output node."""
        conditions = []
        visited = set()

        def trace_back(node: AutomationNode) -> None:
            if node.id in visited:
                return
            visited.add(node.id)

            if node.node_type == NodeType.CONDITION:
                conditions.append(node)
                return

            # Find nodes connected to this node's inputs
            for connection in self.connections:
                if connection.to_node_id == node.id:
                    from_node = next((n for n in self.nodes if n.id == connection.from_node_id), None)
                    if from_node:
                        trace_back(from_node)

        trace_back(output_node)
        return conditions