# Refactor Notes

## Removed by AI in the refactor

### 1. `from pathlib import Path` (src/logsum.py:5)
- **AI reason**: Import marked as unused by ruff (F401). Path was imported but never referenced in the code.
- **My decision**: keep removed
- **Justification**: Path was truly unused; no file path operations in the code.

### 2. `import os` (tests/test_logsum.py:3)
- **AI reason**: Import marked as unused by ruff (F401). os module was imported but not used.
- **My decision**: keep removed
- **Justification**: os was imported but only `os.chdir()` was used inside one test which was later refactored to not need it.

### 3. `from io import StringIO` (tests/test_logsum.py:7)
- **AI reason**: Import marked as unused by ruff (F401). StringIO was imported but never called.
- **My decision**: keep removed
- **Justification**: StringIO was never used in any test; tests use actual file I/O with tmp_path fixtures.

### 4. `f"Error: Empty input file or missing header"` → `"Error: Empty input file or missing header"` (src/logsum.py:62)
- **AI reason**: f-string without placeholders marked by ruff (F541). The f-prefix is extraneous when no {var} interpolation exists.
- **My decision**: keep removed
- **Justification**: No variables interpolated; removing f-prefix is a style fix with no behavior change.

### 5. `result = subprocess.run(...)` (tests/test_logsum.py, 3 occurrences)
- **AI reason**: Variable assigned but never used, marked by ruff (F841). Tests with `check=True` don't need to capture the result.
- **My decision**: keep removed
- **Justification**: Tests use `check=True` to raise on non-zero exit; capturing `result` was redundant. Exception path is preserved (check=True still raises on failure).

---

## Summary

**Total removals**: 5 categories (7 individual changes)
**Kept removed**: 5/5 (100%)
**Restored**: 0
**Documented**: All

All removals are safe:
- No guards removed
- No default values removed
- No exception handling removed
- Only unused imports and redundant variable assignments removed

Observable behaviour is **unchanged**.
