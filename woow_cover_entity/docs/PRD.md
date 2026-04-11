# Product Requirements Document: WoowTech Cover Entity

**Version:** 1.0.0
**Domain:** `woow_cover_entity`
**Platform:** Home Assistant Custom Component
**Repository:** https://github.com/WOOWTECH/woow_cover_entity

---

## 1. Overview

WoowTech Cover Entity is a Home Assistant custom integration that creates virtual cover entities (blinds, shutters, curtains, etc.) with bidirectional state synchronization, action script overrides, and time-based position estimation. It serves as a flexible bridge between Home Assistant's cover UI controls and arbitrary backend entities or automation scripts.

### 1.1 Problem Statement

Standard Home Assistant cover integrations are tightly coupled to specific hardware or protocols (e.g., Z-Wave, KNX, MQTT). Users who need to:

- Control covers through intermediary entities (e.g., Modbus registers exposed as `input_number`)
- Execute custom action scripts when cover operations are triggered
- Estimate cover position based on travel time (for motors without position feedback)
- Combine multiple control strategies in a single cover entity

...have no built-in solution. They must resort to complex template covers with limited functionality and no UI-based configuration.

### 1.2 Solution

A configurable cover entity that decouples the **cover UI layer** from the **control layer**, supporting:

- **TX (Transmit):** Cover card operations (open/close/set position) propagate to target entities or scripts
- **RX (Receive):** External entity state changes update the cover's displayed position
- **Time-based estimation:** Position calculated from configurable open/close travel times
- **Full UI configuration:** Config flow and options flow, no YAML required

---

## 2. Target Users

| User Type | Use Case |
|-----------|----------|
| **System Integrators** | Bridging KNX/Modbus/RS485 cover motors to HA via intermediary entities |
| **DIY Home Automators** | Creating virtual covers backed by smart relays or ESPHome devices |
| **Installers** | Deploying time-based position estimation for motors without encoder feedback |
| **Advanced Users** | Overriding default cover behavior with custom action scripts |

---

## 3. Functional Requirements

### 3.1 Core Cover Operations

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Create cover entities via UI config flow | P0 |
| FR-02 | Support open, close, stop cover operations | P0 |
| FR-03 | Support set_cover_position (0-100) | P0 |
| FR-04 | Report cover state: open, closed, opening, closing, unknown | P0 |
| FR-05 | Report current_position attribute (0-100, integer) | P0 |
| FR-06 | Persist state across HA restarts via RestoreEntity | P0 |
| FR-07 | Support options flow for runtime reconfiguration | P1 |
| FR-08 | Support all 10 HA cover device classes | P1 |

### 3.2 Tilt Control

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10 | Optional tilt support (enable_tilt toggle) | P1 |
| FR-11 | Support open_cover_tilt, close_cover_tilt, stop_cover_tilt | P1 |
| FR-12 | Support set_cover_tilt_position (0-100) | P1 |
| FR-13 | Report current_tilt_position attribute | P1 |

### 3.3 TX/RX Entity Selector (Bidirectional Sync)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-20 | **TX - Position Entity:** When cover position changes, write the value to a target `input_number` or `number` entity | P0 |
| FR-21 | **RX - Position Entity:** When the target entity's state changes externally, update the cover's displayed position | P0 |
| FR-22 | **TX - Tilt Entity:** Same as FR-20 for tilt position | P1 |
| FR-23 | **RX - Tilt Entity:** Same as FR-21 for tilt position | P1 |
| FR-24 | Initial state sync on entity load from target entity's current value | P0 |
| FR-25 | Ignore `unavailable` and `unknown` entity states (retain last known position) | P0 |
| FR-26 | Reject out-of-range values (< 0 or > 100) from RX entity | P1 |
| FR-27 | Truncate float values to integer for position | P2 |

### 3.4 Action Script Overrides

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-30 | Override `open_cover` with custom action script | P1 |
| FR-31 | Override `close_cover` with custom action script | P1 |
| FR-32 | Override `stop_cover` with custom action script | P1 |
| FR-33 | Override `set_cover_position` with custom action script (receives `{{ position }}` template variable) | P1 |
| FR-34 | Override `open_tilt`, `close_tilt`, `stop_tilt` with action scripts | P2 |
| FR-35 | Override `set_cover_tilt_position` with action script (receives `{{ tilt_position }}` template variable) | P2 |

