# Quickstart: Full TX/RX Demo Climate Entity

Set up a fully bidirectional climate entity that aggregates 10+ helper entities
into one climate card with all 9 controls working in both directions.

**Time:** ~10 minutes
**Result:** `climate.demo_climate_full_tx_rx` with all 9 climate controls fully bidirectional

---

## Architecture

```
  Climate Card (UI)              Helper Entities (HA)
  =====================         =======================

  HVAC Mode selector    <--TX-->  input_select.test_hvac_mode
  Fan Mode selector     <--TX-->  input_select.test_fan_mode
  Preset Mode selector  <--TX-->  input_select.test_preset_mode
  Swing Mode selector   <--TX-->  input_select.test_swing_mode
  Swing Horiz selector  <--TX-->  input_select.test_swing_horizontal_mode
  Target Temperature    <--TX-->  input_number.test_target_temperature
  Target Humidity       <--TX-->  input_number.test_target_humidity

  Current Temperature   <--RX--  sensor.test_room_temperature
                                    ^ reads from input_number.test_room_temp_value
  Current Humidity      <--RX--  sensor.test_room_humidity
                                    ^ template sensor (feeds current_humidity display)

  Heater ON/OFF         ---TX-->  input_boolean.test_heater     (auto-control)
  Cooler ON/OFF         ---TX-->  input_boolean.test_ac_unit    (auto-control)
```

**TX** = When you tap a control on the climate card, it sends the value to the external entity.
**RX** = When the external entity changes (e.g., via Developer Tools), the climate card updates.

---

## Step 1: Add Helper Entities to configuration.yaml

Copy this entire block into your HA `configuration.yaml`:

```yaml
# =====================================================
# Climate Template Demo: Helper Entities
# =====================================================

input_boolean:
  test_heater:
    name: Test Heater
    icon: mdi:radiator
  test_ac_unit:
    name: Test AC Unit
    icon: mdi:air-conditioner

input_number:
  test_room_temp_value:
    name: "Room Temperature Control"
    min: -10
    max: 50
    step: 0.5
    initial: 21.5
    mode: slider
    unit_of_measurement: "°C"
    icon: mdi:thermometer
  test_target_temperature:
    name: "Test Target Temperature (TX/RX)"
    min: 7
    max: 35
    step: 0.5
    initial: 21
    unit_of_measurement: "°C"
    icon: mdi:thermometer-chevron-up
    mode: slider
  test_target_humidity:
    name: "Test Target Humidity (TX/RX)"
    min: 0
    max: 100
    step: 1
    initial: 50
    unit_of_measurement: "%"
    icon: mdi:water-percent
    mode: slider

input_select:
  test_fan_mode:
    name: "Test Fan Mode (TX/RX)"
    options:
      - "auto"
      - "low"
      - "medium"
      - "high"
    initial: "auto"
    icon: mdi:fan
  test_hvac_mode:
    name: "Test HVAC Mode (TX/RX)"
    options:
      - "off"
      - "heat"
      - "cool"
      - "heat_cool"
    initial: "off"
    icon: mdi:thermostat
  test_preset_mode:
    name: "Test Preset Mode (TX/RX)"
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
  test_swing_mode:
    name: "Test Swing Mode (TX/RX)"
    options:
      - "on"
      - "off"
    initial: "off"
    icon: mdi:arrow-up-down
  test_swing_horizontal_mode:
    name: "Test Swing Horizontal Mode (TX/RX)"
    options:
      - "on"
      - "off"
    initial: "off"
    icon: mdi:arrow-left-right

template:
  - sensor:
      - name: "Test Room Temperature"
        unit_of_measurement: "°C"
        device_class: temperature
        state: "{{ states('input_number.test_room_temp_value') | float(21.5) }}"
      - name: "Test Room Humidity"
        unit_of_measurement: "%"
        device_class: humidity
        state: "{{ states('input_number.test_target_humidity') | float(50) }}"
```

**Restart HA** after adding this.

### Entity Inventory (12 entities total)

