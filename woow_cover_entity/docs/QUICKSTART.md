# Quickstart: Full TX/RX Demo Cover Entity

Set up a fully bidirectional cover entity that aggregates helper entities
into one cover card with position tracking, tilt control, and time-based estimation.

**Time:** ~5 minutes
**Result:** `cover.demo_cover_tx_rx` with position, tilt, and time-based estimation

---

## Architecture

```
  Cover Card (UI)                Helper Entities (HA)
  =====================         ==========================

  Position (0-100%)     <--TX-->  input_number.cover_position
  Tilt Position (0-100%) <--TX-->  input_number.cover_tilt
  Stop                  ---TX-->  input_boolean.cover_stop_signal
```

**TX** = When you control the cover card, it sends the value to the external entity.
**RX** = When the external entity changes (e.g., via Developer Tools), the cover card updates.

### Time-Based Position Estimation

For covers without position feedback (e.g., Somfy PoE motors), configure
**Opening Time** and **Closing Time**. The cover estimates position based on elapsed time:

```
  Open command → Timer starts → Position increments every ~1 second
  Stop command → Timer stops → Position freezes at estimated value

  Example: Opening Time = 20s
  After 10s → Position = 50%
  After 20s → Position = 100% (timer auto-stops)
```

---

## Step 1: Add Helper Entities to configuration.yaml

Copy this entire block into your HA `configuration.yaml`:

```yaml
# =====================================================
# WoowTech Cover Entity Demo: Helper Entities
# =====================================================

input_boolean:
  cover_stop_signal:
    name: Cover Stop Signal
    icon: mdi:stop

input_number:
  cover_position:
    name: "Cover Position"
    min: 0
    max: 100
    step: 1
    initial: 0
    mode: slider
    unit_of_measurement: "%"
    icon: mdi:window-shutter
  cover_tilt:
    name: "Cover Tilt Position"
    min: 0
    max: 100
    step: 1
    initial: 0
    mode: slider
    unit_of_measurement: "%"
    icon: mdi:angle-acute
```

## Step 2: Restart Home Assistant

```
Settings > System > Restart
```

After restart, verify helper entities exist in Developer Tools > States:
- `input_number.cover_position` (0)
- `input_number.cover_tilt` (0)
- `input_boolean.cover_stop_signal` (off)

## Step 3: Install the Custom Component

Copy the `custom_components/woow_cover_entity/` folder into your HA `custom_components/` directory:

```
<ha_config>/
  custom_components/
    woow_cover_entity/
      __init__.py
      config_flow.py
      const.py
      cover.py
      manifest.json
      strings.json
```

Restart HA again after copying.

## Step 4: Create the Cover Entity via Config Flow

```
Settings > Devices & Services > Add Integration > WoowTech Cover Entity
```

### Option A: Full TX/RX with Entity Selectors

For covers with external position feedback:

| Field | Value |
|-------|-------|
| **Name** | `Demo Cover TX/RX` |
| **Device Class** | `Blind` |
| **Enable Tilt** | Yes |
| **Position Entity** | `input_number.cover_position` |
| **Tilt Position Entity** | `input_number.cover_tilt` |
| **Stop Cover Action** | `input_boolean.turn_on` target: `input_boolean.cover_stop_signal` |

Click Submit. Entity `cover.demo_cover_tx_rx` is created.

### Option B: Time-Based Position Estimation

For covers without position feedback (e.g., Somfy motors):

| Field | Value |
|-------|-------|
| **Name** | `Demo Timed Cover` |
| **Device Class** | `Shutter` |
| **Enable Tilt** | Yes |
| **Opening Time** | `20` (seconds to fully open) |
| **Closing Time** | `15` (seconds to fully close) |
| **Tilt Opening Time** | `3` (seconds to fully tilt open) |
| **Tilt Closing Time** | `2` (seconds to fully tilt close) |
| **Open Cover Action** | (action to command motor to open) |
| **Close Cover Action** | (action to command motor to close) |
| **Stop Cover Action** | (action to command motor to stop) |

Click Submit. Entity `cover.demo_timed_cover` is created with `SET_POSITION` and `STOP` auto-enabled.

## Step 5: Verify TX (Cover Card -> Helper Entities)

### For Option A (Entity Selector mode):

1. Open the cover card in Lovelace
2. **Press Open** -> `input_number.cover_position` updates to 100
3. **Set position to 50%** -> `input_number.cover_position` updates to 50
4. **Press Close** -> `input_number.cover_position` updates to 0
5. **Open tilt** -> `input_number.cover_tilt` updates to 100
6. **Set tilt to 50%** -> `input_number.cover_tilt` updates to 50
7. **Press Stop** -> stop action script fires