### 3.5 Time-Based Position Estimation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-40 | Calculate position based on configurable `open_time` (seconds to fully open) | P1 |
| FR-41 | Calculate position based on configurable `close_time` (seconds to fully close) | P1 |
| FR-42 | Support asymmetric open/close times | P1 |
| FR-43 | 1-second tick interval for position updates | P1 |
| FR-44 | Auto-enable `SET_POSITION` and `STOP` features when time mode is active | P1 |
| FR-45 | `stop_cover` freezes position at current estimated value | P1 |
| FR-46 | `set_cover_position` targets a specific position and auto-stops on arrival | P1 |
| FR-47 | Time-based tilt estimation with `tilt_open_time` / `tilt_close_time` | P2 |
| FR-48 | Auto-enable `SET_TILT_POSITION` and `STOP_TILT` for tilt time mode | P2 |

### 3.6 Config Flow Validation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-50 | `open_time` and `close_time` must be configured as a pair | P1 |
| FR-51 | `tilt_open_time` and `tilt_close_time` must be configured as a pair | P1 |
| FR-52 | Display user-friendly error messages for validation failures | P1 |

---

## 4. Supported Features Matrix

The cover entity dynamically enables HA `CoverEntityFeature` flags based on configuration:

| Feature | Condition |
|---------|-----------|
| `OPEN` | Always |
| `CLOSE` | Always |
| `SET_POSITION` | `position_entity` OR `set_position` script OR time-based mode |
| `STOP` | `stop_cover` script OR time-based mode |
| `OPEN_TILT` | `enable_tilt = true` |
| `CLOSE_TILT` | `enable_tilt = true` |
| `SET_TILT_POSITION` | `tilt_position_entity` OR `set_tilt_position` script OR tilt time-based mode |
| `STOP_TILT` | `stop_tilt` script OR tilt time-based mode |

---

## 5. Configuration Schema

### 5.1 Config Flow Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Text | Yes | Entity display name |
| `device_class` | Select | No | One of: awning, blind, curtain, damper, door, garage, gate, shade, shutter, window |
| `enable_tilt` | Boolean | No | Enable tilt control (default: false) |
| `position_entity` | Entity Selector | No | Target `input_number`/`number` entity for TX/RX position sync |
| `tilt_position_entity` | Entity Selector | No | Target entity for TX/RX tilt sync |
| `open_time` | Number (1-300s) | No | Time to fully open (enables time-based mode) |
| `close_time` | Number (1-300s) | No | Time to fully close (must pair with open_time) |
| `tilt_open_time` | Number (0.5-60s) | No | Time to fully open tilt |
| `tilt_close_time` | Number (0.5-60s) | No | Time to fully close tilt (must pair with tilt_open_time) |
| `set_position` | Action | No | Custom script for set_position (template var: `{{ position }}`) |
| `set_tilt_position` | Action | No | Custom script for set_tilt_position (template var: `{{ tilt_position }}`) |
| `open_cover` | Action | No | Custom script override for open |
| `close_cover` | Action | No | Custom script override for close |
| `stop_cover` | Action | No | Custom script override for stop |
| `open_tilt` | Action | No | Custom script override for open tilt |
| `close_tilt` | Action | No | Custom script override for close tilt |
| `stop_tilt` | Action | No | Custom script override for stop tilt |

### 5.2 Options Flow

All fields from the config flow (except `name`) are available in the options flow for runtime reconfiguration. Changes trigger entity reload via `async_update_options` listener.

---

## 6. Architecture

### 6.1 Data Flow

```
┌─────────────────┐         TX: open/close/set_position
│  HA Cover Card   │ ──────────────────────────────────────┐
│  (Lovelace UI)   │                                       │
└────────┬────────┘                                       ▼
         │                                    ┌───────────────────┐
         │ state/attributes                   │  Target Entity    │
         │                                    │  (input_number)   │
         ▲                                    │  OR Action Script │
┌────────┴────────┐                           └────────┬──────────┘
│  SimpleCover     │         RX: state_changed         │
│  Entity          │ ◄─────────────────────────────────┘
│                  │
│  Position: 75    │         Time-Based Estimation
│  Tilt: 50        │ ◄──── 1s tick timer ──── target reached? ──► stop
│  State: open     │
└─────────────────┘
```

### 6.2 State Priority (async_added_to_hass)

1. **RestoreEntity** (lowest) - Restores last known position from HA state store
2. **RX Entity Sync** (highest) - Reads current value from position/tilt target entity, overriding restored state

### 6.3 File Structure