| Entity ID | Type | Purpose |
|-----------|------|---------|
| `input_boolean.test_heater` | switch | Heater ON/OFF (auto-controlled) |
| `input_boolean.test_ac_unit` | switch | Cooler ON/OFF (auto-controlled) |
| `input_number.test_room_temp_value` | slider | Simulate room temperature changes |
| `input_number.test_target_temperature` | slider | TX/RX target for set_temperature |
| `input_number.test_target_humidity` | slider | TX/RX target for set_humidity |
| `input_select.test_hvac_mode` | dropdown | TX/RX target for HVAC mode |
| `input_select.test_fan_mode` | dropdown | TX/RX target for fan mode |
| `input_select.test_preset_mode` | dropdown | TX/RX target for preset mode |
| `input_select.test_swing_mode` | dropdown | TX/RX target for swing mode |
| `input_select.test_swing_horizontal_mode` | dropdown | TX/RX target for horizontal swing |
| `sensor.test_room_temperature` | sensor | Template sensor feeding current_temperature |
| `sensor.test_room_humidity` | sensor | Template sensor feeding current_humidity |

---

## Step 2: Create the Climate Entity via Config Flow

### Option A: Via the HA UI

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **"Climate Template"**
3. Select **"Simple (Entity Selectors)"** mode
4. Fill in the basic fields:

| Field | Value |
|-------|-------|
| Name | `Demo Climate (Full TX/RX)` |
| Temperature Sensor | `sensor.test_room_temperature` |
| Heater Entity | `input_boolean.test_heater` |
| Cooler Entity | `input_boolean.test_ac_unit` |
| HVAC Modes | off, heat, cool, heat_cool |
| Min Temp | 7 |
| Max Temp | 35 |
| Temp Step | 0.5 |
| Fan Modes | auto, low, medium, high |
| Preset Modes | eco, comfort, away, boost, home, sleep, activity |
| Swing Modes | on, off |
| Swing Horizontal Modes | on, off |

5. Set **Entity Selectors** (for TX/RX):

| Field | Value |
|-------|-------|
| HVAC Mode Entity | `input_select.test_hvac_mode` |
| Fan Mode Entity | `input_select.test_fan_mode` |
| Preset Mode Entity | `input_select.test_preset_mode` |
| Swing Mode Entity | `input_select.test_swing_mode` |
| Horizontal Swing Entity | `input_select.test_swing_horizontal_mode` |
| Target Temperature Entity | `input_number.test_target_temperature` |
| Target Humidity Entity | `input_number.test_target_humidity` |
| Humidity Sensor | `sensor.test_room_humidity` |

6. Set **Action Scripts** (optional TX overrides):

See Step 3 below — these can be added later via Options Flow.

7. Click **Submit**

### Option B: Via the HA REST API (for LLM automation)

