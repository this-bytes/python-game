---
goal: Cybersecurity Firm Idle/Tycoon/RPG Game - Full Implementation
version: 1.0
date_created: 2025-10-16
last_updated: 2025-10-16
owner: Development Team
status: Planned
tags: [feature, game, architecture, pygame, idle-game, tycoon, rpg, json-driven]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This implementation plan outlines the development of a cybersecurity firm management game that blends Idle, Tycoon, and RPG mechanics. The game centers on managing a startup cybersecurity firm where players triage security incidents, assign specialized agents, and grow their business through strategic resource allocation. The architecture follows a "vibe coding" philosophy with Pygame as a minimal visual dashboard while all game data lives in external JSON files, enabling rapid iteration and live balancing through CRUD tools.

## 1. Requirements & Constraints

### Core Requirements

- **REQ-001**: Implement idle game mechanics with continuous incident generation
- **REQ-002**: Implement tycoon mechanics with profit optimization and business growth
- **REQ-003**: Implement RPG mechanics with specialist leveling, XP, and skill progression
- **REQ-004**: Generate security incidents at configurable rates with varying difficulty levels
- **REQ-005**: Implement specialist roster management with unique specialties (Network, Malware, Forensics, etc.)
- **REQ-006**: Implement incident-to-specialist assignment system with manual triage
- **REQ-007**: Track SLA deadlines for each incident with visual feedback
- **REQ-008**: Calculate profits based on incident resolution success and SLA compliance
- **REQ-009**: Implement XP and leveling system for specialists
- **REQ-010**: Implement automation scripts that unlock at specific specialist levels
- **REQ-011**: Support multi-client system with different incident rates and SLA requirements
- **REQ-012**: Implement game state persistence (save/load functionality)

### Technical Architecture Requirements

- **REQ-013**: Use Pygame as minimal visual dashboard and renderer only
- **REQ-014**: Store ALL game parameters in external JSON files (no hardcoded values)
- **REQ-015**: Implement clear separation between game logic and rendering
- **REQ-016**: Support hot-reloading of JSON configuration files
- **REQ-017**: Implement backend server with CRUD API for live game balancing
- **REQ-018**: Enable spawning of specific incidents via backend tools
- **REQ-019**: Enable specialist stat/level modification via backend tools
- **REQ-020**: Support real-time parameter tweaking without game restart

### Data-Driven Design Requirements

- **REQ-021**: Specialists: name, specialty, level, XP, stats, automation_scripts stored in JSON
- **REQ-022**: Incidents: type, difficulty, specialty_required, sla_seconds, reward stored in JSON
- **REQ-023**: Clients: name, incident_rate, sla_multiplier, reputation stored in JSON
- **REQ-024**: Automation scripts: name, trigger_conditions, specialist_level_required, effect stored in JSON
- **REQ-025**: Game economy parameters: base_rewards, xp_curves, leveling_thresholds stored in JSON

### UI/UX Requirements

- **REQ-026**: Display real-time incident queue with priority indicators
- **REQ-027**: Display specialist roster with current status and stats
- **REQ-028**: Display SLA countdown timers for active incidents
- **REQ-029**: Display profit/revenue metrics and company performance
- **REQ-030**: Implement drag-and-drop or click-based assignment interface
- **REQ-031**: Display specialist progression and automation unlocks
- **REQ-032**: Show active automation scripts and their effects

### Development Workflow Requirements

- **REQ-033**: Create `.github/copilot-instructions.md` with project context for AI coding agents
- **REQ-034**: Enable iterative development with external parameter tuning
- **REQ-035**: Support rapid prototyping and balance testing
- **REQ-036**: Maintain clean separation for independent module development

### Constraints

- **CON-001**: Must use Pygame framework (no other game engines)
- **CON-002**: Must maintain JSON-first architecture (no migration to database for MVP)
- **CON-003**: Backend server must be lightweight (Flask/FastAPI suggested)
- **CON-004**: Must support Python 3.9+ for compatibility
- **CON-005**: Must maintain < 100ms response time for UI interactions
- **CON-006**: Must support graceful degradation if backend server is offline
- **CON-007**: JSON files must be human-readable and easily editable

### Guidelines

