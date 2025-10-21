---
applyto: "**"
---

# Documentation Guidelines - Instructions

**This file explains when to add to instruction files vs feature documentation.**

Reference this when:
- Deciding where to document something
- Understanding documentation hierarchy
- Contributing to the project
- Organizing new documentation

---

## Documentation Hierarchy

### Instruction Files (`.github/*-instructions.md`)

**Purpose**: Permanent project guidelines, coding standards, and architectural patterns that apply to ALL code.

**When to use**:
- Coding standards and quality gates
- Project-wide architectural patterns
- Development workflows that don't change
- Plugin system architecture
- Testing requirements and patterns
- Code style conventions
- Common anti-patterns to avoid

**Examples**:
- "All functions must have type hints" → `core-standards.instructions.md`
- "Plugin lifecycle: initialize/update/shutdown" → `plugin-system.instructions.md`
- "Test naming convention: test_<subject>_<action>_<outcome>" → `testing.instructions.md`
- "How to add a new game system" → `workflows.instructions.md`

**Characteristics**:
- Rarely changes once established
- Applies to all future code
- Describes HOW to build, not WHAT was built
- Process and pattern focused
- Cross-references other instruction files

---

### Feature Documentation (`docs/*.md`)

**Purpose**: Specific feature explanations, design decisions, and implementation details for individual systems.

**When to use**:
- Explaining a specific feature's design
- Documenting game mechanics
- Implementation notes for a particular system
- Feature-specific API documentation
- Roadmaps and progress tracking

**Examples**:
- "How the burnout system works" → `docs/BURNOUT_SYSTEM.md`
- "Idle mechanics implementation" → `docs/IDLE_MECHANICS_SUMMARY.md`
- "RPG systems design" → `docs/RPG_SYSTEMS_IMPLEMENTATION.md`
- "Backend API specification" → `docs/BACKEND_SPECIFICATION.md`

**Characteristics**:
- Feature-specific content
- May become outdated as features evolve
- Describes WHAT was built and WHY
- Implementation and design focused
- Can be updated or archived as features change

---

### README Files (`*/README.md`)

**Purpose**: Quick start guides, directory explanations, and usage instructions.

**When to use**:
- Directory-level overview
- Quick start instructions
- Setup and installation
- High-level project description

**Examples**:
- Project overview → `README.md`
- Backend setup → `backend/README.md`
- UI quick start → `docs/QUICK_START_UI.md`

**Characteristics**:
- Entry point for new developers
- Practical "how to run" information
- Links to deeper documentation
- Minimal theory, maximum practicality

---

## Decision Matrix

Ask yourself:

### "Does this apply to ALL code forever?"
→ **YES**: Add to instruction file
→ **NO**: Continue below

### "Is this about coding standards or patterns?"
→ **YES**: Add to relevant instruction file
  - Code quality → `core-standards.instructions.md`
  - Naming/style → `code-style.instructions.md`
  - Architecture → `architecture.instructions.md`
  - Plugins → `plugin-system.instructions.md`
  - Tests → `testing.instructions.md`
  - JSON config → `data-driven.instructions.md`
  - Workflows → `workflows.instructions.md`
→ **NO**: Continue below

### "Is this explaining a specific feature?"
→ **YES**: Add to `docs/` folder
  - Create `docs/FEATURE_NAME.md`
  - Link from main README if needed
→ **NO**: Continue below

### "Is this a quick start or setup guide?"
→ **YES**: Add to appropriate README file
  - Root README for project overview
  - Subdirectory README for that area
→ **NO**: Might not need documentation yet

---

## Instruction File Ownership

Each instruction file has a specific focus:

### `copilot-instructions.md`
- **Entry point** - Main navigation hub
- References all other instruction files
- High-level project overview
- Quick reference tables

### `core-standards.instructions.md`
- 15-point quality gate
- 15 red flag instant rejections
- Daily pre-commit checklist
- Core mandate and philosophy
- What defines "excellence"

### `code-style.instructions.md`
- Naming conventions (classes, functions, variables)
- Type hints and docstrings
- Error handling patterns
- Logging levels
- Anti-patterns with examples
- Code formatting rules

### `architecture.instructions.md`
- Project structure (`/src/`, `/data/`, `/backend/`)
- Separation of concerns
- Design patterns used
- Module organization
- Dependency rules

### `plugin-system.instructions.md`
- GameSystem base class
- Plugin lifecycle methods
- Event-driven communication
- All registered plugins
- Plugin development checklist
- Common plugin patterns

### `testing.instructions.md`
- Testing mandate (every public function)
- Test organization structure
- Fixture patterns
- Naming conventions for tests
- Coverage requirements
- Edge case testing

### `data-driven.instructions.md`
- JSON configuration patterns
- All config file structures
- Hot-reload capabilities
- Configuration access patterns
- Game balance workflow

### `workflows.instructions.md`
- Step-by-step task guides
- "How to add X" tutorials
- Common development workflows
- Backend debugging commands
- Pre-commit checklist

