# Quickstart: Full TX/RX Demo Fan Entity

Set up a fully bidirectional fan entity that aggregates 5 helper entities
into one fan card with all controls working in both directions.

**Time:** ~5 minutes
**Result:** `fan.demo_fan_full_tx_rx` with all 5 fan controls fully bidirectional

---

## Architecture

```
  Fan Card (UI)                  Helper Entities (HA)
  =====================         ==========================

  Power ON/OFF          <--TX-->  input_boolean.fan_power
  Speed % (0-100)       <--TX-->  input_number.fan_speed
  Preset Mode selector  <--TX-->  input_select.fan_preset_mode
  Oscillation toggle    <--TX-->  input_boolean.fan_oscillation
  Direction selector    <--TX-->  input_select.fan_direction
```

**TX** = When you tap a control on the fan card, it sends the value to the external entity.
**RX** = When the external entity changes (e.g., via Developer Tools), the fan card updates.

---

## Step 1: Add Helper Entities to configuration.yaml

Copy this entire block into your HA `configuration.yaml`:

```yaml
# =====================================================
# WoowTech Fan Entity Demo: Helper Entities
# =====================================================

input_boolean:
  fan_power:
    name: Fan Power Switch
    icon: mdi:power
  fan_oscillation:
    name: Fan Oscillation
    icon: mdi:rotate-3d-variant

input_number:
  fan_speed:
    name: "Fan Speed Percentage"
    min: 0
    max: 100
    step: 1
    initial: 0
    mode: slider
    unit_of_measurement: "%"
    icon: mdi:speedometer

input_select:
  fan_preset_mode:
    name: Fan Preset Mode
    options:
      - auto
      - sleep
      - smart
      - natural
      - breeze
      - silent
      - turbo
    initial: auto
    icon: mdi:fan-auto
  fan_direction:
    name: Fan Direction
    options:
      - forward
      - reverse
    initial: forward
    icon: mdi:rotate-left
```

## Step 2: Restart Home Assistant

```
Settings > System > Restart
```

After restart, verify all 5 helper entities exist in Developer Tools > States:
- `input_boolean.fan_power` (off)
- `input_boolean.fan_oscillation` (off)
- `input_number.fan_speed` (0)
- `input_select.fan_preset_mode` (auto)
- `input_select.fan_direction` (forward)

## Step 3: Install the Custom Component

Copy the `custom_components/woow_fan_entity/` folder into your HA `custom_components/` directory:

```
<ha_config>/
  custom_components/
    woow_fan_entity/
      __init__.py
      config_flow.py
      const.py
      fan.py
      manifest.json
      strings.json
```

Restart HA again after copying.

## Step 4: Create the Fan Entity via Config Flow

```
Settings > Devices & Services > Add Integration > WoowTech Fan Entity
```

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `Demo Fan Full TX/RX` |
| **Switch Entity** | `input_boolean.fan_power` |
| **Speed Count** | `4` |
| **Preset Modes** | `auto`, `sleep`, `turbo` |
| **Enable Oscillation** | Yes |
| **Enable Direction** | Yes |
| **Percentage Entity** | `input_number.fan_speed` |
| **Preset Mode Entity** | `input_select.fan_preset_mode` |
| **Oscillation Entity** | `input_boolean.fan_oscillation` |
| **Direction Entity** | `input_select.fan_direction` |

Click Submit. The entity `fan.demo_fan_full_tx_rx` is created.

## Step 5: Verify TX (Fan Card → Helper Entities)

1. Open the fan card in Lovelace (or use Developer Tools > Services)
2. **Turn on the fan** → `input_boolean.fan_power` turns ON, `input_number.fan_speed` = 25
3. **Set speed to 75%** → `input_number.fan_speed` updates to 75
4. **Select preset "sleep"** → `input_select.fan_preset_mode` updates to "sleep"
5. **Toggle oscillation ON** → `input_boolean.fan_oscillation` turns ON
6. **Set direction "reverse"** → `input_select.fan_direction` updates to "reverse"
7. **Turn off the fan** → `input_boolean.fan_power` turns OFF, speed = 0

## Step 6: Verify RX (Helper Entities → Fan Card)

1. Go to Developer Tools > States
2. **Set** `input_boolean.fan_power` **to** `on` → Fan card shows ON
3. **Set** `input_number.fan_speed` **to** `50` → Fan card shows 50% speed
4. **Set** `input_select.fan_preset_mode` **to** `turbo` → Fan card shows "turbo" preset
5. **Set** `input_boolean.fan_oscillation` **to** `on` → Fan card shows oscillation ON
6. **Set** `input_select.fan_direction` **to** `reverse` → Fan card shows "reverse"

All 5 controls should be fully bidirectional.

