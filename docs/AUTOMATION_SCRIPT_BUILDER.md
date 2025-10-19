# Automation Script Builder

The Automation Script Builder provides a visual drag-and-drop interface for creating custom automation scripts without writing code. Players can build complex automation rules by connecting nodes representing conditions, actions, and logic operators.

## Overview

The automation script builder allows players to create custom automation scripts through an intuitive node-based interface. Instead of editing JSON files directly, players can drag and drop nodes to create automation rules that automatically handle incident assignments, apply stat boosts, and execute complex logic chains.

## Features

- **Visual Node Editor**: Drag-and-drop interface for building automation rules
- **Node Palette**: Pre-built nodes for common conditions, actions, and logic
- **Connection System**: Visual connections between nodes to define rule flow
- **Real-time Validation**: Immediate feedback on rule validity and potential issues
- **Template System**: Pre-built templates for common automation patterns
- **Export to JSON**: Convert visual rules to JSON for use in the automation system

## Node Types

### Condition Nodes

Condition nodes evaluate whether certain criteria are met before executing actions.

#### Difficulty Condition
- **Purpose**: Check incident difficulty level
- **Parameters**:
  - `max_difficulty`: Maximum difficulty level (1-5)
- **Example**: Only trigger for incidents with difficulty ≤ 2

#### Specialty Match Condition
- **Purpose**: Check if specialist specialty matches incident requirements
- **Parameters**:
  - `specialty_match`: Whether specialty must match (boolean)
- **Example**: Only assign to specialists with matching specialty

#### Specialist Available Condition
- **Purpose**: Check if specialist is currently available
- **Parameters**:
  - `specialist_available`: Whether specialist must be available (boolean)
- **Example**: Only assign to specialists who aren't busy

### Action Nodes

Action nodes perform specific automation effects when conditions are met.

#### Auto Assign Action
- **Purpose**: Automatically assign incidents to specialists
- **Parameters**:
  - `action_type`: "auto_assign"
- **Effect**: Assigns the incident to the specialist

#### Speed Boost Action
- **Purpose**: Temporarily increase specialist resolution speed
- **Parameters**:
  - `action_type`: "speed_boost"
  - `magnitude`: Speed multiplier (e.g., 1.5 = 50% faster)
- **Effect**: Increases resolution speed for duration

#### Accuracy Boost Action
- **Purpose**: Temporarily increase specialist accuracy
- **Parameters**:
  - `action_type`: "accuracy_boost"
  - `magnitude`: Accuracy bonus (e.g., 1.2 = 20% more accurate)
- **Effect**: Reduces error chance during resolution

#### XP Boost Action
- **Purpose**: Temporarily increase XP gains
- **Parameters**:
  - `action_type`: "xp_boost"
  - `magnitude`: XP multiplier (e.g., 1.25 = 25% more XP)
- **Effect**: Increases XP earned from incident resolution

### Logic Nodes

Logic nodes combine multiple conditions using boolean logic.

#### AND Logic
- **Purpose**: Require all input conditions to be true
- **Inputs**: Multiple condition results
- **Output**: True only if all inputs are true

#### OR Logic
- **Purpose**: Require any input condition to be true
- **Inputs**: Multiple condition results
- **Output**: True if at least one input is true

### Output Node

The output node executes the automation script when all conditions are met.

#### Execute Script Output
- **Purpose**: Execute the completed automation rule
- **Inputs**: Result from logic/condition chain
- **Effect**: Creates and registers the automation script

## Usage Guide

### Accessing the Builder

1. Open the game UI
2. Navigate to the Automation view (F5)
3. The Automation Script Builder panel will be displayed

### Creating a Basic Script

1. **Start with Conditions**: Drag condition nodes from the palette to the canvas
2. **Add Logic**: Connect conditions to logic nodes (AND/OR) if needed
3. **Add Actions**: Drag action nodes and connect them to the logic output
4. **Connect to Output**: Connect the final action to the Execute Script output node
5. **Configure Parameters**: Click on nodes to edit their parameters
6. **Test the Script**: Use the "Test Script" button to validate the rule
7. **Save the Script**: Click "Build Script" to create the automation script

### Example: Low-Difficulty Auto-Assign

This example creates an automation script that automatically assigns low-difficulty incidents to available specialists with matching specialties.

1. **Add Difficulty Condition**:
   - Drag "Difficulty ≤" node to canvas
   - Set `max_difficulty` to 2

2. **Add Specialty Match Condition**:
   - Drag "Specialty Match" node to canvas
   - Set `specialty_match` to true

3. **Add Available Condition**:
   - Drag "Specialist Available" node to canvas
   - Set `specialist_available` to true

4. **Add AND Logic**:
   - Drag "AND" node to canvas
   - Connect all three conditions to the AND inputs

5. **Add Auto Assign Action**:
   - Drag "Auto Assign" node to canvas
   - Connect AND output to Auto Assign input

