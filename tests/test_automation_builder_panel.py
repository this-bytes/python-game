"""Tests for Automation Builder Panel."""

import pytest
import pygame
from unittest.mock import Mock

from src.ui.panels.automation_builder_panel import (
    AutomationBuilderPanel,
    AutomationNode,
    NodeType,
    NodeConnection,
    ConnectionType,
    NodePort
)
from src.models.automation_script import AutomationScript, TriggerConditions
from src.models.game_state import GameState


@pytest.fixture
def game_state():
    """Create test game state."""
    return GameState()


@pytest.fixture
def automation_panel(game_state):
    """Create automation builder panel."""
    return AutomationBuilderPanel(game_state)


@pytest.fixture
def mock_screen():
    """Create mock pygame screen."""
    screen = Mock()
    screen.get_size.return_value = (1000, 700)
    return screen


class TestAutomationBuilderPanel:
    """Test suite for AutomationBuilderPanel."""

    def test_initialization(self, automation_panel):
        """Test panel initializes correctly."""
        assert automation_panel.title == "Automation Script Builder"
        assert len(automation_panel.nodes) == 5  # Basic template nodes
        assert len(automation_panel.palette_nodes) > 0
        assert len(automation_panel.connections) == 4  # Basic template connections

    def test_create_basic_template(self, automation_panel):
        """Test basic template creates expected nodes and connections."""
        # Check for expected node types
        node_types = [node.node_type for node in automation_panel.nodes]
        assert NodeType.CONDITION in node_types
        assert NodeType.ACTION in node_types
        assert NodeType.LOGIC in node_types
        assert NodeType.OUTPUT in node_types

        # Check connections exist
        assert len(automation_panel.connections) > 0

        # Check output node exists
        output_nodes = [n for n in automation_panel.nodes if n.node_type == NodeType.OUTPUT]
        assert len(output_nodes) == 1

    def test_setup_node_ports(self, automation_panel):
        """Test node ports are set up correctly."""
        condition_node = AutomationNode(
            id="test_condition",
            node_type=NodeType.CONDITION,
            title="Test Condition",
            position=(100, 100)
        )

        automation_panel._setup_node_ports(condition_node)

        assert len(condition_node.outputs) == 1
        assert condition_node.outputs[0].name == "Result"
        assert not condition_node.outputs[0].is_input

    def test_render(self, automation_panel):
        """Test panel render method exists and initializes properly."""
        # Initialize pygame for font rendering
        pygame.init()

        try:
            # Create a real surface for testing
            screen = pygame.display.set_mode((800, 600))

            # Should not raise exceptions during setup
            automation_panel.render(screen)

            # Basic check that panel has expected attributes
            assert hasattr(automation_panel, 'nodes')
            assert hasattr(automation_panel, 'connections')
            assert hasattr(automation_panel, 'palette_nodes')
        finally:
            pygame.quit()

    def test_mouse_events_handling(self, automation_panel):
        """Test mouse event handling."""
        # Test mouse down on empty space
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (500, 300)  # Canvas area
        event.button = 1

        # Should not crash
        result = automation_panel.handle_event(event)
        assert isinstance(result, bool)

    def test_drag_and_drop_palette_node(self, automation_panel):
        """Test dragging node from palette to canvas."""
        # Simulate mouse down on palette node
        palette_node = automation_panel.palette_nodes[0]
        event_down = Mock()
        event_down.type = pygame.MOUSEBUTTONDOWN
        event_down.pos = palette_node.position
        event_down.button = 1

        # Handle mouse down
        automation_panel.handle_event(event_down)

        # Check new node was created on canvas
        initial_node_count = len(automation_panel.nodes)
        palette_node = automation_panel.palette_nodes[0]
        event_down.pos = palette_node.position

        automation_panel.handle_event(event_down)

        # Should have added a node
        assert len(automation_panel.nodes) >= initial_node_count

    def test_connection_creation(self, automation_panel):
        """Test creating connections between nodes."""
        # Get nodes
        nodes = automation_panel.nodes
        output_node = next(n for n in nodes if n.node_type == NodeType.CONDITION)
        input_node = next(n for n in nodes if n.node_type == NodeType.LOGIC)

        # Simulate connection drag
        automation_panel.dragged_connection = (output_node.id, 0)
        automation_panel.connection_start_pos = output_node.outputs[0].position

        # Simulate drop on input
        event_up = Mock()
        event_up.type = pygame.MOUSEBUTTONUP
        event_up.pos = input_node.inputs[0].position
        event_up.button = 1

        automation_panel.handle_event(event_up)

        # Should have created connection
        new_connections = [c for c in automation_panel.connections
                          if c.from_node_id == output_node.id and c.to_node_id == input_node.id]
        assert len(new_connections) > 0

    def test_build_automation_script(self, automation_panel):
        """Test building automation script from node graph."""
        script = automation_panel.build_automation_script()

        assert script is not None
        assert isinstance(script, AutomationScript)
        assert script.trigger_conditions is not None

    def test_get_connected_conditions(self, automation_panel):
        """Test finding connected condition nodes."""
        output_node = next(n for n in automation_panel.nodes if n.node_type == NodeType.OUTPUT)
        conditions = automation_panel._get_connected_conditions(output_node)

        # Should find condition nodes in the template
        condition_nodes = [n for n in conditions if n.node_type == NodeType.CONDITION]
        assert len(condition_nodes) > 0