### `documentation-guidelines.instructions.md` (this file)
- When to use instruction files
- When to use feature docs
- Documentation hierarchy
- Where to put new documentation

---

## Examples

### Example 1: New Anti-Pattern Discovered

**Question**: Found a new anti-pattern - using `time.sleep()` in game loop instead of delta time.

**Decision**:
- ❌ Not feature-specific
- ✅ Coding standard that applies to ALL code
- ✅ Anti-pattern example

**Action**: Add to `code-style.instructions.md` under anti-patterns section.

---

### Example 2: Burnout System Design

**Question**: Need to document how the burnout system works.

**Decision**:
- ✅ Feature-specific
- ❌ Not a universal coding standard
- ✅ Implementation details

**Action**: Create `docs/BURNOUT_SYSTEM.md` with design and implementation notes.

---

### Example 3: New Testing Pattern

**Question**: Discovered a great pattern for mocking EventBus in tests.

**Decision**:
- ❌ Not feature-specific
- ✅ Testing pattern that applies to ALL tests
- ✅ Should be standardized

**Action**: Add to `testing.instructions.md` under fixture patterns section.

---

### Example 4: Backend Setup Instructions

**Question**: Need to explain how to run the backend server.

**Decision**:
- ✅ Quick start / setup guide
- ❌ Not a coding standard
- ✅ Practical "how to run" info

**Action**: Add to `backend/README.md` or `docs/BACKEND_QUICKSTART.md`.

---

### Example 5: New Plugin Lifecycle Method

**Question**: Added new optional lifecycle method `on_pause()` to GameSystem.

**Decision**:
- ❌ Not feature-specific
- ✅ Plugin architecture change
- ✅ Applies to ALL future plugins

**Action**: Update `plugin-system.instructions.md` to document the new lifecycle method.

---

## Updating Instruction Files

### When to Update

Update instruction files when:
- New coding standard established
- New architectural pattern adopted
- New workflow becomes standard
- Anti-pattern identified
- Testing pattern standardized
- Plugin architecture changes

### When NOT to Update

Don't update instruction files for:
- Feature-specific implementation details
- One-off solutions
- Temporary workarounds
- Experimental code
- Feature roadmaps

### How to Update

1. **Identify the right file** - Use decision matrix above
2. **Find the relevant section** - Each file is organized logically
3. **Add clear examples** - Show ❌ WRONG and ✅ CORRECT
4. **Update cross-references** - Link to related sections
5. **Keep it concise** - Instruction files should be scannable
6. **Update copilot-instructions.md** - If you add a new major section

---

## File Naming Conventions

### Instruction Files
- Pattern: `<topic>-instructions.md`
- Location: `.github/`
- Examples:
  - `core-standards.instructions.md`
  - `plugin-system.instructions.md`
  - `testing.instructions.md`

### Feature Documentation
- Pattern: `<FEATURE_NAME>.md` (UPPERCASE for visibility)
- Location: `docs/`
- Examples:
  - `docs/BURNOUT_SYSTEM.md`
  - `docs/RPG_SYSTEMS_IMPLEMENTATION.md`
  - `docs/ARCHITECTURE_ROADMAP.md`

### README Files
- Pattern: `README.md` (always this exact name)
- Location: Root or subdirectories
- Examples:
  - `README.md` (project root)
  - `backend/README.md`
  - `docs/README.md`

---

## Quick Reference

| Type of Content | Where It Goes |
|----------------|---------------|
| Coding standards | `core-standards.instructions.md` |
| Naming conventions | `code-style.instructions.md` |
| Anti-patterns | `code-style.instructions.md` |
| Architecture patterns | `architecture.instructions.md` |
| Plugin architecture | `plugin-system.instructions.md` |
| Testing standards | `testing.instructions.md` |
| JSON config patterns | `data-driven.instructions.md` |
| Development workflows | `workflows.instructions.md` |
| Feature design | `docs/FEATURE_NAME.md` |
| Setup instructions | `README.md` files |
| API documentation | `docs/API_NAME.md` |
| Progress tracking | `docs/PROGRESS.md` |

---

## Maintenance

### Regular Reviews

Review instruction files:
- When standards evolve
- When new patterns emerge
- When anti-patterns are identified
- After major architectural changes

### Keeping Current

- Instruction files should rarely change
- When they do change, it's significant
- Update cross-references when adding sections
- Archive outdated feature docs to `docs/archive/`

### Avoiding Bloat

- Keep instruction files focused
- Don't duplicate content between files
- Use cross-references instead
- Move feature-specific content to `docs/`
- Delete obsolete examples

---

## See Also

- **[copilot-instructions.md](../copilot-instructions.md)** - Main instructions and navigation hub
- **[core-standards.instructions.md](core-standards.instructions.md)** - Quality standards
- **[workflows.instructions.md](workflows.instructions.md)** - How to add features
- **[architecture.instructions.md](architecture.instructions.md)** - Project structure
