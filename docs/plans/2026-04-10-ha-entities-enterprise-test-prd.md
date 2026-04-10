# PRD: HA Custom Components Enterprise-Grade Test Plan

## 1. Overview

Comprehensive, enterprise-grade test plan for 4 Home Assistant custom component packages:
- **woow_fan_entity** — Fan template with TX/RX, preset modes, oscillation, direction
- **template_light_composer** — Light template with brightness, color temp, state templates
- **climate_template** — Climate with heater/cooler dual control, temperature sensor tracking
- **woow_cover_entity** — Cover with time-based position estimation, tilt support

### Target Instance
- **URL**: `http://localhost:18125`
- **Auth**: admin/admin
- **Container**: podman `homeassistant`

### Test Entities
| Entity ID | Package | Features |
|-----------|---------|----------|
| `fan.test_woowfan` | woow_fan_entity | speed, preset, oscillation, direction |
| `light.test_light_full` | template_light_composer | brightness, color_temp, on/off |
| `climate.test_climate` | climate_template | heat/cool/heat_cool, temperature |
| `cover.test_cover` | woow_cover_entity | position, tilt (time-based) |

---

## 2. Test Strategy

### 2.1 Test Layers

| Layer | Method | Scope |
|-------|--------|-------|
| **L1: API Unit** | REST API (`/api/services/...`) | Service calls, state reads, attribute verification |
| **L2: API Edge** | REST API with boundary values | Min/max, invalid types, missing params, concurrent calls |
| **L3: API Stress** | Rapid sequential API calls | Rate-limit behavior, state consistency under load |
| **L4: Browser UI** | Chrome DevTools MCP | Click controls, verify UI reflects state, config flow |
| **L5: Persistence** | API + container restart | RestoreEntity, state survival across HA restarts |
| **L6: Integration** | Cross-entity interactions | Helper entities (input_number, input_boolean) react correctly |

### 2.2 Test Rounds

| Round | Focus | Method |
|-------|-------|--------|
| **Round 1** | Functional — All service calls + state verification | API |
| **Round 2** | Edge cases — Boundaries, invalid inputs, error handling | API |
| **Round 3** | Browser UI — Visual verification, config flow, controls | Chrome DevTools |
| **Round 4** | Persistence + Stress — Restart survival, rapid calls | API + podman |

---

## 3. Test Cases Per Entity

### 3.1 Fan (`fan.test_woowfan`)

#### Functional (Round 1)
- F-FAN-001: turn_on → state=on, percentage > 0
- F-FAN-002: turn_off → state=off, percentage=0
- F-FAN-003: set_percentage(50) → percentage=50
- F-FAN-004: set_percentage(100) → percentage=100
- F-FAN-005: set_percentage(0) → state=off
- F-FAN-006: set_preset_mode("sleep") → preset_mode="sleep"
- F-FAN-007: set_preset_mode("turbo") → preset_mode="turbo"
- F-FAN-008: oscillate(true) → oscillating=True
- F-FAN-009: oscillate(false) → oscillating=False
- F-FAN-010: set_direction("reverse") → direction="reverse"
- F-FAN-011: set_direction("forward") → direction="forward"
- F-FAN-012: toggle → state flips
- F-FAN-013: increase_speed → percentage increases by step
- F-FAN-014: decrease_speed → percentage decreases by step

#### Edge (Round 2)
- E-FAN-001: set_percentage(-1) → error or clamped
- E-FAN-002: set_percentage(101) → error or clamped
- E-FAN-003: set_percentage(0.5) → handled gracefully
- E-FAN-004: set_preset_mode("nonexistent") → error
- E-FAN-005: set_direction("invalid") → no state change
- E-FAN-006: rapid toggle 20x → final state consistent
- E-FAN-007: turn_on with percentage=50 simultaneously
- E-FAN-008: turn_off while already off → no error

### 3.2 Light (`light.test_light_full`)

#### Functional (Round 1)
- F-LGT-001: turn_on → state=on
- F-LGT-002: turn_off → state=off
- F-LGT-003: turn_on with brightness=128 → brightness=128
- F-LGT-004: turn_on with brightness=255 → brightness=255
- F-LGT-005: turn_on with brightness=1 → brightness=1
- F-LGT-006: turn_on with color_temp_kelvin=2500 → min temp
- F-LGT-007: turn_on with color_temp_kelvin=6500 → max temp
- F-LGT-008: turn_on with color_temp_kelvin=4000 → mid temp
- F-LGT-009: toggle → state flips
- F-LGT-010: turn_on with transition=2 → accepted (supports_transition)

