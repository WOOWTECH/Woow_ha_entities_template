# Building Blocks for Every `set_*` Action

This document is a **reference catalog** of the 7 `set_*` actions in the Climate Template
integration. Each section shows the building-block entity, how to wire it, and how to
verify it works.

> **Who is this for?** LLMs or developers creating custom climate entities that need
> to understand which HA entity type to use for each control, what action script to
> write, and what template variable is available.

---

## Architecture: How `set_*` Actions Flow

```
                  HA Climate Card UI
                         |
         user taps a control (e.g. Fan: High)
                         |
                         v
              +-----------------------+
              |  async_set_fan_mode() |
              +-----------------------+
                         |
            TX Priority Chain (checked in order):
                         |
         +---------------+---------------+
         |                               |
    1. Action Script?              2. Entity Selector?
    (if configured)                (if configured)
         |                               |
    Script.async_run(               _async_set_entity_state(
      {"fan_mode":"high"})            "input_select.x", "high")
         |                               |
         v                               v
    Calls any HA service           Auto-detects domain:
    (you define the YAML)            input_select → select_option
                                     select       → select_option
                                     fan          → set_preset_mode
                                     switch       → turn_on/turn_off
                                     input_number → set_value
                                     number       → set_value
                                              |
                                              v
                                     3. If neither → Optimistic only
                                        (internal state, no TX)
```

### RX (Reverse Direction)

When an external entity changes state, the climate entity automatically picks it up
via `async_track_state_change_event` listeners registered in `async_added_to_hass()`.

---

## Quick Reference Table

| # | `set_*` Action | Template Variable | Entity Selector Domains | Entity Config Key | Action Script Config Key |
|---|---------------|-------------------|------------------------|-------------------|--------------------------|
| 1 | `set_temperature` | `{{ temperature }}` | input_number, number | `target_temperature_entity` | `set_temperature` |
| 2 | `set_hvac_mode` | `{{ hvac_mode }}` | input_select, select | `hvac_mode_entity` | `set_hvac_mode` |
| 3 | `set_fan_mode` | `{{ fan_mode }}` | input_select, select, fan | `fan_mode_entity` | `set_fan_mode` |
| 4 | `set_preset_mode` | `{{ preset_mode }}` | input_select, select | `preset_mode_entity` | `set_preset_mode` |
| 5 | `set_swing_mode` | `{{ swing_mode }}` | input_select, select, switch, input_boolean | `swing_mode_entity` | `set_swing_mode` |
| 6 | `set_swing_horizontal_mode` | `{{ swing_horizontal_mode }}` | input_select, select, switch, input_boolean | `swing_horizontal_mode_entity` | `set_swing_horizontal_mode` |
| 7 | `set_humidity` | `{{ humidity }}` | input_number, number | `humidity_entity` | `set_humidity` |

---

## 1. `set_temperature` — Target Temperature

**What it controls:** The desired temperature setpoint on the climate card.

**Template variable:** `{{ temperature }}` (float, e.g. `22.5`)

For `heat_cool` mode, also: `{{ target_temp_high }}` and `{{ target_temp_low }}`

### Building Block Entity

```yaml
# configuration.yaml
input_number:
  aircon_target_temp:
    name: "AC Target Temperature"
    min: 16
    max: 30
    step: 0.5
    initial: 22
    unit_of_measurement: "°C"
    icon: mdi:thermometer-chevron-up
    mode: slider
```

### Wiring (Simple Mode)

In the config flow UI, set:
- **Target Temperature Entity:** `input_number.aircon_target_temp`

The integration will automatically:
- **TX:** Call `input_number.set_value` when user adjusts temperature on climate card
- **RX:** Update climate card when `input_number.aircon_target_temp` changes externally

### Action Script Override

```yaml
# In config flow "Set Temperature Action" field:
- action: input_number.set_value
  target:
    entity_id: input_number.aircon_target_temp
  data:
    value: "{{ temperature }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_number.aircon_target_temp') | float(22) }}
```

### Verify

```bash
# TX: Climate card -> entity
curl -X POST http://127.0.0.1:8123/api/services/climate/set_temperature \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","temperature":25}'
# Check: input_number.aircon_target_temp should be 25.0

# RX: Entity -> climate card
curl -X POST http://127.0.0.1:8123/api/services/input_number/set_value \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_number.aircon_target_temp","value":28}'
# Check: climate.my_ac temperature attribute should be 28
```

---

## 2. `set_hvac_mode` — HVAC Mode

