# Rich Logging System Documentation

## Overview

The game now features a **comprehensive, production-grade logging system** with the following capabilities:

- 🎨 **Color-coded console output** for easy visual debugging
- 📝 **Rotating file handlers** to prevent log bloat (10MB max, 5 backups)
- ⏱️ **Performance tracking** with automatic timing of operations
- 🔍 **Exception tracking** with full stack traces and context
- 🏗️ **Structured logging** with component tagging
- 🔧 **Context managers** for operation tracking

## Quick Start

### Basic Logging

```python
from src.utils.logger import GameLogger

# Create a logger for your module
logger = GameLogger("my_module")

# Use standard logging methods
logger.info("[SYSTEM] System initialized successfully")
logger.warning("[SYSTEM] Resource running low", resource="memory", usage=85)
logger.error("[SYSTEM] Failed to load configuration", exception=e, path="/config/game.json")
```

### Operation Tracking with Context Manager

```python
from src.utils.logger import GameLogger

logger = GameLogger("my_module")

# Track operation with automatic timing and exception handling
with logger.operation("Loading Game Data") as op:
    # Do work...
    game_data = load_data()
    
    # Add context for logging
    op.add_context('items_loaded', len(game_data))
    
    # If exception occurs, it's automatically logged with context
```

**Output:**
```
09:06:46 | INFO  | my_module | [SYSTEM] Starting: Loading Game Data
09:06:46 | INFO  | my_module | [SYSTEM] Completed: Loading Game Data (15.23ms) | items_loaded=42
```

### Environment Variables

Control logging behavior via environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL=DEBUG
python src/main.py

# Or inline
LOG_LEVEL=DEBUG python src/main.py
```

## Features

### 1. Color-Coded Console Output

Log levels are automatically color-coded for easy scanning:

- **DEBUG**: Dim gray - detailed debugging information
- **INFO**: Bright blue - normal operations
- **WARNING**: Bright yellow - potential issues
- **ERROR**: Bright red - errors that need attention
- **CRITICAL**: Red background + white text - severe failures

Components are also color-coded:
- **[GAME]**: Bright magenta
- **[SYSTEM]**: Bright green
- **[UI]**: Bright cyan
- **[BACKEND]**: Yellow
- **[PERFORMANCE]**: Cyan

### 2. Rotating File Handlers

Logs are automatically written to timestamped files:

```
logs/
  game_20251019_090646.log  (latest)
  game_20251019_090637.log
  ...
```

**Configuration:**
- Max file size: 10MB per log file
- Backup count: 5 previous log files kept
- Automatic rotation when size limit reached

### 3. Performance Tracking

The context manager automatically tracks operation duration:

```python
with logger.operation("Database Query"):
    results = db.query("SELECT * FROM incidents")
    
# Automatically logs:
# [SYSTEM] Starting: Database Query
# [SYSTEM] Completed: Database Query (45.67ms)
```

### 4. Exception Tracking

Exceptions are logged with full context and stack traces:

```python
try:
    risky_operation()
except Exception as e:
    logger.error(
        "[SYSTEM] Failed to complete operation",
        exception=e,
        context={'user_id': user_id, 'attempt': 3}
    )
```

**Output includes:**
- Exception type and message
- Full stack trace
- Custom context data
- Timestamp and logger name

### 5. Structured Logging

Add key-value context to any log message:

```python
logger.info(
    "[EVENT] Incident assigned",
    incident_id="inc_001",
    specialist_id="spec_005",
    difficulty=3,
    priority="high"
)

# Output:
# 09:06:46 | INFO | my_module | [EVENT] Incident assigned | incident_id=inc_001 | specialist_id=spec_005 | difficulty=3 | priority=high
```

## Log Components

Use component tags to categorize log messages:

| Component | Usage | Color |
|-----------|-------|-------|
| `[GAME]` | Core game operations | Bright Magenta |
| `[SYSTEM]` | System initialization/shutdown | Bright Green |
| `[UI]` | User interface events | Bright Cyan |
| `[BACKEND]` | Backend integration | Yellow |
| `[EVENT]` | Game events (incidents, assignments) | Magenta |
| `[PERFORMANCE]` | Performance metrics | Cyan |
| `[SAVE]` | Save/load operations | Blue |
| `[PLUGIN]` | Plugin system | Green |

Example:
```python
logger.info("[GAME] Starting main game loop...")
logger.debug("[SYSTEM] Initializing plugin architecture...")
logger.warning("[BACKEND] Backend not available, running standalone")
```

## Advanced Usage

### Custom Log Levels

```python
# Debug logging (very detailed)
logger.debug("[SYSTEM] Variable state", var1=value1, var2=value2)