6. **Connect to Output**:
   - Connect Auto Assign output to Execute Script input

The resulting script will automatically assign incidents with difficulty ≤ 2 to available specialists with matching specialties.

### Advanced Example: Conditional Boosts

This example creates a script that applies speed boosts only during high-burnout situations.

1. **Add Burnout Condition** (custom node for burnout > 80%)
2. **Add Speed Boost Action** with 1.5x multiplier
3. **Connect directly** (no logic needed for single condition)
4. **Result**: Specialists get speed boost when burnout is critical

## Node Configuration

### Editing Node Parameters

1. **Click on a node** to select it (highlighted border)
2. **Right-click** or use the context menu to edit parameters
3. **Modify values** in the parameter dialog
4. **Click "Apply"** to save changes

### Node Connections

- **Creating Connections**: Drag from output port (right side) to input port (left side)
- **Removing Connections**: Right-click on connection line and select "Delete"
- **Connection Validation**: Invalid connections are shown in red
- **Flow Direction**: Connections only flow from outputs to inputs

## Templates

The builder includes several pre-built templates for common automation patterns:

### Basic Auto-Assign
- Conditions: Difficulty ≤ 2, Specialty Match, Available
- Action: Auto Assign
- Logic: AND

### Emergency Boost
- Conditions: Burnout > 80%
- Action: Speed Boost (1.5x)
- Logic: Direct connection

### High-Value Focus
- Conditions: Incident Reward > 1000, Specialty Match
- Action: Accuracy Boost (1.3x)
- Logic: AND

## Validation and Testing

### Real-time Validation

The builder provides immediate feedback on rule validity:

- **Green connections**: Valid connections
- **Red connections**: Invalid connections (wrong data types)
- **Warning icons**: Potential issues (missing parameters, circular references)
- **Error messages**: Critical issues that prevent script creation

### Testing Scripts

Before deploying automation scripts:

1. **Click "Test Script"** to validate the rule logic
2. **Review test results** showing which conditions would trigger
3. **Check for conflicts** with existing automation scripts
4. **Verify performance impact** on game systems

## Integration with Automation System

### Script Generation

When you click "Build Script", the visual rule is converted to:

1. **AutomationScript object** with proper trigger conditions
2. **JSON configuration** stored in `data/automation_scripts.json`
3. **Registration** with the automation processor
4. **Activation** based on specialist level and feature flags

### Priority and Conflicts

- **Priority System**: Scripts execute in priority order (higher = first)
- **Conflict Resolution**: Multiple scripts can trigger for the same incident
- **Cooldowns**: Scripts have cooldowns to prevent spam execution

## Best Practices

### Rule Design

1. **Start Simple**: Begin with basic conditions and single actions
2. **Test Incrementally**: Add complexity one node at a time
3. **Use Logic Wisely**: AND for strict requirements, OR for flexible triggers
4. **Consider Performance**: Complex rules may impact game performance

### Maintenance

1. **Document Rules**: Add comments to complex automation rules
2. **Version Control**: Track changes to automation configurations
3. **Regular Review**: Audit automation rules for effectiveness
4. **Balance Testing**: Ensure automation doesn't break game balance

## Troubleshooting

### Common Issues

**Script Not Triggering**
- Check condition parameters are correct
- Verify specialist meets level requirements
- Ensure script is enabled and not on cooldown

**Invalid Connections**
- Check data types match between nodes
- Ensure flow direction is correct (output → input)
- Verify all required inputs are connected

**Performance Issues**
- Simplify complex logic chains
- Reduce number of active automation scripts
- Check for circular references in connections

## API Reference

### AutomationBuilderPanel

```python
class AutomationBuilderPanel(Panel):
    """Visual automation script builder."""

    def build_automation_script(self) -> Optional[AutomationScript]:
        """Convert current node graph to AutomationScript."""

    def _create_palette_nodes(self) -> List[AutomationNode]:
        """Create available node types for palette."""

    def _setup_node_ports(self, node: AutomationNode) -> None:
        """Configure input/output ports for node."""
```

### AutomationNode

```python
@dataclass
class AutomationNode:
    """Node in automation builder graph."""

    id: str
    node_type: NodeType
    title: str
    position: Tuple[int, int]
    size: Tuple[int, int] = (120, 80)
    inputs: List[NodePort] = field(default_factory=list)
    outputs: List[NodePort] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within node bounds."""

    def get_port_at_point(self, point: Tuple[int, int]) -> Optional[Tuple[NodePort, int]]:
        """Find port at given point."""
```

## Future Enhancements

- **Custom Node Creation**: Allow players to create custom condition/action nodes
- **Script Sharing**: Import/export automation scripts between games
- **Advanced Logic**: Support for NOT operations and nested logic groups
- **Visual Debugging**: Step-through execution of automation rules
- **Performance Analytics**: Track automation script effectiveness over time