- **GUD-001**: Follow vibe coding philosophy - prefer iteration speed over perfect architecture
- **GUD-002**: Keep Pygame code minimal and focused on rendering only
- **GUD-003**: Make game balance tweakable without code changes
- **GUD-004**: Structure code for easy AI agent comprehension and modification
- **GUD-005**: Use descriptive variable names matching game domain language
- **GUD-006**: Document all JSON schema structures clearly
- **GUD-007**: Implement comprehensive logging for debugging game state

### Architectural Patterns

- **PAT-001**: Model-View-Controller separation (Game Logic / Rendering / Input)
- **PAT-002**: Data-driven design with external configuration
- **PAT-003**: Event-driven architecture for incident generation and resolution
- **PAT-004**: Observer pattern for UI updates based on game state changes
- **PAT-005**: Strategy pattern for different specialist abilities and automation scripts
- **PAT-006**: Factory pattern for incident and specialist creation from JSON

### Security Requirements

- **SEC-001**: Backend API must use authentication tokens for CRUD operations
- **SEC-002**: Validate all JSON input to prevent injection attacks
- **SEC-003**: Implement rate limiting on backend API endpoints
- **SEC-004**: Sanitize user input for save game names and custom data

## 2. Implementation Steps

### Implementation Phase 1: Project Scaffolding & Architecture Setup

**GOAL-001**: Establish project structure, dependencies, and foundational architecture with JSON-driven configuration system

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create project directory structure: `/src/`, `/data/`, `/plan/`, `/tests/`, `/backend/`, `/docs/` | ✅ | 2025-10-16 |
| TASK-002 | Initialize Python virtual environment and create `requirements.txt` with Pygame, Flask/FastAPI dependencies | ✅ | 2025-10-16 |
| TASK-003 | Create `.github/copilot-instructions.md` with comprehensive project context, architecture philosophy, and coding conventions | ✅ | 2025-10-16 |
| TASK-004 | Define JSON schemas for all game entities: specialists, incidents, clients, automation_scripts, game_state | ✅ | 2025-10-16 |
| TASK-005 | Create sample JSON data files in `/data/`: `specialists.json`, `incidents.json`, `clients.json`, `automation_scripts.json`, `game_config.json` | ✅ | 2025-10-16 |
| TASK-006 | Implement JSON loader utility module (`/src/utils/json_loader.py`) with validation and hot-reload capability | ✅ | 2025-10-16 |
| TASK-007 | Create main project README.md with game concept, architecture overview, and setup instructions | ✅ | 2025-10-16 |
| TASK-008 | Setup logging configuration with different levels for game events, debugging, and performance metrics | ✅ | 2025-10-16 |

### Implementation Phase 2: Core Game Logic Layer

**GOAL-002**: Implement all core game mechanics as pure Python logic independent of rendering

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-009 | Implement `Specialist` class with attributes: id, name, specialty, level, xp, stats, status, assigned_incident | | |
| TASK-010 | Implement `Incident` class with attributes: id, type, difficulty, specialty, sla_deadline, reward, status, assigned_specialist | | |
| TASK-011 | Implement `Client` class with attributes: id, name, incident_rate, sla_multiplier, reputation, contract_value | | |
| TASK-012 | Implement `AutomationScript` class with trigger evaluation and effect application logic | | |
| TASK-013 | Implement `GameState` class managing all game entities, current time, total profit, and game progression | | |
| TASK-014 | Implement incident generation system with configurable spawn rates based on client contracts | | |
| TASK-015 | Implement specialist-incident assignment logic with specialty matching and difficulty calculations | | |
| TASK-016 | Implement incident resolution system with time tracking, SLA validation, and reward calculation | | |
| TASK-017 | Implement XP and leveling system with configurable XP curves from JSON data | | |
| TASK-018 | Implement automation script trigger evaluation and automatic incident assignment logic | | |
| TASK-019 | Create game loop controller managing time progression, incident spawning, and state updates | | |
| TASK-020 | Implement save/load system for game state persistence to JSON files | | |

### Implementation Phase 3: Pygame Visual Dashboard

