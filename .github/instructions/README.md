# GitHub Copilot Custom Instructions

This directory contains path-specific custom instructions for GitHub Copilot, following the recommended best practices from [GitHub's official documentation](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).

## Structure

- **Main instructions**: [`.github/copilot-instructions.md`](../copilot-instructions.md) - Repository-wide instructions and overview
- **Path-specific instructions**: This directory (`.github/instructions/`) - Specialized instructions that apply to specific paths

## Instruction Files

Each instruction file includes YAML frontmatter specifying which paths it applies to:

| File | Applies To | Purpose |
|------|------------|---------|
| `architecture.instructions.md` | `src/`, `backend/`, `tests/`, `data/` | Project structure, design patterns, separation of concerns |
| `code-style.instructions.md` | `*.py` files | Naming conventions, type hints, docstrings, anti-patterns |
| `core-standards.instructions.md` | All files (`**/*`) | 15-point quality gate, red flags, daily checklist |
| `data-driven.instructions.md` | `data/*.json`, Python files | JSON configuration patterns, hot-reload |
| `documentation-guidelines.instructions.md` | `docs/`, `*.md` files | When to document, where to document |
| `plugin-system.instructions.md` | `src/core/plugins/`, plugin-related files | Plugin architecture, events, lifecycle |
| `testing.instructions.md` | `tests/`, `src/` Python files | Test requirements, fixtures, coverage standards |
| `workflows.instructions.md` | All files (`**/*`) | Step-by-step guides for common tasks |

## How It Works

GitHub Copilot reads these instruction files to provide context-aware suggestions:

1. **Repository-wide instructions** from `copilot-instructions.md` are always active
2. **Path-specific instructions** from this directory are activated when you work on files matching their `applies_to` patterns
3. **YAML frontmatter** at the top of each file specifies which paths trigger the instructions

## Example YAML Frontmatter

```yaml
---
applies_to:
  - "src/**/*.py"
  - "tests/**/*.py"
---
```

This makes the instructions apply to all Python files in `src/` and `tests/` directories.

## Best Practices

✅ **DO:**
- Keep instructions focused and specific to their domain
- Use clear, actionable guidance
- Include code examples demonstrating patterns
- Update instructions when patterns evolve

❌ **DON'T:**
- Duplicate information across multiple files
- Create overly broad instructions
- Include outdated patterns or deprecated practices
- Forget to update the `applies_to` patterns when restructuring

## References

- [GitHub Copilot Custom Instructions Documentation](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions)
- [Adding Repository Custom Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [Main Instructions File](../copilot-instructions.md)