**What it controls:** The operating mode (off, heat, cool, heat_cool, auto, dry, fan_only).

**Template variable:** `{{ hvac_mode }}` (string, e.g. `"heat"`)

### Building Block Entity

```yaml
input_select:
  aircon_hvac_mode:
    name: "AC HVAC Mode"
    options:
      - "off"
      - "heat"
      - "cool"
      - "heat_cool"
    initial: "off"
    icon: mdi:thermostat
```

### Wiring (Simple Mode)

In the config flow UI, set:
- **HVAC Mode Entity:** `input_select.aircon_hvac_mode`
- **HVAC Modes:** off, heat, cool, heat_cool (must match the input_select options)

The integration will automatically:
- **TX:** Call `input_select.select_option` when user changes HVAC mode on climate card
- **RX:** Update climate card when `input_select.aircon_hvac_mode` changes externally

> **Note:** In Simple Mode, `set_hvac_mode` also controls the heater/cooler switches
> (turning them on/off based on the mode). The entity selector is an *additional*
> TX target — it doesn't replace the built-in heater/cooler logic.

### Action Script Override

```yaml
- action: input_select.select_option
  target:
    entity_id: input_select.aircon_hvac_mode
  data:
    option: "{{ hvac_mode }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_select.aircon_hvac_mode') }}
```

### Verify

```bash
# TX: Climate card -> entity
curl -X POST http://127.0.0.1:8123/api/services/climate/set_hvac_mode \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","hvac_mode":"heat"}'
# Check: input_select.aircon_hvac_mode should be "heat"

# RX: Entity -> climate card
curl -X POST http://127.0.0.1:8123/api/services/input_select/select_option \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_select.aircon_hvac_mode","option":"cool"}'
# Check: climate.my_ac state should be "cool"
```

---

## 3. `set_fan_mode` — Fan Speed

**What it controls:** The fan speed/mode displayed on the climate card.

**Template variable:** `{{ fan_mode }}` (string, e.g. `"high"`)

### Building Block Entity (input_select)

```yaml
input_select:
  aircon_fan_speed:
    name: "AC Fan Speed"
    options:
      - "auto"
      - "low"
      - "medium"
      - "high"
    initial: "auto"
    icon: mdi:fan
```

### Alternative: Fan Entity

If you have an actual `fan` entity in HA, you can use it directly:
- **Entity Selector:** `fan.bedroom_fan`
- **TX Service:** `fan.set_preset_mode` with `preset_mode: "high"`

### Wiring (Simple Mode)

- **Fan Mode Entity:** `input_select.aircon_fan_speed`
- **Fan Modes:** auto, low, medium, high (must match the input_select options)

### Action Script Override

```yaml
- action: input_select.select_option
  target:
    entity_id: input_select.aircon_fan_speed
  data:
    option: "{{ fan_mode }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_select.aircon_fan_speed') }}
```

### Verify

```bash
# TX
curl -X POST http://127.0.0.1:8123/api/services/climate/set_fan_mode \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","fan_mode":"high"}'
# Check: input_select.aircon_fan_speed = "high"

# RX
curl -X POST http://127.0.0.1:8123/api/services/input_select/select_option \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_select.aircon_fan_speed","option":"low"}'
# Check: climate.my_ac fan_mode attribute = "low"
```

---

## 4. `set_preset_mode` — Preset Mode

**What it controls:** Named presets like eco, comfort, sleep, away, boost.

**Template variable:** `{{ preset_mode }}` (string, e.g. `"eco"`)

### Building Block Entity

```yaml
input_select:
  aircon_preset:
    name: "AC Preset"
    options:
      - "none"
      - "eco"
      - "comfort"
      - "away"
      - "boost"
      - "home"
      - "sleep"
      - "activity"
    initial: "none"
    icon: mdi:home-thermometer
```

> **Important:** Include `"none"` in options. HA uses "none" to represent "no preset
> selected". If your configured preset list includes "none", the user can deselect
> any active preset.

### Wiring (Simple Mode)

- **Preset Mode Entity:** `input_select.aircon_preset`
- **Preset Modes:** eco, comfort, away, boost, home, sleep, activity

In Simple Mode, presets also save/restore the target temperature. When a preset
with a configured temperature is activated, the target temp changes to the preset
value. When deactivated (set to "none"), it restores the previous target temp.

### Action Script Override

```yaml
- action: input_select.select_option
  target:
    entity_id: input_select.aircon_preset
  data:
    option: "{{ preset_mode }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_select.aircon_preset') }}
```

