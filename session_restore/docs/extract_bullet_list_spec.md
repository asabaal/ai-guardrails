# _extract_bullet_list() - Test Coverage Specification

## Overview

The `_extract_bullet_list()` helper function extracts a list of items from various string formats commonly used in LLM responses.

**Purpose**: Extract list items from comma-separated or bullet-point formatted strings

**Current Coverage**: To be determined

## Function Signature

```python
def _extract_bullet_list(text: str) -> List[str]
```

## Parameters

| Parameter | Type | Description |
|----------|-------|-----------|
| `text` | str | Text containing list items (comma-separated or bulleted) |

## Returns

List of extracted items as strings, with whitespace trimmed.

## Behavior

### Input Handling
- Accepts None or empty string → returns empty list
- Handles comma-separated lists
- Handles newline-separated lists with bullet markers
- Handles mixed formats
- Strips whitespace from each item
- Filters out empty items

### Supported Formats

#### Comma-Separated
```python
"item1, item2, item3" → ["item1", "item2", "item3"]
```

#### Bullet Points (Dashes)
```python
"""
- item1
- item2
- item3
""" → ["item1", "item2", "item3"]
```

#### Bullet Points (Bullets)
```python
"""
• item1
• item2
• item3
""" → ["item1", "item2", "item3"]
```

#### Numbered List
```python
"""
1. item1
2. item2
3. item3
""" → ["item1", "item2", "item3"]
```

#### Mixed (Comma with Extra Spaces)
```python
"  item1  ,  item2  ,  item3  " → ["item1", "item2", "item3"]
```

## Coverage Areas

### Input Validation
- None input
- Empty string input
- Whitespace-only input

### Format Variations
- Comma-separated
- Bullet points (dash)
- Bullet points (bullet character)
- Numbered lists
- Mixed formats (comma + newlines)

### Edge Cases
- Empty items in list (consecutive commas)
- Extra whitespace around items
- Newlines in input
- Single item
- Very long lists
- Items with special characters
- Items containing commas (should not split)

### Malformed Input
- No commas, no bullets (returns single item as list)
- Only bullet markers with no content
- Leading/trailing commas

## Test Requirements for 100% Coverage

### Empty/None Tests
- None input → empty list
- Empty string → empty list
- Whitespace only → empty list

### Comma-Separated Tests
- Simple comma-separated list
- Comma-separated with extra spaces
- Comma-separated with leading/trailing whitespace
- Single item (no commas)
- Two items
- Many items (10+)

### Bullet Point Tests
- Dash bullet points
- Bullet character (•)
- Numbered list with periods
- Numbered list with parentheses

### Mixed Format Tests
- Comma-separated with newlines
- Bullets with extra spacing
- Mixed bullets and commas

### Edge Case Tests
- Empty items (consecutive commas)
- Items with commas inside (shouldn't split)
- Items with special characters
- Very long list
- Single item without any delimiters
- Leading/trailing delimiters
- Empty items after stripping

## Dependencies

- `re` (from standard library) - For pattern matching
- `List` (from typing) - Type hints

## Error Handling

### Input Errors
- None input → returns []
- Empty string → returns []
- Whitespace-only → returns []

### Format Errors
- No recognizable format → returns list with single stripped item
- Malformed input → returns best-effort extraction

## Implementation Notes

### Algorithm
1. If input is None or empty → return []
2. Check if contains newlines
   - If yes: process as bullet/numbered list
   - If no: process as comma-separated
3. For bullet/numbered: split by newlines, strip markers, strip whitespace, filter empty
4. For comma-separated: split by commas, strip whitespace, filter empty
5. Return result

### Marker Patterns
- Dash: `^-\\s*`
- Bullet: `^•\\s*`
- Numbered: `^\\d+[.)]\\s*`

### Priority
1. Bullet-point formats (newlines detected)
2. Comma-separated format (no newlines)
3. Fallback: single item (strip and return as list)

## Integration Tests

- Integration with `process_turns_incrementally()` for extracting accumulated fields
- Used for: key_decisions, constraints, artifacts, open_questions

## Coverage Target

**Function**: `_extract_bullet_list()`

**Estimated Lines**: 30-50 lines
**Target**: 100% test coverage

**Current Coverage**: Unknown (to be determined)

## Test Files

- `tests/test_turn_summarizer.py` (extend existing file)

## Example Test Cases

```python
def test_comma_separated_list():
    text = "item1, item2, item3"
    result = _extract_bullet_list(text)
    assert result == ["item1", "item2", "item3"]

def test_bullet_points():
    text = """
- item1
- item2
- item3
"""
    result = _extract_bullet_list(text)
    assert result == ["item1", "item2", "item3"]

def test_numbered_list():
    text = """
1. item1
2. item2
3. item3
"""
    result = _extract_bullet_list(text)
    assert result == ["item1", "item2", "item3"]
```
