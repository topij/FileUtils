# FileUtils Logging Control - Feature Specification

**Version**: 1.0  
**Target Version**: FileUtils 0.9.0  
**Author**: md2pptx Team  
**Date**: 2025-11-30

---

## Problem Statement

FileUtils currently logs INFO-level messages to stdout during initialization and operations, which creates challenges for applications that require clean, parseable output formats (JSON, XML, etc.) for automation, CI/CD pipelines, and AI agent integration.

### Current Behavior

```python
fu = FileUtils()
# Output:
# 2025-11-30 11:40:27,448 - FileUtils.core.file_utils - INFO - Project root: /path/to/project
# 2025-11-30 11:40:27,449 - FileUtils.core.file_utils - INFO - FileUtils initialized with local storage
```

### Impact on Consuming Applications

Applications using `--output-format json` or similar structured output modes must implement workarounds to suppress FileUtils logging:

```python
# Current workaround (hacky)
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()
fu = FileUtils()
sys.stdout = old_stdout
```

This approach:
- ❌ Requires intimate knowledge of FileUtils internals
- ❌ Fragile and version-dependent
- ❌ Adds unnecessary complexity to consuming code
- ❌ May break if FileUtils changes logging implementation

---

## Proposed Solution

Add **optional** logging control parameters to FileUtils initialization, maintaining full backward compatibility.

### Design Goals

1. ✅ **Zero breaking changes** - existing code continues to work unchanged
2. ✅ **Simple common case** - one parameter for quiet mode
3. ✅ **Flexible advanced case** - fine-grained log level control
4. ✅ **Pythonic** - follows Python logging conventions
5. ✅ **Performance** - avoid unnecessary string formatting

---

## API Specification

### Constructor Signature

```python
class FileUtils:
    def __init__(
        self,
        storage_type: str = "local",
        quiet: bool = False,
        log_level: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize FileUtils with optional logging control.
        
        Args:
            storage_type: Storage backend ('local', 'azure', etc.)
            quiet: If True, suppress all logging except CRITICAL errors.
                   Shorthand for log_level=logging.CRITICAL.
            log_level: Explicit logging level (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL).
                      If provided, overrides 'quiet' parameter.
            **kwargs: Additional storage-specific parameters
        
        Examples:
            # Default behavior (backward compatible)
            fu = FileUtils()
            
            # Quiet mode for automation
            fu = FileUtils(quiet=True)
            
            # Custom log level
            fu = FileUtils(log_level=logging.WARNING)
            
            # With storage type
            fu = FileUtils(storage_type="azure", quiet=True)
        """
```

### Parameter Priority

1. `log_level` (if explicitly provided)
2. `quiet=True` → equivalent to `log_level=logging.CRITICAL`
3. Default → `logging.INFO` (current behavior)

---

## Implementation Requirements

### 1. Logger Configuration

```python
import logging

class FileUtils:
    def __init__(self, storage_type="local", quiet=False, log_level=None, **kwargs):
        # Determine effective log level
        if log_level is not None:
            effective_level = log_level
        elif quiet:
            effective_level = logging.CRITICAL
        else:
            effective_level = logging.INFO  # Default (backward compatible)
        
        # Configure FileUtils logger
        self.logger = logging.getLogger("FileUtils.core.file_utils")
        self.logger.setLevel(effective_level)
        
        # Apply to all FileUtils sub-loggers
        logging.getLogger("FileUtils").setLevel(effective_level)
        
        # ... rest of initialization
```

### 2. Lazy Logging (Performance Optimization)

Replace eager string formatting:

```python
# Before (always formats, even if not logged)
logging.info(f"Project root: {self.root}")
```

With lazy evaluation:

```python
# After (only formats if INFO level is enabled)
if self.logger.isEnabledFor(logging.INFO):
    logging.info(f"Project root: {self.root}")
```

**Benefit**: Avoids expensive string operations when logging is suppressed.

### 3. Respect External Logger Configuration

If a logger is already configured externally (e.g., by the consuming application), FileUtils should respect that configuration:

```python
def __init__(self, ...):
    # Get logger
    self.logger = logging.getLogger("FileUtils.core.file_utils")
    
    # Only set level if not already configured AND if user provided preferences
    if not self.logger.handlers and (log_level is not None or quiet):
        self.logger.setLevel(effective_level)
```

---

## Usage Examples

### Example 1: JSON Output Application

```python
# Application with JSON output mode
import json
from FileUtils import FileUtils

def generate_report(output_format='text'):
    # Suppress FileUtils logging for JSON mode
    fu = FileUtils(quiet=(output_format == 'json'))
    
    # ... generate report
    
    if output_format == 'json':
        print(json.dumps({"status": "success", "file": result}))
    else:
        print(f"Report generated: {result}")
```