### Verify

```bash
# TX
curl -X POST http://127.0.0.1:8123/api/services/climate/set_preset_mode \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","preset_mode":"eco"}'
# Check: input_select.aircon_preset = "eco"

# RX
curl -X POST http://127.0.0.1:8123/api/services/input_select/select_option \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_select.aircon_preset","option":"boost"}'
# Check: climate.my_ac preset_mode attribute = "boost"
```

---

## 5. `set_swing_mode` — Vertical Swing / Vane

**What it controls:** Vertical airflow direction (swing/vane position).

**Template variable:** `{{ swing_mode }}` (string, e.g. `"on"`)

### Building Block Entity — Option A: input_select (multi-position)

```yaml
input_select:
  aircon_vane:
    name: "AC Vane Position"
    options:
      - "on"
      - "off"
    initial: "off"
    icon: mdi:arrow-up-down
```

### Building Block Entity — Option B: switch (on/off toggle)

```yaml
# If your real AC just has a swing on/off toggle:
switch:
  - platform: template
    switches:
      aircon_swing:
        friendly_name: "AC Swing"
        value_template: "{{ is_state('input_boolean.aircon_swing_state', 'on') }}"
        turn_on:
          action: input_boolean.turn_on
          target:
            entity_id: input_boolean.aircon_swing_state
        turn_off:
          action: input_boolean.turn_off
          target:
            entity_id: input_boolean.aircon_swing_state
```

When using a `switch` or `input_boolean` entity:
- **TX for "on":** calls `homeassistant.turn_on`
- **TX for "off":** calls `homeassistant.turn_off`

### Wiring (Simple Mode)

- **Swing Mode Entity:** `input_select.aircon_vane` (or `switch.aircon_swing`)
- **Swing Modes:** on, off

### Action Script Override

```yaml
- action: input_select.select_option
  target:
    entity_id: input_select.aircon_vane
  data:
    option: "{{ swing_mode }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_select.aircon_vane') }}
```

### Verify

```bash
# TX
curl -X POST http://127.0.0.1:8123/api/services/climate/set_swing_mode \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","swing_mode":"on"}'
# Check: input_select.aircon_vane = "on"

# RX
curl -X POST http://127.0.0.1:8123/api/services/input_select/select_option \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_select.aircon_vane","option":"off"}'
# Check: climate.my_ac swing_mode attribute = "off"
```

---

## 6. `set_swing_horizontal_mode` — Horizontal Swing / Vane

**What it controls:** Horizontal airflow direction (left-right vane).

**Template variable:** `{{ swing_horizontal_mode }}` (string, e.g. `"on"`)

### Building Block Entity

```yaml
input_select:
  aircon_horizontal_vane:
    name: "AC Horizontal Vane"
    options:
      - "on"
      - "off"
    initial: "off"
    icon: mdi:arrow-left-right
```

### Wiring (Simple Mode)

- **Horizontal Swing Entity:** `input_select.aircon_horizontal_vane`
- **Horizontal Swing Modes:** on, off

### Action Script Override

```yaml
- action: input_select.select_option
  target:
    entity_id: input_select.aircon_horizontal_vane
  data:
    option: "{{ swing_horizontal_mode }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_select.aircon_horizontal_vane') }}
```

### Verify

```bash
# TX
curl -X POST http://127.0.0.1:8123/api/services/climate/set_swing_horizontal_mode \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","swing_horizontal_mode":"on"}'
# Check: input_select.aircon_horizontal_vane = "on"

# RX
curl -X POST http://127.0.0.1:8123/api/services/input_select/select_option \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_select.aircon_horizontal_vane","option":"off"}'
# Check: climate.my_ac swing_horizontal_mode attribute = "off"
```

---

## 7. `set_humidity` — Target Humidity

**What it controls:** The desired humidity percentage on the climate card.

**Template variable:** `{{ humidity }}` (integer, e.g. `60`)

### Building Block Entity

```yaml
input_number:
  aircon_target_humidity:
    name: "AC Target Humidity"
    min: 30
    max: 80
    step: 5
    initial: 50
    unit_of_measurement: "%"
    icon: mdi:water-percent
    mode: slider
```

### Companion: Humidity Sensor (read-only RX)

To display **current** humidity on the climate card, you also need a humidity sensor:

```yaml
# Under template: sensor:
- name: "Room Humidity"
  unit_of_measurement: "%"
  device_class: humidity
  state: "{{ states('sensor.your_real_humidity_sensor') | float(50) }}"
```