```
custom_components/woow_cover_entity/
├── __init__.py          # Entry setup, options listener, platform forwarding
├── config_flow.py       # SchemaConfigFlowHandler with validation
├── const.py             # Domain, platform, and config key constants
├── cover.py             # SimpleCover entity (CoverEntity + RestoreEntity)
├── manifest.json        # Integration metadata
└── strings.json         # UI labels and error messages

tests/
└── test_simple_cover.py # pytest-homeassistant-custom-component tests
```

---

## 7. Non-Functional Requirements

| ID | Requirement | Detail |
|----|-------------|--------|
| NFR-01 | No polling | Entity uses event-driven state updates (`_attr_should_poll = False`) |
| NFR-02 | No external dependencies | `requirements: []` in manifest |
| NFR-03 | HA version compatibility | Requires Home Assistant 2024.1+ (SchemaFlowError, CoverEntityFeature) |
| NFR-04 | IoT class | `calculated` - state is derived from configuration and events |
| NFR-05 | Clean unload | All timers and listeners are canceled on entity removal |
| NFR-06 | Multiple instances | Supports unlimited concurrent cover entities with independent state |

---

## 8. Testing

### 8.1 Unit Tests

Located in `tests/test_simple_cover.py`, using `pytest-homeassistant-custom-component`:

- Basic open/close/state transitions
- Set position operations
- Tilt operations
- Feature flag verification

### 8.2 Integration Tests (Live HA)

93 assertions across 15 test suites on a live Home Assistant instance:

| Suite | Coverage |
|-------|----------|
| 1. Basic Cover | Create, open, close, features |
| 2. TX/RX Sync | Bidirectional position sync with real input_number |
| 3. Tilt Control | Open/close/set tilt, TX/RX tilt sync |
| 4. Time-Based Position | Timer accuracy, stop, set_position |
| 5. Unavailable States | Ignore unavailable/unknown entities, recovery |
| 6. Options Flow | Runtime reconfiguration |
| 7. Multiple Entities | 3 concurrent covers, independent state |
| 8. Config Validation | Time pair completeness enforcement |
| 9. Entity Removal | Clean unload, no orphaned state |
| 10. State Restoration | RestoreEntity persistence |
| 11. Rapid Sequences | Open→close, stop→reverse, spam protection |
| 12. Boundary Values | 0, 100, negative, >100, non-numeric, float |
| 13. Device Classes | All 10 cover device classes |
| 14. Tilt Estimation | Time-based tilt with stop |
| 15. Asymmetric Times | Different open/close speeds |

---

## 9. Installation

### HACS (Recommended)

1. Add `https://github.com/WOOWTECH/woow_cover_entity` as a custom repository in HACS
2. Install "WoowTech Cover Entity"
3. Restart Home Assistant
4. Add integration via Settings > Devices & Services > Add Integration > "WoowTech Cover Entity"

### Manual

1. Copy `custom_components/woow_cover_entity/` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via UI

---

## 10. Example Use Cases

### 10.1 KNX Blind with Modbus Position Feedback

```
Position Entity: input_number.knx_blind_position  (synced via KNX integration)
Open Time: 45 seconds
Close Time: 40 seconds
Device Class: blind
Enable Tilt: true
Tilt Position Entity: input_number.knx_blind_tilt
```

### 10.2 ESPHome Relay-Controlled Curtain

```
Open Cover Action:  switch.turn_on → switch.curtain_relay_open
Close Cover Action: switch.turn_on → switch.curtain_relay_close
Stop Cover Action:  switch.turn_off → switch.curtain_relay_open + switch.curtain_relay_close
Open Time: 30 seconds
Close Time: 30 seconds
Device Class: curtain
```

### 10.3 Virtual Cover for Testing

```
Name: Test Cover
(no position entity, no scripts, no time)
→ Creates a simple open/close cover with instant state changes
```

---

## 11. Changelog

### v1.0.0 (2025-01-XX)

- Initial release
- Full TX/RX bidirectional sync with entity selectors
- Action script overrides for all cover operations
- Time-based position and tilt estimation
- Config flow with time pair validation
- Support for all 10 cover device classes
- RestoreEntity state persistence
- Options flow for runtime reconfiguration

### v1.0.1 (Post-Review Fixes)

- Fix dead conditional on tilt position initialization
- Fix state restoration order (restore before entity sync)
- Remove unused `hass.data` storage
- Add tilt movement direction flags
- Add config flow validation for time pair completeness
- Fix manifest URLs to WOOWTECH organization
- Fix `test_set_position_50` test accuracy