#### Edge (Round 2)
- E-LGT-001: turn_on brightness=0 → off or clamped
- E-LGT-002: turn_on brightness=256 → error or clamped
- E-LGT-003: turn_on brightness=-1 → error
- E-LGT-004: turn_on color_temp_kelvin=1000 → below min
- E-LGT-005: turn_on color_temp_kelvin=10000 → above max
- E-LGT-006: rapid on/off 20x → final state consistent
- E-LGT-007: turn_off while already off → no error

### 3.3 Climate (`climate.test_climate`)

#### Functional (Round 1)
- F-CLM-001: set_hvac_mode("heat") → hvac_mode=heat
- F-CLM-002: set_hvac_mode("cool") → hvac_mode=cool
- F-CLM-003: set_hvac_mode("heat_cool") → hvac_mode=heat_cool
- F-CLM-004: set_hvac_mode("off") → hvac_mode=off
- F-CLM-005: set_temperature(20) → temperature=20
- F-CLM-006: set_temperature(16) → min temperature
- F-CLM-007: set_temperature(35) → max temperature
- F-CLM-008: set_temperature(25.5) → half-step
- F-CLM-009: turn_on → state changes from off
- F-CLM-010: turn_off → state=off

#### Edge (Round 2)
- E-CLM-001: set_temperature(15) → below min (16)
- E-CLM-002: set_temperature(36) → above max (35)
- E-CLM-003: set_temperature(0) → extreme low
- E-CLM-004: set_hvac_mode("invalid") → error
- E-CLM-005: rapid mode switching 10x → final state consistent
- E-CLM-006: set_temperature while off → temperature stored

### 3.4 Cover (`cover.test_cover`)

#### Functional (Round 1)
- F-COV-001: open_cover → state=open, position=100
- F-COV-002: close_cover → state=closed, position=0
- F-COV-003: set_cover_position(50) → position=50
- F-COV-004: set_cover_position(0) → closed
- F-COV-005: set_cover_position(100) → open
- F-COV-006: stop_cover → movement stops
- F-COV-007: toggle → state flips

#### Edge (Round 2)
- E-COV-001: set_cover_position(-1) → error or clamped
- E-COV-002: set_cover_position(101) → error or clamped
- E-COV-003: open_cover while fully open → no error
- E-COV-004: close_cover while fully closed → no error
- E-COV-005: rapid open/close 10x → final state consistent
- E-COV-006: set_position during movement → interrupts correctly

---

## 4. Stress Test Specifications

| Test | Operations | Rate | Success Criteria |
|------|-----------|------|------------------|
| Fan rapid toggle | 20x toggle | 100ms interval | No errors, final state deterministic |
| Light rapid brightness | 50 values (1-255) | 50ms interval | All accepted, final value correct |
| Climate mode cycle | 4 modes x 5 rounds | 200ms interval | No errors, final mode correct |
| Cover position sweep | 0→100 in steps of 10 | 500ms interval | Monotonic position changes |
| All-entity concurrent | All 4 entities simultaneously | Parallel | No cross-entity interference |

---

## 5. Browser UI Test Cases

| ID | Test | Steps |
|----|------|-------|
| UI-001 | Fan card controls | Click on/off, verify state badge updates |
| UI-002 | Light brightness slider | Drag slider, verify brightness updates |
| UI-003 | Climate temperature control | Set temperature, verify display |
| UI-004 | Cover position control | Click open/close, verify position |
| UI-005 | Config flow - add new fan | Settings → Integrations → Add → woow_fan |
| UI-006 | Config flow - add new light | Settings → Integrations → Add → template_light |
| UI-007 | Entity detail panel | Click entity → verify all attributes shown |

---

## 6. Persistence Test Protocol

1. Record all entity states via API
2. `podman restart homeassistant`
3. Wait for HA to fully boot
4. Re-read all entity states via API
5. Compare: all states must match pre-restart values

---

## 7. Success Criteria

| Level | Criteria |
|-------|---------|
| **Pass** | All functional tests pass, no errors in HA log |
| **Enterprise** | Edge cases handled gracefully, stress tests stable, persistence confirmed |
| **Production-Ready** | Browser UI works correctly, config flow validated, no warnings in log |