```bash
# 1. Authenticate
HA_URL="http://127.0.0.1:8123"
FLOW=$(curl -s -X POST "${HA_URL}/auth/login_flow" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"'"${HA_URL}/"'","handler":["homeassistant",null],"redirect_uri":"'"${HA_URL}/"'"}')
FLOW_ID=$(echo "$FLOW" | python3 -c "import sys,json; print(json.load(sys.stdin)['flow_id'])")

AUTH_RESULT=$(curl -s -X POST "${HA_URL}/auth/login_flow/${FLOW_ID}" \
  -H "Content-Type: application/json" \
  -d '{"username":"alan","password":"7","client_id":"'"${HA_URL}/"'"}')
AUTH_CODE=$(echo "$AUTH_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])")

TOKEN=$(curl -s -X POST "${HA_URL}/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "client_id=${HA_URL}/" \
  --data-urlencode "code=${AUTH_CODE}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Start config flow
FLOW=$(curl -s -X POST "${HA_URL}/api/config/config_entries/flow" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"handler":"climate_template"}')
FLOW_ID=$(echo "$FLOW" | python3 -c "import sys,json; print(json.load(sys.stdin)['flow_id'])")

# 3. Submit mode selection (simple)
curl -s -X POST "${HA_URL}/api/config/config_entries/flow/${FLOW_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"config_mode":"simple"}'

# 4. Submit full configuration
curl -s -X POST "${HA_URL}/api/config/config_entries/flow/${FLOW_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Climate (Full TX/RX)",
    "temperature_sensor": "sensor.test_room_temperature",
    "heater": "input_boolean.test_heater",
    "cooler": "input_boolean.test_ac_unit",
    "ac_mode": false,
    "hvac_modes": ["off", "heat", "cool", "heat_cool"],
    "min_temp": 7.0,
    "max_temp": 35.0,
    "temp_step": 0.5,
    "fan_modes": ["auto", "low", "medium", "high"],
    "preset_modes": ["eco", "comfort", "away", "boost", "home", "sleep", "activity"],
    "swing_modes": ["on", "off"],
    "swing_horizontal_modes": ["on", "off"],
    "hvac_mode_entity": "input_select.test_hvac_mode",
    "fan_mode_entity": "input_select.test_fan_mode",
    "preset_mode_entity": "input_select.test_preset_mode",
    "swing_mode_entity": "input_select.test_swing_mode",
    "swing_horizontal_mode_entity": "input_select.test_swing_horizontal_mode",
    "target_temperature_entity": "input_number.test_target_temperature",
    "humidity_entity": "input_number.test_target_humidity",
    "humidity_sensor": "sensor.test_room_humidity"
  }'
```

---

## Step 3: Add Action Scripts via Options Flow

Action scripts provide TX override behavior — when the user changes a control,
the action script fires with the new value as a Jinja2 template variable.

### Via the HA REST API

```bash
# 1. Get the config entry ID
ENTRY_ID=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
  "${HA_URL}/api/config/config_entries/entry" \
  | python3 -c "
import sys, json
for e in json.load(sys.stdin):
    if e.get('domain') == 'climate_template':
        print(e['entry_id'])
")

# 2. Start options flow
FLOW=$(curl -s -X POST "${HA_URL}/api/config/config_entries/options/flow" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"handler\":\"${ENTRY_ID}\"}")
FLOW_ID=$(echo "$FLOW" | python3 -c "import sys,json; print(json.load(sys.stdin)['flow_id'])")

# 3. Submit options with all action scripts
curl -s -X POST "${HA_URL}/api/config/config_entries/options/flow/${FLOW_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Climate (Full TX/RX)",
    "temperature_sensor": "sensor.test_room_temperature",
    "heater": "input_boolean.test_heater",
    "cooler": "input_boolean.test_ac_unit",
    "ac_mode": false,
    "hvac_modes": ["off", "heat", "cool", "heat_cool"],
    "min_temp": 7.0,
    "max_temp": 35.0,
    "temp_step": 0.5,
    "fan_modes": ["auto", "low", "medium", "high"],
    "preset_modes": ["eco", "comfort", "away", "boost", "home", "sleep", "activity"],
    "swing_modes": ["on", "off"],
    "swing_horizontal_modes": ["on", "off"],
    "hvac_mode_entity": "input_select.test_hvac_mode",
    "fan_mode_entity": "input_select.test_fan_mode",
    "preset_mode_entity": "input_select.test_preset_mode",
    "swing_mode_entity": "input_select.test_swing_mode",
    "swing_horizontal_mode_entity": "input_select.test_swing_horizontal_mode",
    "target_temperature_entity": "input_number.test_target_temperature",
    "humidity_entity": "input_number.test_target_humidity",
    "humidity_sensor": "sensor.test_room_humidity",
    "set_temperature": [{"action": "input_number.set_value", "target": {"entity_id": "input_number.test_target_temperature"}, "data": {"value": "{{ temperature }}"}}],
    "set_hvac_mode": [{"action": "input_select.select_option", "target": {"entity_id": "input_select.test_hvac_mode"}, "data": {"option": "{{ hvac_mode }}"}}],
    "set_fan_mode": [{"action": "input_select.select_option", "target": {"entity_id": "input_select.test_fan_mode"}, "data": {"option": "{{ fan_mode }}"}}],
    "set_preset_mode": [{"action": "input_select.select_option", "target": {"entity_id": "input_select.test_preset_mode"}, "data": {"option": "{{ preset_mode }}"}}],
    "set_swing_mode": [{"action": "input_select.select_option", "target": {"entity_id": "input_select.test_swing_mode"}, "data": {"option": "{{ swing_mode }}"}}],
    "set_swing_horizontal_mode": [{"action": "input_select.select_option", "target": {"entity_id": "input_select.test_swing_horizontal_mode"}, "data": {"option": "{{ swing_horizontal_mode }}"}}],
    "set_humidity": [{"action": "input_number.set_value", "target": {"entity_id": "input_number.test_target_humidity"}, "data": {"value": "{{ humidity }}"}}]
  }'
```