### For Option B (Time-Based mode):

1. Open the cover card in Lovelace
2. **Press Open** -> position starts at 0%, increments every second
3. **Press Stop mid-movement** -> position freezes (e.g., at 50%)
4. **Set position to 75%** -> position moves from current toward 75%
5. **Press Close** -> position decrements every second toward 0%

## Step 6: Verify RX (Helper Entities -> Cover Card)

> **Note:** RX only works in Entity Selector mode (Option A).
> In Time-Based mode, the timer is the position authority and RX is disabled.

1. Go to Developer Tools > States
2. **Set** `input_number.cover_position` **to** `42` -> Cover card shows 42% open
3. **Set** `input_number.cover_position` **to** `0` -> Cover card shows "Closed"
4. **Set** `input_number.cover_position` **to** `100` -> Cover card shows "Open"
5. **Set** `input_number.cover_tilt` **to** `75` -> Cover card shows tilt at 75%

---

## TX/RX Feature Matrix

| Feature | Entity Selector | Action Script | RX Listener | Action Variable |
|---------|:---:|:---:|:---:|:---:|
| **Position** | `position_entity` | `set_position` | `_async_position_entity_changed` | `{{ position }}` (0-100) |
| **Tilt Position** | `tilt_position_entity` | `set_tilt_position` | `_async_tilt_entity_changed` | `{{ tilt_position }}` (0-100) |
| **Open** | -- | `open_cover` | -- | -- |
| **Close** | -- | `close_cover` | -- | -- |
| **Stop** | -- | `stop_cover` | -- | -- |
| **Open Tilt** | -- | `open_tilt` | -- | -- |
| **Close Tilt** | -- | `close_tilt` | -- | -- |
| **Stop Tilt** | -- | `stop_tilt` | -- | -- |

### TX Priority Chain

For each control action, commands are dispatched via the **first available** channel:

| Control Method | Priority 1 (Highest) | Priority 2 | Priority 3 | Priority 4 (Fallback) |
|----------------|:---:|:---:|:---:|:---:|
| **Open** | `open_cover` script | `set_position` script (position=100) | Position entity (set to 100) | Direct set position=100 |
| **Close** | `close_cover` script | `set_position` script (position=0) | Position entity (set to 0) | Direct set position=0 |
| **Stop** | `stop_cover` script | -- | -- | Clear movement flags |
| **Set Position** | `set_position` script | Position entity (set to value) | -- | Direct set position |
| **Open Tilt** | `open_tilt` script | `set_tilt_position` script (tilt=100) | Tilt entity (set to 100) | Direct set tilt=100 |
| **Close Tilt** | `close_tilt` script | `set_tilt_position` script (tilt=0) | Tilt entity (set to 0) | Direct set tilt=0 |
| **Stop Tilt** | `stop_tilt` script | -- | -- | -- |
| **Set Tilt** | `set_tilt_position` script | Tilt entity (set to value) | -- | Direct set tilt |

In **time-based mode**, the timer system handles position updates instead of entity selectors. Action scripts still fire to command the physical motor.

### RX Behavior Details

**Initial Sync:** On startup, the cover reads the current state from the position entity and tilt entity (if configured) and sets its internal position to match. This happens automatically before the cover card appears in the UI.

**RX Listeners:** After startup, the cover subscribes to state changes on the position and tilt entities. When the external entity changes (e.g., via Developer Tools or another automation), the cover card updates immediately.

**RX Validation:**
- States `unavailable` and `unknown` are ignored (no update)
- Values outside 0-100 are rejected
- Non-numeric values are silently ignored
- Setting the same value again does not trigger an update (HA only fires on *changes*)

**RX Disabled in Time-Based Mode:** When time-based estimation is active, RX listeners return early without processing. The timer is the authoritative source for position.

### Entity Domain Restrictions

Entity selectors for **Position Entity** and **Tilt Position Entity** only accept entities from these domains:
- `input_number` (HA helper entities)
- `number` (native number entities from integrations)

Other entity types (e.g., `sensor`, `input_text`) are not supported for TX/RX binding.

### Movement Flags

During cover movement, the entity sets `is_opening` or `is_closing` flags. These control the animated movement indicator in the UI cover card:

- **Opening:** `is_opening=True` when moving toward a higher position
- **Closing:** `is_closing=True` when moving toward a lower position
- **Arrival:** Both flags cleared when position reaches the target (via RX callback or timer completion)
- **Stop:** Both flags cleared immediately when stop is called

## Time-Based Position Estimation