**GOAL-003**: Create minimal Pygame rendering layer that visualizes game state without containing game logic

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-021 | Initialize Pygame window with configurable resolution and establish rendering pipeline | | |
| TASK-022 | Implement incident queue display panel showing active incidents, difficulty, SLA timers | | |
| TASK-023 | Implement specialist roster display panel showing name, specialty, level, status, current assignment | | |
| TASK-024 | Implement company metrics dashboard displaying total profit, incidents resolved, SLA success rate | | |
| TASK-025 | Implement drag-and-drop UI for assigning specialists to incidents | | |
| TASK-026 | Implement click-based interaction system as alternative to drag-and-drop | | |
| TASK-027 | Create visual indicators for SLA urgency (green/yellow/red countdown timers) | | |
| TASK-028 | Implement specialist detail view showing stats, XP progress, unlocked automation scripts | | |
| TASK-029 | Create notification system for level-ups, automation unlocks, and SLA failures | | |
| TASK-030 | Implement pause/play/speed controls for game time progression | | |
| TASK-031 | Create settings menu for adjusting visual preferences and loading configuration | | |
| TASK-032 | Implement FPS counter and performance monitoring overlay for development | | |

### Implementation Phase 4: Backend CRUD Server

**GOAL-004**: Develop lightweight backend server with REST API for live game parameter manipulation and debugging

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-033 | Setup Flask/FastAPI project structure in `/backend/` directory | | |
| TASK-034 | Implement API endpoints for reading all JSON data files (GET `/specialists`, `/incidents`, `/clients`, `/automation_scripts`) | | |
| TASK-035 | Implement API endpoints for updating specialist stats and level (PUT `/specialists/{id}`) | | |
| TASK-036 | Implement API endpoint for spawning custom incidents (POST `/incidents/spawn`) | | |
| TASK-037 | Implement API endpoint for modifying client incident rates (PUT `/clients/{id}`) | | |
| TASK-038 | Implement API endpoint for hot-reloading game configuration (POST `/config/reload`) | | |
| TASK-039 | Implement authentication middleware with token-based access control | | |
| TASK-040 | Create WebSocket connection for real-time game state monitoring | | |
| TASK-041 | Implement logging of all API operations for audit trail | | |
| TASK-042 | Create simple web-based admin dashboard for CRUD operations (HTML/JS frontend) | | |
| TASK-043 | Implement game state snapshot endpoint for debugging (GET `/game/state`) | | |
| TASK-044 | Add CORS support for cross-origin requests from admin tools | | |

### Implementation Phase 5: Integration & Game Loop

**GOAL-005**: Integrate all components and establish complete game loop with backend communication

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-045 | Create main game entry point (`main.py`) orchestrating all subsystems | | |
| TASK-046 | Integrate Pygame rendering with game state updates at target framerate (60 FPS) | | |
| TASK-047 | Implement background thread for incident generation independent of rendering | | |
| TASK-048 | Setup communication layer between game client and backend server | | |
| TASK-049 | Implement periodic JSON file watching for hot-reload capability | | |
| TASK-050 | Connect automation script execution to game loop with proper timing | | |
| TASK-051 | Implement game state synchronization with backend server | | |
| TASK-052 | Add graceful error handling for missing JSON files or malformed data | | |
| TASK-053 | Implement game pause when backend server is unavailable | | |
| TASK-054 | Create debug mode with enhanced logging and state inspection | | |

### Implementation Phase 6: Testing & Balance Tools

**GOAL-006**: Implement comprehensive testing and create tools for rapid game balance iteration

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-055 | Write unit tests for all game logic classes (Specialist, Incident, Client, etc.) | | |
| TASK-056 | Write integration tests for incident generation and resolution flow | | |
| TASK-057 | Write tests for XP and leveling calculations | | |
| TASK-058 | Write tests for automation script trigger evaluation | | |
| TASK-059 | Write tests for save/load game state persistence | | |
| TASK-060 | Write API tests for all backend CRUD endpoints | | |
| TASK-061 | Create balance testing script that simulates game progression over time | | |
| TASK-062 | Create tool for generating test scenarios with specific incident/specialist configurations | | |
| TASK-063 | Implement performance profiling for identifying bottlenecks | | |
| TASK-064 | Create documentation for using backend tools for game balancing | | |