Wire it via:
- **Humidity Sensor:** `sensor.room_humidity` (in config flow)

This is RX-only — the climate card displays it but never writes to it.

### Wiring (Simple Mode)

- **Target Humidity Entity:** `input_number.aircon_target_humidity`
- The `TARGET_HUMIDITY` feature flag is automatically enabled when this is configured.

### Action Script Override

```yaml
- action: input_number.set_value
  target:
    entity_id: input_number.aircon_target_humidity
  data:
    value: "{{ humidity }}"
```

### Advanced Mode Template (RX)

```jinja2
{{ states('input_number.aircon_target_humidity') | float(50) }}
```

### Verify

```bash
# TX
curl -X POST http://127.0.0.1:8123/api/services/climate/set_humidity \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"climate.my_ac","humidity":65}'
# Check: input_number.aircon_target_humidity = 65.0

# RX
curl -X POST http://127.0.0.1:8123/api/services/input_number/set_value \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"entity_id":"input_number.aircon_target_humidity","value":40}'
# Check: climate.my_ac humidity attribute = 40
```

---

## Bonus: Read-Only Building Blocks (No `set_*`)

These entities feed data **into** the climate card but have no corresponding `set_*` action.

### Current Temperature Sensor

```yaml
input_number:
  room_temp_simulator:
    name: "Room Temperature Simulator"
    min: -10
    max: 50
    step: 0.5
    initial: 22
    unit_of_measurement: "°C"
    mode: slider

template:
  - sensor:
      - name: "Room Temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state: "{{ states('input_number.room_temp_simulator') | float(22) }}"
```

Wire via: **Temperature Sensor:** `sensor.room_temperature`

### Current Humidity Sensor

```yaml
template:
  - sensor:
      - name: "Room Humidity"
        unit_of_measurement: "%"
        device_class: humidity
        state: "{{ states('sensor.your_real_humidity_sensor') | float(50) }}"
```

Wire via: **Humidity Sensor:** `sensor.room_humidity`

### HVAC Action (heating/cooling/idle indicator)

This is **computed** by Simple Mode based on heater/cooler state. In Advanced Mode,
you provide a template:

```jinja2
{% if is_state('input_boolean.test_heater', 'on') %}heating
{% elif is_state('input_boolean.test_ac_unit', 'on') %}cooling
{% else %}idle{% endif %}
```

### Heater / Cooler Switches

```yaml
input_boolean:
  heater_switch:
    name: "Heater"
    icon: mdi:radiator
    initial: false

  cooler_switch:
    name: "Cooler"
    icon: mdi:air-conditioner
    initial: false
```

Wire via: **Heater Entity** / **Cooler Entity** in Simple Mode config flow.

---

## Complete Minimal YAML: All 7 `set_*` Building Blocks

Copy this into your `configuration.yaml` to get all building-block entities for a
fully-wired Climate Template entity:

```yaml
# ===== Heater/Cooler Switches =====
input_boolean:
  demo_heater:
    name: "Demo Heater"
    icon: mdi:radiator
    initial: false
  demo_cooler:
    name: "Demo Cooler"
    icon: mdi:air-conditioner
    initial: false

# ===== Number Controls (set_temperature + set_humidity targets) =====
input_number:
  demo_room_temp_slider:
    name: "Demo Room Temp Slider"
    min: -10
    max: 50
    step: 0.5
    initial: 22
    unit_of_measurement: "°C"
    mode: slider
  demo_target_temp:
    name: "Demo Target Temperature"
    min: 7
    max: 35
    step: 0.5
    initial: 22
    unit_of_measurement: "°C"
    mode: slider
  demo_target_humidity:
    name: "Demo Target Humidity"
    min: 0
    max: 100
    step: 1
    initial: 50
    unit_of_measurement: "%"
    mode: slider

# ===== Mode Selectors (set_hvac_mode + set_fan_mode + set_preset_mode + set_swing* targets) =====
input_select:
  demo_hvac_mode:
    name: "Demo HVAC Mode"
    options: ["off", "heat", "cool", "heat_cool"]
    initial: "off"
  demo_fan_mode:
    name: "Demo Fan Mode"
    options: ["auto", "low", "medium", "high"]
    initial: "auto"
  demo_preset_mode:
    name: "Demo Preset Mode"
    options: ["none", "eco", "comfort", "away", "boost", "home", "sleep", "activity"]
    initial: "none"
  demo_swing_mode:
    name: "Demo Swing Mode"
    options: ["on", "off"]
    initial: "off"
  demo_swing_horizontal_mode:
    name: "Demo Horizontal Swing"
    options: ["on", "off"]
    initial: "off"

# ===== Sensors (read-only RX) =====
template:
  - sensor:
      - name: "Demo Room Temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state: "{{ states('input_number.demo_room_temp_slider') | float(22) }}"
      - name: "Demo Room Humidity"
        unit_of_measurement: "%"
        device_class: humidity
        state: "{{ states('input_number.demo_target_humidity') | float(50) }}"
```