---

## TX/RX Feature Matrix

| Feature | Switch Entity | Entity Selector | Action Script | RX Listener |
|---------|:---:|:---:|:---:|:---:|
| **Power ON/OFF** | `input_boolean.fan_power` | — | — | `_async_switch_changed` |
| **Speed %** | — | `input_number.fan_speed` | `set_percentage` | `_async_percentage_entity_changed` |
| **Preset Mode** | — | `input_select.fan_preset_mode` | `set_preset_mode` | `_async_preset_mode_entity_changed` |
| **Oscillation** | — | `input_boolean.fan_oscillation` | `set_oscillating` | `_async_oscillating_entity_changed` |
| **Direction** | — | `input_select.fan_direction` | `set_direction` | `_async_direction_entity_changed` |

### TX Priority Chain

For each control action, commands dispatch via the **first available** channel:

| Control Method | Priority 1 (Highest) | Priority 2 | Priority 3 (Fallback) |
|----------------|:---:|:---:|:---:|
| **Turn On** | `set_percentage` script (default %) | Percentage entity (default %) | Internal set (default %) |
| **Turn Off** | `set_percentage` script (0) | Percentage entity (0) | Internal set (0) |
| **Set Percentage** | `set_percentage` script | Percentage entity | Internal set |
| **Set Preset Mode** | `set_preset_mode` script | Preset mode entity | Internal set |
| **Set Oscillating** | `set_oscillating` script | Oscillating entity | Internal set |
| **Set Direction** | `set_direction` script | Direction entity | Internal set |

**Note:** Turn on/off also controls the switch entity (if configured) in addition to the speed dispatch.

### TX Domain-Aware Dispatch

The TX helper automatically uses the correct service call based on the entity's domain:

| Entity Domain | Service Used | Value Format |
|---------------|:---:|:---:|
| `input_number`, `number` | `set_value` | float (0-100) |
| `input_select`, `select` | `select_option` | string |
| `switch`, `input_boolean` | `turn_on` / `turn_off` | boolean |

### RX Behavior Details

**Initial Sync:** On startup, the fan reads the current state from all configured entity selectors (percentage, preset mode, oscillating, direction) and sets its internal state to match. This happens automatically before the fan card appears in the UI.

**Switch Sync Logic:** On startup, if the switch entity is ON but percentage is 0, the fan auto-sets a default percentage (`100 / speed_count`). If the switch is OFF but percentage is > 0, the fan sets percentage to 0. The same logic applies when the switch state changes via RX.

**RX Validation:**
- States `unavailable` and `unknown` are ignored (no update)
- Percentage values outside 0-100 are rejected
- Preset modes not in the configured list are silently ignored
- Direction must be exactly `forward` or `reverse`
- Duplicate values (same as current) do not trigger an update
- Non-numeric percentage values are silently ignored

### Speed and Preset Mode Mutual Exclusion

Setting a speed percentage **clears the preset mode** (sets it to None). Conversely, setting a preset mode **clears the percentage** (sets it to None). This mutual exclusion also applies to RX — receiving a percentage > 0 from the entity clears the active preset.

### Turn On Variants

`async_turn_on()` supports three call patterns:
- **Default:** Sets speed to default percentage (`100 / speed_count`) and turns on switch
- **With percentage:** `turn_on(percentage=75)` — delegates to `set_percentage(75)`
- **With preset_mode:** `turn_on(preset_mode="turbo")` — delegates to `set_preset_mode("turbo")`

Setting percentage to 0 automatically redirects to `turn_off()`.

### Entity Domain Restrictions

Entity selectors in the config flow only accept specific entity domains:

| Config Field | Accepted Domains |
|-------------|:---:|
| **Switch Entity** | `switch`, `fan`, `input_boolean` |
| **Percentage Entity** | `input_number`, `number` |
| **Preset Mode Entity** | `input_select`, `select` |
| **Oscillation Entity** | `switch`, `input_boolean` |
| **Direction Entity** | `input_select`, `select` |

---

## Supported Features (Auto-Detection)

The supported features are dynamically determined from your config:

| Feature | Enabled When |
|---------|-------------|
| `TURN_ON` + `TURN_OFF` | Always |
| `SET_SPEED` | Always |
| `PRESET_MODE` | Preset modes list is configured (non-empty) |
| `OSCILLATE` | Enable Oscillation = Yes |
| `DIRECTION` | Enable Direction = Yes |

---

## State Restoration

The fan entity uses Home Assistant's `RestoreEntity` pattern. On HA restart:

- **Percentage** is restored to its last known value
- **Preset mode** is restored (if it's in the configured preset modes list)
- **Oscillating** is restored (if oscillation is enabled)
- **Direction** is restored (if direction is enabled, must be "forward" or "reverse")

If both state restoration and an RX entity are configured, the entity selector state takes precedence (initial sync overrides the restored value). Switch sync logic then adjusts percentage if needed.

---

## Speed Count Reference

| speed_count | Percentage Step | Speed Levels |
|-------------|-----------------|--------------|
| 3 | 33% | 33%, 67%, 100% |
| 4 | 25% | 25%, 50%, 75%, 100% |
| 5 | 20% | 20%, 40%, 60%, 80%, 100% |
| 6 | ~17% | 17%, 33%, 50%, 67%, 83%, 100% |

---

## Default Percentage Calculation

When the fan turns on without a specific percentage, it calculates a default:

```
default_percentage = 100 / speed_count
```

| speed_count | Default % on Turn On |
|:-----------:|:--------------------:|
| 3 | 33% |
| 4 | 25% |
| 5 | 20% |
| 6 | 16% |

---

## Validation and Edge Cases

**Preset Mode Validation:**
- Preset mode must match one of the configured modes exactly
- Invalid preset modes log an error and are not applied
- RX silently ignores preset modes not in the configured list

**Direction Validation:**
- Direction must be exactly `forward` or `reverse`
- Invalid direction values log an error and are not applied

**Percentage Validation:**
- Percentage must be 0-100 (integer)
- RX rejects values outside this range
- Setting percentage to 0 automatically calls `turn_off()`

**No TX Target Configured:**
- If no entity selector or action script is configured for a control, the value is set directly in memory
- The fan card still works for UI testing without external entities

---

## Troubleshooting

**Fan shows "unavailable":**
- Check that `input_boolean.fan_power` exists in Developer Tools > States
- Verify the custom component is loaded: check HA logs for "Setting up woow_fan_entity"

**TX not working (fan card doesn't update helpers):**
- Ensure the entity selectors point to the correct helper entities
- Check HA logs for errors from `custom_components.woow_fan_entity.fan`

**RX not working (helper changes don't update fan card):**
- RX listeners only trigger on state *changes* — setting the same value again won't trigger
- Verify the helper entity state is valid (e.g., preset mode must be in the configured list)

**Preset mode not accepted:**
- The preset mode value must match one of the configured preset modes exactly
- Invalid preset modes from the entity selector are silently ignored

---

## Demo: ESP32 PWM Fan (Linear Interpolation)

This demo shows how to use **Linear Interpolation** to map an ESP32 ADC sensor (0-1023) to fan speed percentage (0-100).

### Architecture

```
  ESP32 ADC (0-1023)
        |
        v
  input_number.esp32_fan_adc     (simulates ESP32 sensor)
        |
        v  Linear Interpolation: 0-1023 → 0-100
        |
  fan.esp32_pwm_fan              (shows 0-100% speed)
```

### Step 1: Add Helper Entity

```yaml
input_number:
  esp32_fan_adc:
    name: "ESP32 Fan ADC Reading"
    min: 0
    max: 1023
    step: 1
    initial: 0
    mode: slider
    unit_of_measurement: "ADC"
    icon: mdi:chip
```

### Step 2: Create Fan Entity via Config Flow

| Field | Value |
|-------|-------|
| **Name** | `ESP32 PWM Fan` |
| **Switch Entity** | _(leave blank)_ |
| **Speed Count** | `4` |
| **Percentage Entity** | `input_number.esp32_fan_adc` |
| **Percentage Input Min** | `0` |
| **Percentage Input Max** | `1023` |
| **Percentage Output Min** | `0` |
| **Percentage Output Max** | `100` |

### Step 3: Verify Mapping

| ADC Slider Value | Expected Fan Speed |
|:----------------:|:------------------:|
| 0 | 0% (off) |
| 256 | ~25% |
| 512 | ~50% |
| 768 | ~75% |
| 1023 | 100% |

### TX Reverse Interpolation (v1.2.0)

When linear interpolation is configured and the entity selector Send path is used (no action script override), outgoing TX writes are automatically reverse-mapped to the external range:

| Fan Action | HA Value | External Entity Receives |
|-----------|----------|-------------------------|
| Set speed 50% | 50 | ~512 |
| Set speed 75% | 75 | ~768 |
| Turn off | 0 | 0 |
| Turn on (100%) | 100 | 1023 |

Action scripts always receive raw 0-100 values via `{{ percentage }}`.

### Testing Checklist

- [ ] Set slider to 0 → fan shows 0%
- [ ] Set slider to 512 → fan shows ~50%
- [ ] Set slider to 1023 → fan shows 100%
- [ ] Set fan to 75% → slider updates to ~768 (reverse interpolation)
- [ ] Existing fans without interpolation still work unchanged