### Implementation Phase 7: Documentation & Developer Experience

**GOAL-007**: Create comprehensive documentation for development, deployment, and gameplay design

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-065 | Document all JSON schema structures with examples and validation rules | | |
| TASK-066 | Create architecture documentation explaining separation of concerns and data flow | | |
| TASK-067 | Write developer guide for adding new specialist types and abilities | | |
| TASK-068 | Write developer guide for creating new incident types and difficulty curves | | |
| TASK-069 | Write developer guide for implementing new automation scripts | | |
| TASK-070 | Create API reference documentation for backend endpoints | | |
| TASK-071 | Document game balancing workflow using backend tools | | |
| TASK-072 | Create deployment guide for running game and backend server | | |
| TASK-073 | Write contribution guidelines for external developers | | |
| TASK-074 | Create gameplay design document outlining progression curves and economy | | |

### Implementation Phase 8: Polish & Extended Features

**GOAL-008**: Add polish, quality-of-life features, and extended gameplay mechanics

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-075 | Implement multiple save slots for different game sessions | | |
| TASK-076 | Add sound effects for key events (incident arrival, resolution, level-up) | | |
| TASK-077 | Implement specialist hiring system with cost and randomization | | |
| TASK-078 | Create specialist upgrade/training system beyond base leveling | | |
| TASK-079 | Implement client relationship system with reputation effects | | |
| TASK-080 | Add achievement/milestone system for long-term goals | | |
| TASK-081 | Implement difficulty scaling and prestige/reset mechanics | | |
| TASK-082 | Create tutorial sequence for new players | | |
| TASK-083 | Implement statistics tracking and visualization | | |
| TASK-084 | Add export functionality for game analytics data | | |

## 3. Alternatives

- **ALT-001**: **Unity/Godot instead of Pygame** - Rejected because requirement explicitly requests Pygame for lightweight, Python-native development matching vibe coding philosophy
- **ALT-002**: **SQLite/Database instead of JSON files** - Rejected for MVP to maintain human-readable, easily editable configuration files; can be future enhancement for production scale
- **ALT-003**: **Electron-based UI instead of Pygame** - Rejected to keep tech stack simple and Python-native; web UI could be alternative frontend consuming same backend
- **ALT-004**: **Real-time multiplayer** - Deferred as out of scope for MVP; single-player idle/tycoon focus first
- **ALT-005**: **GraphQL instead of REST API** - Rejected as overkill for simple CRUD operations; REST API sufficient for backend tools
- **ALT-006**: **Docker containerization** - Deferred as nice-to-have; local development prioritized for iteration speed
- **ALT-007**: **Procedural specialist generation** - Considered but deferred; handcrafted specialists with progression provides better balance control initially
- **ALT-008**: **Real-time 3D visualization** - Rejected; 2D dashboard maintains minimalist philosophy and reduces complexity

## 4. Dependencies

### Runtime Dependencies

- **DEP-001**: Python 3.9+ - Core language runtime
- **DEP-002**: Pygame 2.5+ - Visual rendering and UI framework
- **DEP-003**: Flask 3.0+ or FastAPI 0.104+ - Backend REST API server
- **DEP-004**: Pydantic 2.0+ - JSON schema validation and data models
- **DEP-005**: jsonschema - JSON file validation against schemas
- **DEP-006**: python-dotenv - Environment variable management

### Development Dependencies

- **DEP-007**: pytest - Unit and integration testing framework
- **DEP-008**: pytest-cov - Code coverage reporting
- **DEP-009**: black - Code formatting
- **DEP-010**: pylint or ruff - Code linting
- **DEP-011**: mypy - Static type checking
- **DEP-012**: requests - Testing backend API endpoints

### Optional Dependencies

- **DEP-013**: watchdog - File system monitoring for hot-reload
- **DEP-014**: websockets - Real-time server-client communication
- **DEP-015**: pygame-gui - Enhanced UI widgets (if needed beyond basic Pygame)

### External Tool Dependencies

- **DEP-016**: Git - Version control
- **DEP-017**: VS Code with Copilot - Development environment (per project philosophy)
- **DEP-018**: Postman or curl - API testing tools

## 5. Files

### Core Game Files

