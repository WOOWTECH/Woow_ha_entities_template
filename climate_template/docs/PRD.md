# Product Requirements Document (PRD)

## Climate Template — Home Assistant Custom Integration

**Version:** 1.4.0
**Repository:** [WOOWTECH/woow_climate_component](https://github.com/WOOWTECH/woow_climate_component)
**Status:** Stable Release
**Last Updated:** 2026-03-12

---

## 1. Overview

Climate Template is a Home Assistant custom integration that creates virtual climate (HVAC) entities by composing existing HA entities (sensors, switches, input helpers) into a fully functional thermostat. It bridges the gap between raw hardware entities and a unified climate control interface.

### Problem Statement

Home automation systems often expose heating/cooling hardware as separate, disconnected entities (temperature sensors, relay switches, mode selectors). Users need a way to combine these into a single climate entity with proper thermostat logic, without writing complex automations.

### Solution

Climate Template provides a config-flow-based integration that:
- Composes a `climate` entity from any combination of sensors, switches, and input helpers
- Implements a real thermostat control loop with configurable hysteresis (tolerance bands)
- Supports bidirectional entity synchronization (TX: send commands out; RX: receive state changes in)
- Persists state across HA restarts via `RestoreEntity`
- Supports all HA climate features: HVAC modes, fan modes, preset modes, swing modes, humidity control

---

## 2. Target Users

| User Type | Use Case |
|---|---|
| **Hardware integrators** | Compose climate entities from Modbus/KNX/DMX relay switches and temperature sensors |
| **Smart home builders** | Create virtual thermostats from Zigbee/Z-Wave temperature sensors and smart plugs |
| **System integrators** | Unify heterogeneous HVAC hardware behind a standard HA climate interface |
| **Advanced HA users** | Build custom climate control with input helpers for testing and simulation |

---

## 3. Functional Requirements

### 3.1 Core Thermostat Control

| Requirement | Description | Priority |
|---|---|---|
| **FR-01** | Temperature monitoring from any HA sensor entity (`sensor.*`) | P0 |
| **FR-02** | Heater control via any switchable entity (`input_boolean`, `switch`, `light`, etc.) | P0 |
| **FR-03** | Cooler control via separate switchable entity (optional) | P0 |
| **FR-04** | Hysteresis-based control loop with configurable cold/hot tolerance (default: 0.3) | P0 |
| **FR-05** | AC mode: inverted control where heater entity is used for cooling | P1 |
| **FR-06** | Heat/Cool dual-setpoint mode with independent high/low targets | P1 |
| **FR-07** | Graceful handling when temperature sensor becomes unavailable/unknown | P0 |

### 3.2 HVAC Modes

| Mode | Behavior |
|---|---|
| `off` | All outputs disabled |
| `heat` | Heater activates when current < target - cold_tolerance |
| `cool` | Cooler activates when current > target + hot_tolerance |
| `heat_cool` | Dual-setpoint: heater for low target, cooler for high target |
| `auto`, `dry`, `fan_only` | Passthrough modes (forwarded to external HVAC mode entity) |

Supported modes are user-configurable per instance.

### 3.3 TX/RX Entity Synchronization

**TX (Transmit):** When the user changes a setting on the climate entity, forward the value to an external entity.

**RX (Receive):** When an external entity changes state, sync that value back to the climate entity.

| Feature | TX Target Entity | RX Listener | Action Script Override |
|---|---|---|---|
| Target temperature | `input_number`, `number` | Yes | `set_temperature` |
| HVAC mode | `input_select`, `select` | Yes | `set_hvac_mode` |
| Fan mode | `input_select`, `select`, `fan` | Yes | `set_fan_mode` |
| Preset mode | `input_select`, `select` | Yes | `set_preset_mode` |
| Swing mode | `input_select`, `select`, `switch` | Yes | `set_swing_mode` |
| Swing horizontal | `input_select`, `select`, `switch` | Yes | `set_swing_horizontal_mode` |
| Target humidity | `input_number`, `number` | Yes | `set_humidity` |
| Current humidity | `sensor` (read-only) | Yes | N/A |

**Action Script Override:** For each TX feature, users can optionally configure a custom action script (sequence of HA service calls) instead of using entity-based TX.

### 3.4 Configuration

| Requirement | Description | Priority |
|---|---|---|
| **FR-10** | Config flow UI for initial setup (no YAML) | P0 |
| **FR-11** | Options flow for runtime reconfiguration without removing the entity | P0 |
| **FR-12** | Validation: reject missing temperature sensor, require at least heater or cooler | P0 |
| **FR-13** | Auto-remove `heat_cool` from available modes when no cooler is configured | P1 |
| **FR-14** | Configurable min/max temperature range and step size | P1 |
| **FR-15** | Configurable precision for temperature display | P2 |

### 3.5 State Persistence

| Requirement | Description | Priority |
|---|---|---|
| **FR-20** | Restore HVAC mode, target temperature, presets across HA restarts | P0 |
| **FR-21** | Phase 3 external sync overrides restored state (external entity is source of truth) | P0 |
| **FR-22** | Restore saved preset temperatures | P1 |

### 3.6 Multiple Instances

| Requirement | Description | Priority |
|---|---|---|
| **FR-30** | Support multiple independent climate entities via separate config entries | P0 |
| **FR-31** | Cooler-only instances (no heater) must work without crashes | P0 |
| **FR-32** | Each instance links to its heater/cooler device for HA device registry | P2 |

---

## 4. Non-Functional Requirements

| Requirement | Description | Target |
|---|---|---|
| **NFR-01** | Startup time: entity must be functional within 2s of HA platform setup | < 2s |
| **NFR-02** | Control loop latency: heater/cooler reaction to temperature change | < 500ms |
| **NFR-03** | No polling: all state updates are event-driven via `async_track_state_change_event` | Event-driven |
| **NFR-04** | Thread safety: temperature control uses `asyncio.Lock` to prevent race conditions | Mutex-protected |
| **NFR-05** | HA compatibility: minimum Home Assistant version | 2025.8.0 |
| **NFR-06** | HACS compatible: installable via HACS custom repository | Yes |
| **NFR-07** | No external dependencies: zero `requirements` in manifest | Zero deps |

---

## 5. Architecture

### 5.1 Component Structure

```
custom_components/climate_template/
├── __init__.py          # Entry setup/unload, config entry lifecycle
├── climate.py           # SimpleClimate entity (ClimateEntity + RestoreEntity)
├── config_flow.py       # SchemaConfigFlowHandler for UI configuration
├── const.py             # Constants and configuration keys
├── manifest.json        # Integration metadata
└── strings.json         # UI translation strings
```

### 5.2 Entity Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                  async_added_to_hass()                   │
│                                                          │
│  Phase 1: Register event listeners                       │
│    ├── Temperature sensor → _async_sensor_changed        │
│    ├── Heater switch → _async_switch_changed             │
│    ├── Cooler switch → _async_switch_changed             │
│    ├── Fan/Preset/Swing entities → mode changed          │
│    ├── HVAC mode entity → _async_hvac_mode_changed       │
│    ├── Target temp entity → _async_target_temp_changed   │
│    └── Humidity entity/sensor → humidity changed          │
│                                                          │
│  Phase 2: RestoreEntity                                  │
│    └── Restore previous HVAC mode, target temp, presets  │
│                                                          │
│  Phase 3: External entity sync (overrides Phase 2)       │
│    ├── Sync temperature from sensor                      │
│    ├── Sync HVAC mode from entity                        │
│    ├── Sync fan/preset/swing from entities                │
│    ├── Sync humidity from entity/sensor                   │
│    └── Initialize heater/cooler active state              │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Control Loop

```
Temperature change detected
        │
        ▼
   ┌────────────┐
   │ Sensor      │──unavailable──▶ No action (preserve last state)
   │ available?  │
   └─────┬──────┘
         │ yes
         ▼
   ┌─────────────────┐
   │ HVAC Mode?      │
   ├─────────────────┤
   │ OFF             │──▶ Turn off heater + cooler
   │ HEAT            │──▶ current < target - cold_tolerance → heater ON
   │                 │    current > target + hot_tolerance → heater OFF
   │ COOL            │──▶ current > target + hot_tolerance → cooler ON
   │                 │    current < target - cold_tolerance → cooler OFF
   │ HEAT_COOL       │──▶ current < target_low - tolerance → heater ON
   │                 │    current > target_high + tolerance → cooler ON
   └─────────────────┘
```

---

## 6. Test Coverage

### 6.1 Unit Tests (107 tests)

| Suite | Tests | Coverage |
|---|---|---|
| `test_simple_climate.py` | 20 | Core climate entity behavior |
| `test_entity_aggregation.py` | 26 | TX/RX entity sync, feature flags |
| `test_options_flow.py` | 21 | Config flow, options flow, validation |
| `test_temperature_change.py` | 16 | Thermostat control loop, tolerance bands |
| `test_temperature_unit.py` | 2 | Temperature unit handling |
| `test_t4_bug.py` | 2 | Regression: T4 cooling hvac_action bug |

### 6.2 E2E Live Tests (80 tests)

Executed against a real Home Assistant instance with 13 test helper entities.

| Group | Tests | What it validates |
|---|---|---|
| Config Flow | 7 | Entry creation, field validation, duplicate rejection |
| Heating Mode | 10 | Thermostat activation/deactivation within tolerance bands |
| Cooling Mode | 5 | Cooler entity control with temperature thresholds |
| Heat/Cool Mode | 7 | Dual-setpoint with both heater and cooler |
| AC Mode | 4 | Inverted control (heater entity used for cooling) |
| TX/RX Entity Sync | 12 | Bidirectional state sync for all mode entities |
| RX Control Loop | 4 | External state changes triggering thermostat logic |
| Sensor Unavailable | 4 | Graceful degradation when sensor goes unavailable |
| Preset Save/Restore | 4 | Temperature save/restore across preset switches |
| Options Flow | 7 | Runtime config updates without entity removal |
| Rapid Changes | 3 | Race condition stress testing |
| State Restoration | 5 | RestoreEntity across config entry reloads |
| Heat/Cool Validation | 3 | Auto-removal of heat_cool without cooler |
| Multiple Instances | 4 | Independent coexisting climate entities |

**Total: 187/187 tests passing**

---

## 7. Known Limitations

| Limitation | Description | Workaround |
|---|---|---|
| No scheduling | No built-in time-based scheduling | Use HA automations |
| Single sensor | Only one temperature sensor per instance | Use template sensor to combine |
| No PID control | Bang-bang control only (on/off with hysteresis) | Acceptable for most HVAC use cases |
| No energy tracking | Does not report energy consumption | Use HA energy dashboard with switch entities |

---

## 8. Installation

### Via HACS (Recommended)

1. Add `https://github.com/WOOWTECH/woow_climate_component` as a custom repository in HACS
2. Search for "Climate Template" and install
3. Restart Home Assistant
4. Add integration via Settings > Devices & Services > Add Integration > Climate Template

### Manual

1. Copy `custom_components/climate_template/` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via Settings > Devices & Services

---

## 9. Configuration Reference

### Required Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Display name for the climate entity |
| `temperature_sensor` | entity_id | Temperature sensor entity (e.g., `sensor.room_temp`) |
| `heater` | entity_id | Heater switch entity (optional if cooler is set) |

### Optional Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `cooler` | entity_id | — | Cooler switch entity |
| `ac_mode` | boolean | `false` | Use heater entity for cooling (inverted) |
| `min_temp` | float | 7.0 | Minimum settable temperature |
| `max_temp` | float | 35.0 | Maximum settable temperature |
| `temp_step` | float | 0.5 | Temperature adjustment step |
| `cold_tolerance` | float | 0.3 | Degrees below target before heating |
| `hot_tolerance` | float | 0.3 | Degrees above target before cooling |
| `hvac_modes` | list | `[off, heat]` | Available HVAC modes |
| `fan_modes` | list | — | Available fan modes |
| `preset_modes` | list | — | Available preset modes |
| `swing_modes` | list | — | Available swing modes |
| `hvac_mode_entity` | entity_id | — | External entity for HVAC mode sync |
| `fan_mode_entity` | entity_id | — | External entity for fan mode sync |
| `preset_mode_entity` | entity_id | — | External entity for preset mode sync |
| `swing_mode_entity` | entity_id | — | External entity for swing mode sync |
| `humidity_entity` | entity_id | — | External entity for humidity sync |
| `humidity_sensor` | entity_id | — | Humidity sensor entity |
| `target_temperature_entity` | entity_id | — | External entity for target temp sync |

---

## 10. Release History

| Version | Date | Changes |
|---|---|---|
| 1.4.0 | 2026-03-12 | Fix 5 critical bugs (cooler-only crash, Phase 3 sync), add E2E test suite |
| 1.3.0 | — | Config flow UI, code review fixes, CI workflow |
| 1.2.0 | — | TX/RX entity sync, action script support |
| 1.0.0 | — | Initial stable release with basic thermostat control |
