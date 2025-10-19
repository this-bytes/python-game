# 🎮 Ultimate Game Control Panel

The most comprehensive game management interface ever built for a game backend. This control panel provides complete control over every aspect of the game with professional-grade editing tools, real-time synchronization, and advanced batch operations.

## 🚀 Quick Start

1. **Start the Backend**
   ```bash
   python backend/run_backend.py
   ```

2. **Access the Control Panel**
   - Open browser to: `http://localhost:5001/`
   - Or explicitly: `http://localhost:5001/control-panel`

3. **Legacy Admin Panel** (old version)
   - Still available at: `http://localhost:5001/admin`

## ✨ Features

### 📊 Dashboard
- Real-time game metrics (money, incidents, specialists, SLA compliance)
- Quick action buttons for common operations
- Live event feed showing recent game activities
- Connection status indicator

### 🗂️ Entity Editors

Advanced editors for every game entity type:
- **Incidents** - Create and edit incident types
- **Specialists** - Manage specialist templates
- **Equipment** - Edit equipment items with rarity tiers
- **Clients** - Manage client data
- **Automation Scripts** - Edit automation behaviors
- **Achievements** - Create achievement definitions

Each editor provides:
- ✏️ **Visual card view** with search and filter
- ➕ **Create new** entities from templates
- 📝 **Edit existing** entities with modal editor
- 📋 **Duplicate** entities with smart ID/name updates
- 🗑️ **Delete** with confirmation
- 📥 **Import** from JSON files
- 📤 **Export** to JSON files
- ⚡ **Batch operations** for mass editing

### 🎨 Entity Editor Modal

Three editing modes:
1. **Visual Editor**
   - Form-based editing with appropriate input types
   - Automatic field type detection (text, number, checkbox, textarea)
   - Smart handling of nested objects and arrays
   
2. **JSON Editor**
   - Direct JSON editing with syntax highlighting
   - Real-time validation
   - Format/beautify button
   - Error highlighting
   
3. **Preview Mode**
   - Live preview of entity card appearance
   - Full JSON data view
   - Shows how entity will appear in-game

### ⚡ Batch Operations

Perform bulk operations on multiple entities:
- **Select Multiple** - Checkbox-based multi-select interface
- **Select All / Clear** - Quick selection controls
- **Update Field** - Change a field value across many entities
- **Multiply Stat** - Scale numeric values (e.g., multiply all costs by 1.5x)
- **Add to Stat** - Add a value to numeric fields
- **Change Rarity** - Bulk update rarity tiers
- **Adjust Cost** - Multiply, add, or set costs
- **Delete Selected** - Safe deletion with automatic backups

### 👑 God Mode Controls

Powerful testing and debugging commands:
- **🌊 Spawn Wave** - Spawn 50 incidents instantly
- **✅ Complete All** - Mark all incidents as completed
- **⬆️ Level Up All** - Level up all specialists
- **⚡ Max All Stats** - Set all specialist stats to maximum
- **🧹 Clear All Incidents** - Remove all active incidents
- **💰 Set Money** - Set money to any amount instantly

### ⏱️ Time Controls

- **Game Speed Multiplier** - Adjust from 0.1x to 10x speed
- **Fast Forward** - Skip ahead by any number of seconds
- **Pause/Resume** - Control game flow

### 🎯 Live Game State

- View complete game state in JSON format
- Refresh on demand
- Save state snapshots
- Load state from snapshots

### 🛠️ Advanced Tools

- **🎨 Level Editor** - Create incident waves and scenarios (coming soon)
- **📅 Event Timeline** - View chronological event history
- **🔗 Entity Graph** - Visualize relationships between entities (coming soon)

## 🔌 API Integration

The control panel integrates seamlessly with the backend API:

### Entity Management API

```bash
# List all entities of a type
GET /api/entities/{entity_type}

# Get specific entity
GET /api/entities/{entity_type}/{entity_id}

# Create new entity
POST /api/entities/{entity_type}
Body: { "entity": {...} }

# Update entity
PUT /api/entities/{entity_type}/{entity_id}
Body: { "entity": {...} }

# Delete entity
DELETE /api/entities/{entity_type}/{entity_id}

# Duplicate entity
POST /api/entities/{entity_type}/duplicate/{entity_id}
Body: { "new_id": "..." } (optional)

# Batch operations
POST /api/entities/{entity_type}/batch
Body: {
  "operation": "update|delete",
  "entity_ids": ["id1", "id2"],
  "data": {...}
}

# Get entity template
GET /api/entities/templates/{entity_type}
```

### God Mode API

```bash
# Spawn incident wave
POST /api/godmode/spawn-wave
Body: { "count": 50 }

# Complete all incidents
POST /api/godmode/complete-all-incidents

# Level up all specialists
POST /api/godmode/level-up-all
Body: { "levels": 1 }

# Set money
POST /api/godmode/set-money
Body: { "amount": 1000000 }

# Clear all incidents
POST /api/godmode/clear-incidents

# Max all stats
POST /api/godmode/max-all-stats
```

## 📋 Entity Types

Supported entity types and their JSON files:

| Entity Type | JSON File | Description |
|-------------|-----------|-------------|
| `incidents` | `incidents.json` | Incident type definitions |
| `specialist_templates` | `specialist_templates.json` | Specialist archetypes |
| `equipment` | `equipment.json` | Equipment items |
| `clients` | `clients.json` | Client definitions |
| `automation_scripts` | `automation_scripts.json` | Automation scripts |
| `achievements` | `achievements.json` | Achievement definitions |
| `prestige_upgrades` | `prestige_upgrades.json` | Prestige upgrade tree |
| `abilities` | `abilities.json` | Specialist abilities |