### Config Flow Wiring (Simple Mode)

| Config Field | Entity |
|-------------|--------|
| Temperature Sensor | `sensor.demo_room_temperature` |
| Heater Entity | `input_boolean.demo_heater` |
| Cooler Entity | `input_boolean.demo_cooler` |
| HVAC Modes | off, heat, cool, heat_cool |
| Fan Modes | auto, low, medium, high |
| Preset Modes | eco, comfort, away, boost, home, sleep, activity |
| Swing Modes | on, off |
| Horizontal Swing Modes | on, off |
| **HVAC Mode Entity** | `input_select.demo_hvac_mode` |
| **Fan Mode Entity** | `input_select.demo_fan_mode` |
| **Preset Mode Entity** | `input_select.demo_preset_mode` |
| **Swing Mode Entity** | `input_select.demo_swing_mode` |
| **Horizontal Swing Entity** | `input_select.demo_swing_horizontal_mode` |
| **Target Temperature Entity** | `input_number.demo_target_temp` |
| **Target Humidity Entity** | `input_number.demo_target_humidity` |
| **Humidity Sensor** | `sensor.demo_room_humidity` |

### Action Scripts (Optional — entity selectors handle TX automatically)

Only needed if you want custom logic beyond the auto-detected service calls:

| Action | Script YAML |
|--------|------------|
| Set Temperature | `- action: input_number.set_value`<br>`  target: {entity_id: input_number.demo_target_temp}`<br>`  data: {value: "{{ temperature }}"}` |
| Set HVAC Mode | `- action: input_select.select_option`<br>`  target: {entity_id: input_select.demo_hvac_mode}`<br>`  data: {option: "{{ hvac_mode }}"}` |
| Set Fan Mode | `- action: input_select.select_option`<br>`  target: {entity_id: input_select.demo_fan_mode}`<br>`  data: {option: "{{ fan_mode }}"}` |
| Set Preset Mode | `- action: input_select.select_option`<br>`  target: {entity_id: input_select.demo_preset_mode}`<br>`  data: {option: "{{ preset_mode }}"}` |
| Set Swing Mode | `- action: input_select.select_option`<br>`  target: {entity_id: input_select.demo_swing_mode}`<br>`  data: {option: "{{ swing_mode }}"}` |
| Set Horizontal Swing | `- action: input_select.select_option`<br>`  target: {entity_id: input_select.demo_swing_horizontal_mode}`<br>`  data: {option: "{{ swing_horizontal_mode }}"}` |
| Set Humidity | `- action: input_number.set_value`<br>`  target: {entity_id: input_number.demo_target_humidity}`<br>`  data: {value: "{{ humidity }}"}` |

---

## Entity Type Decision Guide

| If your real device uses... | Use this HA entity type | Example |
|----------------------------|------------------------|---------|
| Multiple named options (low/med/high) | `input_select` | Fan speed, HVAC mode |
| A numeric value (temperature, humidity) | `input_number` | Target temp, humidity |
| An on/off toggle | `input_boolean` or `switch` | Heater, swing |
| A real HA fan entity | `fan` | Ceiling fan speed |
| A real HA select entity | `select` | Smart AC mode selector |
| A real HA number entity | `number` | Smart thermostat setpoint |

### Domain-to-Service Mapping (Auto-detected by Entity Selector TX)

| Entity Domain | Service Called | Data Key |
|--------------|---------------|----------|
| `input_select` | `input_select.select_option` | `option` |
| `select` | `select.select_option` | `option` |
| `fan` | `fan.set_preset_mode` | `preset_mode` |
| `input_boolean` | `homeassistant.turn_on` / `turn_off` | — |
| `switch` | `homeassistant.turn_on` / `turn_off` | — |
| `input_number` | `input_number.set_value` | `value` |
| `number` | `number.set_value` | `value` |