### Action Script Reference

Each action script receives a Jinja2 template variable with the new value:

| Action Key | Template Variable | Target Service | Example |
|------------|-------------------|----------------|---------|
| `set_temperature` | `{{ temperature }}` | `input_number.set_value` | value: 22.5 |
| `set_hvac_mode` | `{{ hvac_mode }}` | `input_select.select_option` | option: "heat" |
| `set_fan_mode` | `{{ fan_mode }}` | `input_select.select_option` | option: "high" |
| `set_preset_mode` | `{{ preset_mode }}` | `input_select.select_option` | option: "eco" |
| `set_swing_mode` | `{{ swing_mode }}` | `input_select.select_option` | option: "on" |
| `set_swing_horizontal_mode` | `{{ swing_horizontal_mode }}` | `input_select.select_option` | option: "on" |
| `set_humidity` | `{{ humidity }}` | `input_number.set_value` | value: 60 |

---

## Step 4: Verify Everything Works

### Automated Test Script

```bash
./tests/test_e2e_live_tx_rx.sh [username] [password]
# Default: alan / 7
# Set HA_URL env var if not localhost:8123
```

Expected output: **23 PASS / 0 FAIL**

### Manual Verification

**Test TX (Climate Card -> External Entity):**

1. Open the climate card for "Demo Climate (Full TX/RX)"
2. Change fan mode to "high"
3. Go to Developer Tools > States
4. Check `input_select.test_fan_mode` -- should show "high"
5. Repeat for each control (preset, swing, temperature, humidity)

**Test RX (External Entity -> Climate Card):**

1. Go to Developer Tools > States
2. Set `input_select.test_fan_mode` to "low"
3. Check climate card -- fan mode should update to "low"
4. Set `input_number.test_target_temperature` to 28
5. Check climate card -- target temperature should update to 28
6. Drag `input_number.test_room_temp_value` slider to 30
7. Check climate card -- current temperature should update

### Via REST API

```bash
# TX: Set fan mode to "high" via climate service
curl -X POST http://127.0.0.1:8123/api/services/climate/set_fan_mode \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"climate.demo_climate_full_tx_rx","fan_mode":"high"}'

# Verify: Check the target entity changed
curl -s -H "Authorization: Bearer ${TOKEN}" \
  http://127.0.0.1:8123/api/states/input_select.test_fan_mode \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])"
# Expected: high

# RX: Change external entity
curl -X POST http://127.0.0.1:8123/api/services/input_select/select_option \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"entity_id":"input_select.test_fan_mode","option":"low"}'

# Verify: Check climate card updated
curl -s -H "Authorization: Bearer ${TOKEN}" \
  http://127.0.0.1:8123/api/states/climate.demo_climate_full_tx_rx \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['attributes']['fan_mode'])"
# Expected: low
```

---

## How TX Priority Works

When a user taps a control on the climate card, the component uses this priority chain:

```
1. Action script configured?  -->  Run action script (renders Jinja2 template)
2. Entity selector configured? -->  Call appropriate service on target entity
3. Neither?                    -->  Optimistic internal state update only (no TX)
```

When **both** an action script and entity selector are configured for the same
control, the action script takes priority and the entity selector is used only
for RX (state listening).

---

## Cleanup: Delete the Demo Entity

### Via REST API

