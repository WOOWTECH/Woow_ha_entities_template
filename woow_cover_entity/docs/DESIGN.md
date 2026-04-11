# Design Architecture: WoowTech Cover Entity

## Overview

A Home Assistant custom component that creates virtual cover entities with full **TX/RX bidirectional state sync**. Each cover feature delegates control to external HA entities (entity selectors) with optional action script overrides.

Follows the same architecture as `woow_fan_entity` and `climate_template`.

## CoverEntity Features

HA's `CoverEntity` supports 8 features via `CoverEntityFeature`:

| Feature | Flag | Description |
|---------|------|-------------|
| `OPEN` | 1 | Open the cover |
| `CLOSE` | 2 | Close the cover |
| `SET_POSITION` | 4 | Move to a specific position (0-100%) |
| `STOP` | 8 | Stop the cover mid-movement |
| `OPEN_TILT` | 16 | Open the tilt/blinds |
| `CLOSE_TILT` | 32 | Close the tilt/blinds |
| `STOP_TILT` | 64 | Stop the tilt movement |
| `SET_TILT_POSITION` | 128 | Move tilt to a specific position (0-100%) |

### Cover States

| State | Description |
|-------|-------------|
| `open` | Cover is open (position > 0) |
| `closed` | Cover is closed (position = 0) |
| `opening` | Cover is currently opening |
| `closing` | Cover is currently closing |

### Device Classes

`awning`, `blind`, `curtain`, `damper`, `door`, `garage`, `gate`, `shade`, `shutter`, `window`

## TX/RX Architecture

```
  Cover Card (UI)                 Helper Entities (HA)
  ======================         ==========================

  Open / Close / Stop    <--TX-->  input_boolean (open/close state)
  Position (0-100)       <--TX-->  input_number / number
  Tilt Position (0-100)  <--TX-->  input_number / number
```

**TX** = Cover card control sends value to the external entity
**RX** = External entity change updates the cover card automatically

### TX Priority Chain

For each feature, commands are sent via the first available channel:
1. **Action script override** (highest priority)
2. **Entity selector** (medium priority)
3. **Default internal logic** (lowest priority)

## TX/RX Feature Matrix

| Feature | Entity Selector | Action Script | RX Listener | Action Variable |
|---------|:---:|:---:|:---:|:---:|
| **Position** | `position_entity` | `set_position` | `_async_position_entity_changed` | `{{ position }}` (0-100) |
| **Tilt Position** | `tilt_position_entity` | `set_tilt_position` | `_async_tilt_entity_changed` | `{{ tilt_position }}` (0-100) |
| **Open** | — | `open_cover` | — | — |
| **Close** | — | `close_cover` | — | — |
| **Stop** | — | `stop_cover` | — | — |
| **Open Tilt** | — | `open_tilt` | — | — |
| **Close Tilt** | — | `close_tilt` | — | — |
| **Stop Tilt** | — | `stop_tilt` | — | — |

### Design Decisions

1. **Position entity** gets full TX/RX (entity selector + action script + RX listener) because position is continuous state (0-100).
2. **Tilt position entity** gets full TX/RX for the same reason.
3. **Open/Close/Stop** are command-only actions (no continuous state to sync), so they only get action script overrides. The cover state (open/closed/opening/closing) is derived from the position.
4. **No switch entity** for open/close — unlike fan's power switch, cover open/close is position-based. Position 0 = closed, position > 0 = open.

## Config Flow Schema

### Basic Settings

| Field | Required | Default | Type | Description |
|-------|:--------:|---------|------|-------------|
| `name` | Yes | — | text | Friendly name |
| `device_class` | No | — | select | Cover device class (blind, shade, curtain, etc.) |
| `enable_tilt` | No | false | boolean | Enable tilt position control |

### Entity Selectors (TX/RX)

| Field | Required | Type | Domain Filter | Description |
|-------|:--------:|------|---------------|-------------|
| `position_entity` | No | entity | `input_number`, `number` | Position entity for TX/RX (0-100) |
| `tilt_position_entity` | No | entity | `input_number`, `number` | Tilt position entity for TX/RX (0-100) |

### Action Script Overrides

