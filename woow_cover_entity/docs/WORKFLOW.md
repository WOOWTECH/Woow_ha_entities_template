# Implementation Workflow: WoowTech Cover Entity

## Phase 1: Project Skeleton

### Step 1.1: Create project files
- [x] `DESIGN.md` — Architecture document
- [x] `WORKFLOW.md` — This file
- [ ] `.gitignore`
- [ ] `pyproject.toml`
- [ ] `tests/__init__.py`

### Step 1.2: Initialize git repository
- [ ] `git init`
- [ ] Initial commit with skeleton files

## Phase 2: Source Implementation

### Step 2.1: const.py
Constants for domain, platforms, configuration keys, defaults.
- Domain: `woow_cover_entity`
- Platform: `cover`
- Config keys: all entity selectors, action scripts, feature flags
- Defaults: name, device class

### Step 2.2: manifest.json
Integration metadata with domain, name, config_flow, version.

### Step 2.3: strings.json
UI labels for config flow and options flow steps.

### Step 2.4: __init__.py
Standard HA integration setup:
- `async_setup()` — no-op
- `async_setup_entry()` — forward to cover platform, register options listener
- `async_update_options()` — reload on options change
- `async_unload_entry()` — unload platforms, cleanup data

### Step 2.5: config_flow.py
SchemaConfigFlowHandler with:
- CONFIG_SCHEMA: name, device_class, enable_tilt, position_entity, tilt_position_entity, all action scripts
- OPTIONS_SCHEMA: same fields minus name
- CONFIG_FLOW + OPTIONS_FLOW dicts
- WoowCoverEntityConfigFlowHandler class

### Step 2.6: cover.py
SimpleCover entity class:
1. `__init__()` — Initialize all attributes, set supported_features
2. `async_added_to_hass()` — Register RX listeners, sync initial state, restore state
3. TX helper: `_async_set_entity_state()` — Send value to external entity by domain
4. RX callbacks: `_async_position_entity_changed()`, `_async_tilt_entity_changed()`
5. Cover methods: `async_open_cover()`, `async_close_cover()`, `async_stop_cover()`, `async_set_cover_position()`
6. Tilt methods: `async_open_cover_tilt()`, `async_close_cover_tilt()`, `async_stop_cover_tilt()`, `async_set_cover_tilt_position()`

## Phase 3: Test Implementation

### Step 3.1: test_simple_cover.py
Core cover operations without entity selectors:
- Open/close/stop
- Position set (0, 50, 100)
- Tilt open/close/stop
- Tilt position set
- State derivation (is_closed from position)
- State restoration
- Device class
- Supported features

### Step 3.2: test_entity_aggregation.py
TX/RX with entity selectors and action scripts:
- Position entity TX (set_cover_position → input_number updates)
- Position entity RX (input_number change → cover position updates)
- Tilt entity TX/RX
- Action script overrides for all 8 commands
- Initial state sync
- TX priority chain

### Step 3.3: test_options_flow.py
Config entry and flow tests:
- Entry creation + setup
- Entry unload
- Options flow
- Config flow user step
- Full entry with all features

### Step 3.4: Run tests
- `pytest tests/ -v`
- Fix any failures
- Target: 60+ tests all passing

## Phase 4: Documentation

### Step 4.1: README.md
Comprehensive project documentation.

### Step 4.2: docs/QUICKSTART.md
Step-by-step demo setup guide.

### Step 4.3: example_configuration.yaml
Helper entities for testing.

## Phase 5: Deployment & Verification

### Step 5.1: Deploy to HA
- Add helper entities to `/Users/alanlin/core/config/configuration.yaml`
- Copy component to `/Users/alanlin/core/config/custom_components/woow_cover_entity/`
- Also copy to `/Users/alanlin/core/custom_components/woow_cover_entity/`
- Restart HA

### Step 5.2: Live TX/RX verification
- Create demo entity via config flow
- Verify TX: cover card → helper entities
- Verify RX: helper entities → cover card

### Step 5.3: Git tag
- Commit all files
- Tag `v1.0.0`