# Info logging (normal operations)
logger.info("[GAME] Game initialized successfully")

# Warning logging (potential issues)
logger.warning("[SYSTEM] Memory usage high", usage_percent=85)

# Error logging (errors that need attention)
logger.error("[GAME] Failed to load save file", exception=e, file_path=path)

# Critical logging (severe failures)
logger.critical("[GAME] FATAL ERROR - Cannot continue", exception=e)
```

### Operation Context

Add context data to operations for better debugging:

```python
with logger.operation("Processing Incident") as op:
    op.add_context('incident_id', incident.id)
    op.add_context('specialist', specialist.name)
    
    # Process incident...
    result = process_incident(incident, specialist)
    
    op.add_context('success', result.success)
    op.add_context('duration', result.duration)

# If successful:
# [SYSTEM] Completed: Processing Incident (123.45ms) | incident_id=inc_001 | specialist=Alice Chen | success=True | duration=120

# If exception:
# [ERROR] Exception during Processing Incident
# Exception Type: ValueError
# Exception Message: Invalid incident state
# Context:
#   incident_id: inc_001
#   specialist: Alice Chen
#   duration_ms: 123.45
# Stack Trace: ...
```

### Performance Logging

```python
from src.utils.logger import log_performance

# Manual performance logging
start_time = time.time()
result = expensive_operation()
duration_ms = (time.time() - start_time) * 1000

log_performance(
    logger.logger,
    "Expensive Operation",
    duration_ms,
    result_count=len(result),
    cache_hit=False
)

# Output:
# [PERFORMANCE] Expensive Operation: 234.56ms | result_count=42 | cache_hit=False
```

### Game Event Logging

```python
from src.utils.logger import log_game_event

log_game_event(
    logger.logger,
    'INCIDENT_RESOLVED',
    f"Incident {incident_id} resolved successfully",
    specialist=specialist_id,
    sla_met=True,
    reward=500,
    xp=100
)

# Output:
# [EVENT] [INCIDENT_RESOLVED] Incident inc_001 resolved successfully | specialist=spec_005 | sla_met=True | reward=500 | xp=100
```

## Configuration

### Setup Logging in Your Application

```python
from src.utils.logger import setup_logging
from datetime import datetime
import os

# Configure logging at application startup
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_file = f'logs/game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

setup_logging(
    log_level=log_level,          # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file=log_file,             # Path to log file
    log_to_console=True,           # Whether to output to console
    use_colors=True,               # Whether to use ANSI colors
    max_file_size=10*1024*1024,    # 10MB per file
    backup_count=5                 # Keep 5 backup files
)
```

### Disable Colors (for CI/CD)

```python
setup_logging(
    log_level='INFO',
    log_file='logs/game.log',
    log_to_console=True,
    use_colors=False  # Disable colors for non-terminal output
)
```

### Change Log Level at Runtime

```bash
# Debug mode
LOG_LEVEL=DEBUG python src/main.py --new-game

# Error-only mode
LOG_LEVEL=ERROR python src/main.py
```

## Log File Format

### Console Output (with colors)
```
09:06:46 | INFO     | main | [GAME] Starting main game loop...
09:06:46 | DEBUG    | system_manager | [SYSTEM] Initializing plugin architecture...
09:06:46 | WARNING  | backend | [BACKEND] Backend not available, running standalone
09:06:46 | ERROR    | save_manager | [SAVE] Failed to load save file | path=/saves/slot_1.json
```

### File Output (no colors, more detail)
```
2025-10-19 09:06:46 | INFO     | main                 | [GAME] Starting main game loop...
2025-10-19 09:06:46 | DEBUG    | system_manager       | [SYSTEM] Initializing plugin architecture...
2025-10-19 09:06:46 | WARNING  | backend              | [BACKEND] Backend not available, running standalone
2025-10-19 09:06:46 | ERROR    | save_manager         | [SAVE] Failed to load save file | path=/saves/slot_1.json
```

## Debugging Tips

### Finding Errors Quickly

```bash
# View only errors from latest log
cd logs
tail -1000 game_*.log | grep ERROR

