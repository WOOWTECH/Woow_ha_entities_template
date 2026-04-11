# Product Requirements Document (PRD)
## Template Light Composer for Home Assistant

**Document Version:** 2.0
**Date:** March 2026
**Product Owner:** WOOWTECH
**Status:** v1.0.0 - Verified & Production-Ready

---

## 1. Executive Summary

### 1.1 Product Vision
Template Light Composer is a Home Assistant custom integration that creates virtual light entities by composing state, brightness, and color temperature from existing HA entities through Jinja2 templates, with configurable actions for bidirectional control.

### 1.2 Problem Statement
Home Assistant users need to:
- Represent complex physical lighting systems (e.g., KNX, DMX, Modbus) as standard HA light entities
- Map non-light entities (input_boolean, input_number, sensors) into the light entity interface
- Achieve bidirectional control: reading state from one entity while sending commands via another
- Avoid writing YAML template lights, which are error-prone and hard to maintain

### 1.3 Solution
A config-flow-based integration with a 3-step setup wizard that:
1. Maps source entities to light attributes (state, brightness, color temperature)
2. Configures actions (scripts, services, scenes) for light control commands
3. Provides advanced options (transitions, icons, availability templates)

### 1.4 Release Status
**v1.0.0 - Production Ready**
- 27/27 automated tests passing
- 5 critical/high bugs found and fixed during testing
- Zero errors in HA logs during test execution
- Verified on Home Assistant 2025.4.2

---

## 2. Target Users

### 2.1 Primary Users
- **System Integrators**: Building HA installations over KNX/DMX/Modbus where physical lights are represented by helper entities
- **Advanced HA Users**: Needing template-based light entities without writing YAML

### 2.2 Use Cases
| Use Case | Description |
|----------|-------------|
| KNX Light Mapping | Map `input_boolean` (on/off) + `input_number` (brightness 0-255) + `input_number` (color temp 2500-6500K) into a standard light entity |
| DMX Channel Control | Create a light entity that reads DMX channel values and sends set_value commands to DMX channels |
| Scene-Based Lighting | Light entity that activates scenes for turn_on/turn_off |
| Sensor-Based Virtual Light | Light whose state and brightness derive from sensor readings |

---

## 3. Functional Requirements

### 3.1 Config Flow (3-Step Wizard)

#### Step 1: Basic Configuration & Templates
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | - | Light entity name (becomes unique_id) |
| `state_entity` | entity selector | No | - | Source entity for on/off state |
| `state_attribute` | string | No | "state" | Attribute to read from state entity |
| `state_operator` | select | No | "==" | Comparison operator (>, <, >=, <=, ==, !=) |
| `state_threshold` | float | No | 0 | Threshold for operator comparison |
| `level_entity` | entity selector | No | - | Source entity for brightness (0-255) |
| `level_attribute` | string | No | "state" | Attribute to read from level entity |
| `level_unit` | string | No | - | Unit of measurement label |
| `temperature_entity` | entity selector | No | - | Source entity for color temperature |
| `temperature_attribute` | string | No | "state" | Attribute to read from temperature entity |
| `min_temperature` | int | No | 2500 | Minimum color temperature (Kelvin) |
| `max_temperature` | int | No | 6500 | Maximum color temperature (Kelvin) |

**Validation:**
- Name must be non-empty
- Entities are checked against HA entity registry
- `min_temperature` must be less than `max_temperature`
- Unique ID generated from name (lowercased, underscored)

#### Step 2: Actions Configuration
For each of the 4 action slots, two fields are shown:

| Action Slot | Fields | Description |
|-------------|--------|-------------|
| Turn On | type + target | Called when `light.turn_on` is invoked |
| Turn Off | type + target | Called when `light.turn_off` is invoked |
| Set Brightness | type + target | Called when brightness parameter is passed to `light.turn_on` |
| Set Temperature | type + target | Called when color_temp_kelvin parameter is passed to `light.turn_on` |

**Action Types:**
| Type | Target Format | Example |
|------|--------------|---------|
| `script` | `script.<name>` | `script.turn_on_living_room` |
| `service` | `<domain>.<service>` | `input_boolean.turn_on`, `input_number.set_value` |
| `scene` | `scene.<name>` | `scene.living_room_bright` |

**Available Services (auto-discovered):**
- `light.turn_on`, `light.turn_off`, `light.toggle`
- `input_number.set_value`
- `input_select.select_option`
- `input_boolean.turn_on`, `input_boolean.turn_off`, `input_boolean.toggle`