```bash
# Find the entry ID
ENTRY_ID=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
  "${HA_URL}/api/config/config_entries/entry" \
  | python3 -c "
import sys, json
for e in json.load(sys.stdin):
    if e.get('domain') == 'climate_template':
        print(e['entry_id'])
")

# Delete it
curl -s -X DELETE "${HA_URL}/api/config/config_entries/entry/${ENTRY_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
# Returns: {"require_restart": false}
```

### Via UI

Settings > Devices & Services > Climate Template > ... menu > Delete

---

## Troubleshooting

### Action scripts return 500 error / templates not rendered

Action scripts from the config flow UI store Jinja templates as plain strings.
The component must validate them through `cv.SCRIPT_SCHEMA()` to convert
string templates into HA `Template` objects. If you see errors like
`"Invalid option: {{ fan_mode }}"`, the SCRIPT_SCHEMA validation is missing.

### Entity selector not found

Ensure all helper entities exist in `configuration.yaml` and HA has been
restarted after adding them. Use Developer Tools > States to verify each
entity exists.

### Temperature shows wrong unit

The climate card always displays in the HA **system unit** (Settings > System >
General > Unit System). The `temperature_unit` config option was removed --
the component always uses the system unit.

### RX not working (external changes don't update climate card)

Check that the entity selector field is configured (not just the action script).
Entity selectors provide RX via `async_track_state_change_event`. Action scripts
alone only provide TX.

---

## Complete Options JSON (copy-paste reference)

This is the exact JSON stored in `.storage/core.config_entries` for the demo entity:

```json
{
  "ac_mode": false,
  "config_mode": "simple",
  "cooler": "input_boolean.test_ac_unit",
  "fan_mode_entity": "input_select.test_fan_mode",
  "fan_modes": ["auto", "low", "medium", "high"],
  "heater": "input_boolean.test_heater",
  "humidity_entity": "input_number.test_target_humidity",
  "humidity_sensor": "sensor.test_room_humidity",
  "hvac_mode_entity": "input_select.test_hvac_mode",
  "hvac_modes": ["off", "heat", "cool", "heat_cool"],
  "max_temp": 35.0,
  "min_temp": 7.0,
  "name": "Demo Climate (Full TX/RX)",
  "preset_mode_entity": "input_select.test_preset_mode",
  "preset_modes": ["eco", "comfort", "away", "boost", "home", "sleep", "activity"],
  "set_fan_mode": [{"action": "input_select.select_option", "data": {"option": "{{ fan_mode }}"}, "target": {"entity_id": "input_select.test_fan_mode"}}],
  "set_humidity": [{"action": "input_number.set_value", "data": {"value": "{{ humidity }}"}, "target": {"entity_id": "input_number.test_target_humidity"}}],
  "set_hvac_mode": [{"action": "input_select.select_option", "data": {"option": "{{ hvac_mode }}"}, "target": {"entity_id": "input_select.test_hvac_mode"}}],
  "set_preset_mode": [{"action": "input_select.select_option", "data": {"option": "{{ preset_mode }}"}, "target": {"entity_id": "input_select.test_preset_mode"}}],
  "set_swing_horizontal_mode": [{"action": "input_select.select_option", "data": {"option": "{{ swing_horizontal_mode }}"}, "target": {"entity_id": "input_select.test_swing_horizontal_mode"}}],
  "set_swing_mode": [{"action": "input_select.select_option", "data": {"option": "{{ swing_mode }}"}, "target": {"entity_id": "input_select.test_swing_mode"}}],
  "set_temperature": [{"action": "input_number.set_value", "data": {"value": "{{ temperature }}"}, "target": {"entity_id": "input_number.test_target_temperature"}}],
  "swing_horizontal_mode_entity": "input_select.test_swing_horizontal_mode",
  "swing_horizontal_modes": ["on", "off"],
  "swing_mode_entity": "input_select.test_swing_mode",
  "swing_modes": ["on", "off"],
  "target_temperature_entity": "input_number.test_target_temperature",
  "temp_step": 0.5,
  "temperature_sensor": "sensor.test_room_temperature"
}
```