| Field | Required | Type | Variable | Description |
|-------|:--------:|------|----------|-------------|
| `set_position` | No | action | `{{ position }}` | Override for position changes |
| `set_tilt_position` | No | action | `{{ tilt_position }}` | Override for tilt position changes |
| `open_cover` | No | action | — | Override for open command |
| `close_cover` | No | action | — | Override for close command |
| `stop_cover` | No | action | — | Override for stop command |
| `open_tilt` | No | action | — | Override for open tilt command |
| `close_tilt` | No | action | — | Override for close tilt command |
| `stop_tilt` | No | action | — | Override for stop tilt command |

## State Derivation

The cover state is derived from position:

```python
@property
def is_closed(self) -> bool | None:
    if self._attr_current_cover_position is not None:
        return self._attr_current_cover_position == 0
    return None

@property
def is_opening(self) -> bool | None:
    return self._is_opening

@property
def is_closing(self) -> bool | None:
    return self._is_closing
```

When `open_cover` is called:
1. Set `_is_opening = True`, write state
2. TX: action script or set position to 100
3. When position entity updates via RX, `_is_opening = False`

When `close_cover` is called:
1. Set `_is_closing = True`, write state
2. TX: action script or set position to 0
3. When position entity updates via RX, `_is_closing = False`

When `stop_cover` is called:
1. Set `_is_opening = False`, `_is_closing = False`
2. TX: fire action script (no default position to set)

## File Structure

```
woow_cover_entity/
  custom_components/woow_cover_entity/
    __init__.py          # Integration setup, entry load/unload
    config_flow.py       # Config flow + options flow (SchemaConfigFlowHandler)
    const.py             # Domain, platform, and configuration constants
    cover.py             # SimpleCover entity with TX/RX support
    manifest.json        # Integration metadata
    strings.json         # UI labels and descriptions
  tests/
    __init__.py
    test_simple_cover.py        # Core cover operations
    test_entity_aggregation.py  # TX/RX entity selectors, RX listeners, action scripts
    test_options_flow.py        # Config entry, options flow, config flow
  docs/
    QUICKSTART.md        # Step-by-step demo setup
  example_configuration.yaml    # Helper entities for testing
  pyproject.toml         # pytest configuration
  .gitignore
  README.md
  DESIGN.md
  WORKFLOW.md
```

## SimpleCover Entity Class

```
class SimpleCover(CoverEntity, RestoreEntity):
    _attr_should_poll = False

    # State
    _attr_current_cover_position: int | None = None
    _attr_current_cover_tilt_position: int | None = None
    _is_opening: bool = False
    _is_closing: bool = False

    # TX/RX
    _position_entity_id: str | None
    _tilt_position_entity_id: str | None

    # Action scripts
    _set_position_script: Script | None
    _set_tilt_position_script: Script | None
    _open_cover_script: Script | None
    _close_cover_script: Script | None
    _stop_cover_script: Script | None
    _open_tilt_script: Script | None
    _close_tilt_script: Script | None
    _stop_tilt_script: Script | None
```

### Supported Features Logic

```python
features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

if position_entity or set_position_action:
    features |= CoverEntityFeature.SET_POSITION

if stop_cover_action:
    features |= CoverEntityFeature.STOP

if enable_tilt:
    features |= CoverEntityFeature.OPEN_TILT | CoverEntityFeature.CLOSE_TILT
    if tilt_position_entity or set_tilt_position_action:
        features |= CoverEntityFeature.SET_TILT_POSITION
    if stop_tilt_action:
        features |= CoverEntityFeature.STOP_TILT
```

## Test Strategy

### test_simple_cover.py (~25 tests)
- Open/close/stop cover
- Set position (0, 50, 100)
- Open/close/stop tilt
- Set tilt position
- State derivation (is_closed, is_opening, is_closing)
- State restoration
- Device class configuration
- Supported features based on config

### test_entity_aggregation.py (~25 tests)
- TX: position entity selector sends value
- TX: tilt position entity selector sends value
- TX: action script override for position
- TX: action script override for tilt
- TX: action script for open/close/stop
- RX: position entity change updates cover
- RX: tilt entity change updates cover
- Initial state sync from entities
- TX priority: action script > entity selector

### test_options_flow.py (~10 tests)
- Config entry creation and setup
- Config entry unload
- Options flow update
- Config flow user step
- Full entry with all features