#### Step 3: Advanced Options
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `supports_transition` | boolean | True | Enable `LightEntityFeature.TRANSITION` |
| `icon` | icon selector | `mdi:lightbulb` | MDI icon for the entity |
| `device_class` | string | - | HA device class |
| `availability_template` | string (Jinja2) | - | Custom availability template |

### 3.2 Light Entity Behavior

#### Color Modes (auto-detected from configuration)
| Mode | Condition | Features |
|------|-----------|----------|
| `COLOR_TEMP` | `temperature_entity` configured | Brightness + color temperature control |
| `BRIGHTNESS` | Only `level_entity` configured | Brightness-only control |
| `ONOFF` | Neither level nor temperature configured | On/off toggle only |

#### Reactive State Tracking
- Uses `async_track_state_change_event` to subscribe to source entity changes
- Template re-evaluation triggers on any tracked entity state change
- State updates propagate to HA within one event loop cycle

#### Template Auto-Generation
Templates are automatically generated from the configured entities:

```jinja2
# State template (for input_boolean)
{{ states('input_boolean.light_state') == 'on' }}

# State template (with operator/threshold)
{{ state_attr('entity', 'attribute')|int(0) > 10 }}

# Level template
{{ states('input_number.brightness')|int(0) }}

# Temperature template
{{ states('input_number.color_temp')|int(0) }}
```

#### Action Execution Logic

**`light.turn_on` call flow:**
1. If `brightness` kwarg present AND `set_level_action` configured: execute set_level_action
2. If `color_temp_kelvin` kwarg present AND `set_temperature_action` configured: execute set_temperature_action
3. Always execute `turn_on_action` (ensures light actually turns on)

**`light.turn_off` call flow:**
1. Execute `turn_off_action`

**Auto-population in `_execute_action`:**
- `entity_id`: Inferred from action role (turn_on/off -> state_entity, set_level -> level_entity, set_temperature -> temperature_entity)
- `value`: For `input_number.set_value` service, auto-populated from brightness or color_temp_kelvin kwargs

#### State Restoration
- Implements `RestoreEntity` for persistence across HA restarts
- Restores: `is_on`, `brightness`, `color_temp_kelvin`

#### Extra State Attributes Exposed
- `level_entity`: Source entity ID for brightness
- `state_entity`: Source entity ID for on/off state
- `temperature_entity`: Source entity ID for color temperature
- `level_unit`: Custom unit label (if configured)

### 3.3 Error Handling
| Scenario | Behavior |
|----------|----------|
| Template rendering fails (`TemplateError`) | Logged, previous value retained |
| Source entity unavailable | Availability template can detect; defaults to available |
| Service call fails (`ServiceNotFound`, `HomeAssistantError`) | Logged, entity state not updated |
| Config entry removed while DOMAIN not in hass.data | Guarded with `if DOMAIN in hass.data` |

---

## 4. Technical Architecture

### 4.1 File Structure
| File | Purpose |
|------|---------|
| `__init__.py` | Integration lifecycle (setup, unload, reload, remove) |
| `config_flow.py` | 3-step config flow wizard (`TemplateComposerConfigFlow`) |
| `light.py` | Light entity implementation (`TemplateComposerLight`) |
| `const.py` | Constants, configuration keys, defaults |
| `manifest.json` | Integration metadata |

### 4.2 Class Hierarchy
```
TemplateComposerLight
  ├── extends LightEntity (HA light platform)
  └── extends RestoreEntity (state persistence)

TemplateComposerConfigFlow
  └── extends ConfigFlow (HA config entry flow)
```

### 4.3 Data Flow

```
Source Entity Change
       ↓
async_track_state_change_event
       ↓
_async_state_changed (callback)
       ↓
_async_update_state (async task)
       ↓
┌─ Evaluate availability_template → _attr_available
├─ Evaluate state_template → _attr_is_on
├─ Evaluate level_template → _attr_brightness (clamped 0-255)
└─ Evaluate temperature_template → _attr_color_temp_kelvin (clamped min-max)
       ↓
async_write_ha_state()
       ↓
HA UI Updated
```

### 4.4 Dependencies
- **Home Assistant Core**: 2024.1+
- **Python**: 3.11+
- **External packages**: None (`requirements: []`)
- **HA Dependencies**: `light` platform only

### 4.5 Integration Metadata
```json
{
  "domain": "template_light_composer",
  "name": "Template Light Composer",
  "version": "1.0.0",
  "config_flow": true,
  "iot_class": "calculated",
  "codeowners": ["@WOOWTECH"]
}
```

---

## 5. Quality Assurance

### 5.1 Test Results (v1.0.0)