- **FILE-001**: `/src/main.py` - Game entry point, initializes all subsystems and runs main loop
- **FILE-002**: `/src/models/specialist.py` - Specialist class definition and behavior
- **FILE-003**: `/src/models/incident.py` - Incident class definition and lifecycle management
- **FILE-004**: `/src/models/client.py` - Client class definition and contract management
- **FILE-005**: `/src/models/automation_script.py` - Automation script logic and trigger evaluation
- **FILE-006**: `/src/models/game_state.py` - Central game state management class
- **FILE-007**: `/src/core/game_loop.py` - Main game loop controller and time management
- **FILE-008**: `/src/core/incident_generator.py` - Incident spawning system
- **FILE-009**: `/src/core/assignment_system.py` - Specialist-incident assignment logic
- **FILE-010**: `/src/core/resolution_system.py` - Incident resolution and reward calculation
- **FILE-011**: `/src/core/progression_system.py` - XP, leveling, and automation unlocking
- **FILE-012**: `/src/core/save_manager.py` - Save/load game state persistence

### Rendering Files

- **FILE-013**: `/src/ui/renderer.py` - Main Pygame rendering coordinator
- **FILE-014**: `/src/ui/panels/incident_queue_panel.py` - Incident queue visualization
- **FILE-015**: `/src/ui/panels/specialist_roster_panel.py` - Specialist roster visualization
- **FILE-016**: `/src/ui/panels/metrics_panel.py` - Company performance dashboard
- **FILE-017**: `/src/ui/panels/specialist_detail_panel.py` - Detailed specialist view
- **FILE-018**: `/src/ui/input_handler.py` - Mouse/keyboard input processing
- **FILE-019**: `/src/ui/drag_drop.py` - Drag-and-drop interaction system
- **FILE-020**: `/src/ui/notifications.py` - Notification and alert system

### Utility Files

- **FILE-021**: `/src/utils/json_loader.py` - JSON loading and hot-reload utilities
- **FILE-022**: `/src/utils/logger.py` - Logging configuration and utilities
- **FILE-023**: `/src/utils/validators.py` - JSON schema validators
- **FILE-024**: `/src/utils/time_manager.py` - Game time tracking and manipulation

### Backend Files

- **FILE-025**: `/backend/app.py` - Flask/FastAPI application entry point
- **FILE-026**: `/backend/routes/specialists.py` - Specialist CRUD endpoints
- **FILE-027**: `/backend/routes/incidents.py` - Incident management endpoints
- **FILE-028**: `/backend/routes/clients.py` - Client management endpoints
- **FILE-029**: `/backend/routes/config.py` - Configuration and hot-reload endpoints
- **FILE-030**: `/backend/routes/game_state.py` - Game state inspection endpoints
- **FILE-031**: `/backend/middleware/auth.py` - Authentication middleware
- **FILE-032**: `/backend/static/admin.html` - Web-based admin dashboard

### Data Files

- **FILE-033**: `/data/specialists.json` - Specialist roster configuration
- **FILE-034**: `/data/incidents.json` - Incident type definitions
- **FILE-035**: `/data/clients.json` - Client contract definitions
- **FILE-036**: `/data/automation_scripts.json` - Automation script configurations
- **FILE-037**: `/data/game_config.json` - Core game parameters and economy settings
- **FILE-038**: `/data/schemas/specialist_schema.json` - JSON schema for specialists
- **FILE-039**: `/data/schemas/incident_schema.json` - JSON schema for incidents
- **FILE-040**: `/data/schemas/client_schema.json` - JSON schema for clients
- **FILE-041**: `/data/schemas/automation_script_schema.json` - JSON schema for automation scripts
- **FILE-042**: `/data/saves/savegame_*.json` - Save game files (generated at runtime)

### Configuration Files

- **FILE-043**: `/requirements.txt` - Python package dependencies
- **FILE-044**: `/.env` - Environment variables (API keys, server ports, etc.)
- **FILE-045**: `/pytest.ini` - Pytest configuration
- **FILE-046**: `/pyproject.toml` - Python project metadata and tool configuration
- **FILE-047**: `/.gitignore` - Git ignore patterns
- **FILE-048**: `/.github/copilot-instructions.md` - AI agent project instructions