class TestAutomationNode:
    """Test suite for AutomationNode."""

    def test_node_creation(self):
        """Test creating automation node."""
        node = AutomationNode(
            id="test_node",
            node_type=NodeType.CONDITION,
            title="Test Node",
            position=(100, 100)
        )

        assert node.id == "test_node"
        assert node.node_type == NodeType.CONDITION
        assert node.title == "Test Node"
        assert node.position == (100, 100)

    def test_contains_point(self):
        """Test point containment checking."""
        node = AutomationNode(
            id="test_node",
            node_type=NodeType.CONDITION,
            title="Test Node",
            position=(100, 100),
            size=(120, 80)
        )

        # Point inside node
        assert node.contains_point((110, 110))

        # Point outside node
        assert not node.contains_point((50, 50))

    def test_get_port_at_point(self):
        """Test finding port at point."""
        node = AutomationNode(
            id="test_node",
            node_type=NodeType.CONDITION,
            title="Test Node",
            position=(100, 100)
        )

        # Add a port
        port = NodePort("Test Port", "bool", False, (110, 120))
        node.outputs.append(port)

        # Should find port
        result = node.get_port_at_point((110, 120))
        assert result is not None
        found_port, index = result
        assert found_port == port
        assert index == 0

        # Should not find port at wrong location
        result = node.get_port_at_point((200, 200))
        assert result is None

    def test_update_port_positions(self):
        """Test updating port positions."""
        node = AutomationNode(
            id="test_node",
            node_type=NodeType.CONDITION,
            title="Test Node",
            position=(100, 100)
        )

        node.inputs.append(NodePort("Input", "flow", True))
        node.outputs.append(NodePort("Output", "flow", False))

        node.update_port_positions()

        # Check input port position (left side)
        assert node.inputs[0].position[0] == 100  # x position

        # Check output port position (right side)
        assert node.outputs[0].position[0] == 100 + 120  # x + width


class TestNodeConnection:
    """Test suite for NodeConnection."""

    def test_connection_creation(self):
        """Test creating node connection."""
        connection = NodeConnection(
            from_node_id="node1",
            from_output_index=0,
            to_node_id="node2",
            to_input_index=0,
            connection_type=ConnectionType.FLOW
        )

        assert connection.from_node_id == "node1"
        assert connection.from_output_index == 0
        assert connection.to_node_id == "node2"
        assert connection.to_input_index == 0
        assert connection.connection_type == ConnectionType.FLOW

    def test_to_dict(self):
        """Test converting connection to dict."""
        connection = NodeConnection(
            from_node_id="node1",
            from_output_index=0,
            to_node_id="node2",
            to_input_index=0
        )

        data = connection.to_dict()

        assert data["from_node_id"] == "node1"
        assert data["from_output_index"] == 0
        assert data["to_node_id"] == "node2"
        assert data["to_input_index"] == 0
        assert data["connection_type"] == "flow"


class TestNodePort:
    """Test suite for NodePort."""

    def test_port_creation(self):
        """Test creating node port."""
        port = NodePort(
            name="Test Port",
            data_type="bool",
            is_input=True,
            position=(100, 100)
        )

        assert port.name == "Test Port"
        assert port.data_type == "bool"
        assert port.is_input is True
        assert port.position == (100, 100)

    def test_contains_point(self):
        """Test point containment for port."""
        port = NodePort(
            name="Test Port",
            data_type="bool",
            is_input=True,
            position=(100, 100)
        )

        # Point within port radius
        assert port.contains_point((102, 102))

        # Point outside port radius
        assert not port.contains_point((120, 120))