**Environment:** Home Assistant 2025.4.2 on Linux (podman container)
**Method:** Automated REST API test suite, 27 test cases
**Result:** 27/27 PASS

| Phase | Tests | Result |
|-------|-------|--------|
| Basic Functionality | T01-T07 (7 tests) | 7/7 PASS |
| Edge Cases | T10a-T18 (7 tests) | 7/7 PASS |
| Turn On with Parameters | T19-T21 (4 tests) | 4/4 PASS |
| Integration Lifecycle | T22-T24 (3 tests) | 3/3 PASS |
| Action Edge Cases | T25-T30 (6 tests) | 6/6 PASS |

#### Test Case Details

**Basic Functionality:**
- T01: Entity exists with correct type
- T02: Attributes correct (color_temp mode, kelvin range 2500-6500)
- T03: State tracks input_boolean reactively
- T04: Brightness tracks input_number reactively
- T05: Color temp tracks input_number reactively
- T06: `light.turn_on` service fires turn-on action
- T07: `light.turn_off` service fires turn-off action

**Edge Cases:**
- T10a/T10b: Brightness boundary values (0 and 255)
- T11a/T11b: Color temp boundary values (2500K and 6500K)
- T16a: Rapid state changes (10 toggles, final state correct)
- T16b: Rapid brightness sweep (sequential changes converge)
- T18: Extra state attributes exposed correctly

**Turn On with Parameters:**
- T19: `light.turn_on` with `brightness` sets brightness AND turns on
- T20: `light.turn_on` with `color_temp_kelvin` sets color_temp AND turns on
- T20b: `light.turn_on` with both parameters fires all three actions
- T21: Turn off/on cycle preserves brightness value

**Integration Lifecycle:**
- T22: Integration reload - entity survives
- T23: State restoration after reload
- T24: Entity functional post-reload

**Action Edge Cases:**
- T25: Turn on when already on (idempotent)
- T26: Turn off when already off (idempotent)
- T27: Set brightness while off, verify on turn-on
- T28: Color temp consistent through on/off cycle
- T29: TRANSITION feature flag supported
- T30: Color mode is color_temp when ON

### 5.2 Bugs Found & Fixed

| # | Severity | Bug | Root Cause | Fix |
|---|----------|-----|------------|-----|
| 1 | Critical | Config flow action targets not collected | Progressive disclosure required multiple form round-trips; targets never shown | Rewrote `async_step_actions` to show type+target together |
| 2 | Critical | Missing entity_id in service calls | `_execute_action` didn't pass entity_id to services | Added `_get_target_entity_for_action()` auto-population |
| 3 | High | Missing value for `input_number.set_value` | No auto-population of the `value` parameter | Added auto-populate from brightness/color_temp kwargs |
| 4 | High | Duplicate kwargs TypeError | Explicit `brightness=brightness` conflicted with `**kwargs` | Removed explicit kwargs, rely on `**kwargs` passthrough |
| 5 | High | `turn_on` with params doesn't turn on | `handled_by_specialized` guard skipped turn_on action | Always call turn_on action regardless of specialized actions |

### 5.3 HA Logs
- Zero errors from `template_light_composer` during all 27 tests
- Zero warnings specific to the integration
- Only standard "custom integration not tested" notice (expected)

### 5.4 Known Limitations
1. Script and scene action types accepted by config flow but not runtime-tested with live entities
2. Multi-instance behavior (multiple config entries) not tested
3. No long-term stability test (hours/days of continuous operation)
4. `availability_template` not stress-tested with complex Jinja2 expressions
5. RGB color mode not supported (only color_temp, brightness, onoff)
6. No config flow options flow for editing existing entries (requires delete + recreate)

---

## 6. Installation

### 6.1 Manual Installation
1. Copy `template_light_composer/` directory to `<HA config>/custom_components/`
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search for "Template Light Composer"
5. Follow the 3-step wizard

### 6.2 Prerequisites
- Helper entities must already exist before configuring the integration
- Example helpers needed for a full-featured light:
  - `input_boolean` for on/off state
  - `input_number` (0-255) for brightness
  - `input_number` (2500-6500) for color temperature

---

## 7. Roadmap

### v1.1 (Planned)
- Options flow for editing existing config entries
- Translations (`strings.json`) for multi-language support
- HACS repository listing

### v1.2 (Planned)
- RGB color mode support
- Effect support
- Parameter mapping UI in config flow (template-based parameter values)
- Import/export configuration

### v2.0 (Future)
- Multi-entity grouping (combine multiple source lights)
- Template preview in config flow
- Diagnostics platform for debugging