### Documentation Files

- **FILE-049**: `/README.md` - Project overview and quick start guide
- **FILE-050**: `/docs/architecture.md` - System architecture documentation
- **FILE-051**: `/docs/json_schemas.md` - JSON schema documentation
- **FILE-052**: `/docs/api_reference.md` - Backend API reference
- **FILE-053**: `/docs/developer_guide.md` - Developer contribution guide
- **FILE-054**: `/docs/balancing_guide.md` - Game balancing workflow documentation
- **FILE-055**: `/docs/gameplay_design.md` - Game design document

### Test Files

- **FILE-056**: `/tests/test_specialist.py` - Specialist class tests
- **FILE-057**: `/tests/test_incident.py` - Incident class tests
- **FILE-058**: `/tests/test_assignment.py` - Assignment system tests
- **FILE-059**: `/tests/test_progression.py` - XP and leveling tests
- **FILE-060**: `/tests/test_automation.py` - Automation script tests
- **FILE-061**: `/tests/test_save_load.py` - Save/load functionality tests
- **FILE-062**: `/tests/test_api.py` - Backend API endpoint tests
- **FILE-063**: `/tests/conftest.py` - Pytest fixtures and configuration

## 6. Testing

### Unit Tests

- **TEST-001**: Test Specialist class initialization, stat calculations, leveling, and XP gain
- **TEST-002**: Test Incident class initialization, SLA tracking, difficulty calculations
- **TEST-003**: Test Client class initialization, incident rate calculations, reputation changes
- **TEST-004**: Test AutomationScript trigger evaluation with various game state conditions
- **TEST-005**: Test GameState add/remove/update operations for all entity types
- **TEST-006**: Test incident generation rates match configured client parameters
- **TEST-007**: Test assignment validation (specialty matching, specialist availability)
- **TEST-008**: Test resolution calculations (time taken, SLA compliance, rewards)
- **TEST-009**: Test XP curve calculations and level thresholds from JSON data
- **TEST-010**: Test JSON loading with valid and invalid data structures

### Integration Tests

- **TEST-011**: Test complete incident lifecycle: generation → assignment → resolution → reward
- **TEST-012**: Test multiple concurrent incidents assigned to different specialists
- **TEST-013**: Test specialist leveling unlocking automation scripts at correct thresholds
- **TEST-014**: Test automation scripts automatically assigning appropriate incidents
- **TEST-015**: Test SLA failure path with penalties and reputation loss
- **TEST-016**: Test save game state and reload with exact state preservation
- **TEST-017**: Test hot-reload of JSON configuration while game is running
- **TEST-018**: Test backend API modifying specialist stats reflected in game immediately
- **TEST-019**: Test backend API spawning custom incidents appearing in game queue
- **TEST-020**: Test game continues functioning when backend server is offline

### System Tests

- **TEST-021**: Test complete game session: start → hire specialists → resolve incidents → level up → save → exit
- **TEST-022**: Test game balance: simulate 1 hour of gameplay, verify progression feels appropriate
- **TEST-023**: Test performance: verify 60 FPS maintained with 50+ active incidents
- **TEST-024**: Test UI interactions: drag-and-drop, clicking, menu navigation
- **TEST-025**: Test backend admin dashboard full CRUD workflow
- **TEST-026**: Stress test incident generation with extremely high rates
- **TEST-027**: Test edge cases: zero specialists, zero incidents, all specialists busy
- **TEST-028**: Test data validation: attempt to load malformed JSON files

### Balance Testing

- **TEST-029**: Verify early game (0-30min) provides steady progression without grinding
- **TEST-030**: Verify mid game (30min-2hr) introduces automation unlocks at satisfying pace
- **TEST-031**: Verify late game (2hr+) automation handles most incidents with strategic oversight
- **TEST-032**: Verify SLA timers are challenging but achievable with proper planning
- **TEST-033**: Verify profit curves support hiring additional specialists at appropriate times
- **TEST-034**: Verify specialist specialization matters for optimal incident matching

## 7. Risks & Assumptions

### Technical Risks