## 🎨 UI Features

### Sidebar Navigation
- Collapsible sections
- Active state highlighting
- Icon indicators
- Organized by category (Overview, Entity Editors, Tools, Godmode)

### Toast Notifications
- Success messages (green)
- Error messages (red)
- Warning messages (orange)
- Auto-dismiss after 5 seconds
- Closeable by user

### Modal System
- Full-screen overlay
- Tab-based navigation
- Responsive sizing
- Clean close/cancel actions

### Card Layout
- Responsive grid (auto-fill)
- Rarity badges (common/rare/epic/legendary)
- Hover effects
- Action buttons (Edit/Duplicate/Delete)

## 🔧 Technical Architecture

### Frontend (JavaScript)

```
control-panel.js           - Main controller, routing, data management
entity-editor-modal.js     - Modal editor with visual/JSON/preview modes
batch-operations.js        - Bulk operations interface
control-panel.css          - Complete styling system
control-panel.html         - Main page structure
```

### Backend (Python Flask)

```
routes/entity_management.py  - Entity CRUD API routes
routes/godmode.py            - God mode command routes
routes/config_routes.py      - Configuration hot-reload
routes/time.py               - Time control routes
routes/state.py              - Game state management
```

### Design Patterns

- **Class-based architecture** - Each major system is a JavaScript class
- **Event-driven communication** - WebSocket/polling for real-time updates
- **API-first design** - All operations go through REST API
- **Backup on modify** - Automatic `.backup` files created
- **Toast feedback** - User always knows operation status

## 🎯 Use Cases

### Game Balancing
1. Open equipment editor
2. Select multiple items by rarity
3. Use batch operations to adjust stats
4. Preview changes in entity cards
5. Export modified config for version control

### Testing Incident System
1. Use God Mode to spawn incident wave
2. Monitor in dashboard
3. Adjust time speed to accelerate
4. Use complete-all to test completion logic
5. View event timeline to see what happened

### Creating New Content
1. Open desired entity editor (e.g., equipment)
2. Click "Create New"
3. Fill in visual form OR edit JSON directly
4. Preview how it looks
5. Save to add to game

### Mass Data Updates
1. Open entity editor
2. Click "Batch Edit"
3. Select entities to modify
4. Choose operation (e.g., "Change Rarity")
5. Execute to update all at once

## 🚨 Safety Features

- **Automatic Backups** - Every file modification creates a `.backup` file
- **Confirmation Dialogs** - Delete operations require confirmation
- **Validation** - JSON syntax validation before save
- **Error Handling** - Clear error messages on failures
- **Undo via Backup** - Manually restore from `.backup` files if needed

## 🎓 Best Practices

1. **Always test changes** in God Mode before production
2. **Use batch operations** for consistency across similar entities
3. **Export before major changes** as additional backup
4. **Check event timeline** to debug unexpected behavior
5. **Monitor dashboard metrics** to see immediate impact
6. **Use visual editor** for simple changes, JSON for complex structures

## 🔮 Future Enhancements

Planned features:
- **Level Editor** - Drag-and-drop incident wave designer
- **Entity Graph Visualizer** - See relationships between entities
- **Undo/Redo System** - Multi-level undo for all operations
- **Advanced Filtering** - Search entities by any field
- **Data Visualization** - Charts for game balance analysis
- **Template Library** - Pre-made entity templates
- **Diff Viewer** - See what changed between versions
- **Real-time Collaboration** - Multiple admins editing simultaneously

## 📝 Tips & Tricks

### Quick Actions
- Press `Ctrl+F` in JSON editor to search
- Click entity name in dashboard to jump to that editor
- Use export/import to share entity configs between games

### Keyboard Shortcuts (planned)
- `Ctrl+S` - Save entity
- `Ctrl+D` - Duplicate entity
- `Ctrl+Z` - Undo last change
- `Esc` - Close modal

### Performance
- The control panel loads all entity data on startup
- Use refresh button if you edit JSON files manually
- Batch operations are more efficient than editing individually

## 🐛 Troubleshooting

**Q: Changes aren't appearing in game?**
- Click "Reload Config" in control panel
- Or restart the game

**Q: Can't see entity editor changes?**
- Check browser console for errors
- Verify backend is running (`http://localhost:5001/health`)
- Try refreshing the page

**Q: Batch operation failed?**
- Check that all selected entities have the target field
- Verify operation type matches data type (e.g., multiply on numbers)
- Look at backup files if data was corrupted

**Q: JSON editor shows validation error?**
- Check for missing commas, quotes, or brackets
- Use "Format JSON" button to fix indentation
- Copy JSON to external validator if needed

## 📚 Related Documentation

- [Backend README](./README.md) - General backend documentation
- [API Documentation](./README.md#-api-endpoints) - Complete API reference
- [Game Architecture](../ARCHITECTURE.md) - Overall game design
- [Plugin System](../docs/PLUGIN_SYSTEM.md) - Game systems architecture

## 🤝 Contributing

When adding new features to the control panel:

1. **Follow existing patterns** - Use same class structure
2. **Add to sidebar** - Update `control-panel.html` navigation
3. **Create view renderer** - Add method in `ControlPanel` class
4. **Add API routes** - Create backend routes if needed
5. **Test thoroughly** - Verify all CRUD operations work
6. **Update this README** - Document new features

## 📄 License

Same as main project.

---

**Built with:** Flask, JavaScript ES6+, CSS3, REST API  
**Status:** ✅ Production Ready  
**Maintainer:** Development Team