# Watch logs in real-time
tail -f game_*.log

# Find specific component logs
grep "\[SYSTEM\]" game_20251019_090646.log

# Find performance issues
grep "PERFORMANCE" game_20251019_090646.log | grep -E "[0-9]{3,}\."  # >100ms operations
```

### Common Debugging Patterns

1. **Startup Issues**: Look for ERROR/CRITICAL during initialization
   ```bash
   grep -E "ERROR|CRITICAL" game_*.log | grep "Initialization"
   ```

2. **Performance Problems**: Find slow operations
   ```bash
   grep "Completed:" game_*.log | awk -F'[()]' '{print $2}' | sort -n | tail -10
   ```

3. **Exception Tracking**: Find all exceptions with context
   ```bash
   grep -A 20 "Exception during" game_*.log
   ```

## Best Practices

### ✅ DO

- Use component tags consistently: `[GAME]`, `[SYSTEM]`, `[UI]`, etc.
- Add context to error logs: `exception=e, user_id=id, path=path`
- Use operation context managers for multi-step operations
- Log state transitions: "Starting X", "Completed X"
- Include relevant IDs in log messages
- Use appropriate log levels (don't log everything as INFO)

### ❌ DON'T

- Don't log sensitive data (passwords, API keys, user PII)
- Don't log inside tight loops (performance impact)
- Don't use print() - use logger instead
- Don't catch exceptions silently without logging
- Don't forget to add context to exceptions
- Don't use generic messages like "Error occurred"

## Examples from the Codebase

### Game Initialization

```python
def initialize(self) -> bool:
    with self.logger.operation("Game Initialization") as op:
        try:
            op.add_context('mode', self.args.mode.value)
            
            # Initialize components...
            with self.logger.operation("Save Manager Initialization"):
                self.save_manager = SaveManager()
                self.logger.info("[GAME] Save manager initialized successfully")
            
            # More initialization...
            return True
            
        except Exception as e:
            self.logger.error("[GAME] Failed to initialize game", exception=e)
            return False
```

### Plugin Registration

```python
with self.logger.operation("Plugin Registration"):
    plugins = [
        ("IdlePlugin", IdlePlugin()),
        ("PrestigeSystem", PrestigeSystem()),
        # ... more plugins
    ]
    
    for plugin_name, plugin_instance in plugins:
        self.logger.debug(f"[SYSTEM] Registering {plugin_name}...")
        self.system_manager.register_system(plugin_instance)
    
    self.logger.info(f"[SYSTEM] Registered {len(plugins)} game systems")
```

### Error Handling with Context

```python
try:
    specialist = self.save_manager.load_game(slot)
except FileNotFoundError as e:
    self.logger.error(
        "[SAVE] Save file not found",
        exception=e,
        slot=slot,
        save_dir=self.save_manager.save_dir
    )
    # Fallback behavior...
```

## Troubleshooting

### Logs Not Appearing

1. Check log level: `export LOG_LEVEL=DEBUG`
2. Verify log directory exists: `ls -la logs/`
3. Check file permissions: `ls -la logs/`

### Colors Not Working

1. Terminal doesn't support ANSI codes
2. Disable colors: `setup_logging(..., use_colors=False)`
3. Or use: `export NO_COLOR=1`

### Log Files Too Large

1. Logs auto-rotate at 10MB
2. Adjust: `setup_logging(..., max_file_size=5*1024*1024)`  # 5MB
3. Adjust backup count: `setup_logging(..., backup_count=3)`

### Performance Impact

1. Set log level to INFO or WARNING in production
2. Don't log in tight loops
3. Use DEBUG only during development

## Migration from Old Logging

**Old:**
```python
self.logger.logger.info("[GAME] Message")
self.logger.logger.error(f"[GAME] Failed: {e}")
```

**New:**
```python
self.logger.info("[GAME] Message")
self.logger.error("[GAME] Failed", exception=e, context_key=value)
```

The new API is cleaner and provides better exception handling with automatic stack traces.

## Summary

The new logging system provides:

✅ **Production-grade reliability** with rotating file handlers  
✅ **Developer-friendly** color-coded console output  
✅ **Performance tracking** with automatic operation timing  
✅ **Exception tracking** with full stack traces and context  
✅ **Structured logging** with key-value pairs  
✅ **Easy debugging** with component tagging and context managers  

Start using it today to make debugging and monitoring your game dramatically easier!