| Config Option | Range | Description |
|---------------|-------|-------------|
| **Opening Time** | 1-300 seconds | Time to fully open (0% -> 100%) |
| **Closing Time** | 1-300 seconds | Time to fully close (100% -> 0%) |
| **Tilt Opening Time** | 0.5-60 seconds | Time for tilt to fully open |
| **Tilt Closing Time** | 0.5-60 seconds | Time for tilt to fully close |

- Both Opening Time and Closing Time must be set together (partial config is ignored with a warning)
- Both Tilt Opening Time and Tilt Closing Time must be set together (same pair validation)
- Time-based mode auto-enables `SET_POSITION` and `STOP` features
- Tilt time-based mode auto-enables `SET_TILT_POSITION` and `STOP_TILT` features (when Enable Tilt is also on)
- When time-based mode is active, RX from position entity is disabled (timer is authoritative)
- When tilt time-based mode is active, RX from tilt entity is disabled
- Position updates every ~1 second during movement
- Open/close times can differ (closing is often faster due to gravity)
- If position is unknown at the start of movement, it defaults to 0 (fully closed)

---

## Supported Features (Auto-Detection)

The supported features are dynamically determined from your config:

| Feature | Enabled When |
|---------|-------------|
| `OPEN` + `CLOSE` | Always |
| `SET_POSITION` | position_entity OR set_position action OR time-based mode |
| `STOP` | stop_cover action OR time-based mode |
| `OPEN_TILT` + `CLOSE_TILT` | Enable Tilt = Yes |
| `SET_TILT_POSITION` | tilt_position_entity OR set_tilt_position action OR tilt time-based mode |
| `STOP_TILT` | stop_tilt action OR tilt time-based mode |

---

## Device Classes

The following device classes are available in the config flow dropdown:

| Value | Label | Typical Use |
|-------|-------|-------------|
| `awning` | Awning | Retractable awnings |
| `blind` | Blind | Window blinds with tilt |
| `curtain` | Curtain | Fabric curtains |
| `damper` | Damper | HVAC dampers |
| `door` | Door | Doors and hatches |
| `garage` | Garage | Garage doors |
| `gate` | Gate | Entry gates |
| `shade` | Shade | Window shades |
| `shutter` | Shutter | Rolling shutters |
| `window` | Window | Operable windows |

Device class is optional. It affects the icon and terminology shown in the UI.

---

## State Restoration

The cover entity uses Home Assistant's `RestoreEntity` pattern. On HA restart:

- **Position** is restored to its last known value before shutdown
- **Tilt position** is restored (if tilt is enabled)
- No movement is in progress after restart (timers are not restored)

If both state restoration and an RX entity are configured, the entity selector state takes precedence (initial sync overrides the restored value).

---

## Validation and Edge Cases

**Pair Validation:**
- If only `Opening Time` is set without `Closing Time` (or vice versa), the partial config is ignored with a warning in the HA log
- Same applies for `Tilt Opening Time` / `Tilt Closing Time` pair
- The entity will still work, just without time-based estimation

**Position Clamping:**
- All position values are clamped to the 0-100 range
- RX values outside 0-100 are rejected (not applied)
- Timer ticks never overshoot the target or boundary

**Invalid Device Class:**
- If an unrecognized device class string is configured, a warning is logged and no device class is set

**No TX Target Configured:**
- If no entity selector, action script, or time-based mode is configured for a control, the position is set directly in memory
- Open sets position to 100, Close sets to 0
- This is useful for testing the UI card without any external entities

---

## Troubleshooting

**Cover shows "unavailable":**
- Check that the custom component is loaded: HA logs should show "Setting up woow_cover_entity"
- Verify helper entities exist in Developer Tools > States

**TX not working (cover card doesn't update helpers):**
- Ensure entity selectors point to the correct helper entities
- Check HA logs for errors from `custom_components.woow_cover_entity.cover`

**RX not working (helper changes don't update cover card):**
- RX only works in Entity Selector mode, NOT in Time-Based mode
- RX listeners only trigger on state *changes* -- setting the same value again won't trigger
- Verify position value is a valid number between 0-100

**Time-based position not updating:**
- Verify both Opening Time AND Closing Time are configured (both are required)
- Verify both Tilt Opening Time AND Tilt Closing Time if using tilt time-based mode
- Check HA logs for "Both open_time and close_time must be configured" or "Both tilt_open_time and tilt_close_time must be configured" warnings
- Position starts from 0 (or last restored position) -- you may need to open first

**Position drift in time-based mode:**
- The timer fires every ~1 second with ~1 second precision
- For a 20s travel time, actual travel may vary by +/- 1 second
- This is acceptable for blind/shutter motors which have mechanical variance