- **RISK-001**: Pygame performance degradation with large number of UI elements - Mitigation: Implement efficient rendering with dirty rect updates, limit active UI panels
- **RISK-002**: JSON file corruption during hot-reload - Mitigation: Implement file locking, backup system, and validation before applying changes
- **RISK-003**: Backend server disconnection causing game state desync - Mitigation: Implement reconnection logic and conflict resolution strategy
- **RISK-004**: Python GIL limiting concurrent incident processing - Mitigation: Profile early, consider multiprocessing if needed, but likely not bottleneck for game scale
- **RISK-005**: Save file growth over long game sessions - Mitigation: Implement cleanup of resolved incidents, compress save files

### Design Risks

- **RISK-006**: Automation scripts making game too passive too quickly - Mitigation: Careful balancing of unlock thresholds, maintain strategic decisions even with automation
- **RISK-007**: Incident generation becoming overwhelming or boring - Mitigation: Extensive playtesting, configurable difficulty modes
- **RISK-008**: Specialist progression feeling too slow or too fast - Mitigation: JSON-driven XP curves allow rapid iteration based on playtest feedback
- **RISK-009**: UI becoming cluttered with too much information - Mitigation: Implement tabbed panels, collapsible sections, focus on essential data

### Project Risks

- **RISK-010**: Scope creep adding features beyond MVP - Mitigation: Strict adherence to implementation plan phases, defer extended features to Phase 8
- **RISK-011**: Over-engineering architecture for "vibe coding" project - Mitigation: Follow GUD-001 guideline, prioritize iteration speed over perfect patterns
- **RISK-012**: JSON schema changes breaking existing save files - Mitigation: Implement version migration system, maintain backward compatibility

### Assumptions

- **ASSUMPTION-001**: Single-player experience is sufficient for MVP (no multiplayer/leaderboards)
- **ASSUMPTION-002**: Players will engage with backend tools for game balancing (developer/power-user audience)
- **ASSUMPTION-003**: JSON file size will remain manageable for manual editing (<100KB per file)
- **ASSUMPTION-004**: Game sessions typically last 30min-3hr per sitting
- **ASSUMPTION-005**: Players understand basic idle/tycoon game conventions (automation, prestige, etc.)
- **ASSUMPTION-006**: Development environment is VS Code with GitHub Copilot access
- **ASSUMPTION-007**: Target platform is desktop (Windows/Mac/Linux) with mouse input
- **ASSUMPTION-008**: Python 3.9+ runtime is acceptable for player base (not web-based distribution)
- **ASSUMPTION-009**: Backend server runs locally or on LAN (not public-facing production deployment)
- **ASSUMPTION-010**: Game balance is iterative and will require multiple tuning cycles

## 8. Related Specifications / Further Reading

### Game Design References

- **Idle Game Design Principles**: [https://www.gamedeveloper.com/design/the-math-of-idle-games](https://www.gamedeveloper.com/design/the-math-of-idle-games)
- **Tycoon Game Progression Curves**: Study games like Game Dev Tycoon, Planet Coaster for economy balancing
- **RPG Leveling Systems**: D&D 5e XP progression curves, skill tree design patterns

### Technical References

- **Pygame Documentation**: [https://www.pygame.org/docs/](https://www.pygame.org/docs/)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **JSON Schema Specification**: [https://json-schema.org/](https://json-schema.org/)
- **Pydantic Models**: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)

### Architecture Patterns

- **Data-Driven Game Architecture**: [https://gameprogrammingpatterns.com/data-locality.html](https://gameprogrammingpatterns.com/data-locality.html)
- **Entity-Component Systems**: Reference for separation of game logic and rendering
- **Event-Driven Programming**: [https://www.pythoncentral.io/observer-design-pattern/](https://www.pythoncentral.io/observer-design-pattern/)

### Similar Projects

- Study open-source idle games for UI patterns and progression systems
- Examine cybersecurity training simulators for domain-appropriate incident types
- Review "Papers, Please" for triage-style gameplay inspiration

### Internal Documents

- `/plan/feature-cybersec-idle-game-1.md` (this document)
- `.github/copilot-instructions.md` (to be created in TASK-003)
- `/docs/architecture.md` (to be created in TASK-066)
- `/docs/gameplay_design.md` (to be created in TASK-074)
