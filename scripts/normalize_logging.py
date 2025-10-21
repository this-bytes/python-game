"""Normalize occurrences of double .logger references across src/.

This script makes conservative replacements in the following order:
1. Replace "self._logger.logger" -> "self._logger"
2. Replace "self.logger.logger" -> "self.logger"
3. Replace "._logger.logger" -> "._logger"
4. Replace ".logger.logger" -> ".logger" (catch-all)

It creates a simple backup of each modified file as <file>.bak and prints a summary.

Run from the repository root: python scripts/normalize_logging.py
"""

import re
from pathlib import Path

ROOT = Path('src')
PATTERNS = [
    (re.compile(r'self\._logger\.logger'), 'self._logger'),
    (re.compile(r'self\.logger\.logger'), 'self.logger'),
    (re.compile(r'\._logger\.logger'), '._logger'),
    (re.compile(r'\.logger\.logger'), '.logger'),
]

modified = []

for py in ROOT.rglob('*.py'):
    text = py.read_text(encoding='utf-8')
    new = text
    for pat, repl in PATTERNS:
        new = pat.sub(repl, new)
    if new != text:
        bak = py.with_suffix(py.suffix + '.bak')
        bak.write_text(text, encoding='utf-8')
        py.write_text(new, encoding='utf-8')
        modified.append(str(py))

print(f"Modified {len(modified)} files")
for f in modified:
    print(f" - {f}")

if not modified:
    print('No changes made')
else:
    print('Backups saved with .bak extension')