### Example 2: CI/CD Pipeline

```python
# CI/CD script requiring clean stdout
fu = FileUtils(quiet=True)

# All FileUtils operations silently succeed or raise exceptions
fu.copy("source.txt", "dest.txt")
```

### Example 3: Debug Mode

```python
# Development with verbose logging
fu = FileUtils(log_level=logging.DEBUG)

# Shows all FileUtils internal operations
```

### Example 4: Warning-Only Mode

```python
# Production monitoring - only log warnings and errors
fu = FileUtils(log_level=logging.WARNING)
```

---

## Backward Compatibility

### Existing Code (Unmodified)

```python
fu = FileUtils()  # Works exactly as before
fu = FileUtils(storage_type="azure")  # Works exactly as before
```

**Guarantee**: All existing code continues to work with identical behavior.

### Migration Path

Applications can gradually adopt the new parameters:

```python
# Phase 1: No changes needed
fu = FileUtils()

# Phase 2: Add quiet mode when convenient
fu = FileUtils(quiet=should_be_quiet())

# Phase 3: Fine-tune log levels as needed
fu = FileUtils(log_level=get_log_level())
```

---

## Testing Requirements

### Unit Tests

```python
def test_default_logging():
    """Default behavior unchanged."""
    fu = FileUtils()
    assert fu.logger.level == logging.INFO

def test_quiet_mode():
    """Quiet mode sets CRITICAL level."""
    fu = FileUtils(quiet=True)
    assert fu.logger.level == logging.CRITICAL

def test_explicit_log_level():
    """Explicit log level takes precedence."""
    fu = FileUtils(log_level=logging.WARNING)
    assert fu.logger.level == logging.WARNING

def test_quiet_overridden_by_log_level():
    """log_level overrides quiet parameter."""
    fu = FileUtils(quiet=True, log_level=logging.DEBUG)
    assert fu.logger.level == logging.DEBUG
```

### Integration Tests

```python
def test_json_output_clean():
    """JSON output contains no logging pollution."""
    fu = FileUtils(quiet=True)
    
    # Capture stdout
    output = capture_stdout(lambda: generate_json_report(fu))
    
    # Should be valid JSON
    data = json.loads(output)
    assert "status" in data
```

---

## Documentation Requirements

### Docstring Updates

- Update `FileUtils.__init__` docstring with new parameters
- Add examples section showing quiet mode and log_level usage
- Document parameter priority/precedence

### README/User Guide

Add section on logging control:

```markdown
## Logging Control

FileUtils logs operations at INFO level by default. For automation and structured output scenarios, you can suppress logging:

### Quiet Mode
```python
fu = FileUtils(quiet=True)  # Only CRITICAL errors logged
```

### Custom Log Level
```python
import logging
fu = FileUtils(log_level=logging.WARNING)  # Only WARNING and above
```
```

---

## Implementation Checklist

- [ ] Add `quiet` and `log_level` parameters to `__init__`
- [ ] Implement log level determination logic
- [ ] Update all logging calls to use lazy evaluation (`isEnabledFor`)
- [ ] Add unit tests for new parameters
- [ ] Add integration tests for quiet mode
- [ ] Update docstrings
- [ ] Update README with logging control section
- [ ] Update CHANGELOG
- [ ] Verify backward compatibility with existing test suite

---

## Success Criteria

1. ✅ All existing FileUtils tests pass without modification
2. ✅ New tests for quiet mode and log_level pass
3. ✅ md2pptx can remove stdout redirection workaround
4. ✅ JSON output from consuming applications is clean
5. ✅ No performance regression in default mode
6. ✅ Documentation clearly explains new features

---

## Alternative Considered

### Environment Variable Approach

```python
import os
if os.getenv("FILEUTILS_QUIET") == "1":
    # Suppress logging
```

**Rejected because**: Less explicit, harder to test, not Pythonic.

### Context Manager Approach

```python
with FileUtils.quiet():
    fu = FileUtils()
```

**Rejected because**: More complex, less intuitive API.

---

## Questions for FileUtils Team

1. **Logger hierarchy**: Should `quiet=True` affect only `FileUtils.core.file_utils` or all `FileUtils.*` loggers?
2. **Handler management**: Should FileUtils add handlers, or rely on root logger configuration?
3. **Storage backends**: Do Azure/GCP storage backends have separate logging that also needs control?
4. **Version target**: Is 0.9.0 appropriate, or should this be 1.0.0 given it's an API addition?

---

## Contact

For questions or clarification:
- **Project**: md2pptx
- **Use Case**: JSON output for AI agents and CI/CD automation
- **Current Version**: FileUtils 0.8.4
