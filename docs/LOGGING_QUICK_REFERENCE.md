# 🎮 Rich Logging System - Quick Reference

## 🚀 Quick Start

```python
from src.utils.logger import GameLogger

logger = GameLogger("my_module")
logger.info("[SYSTEM] Message", key=value)
```

## 📊 Log Levels

| Level | Color | Usage |
|-------|-------|-------|
| `DEBUG` | Gray | Detailed debugging |
| `INFO` | Blue | Normal operations |
| `WARNING` | Yellow | Potential issues |
| `ERROR` | Red | Errors needing attention |
| `CRITICAL` | Red BG | Severe failures |

## 🏷️ Component Tags

```python
logger.info("[GAME] Core game operations")      # Magenta
logger.info("[SYSTEM] System operations")        # Green
logger.info("[UI] UI events")                    # Cyan
logger.info("[BACKEND] Backend integration")     # Yellow
logger.info("[EVENT] Game events")               # Magenta
logger.info("[PERFORMANCE] Performance")         # Cyan
logger.info("[SAVE] Save/load operations")       # Blue
logger.info("[PLUGIN] Plugin system")            # Green
```

## ⏱️ Operation Tracking

```python
# Automatic timing and exception handling
with logger.operation("Operation Name") as op:
    result = do_work()
    op.add_context('items', len(result))
    
# Outputs:
# [SYSTEM] Starting: Operation Name
# [SYSTEM] Completed: Operation Name (15.23ms) | items=42
```

## 🐛 Exception Logging

```python
try:
    risky_operation()
except Exception as e:
    logger.error(
        "[SYSTEM] Failed",
        exception=e,
        user_id=user_id,
        attempt=3
    )
```

## 🔧 Environment Variables

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with specific level
LOG_LEVEL=DEBUG python src/main.py
LOG_LEVEL=ERROR python src/main.py
```

## 📝 Log Methods

```python
# Basic logging
logger.debug("[SYSTEM] Debug info", var=value)
logger.info("[GAME] Normal operation", status="ok")
logger.warning("[SYSTEM] Warning", resource="memory", usage=85)
logger.error("[GAME] Error", exception=e, path="/config")
logger.critical("[GAME] FATAL", exception=e)
```

## 📂 Log Files

```
logs/
  game_20251019_090646.log  ← Latest (10MB max)
  game_20251019_090637.log  ← Backup 1
  game_20251019_090628.log  ← Backup 2
  ...                        ← Up to 5 backups
```

## 🔍 Debugging Commands

```bash
# View latest logs
tail -100 logs/game_*.log

# Watch in real-time
tail -f logs/game_*.log

# Find errors
grep -E "ERROR|CRITICAL" logs/game_*.log

# Find slow operations (>100ms)
grep "Completed:" logs/game_*.log | awk -F'[()]' '{print $2}' | sort -n | tail -10

# Component-specific
grep "\[SYSTEM\]" logs/game_*.log
grep "\[BACKEND\]" logs/game_*.log
```

## ✅ Best Practices

### DO
- ✅ Use component tags: `[GAME]`, `[SYSTEM]`, `[UI]`
- ✅ Add context to errors: `exception=e, path=path`
- ✅ Use operation context managers
- ✅ Log state transitions
- ✅ Include relevant IDs
- ✅ Use appropriate log levels

### DON'T
- ❌ Don't log sensitive data (passwords, API keys)
- ❌ Don't log in tight loops
- ❌ Don't use `print()` - use logger
- ❌ Don't catch exceptions silently
- ❌ Don't use generic messages

## 🎨 Console Output Example

```
09:06:46 | INFO     | main | [GAME] 🎮 Starting Game 🎮
09:06:46 | INFO     | main | [SYSTEM] Starting: Initialization
09:06:46 | DEBUG    | system | [SYSTEM] Loading config...
09:06:46 | INFO     | main | [SYSTEM] Completed: Initialization (45.67ms)
09:06:46 | WARNING  | backend | [BACKEND] Not available, standalone mode
09:06:46 | ERROR    | save | [SAVE] Failed to load | path=/saves/slot_1.json
```

## 📄 Documentation

Full documentation: [`docs/LOGGING_SYSTEM.md`](docs/LOGGING_SYSTEM.md)

## 🆘 Troubleshooting

**Logs not appearing?**
```bash
export LOG_LEVEL=DEBUG
ls -la logs/
```

**Colors not working?**
```python
setup_logging(..., use_colors=False)
```

**Files too large?**
```python
setup_logging(..., max_file_size=5*1024*1024, backup_count=3)
```

---

💡 **Pro Tip**: Use context managers for complex operations - they automatically handle timing and exception logging!

```python
with logger.operation("Complex Task") as op:
    op.add_context('phase', 'initialization')
    # Do work...
    op.add_context('success', True)
```
