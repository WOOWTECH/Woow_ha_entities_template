# Comprehensive Testing Plan for Climate Template Integration

## Overview

This document outlines the comprehensive testing strategy for the Climate Template custom component's new template support features, covering both Simple Mode (entity selectors) and Advanced Mode (Jinja2 templates and action scripts).

## Project Information

- **Project Location:** `/Users/alanlin/hass-template-climate-impl/`
- **Test Entities Configuration:** See `TEST_ENTITIES_CONFIG.yaml`
- **Home Assistant Core Location:** `/Users/alanlin/core/`

## Testing Architecture

### Test Pyramid Strategy

```
                    /\
                   /  \
                  / E2E \          <- Playwright UI Tests (10%)
                 /______\
                /        \
               /   API    \        <- Integration Tests (30%)
              /____________\
             /              \
            /   Unit Tests   \    <- Unit Tests (60%)
           /___________________\
```

### Test Coverage Goals

- **Unit Tests:** 90% code coverage
- **Integration Tests:** All critical user flows
- **E2E Tests:** Complete user journeys for both modes
- **Performance Tests:** Template rendering under load

---

## 1. Test Environment Setup

### 1.1 Test Entities

All test entities are defined in `TEST_ENTITIES_CONFIG.yaml`. Add this configuration to:

```
/Users/alanlin/core/config/configuration.yaml
```

**Key Test Entities:**

**Temperature Sensors:**
- `sensor.test_room_temperature` (21.5°C) - Primary test sensor
- `sensor.test_outdoor_temperature` (-5°C) - For multi-sensor templates
- `sensor.test_average_temperature` - Template sensor (average of room + outdoor)
- `sensor.test_humidity` (65%) - Humidity testing
- `sensor.test_unreliable_temperature` - Intermittently unavailable sensor

**Control Entities:**
- `input_boolean.test_heater` - Heater control
- `input_boolean.test_ac` - AC control
- `input_boolean.test_fan` - Fan control
- `input_select.test_hvac_mode` - HVAC mode selector
- `input_select.test_fan_mode` - Fan mode selector
- `input_select.test_preset_mode` - Preset mode selector
- `input_number.test_target_temp` - Target temperature (7-35°C, step 0.5)

**Mock Climate Entity:**
- `climate.test_real_thermostat` - For testing template reading from existing climate

### 1.2 Test Data Fixtures

Create `tests/fixtures.py` with:
- Mock Home Assistant instance
- Mock entity registry
- Mock state machine
- Template rendering engine fixtures
- Action script execution mocks

---

## 2. Unit Tests

### 2.1 Test File: `tests/test_template_fields.py`

**Purpose:** Test template field handling, validation, and rendering

**Test Cases:**

#### Template Reading Tests

1. **test_simple_entity_state_template**
   - Template: `{{ states('sensor.test_room_temperature') }}`
   - Expected: Returns 21.5
   - Validates: Basic state reading

2. **test_calculated_temperature_template**
   - Template: `{{ (states('sensor.test_room_temperature') | float + states('sensor.test_outdoor_temperature') | float) / 2 }}`
   - Expected: Returns 8.25 ((21.5 + -5) / 2)
   - Validates: Mathematical operations in templates

3. **test_hvac_mode_template_from_input_select**
   - Template: `{{ states('input_select.test_hvac_mode') }}`
   - Expected: Returns current mode value
   - Validates: Reading from input_select

4. **test_hvac_action_conditional_template**
   - Template:
     ```jinja2
     {% if is_state('input_boolean.test_heater', 'on') %}
       heating
     {% elif is_state('input_boolean.test_ac', 'on') %}
       cooling
     {% else %}
       idle
     {% endif %}
     ```
   - Expected: Returns appropriate action based on states
   - Validates: Conditional logic in templates

5. **test_template_with_unavailable_entity**
   - Template: `{{ states('sensor.nonexistent') }}`
   - Expected: Returns 'unknown' or handles gracefully
   - Validates: Error handling for missing entities

6. **test_template_with_invalid_syntax**
   - Template: `{{ states('sensor.test') | invalid_filter }}`
   - Expected: Raises TemplateError
   - Validates: Template validation

7. **test_template_preview_rendering**
   - Template: `{{ states('sensor.test_room_temperature') }}`
   - Expected: Returns current evaluated value with timestamp
   - Validates: Preview functionality

8. **test_numeric_template_conversion**
   - Template: `{{ states('sensor.test_room_temperature') | float }}`
   - Expected: Returns float value 21.5
   - Validates: Type conversion

9. **test_template_with_default_value**
   - Template: `{{ states('sensor.test_room_temperature') | float(20) }}`
   - Expected: Returns 21.5 (or 20 if unavailable)
   - Validates: Default value handling

10. **test_multi_entity_template**
    - Template: `{{ [states('sensor.test_room_temperature'), states('sensor.test_outdoor_temperature')] | max }}`
    - Expected: Returns 21.5
    - Validates: Multiple entity references

#### Template Validation Tests

11. **test_empty_template_validation**
    - Template: ``
    - Expected: No error, treated as None
    - Validates: Empty template handling

12. **test_malformed_jinja_syntax**
    - Template: `{{ states('sensor.test' }}`
    - Expected: ValidationError with helpful message
    - Validates: Syntax error reporting

13. **test_template_with_undefined_variable**
    - Template: `{{ undefined_var }}`
    - Expected: TemplateError
    - Validates: Variable validation

14. **test_template_circular_reference**
    - Template referencing entity that references back
    - Expected: Detects and prevents infinite loop
    - Validates: Circular dependency detection

---

### 2.2 Test File: `tests/test_action_scripts.py`

**Purpose:** Test action script execution, variable passing, and error handling

**Test Cases:**

#### Action Script Execution Tests

1. **test_set_temperature_action_basic**
   - Action:
     ```yaml
     - service: input_number.set_value
       target:
         entity_id: input_number.test_target_temp
       data:
         value: "{{ temperature }}"
     ```
   - Input: temperature=22.5
   - Expected: input_number.test_target_temp set to 22.5
   - Validates: Basic action execution with variable

2. **test_set_hvac_mode_action**
   - Action:
     ```yaml
     - service: input_select.select_option
       target:
         entity_id: input_select.test_hvac_mode
       data:
         option: "{{ hvac_mode }}"
     ```
   - Input: hvac_mode='heat'
   - Expected: input_select.test_hvac_mode set to 'heat'
   - Validates: Mode setting action

3. **test_action_with_multiple_steps**
   - Action:
     ```yaml
     - service: input_number.set_value
       target:
         entity_id: input_number.test_target_temp
       data:
         value: "{{ temperature }}"
     - service: input_boolean.turn_on
       target:
         entity_id: input_boolean.test_heater
     ```
   - Expected: Both actions execute in sequence
   - Validates: Multi-step actions

4. **test_action_with_conditional**
   - Action:
     ```yaml
     - condition: template
       value_template: "{{ temperature > 20 }}"
     - service: input_boolean.turn_on
       target:
         entity_id: input_boolean.test_ac
     ```
   - Expected: AC turns on only if temperature > 20
   - Validates: Conditional action execution

5. **test_action_with_all_variables**
   - Variables: temperature, hvac_mode, fan_mode, preset_mode
   - Expected: All variables accessible in action script
   - Validates: Complete variable context

#### Action Error Handling Tests

6. **test_action_service_not_found**
   - Action: Call non-existent service
   - Expected: Logs error, doesn't crash
   - Validates: Service error handling

7. **test_action_invalid_entity**
   - Action: Target non-existent entity
   - Expected: Logs warning, continues
   - Validates: Entity validation

8. **test_action_timeout**
   - Action: Service that takes too long
   - Expected: Times out gracefully
   - Validates: Timeout handling

9. **test_action_permission_denied**
   - Action: Call restricted service
   - Expected: Permission error handled
   - Validates: Permission checking

10. **test_action_with_invalid_template_variable**
    - Action: Use undefined variable
    - Expected: Error with helpful message
    - Validates: Variable validation in actions

---

### 2.3 Test File: `tests/test_mode_validation.py`

**Purpose:** Test Simple vs Advanced mode validation and constraints

**Test Cases:**

1. **test_simple_mode_requires_entities**
   - Config: Simple mode without temperature sensor
   - Expected: ValidationError
   - Validates: Required entity validation

2. **test_advanced_mode_allows_optional_entities**
   - Config: Advanced mode with only templates
   - Expected: Valid configuration
   - Validates: Template-only configuration

3. **test_mode_field_mutual_exclusivity**
   - Config: Both entity selector AND template for same field
   - Expected: Template takes precedence
   - Validates: Field priority handling

4. **test_template_field_none_option**
   - Config: Template field set to "None"
   - Expected: Field ignored, no template applied
   - Validates: None option handling

5. **test_simple_mode_entity_validation**
   - Config: Invalid entity ID in simple mode
   - Expected: ValidationError with entity not found
   - Validates: Entity existence checking

---

## 3. Integration Tests

### 3.1 Test File: `tests/test_advanced_mode.py`

**Purpose:** Integration tests for Advanced Mode features

**Test Cases:**

#### Template Integration Tests

1. **test_temperature_template_integration**
   - Setup: Create climate with current_temperature_template
   - Template: `{{ (states('sensor.test_room_temperature') | float + states('sensor.test_outdoor_temperature') | float) / 2 }}`
   - Action: Update sensor values
   - Expected: Climate current_temperature updates to calculated value
   - Validates: End-to-end template rendering

2. **test_hvac_mode_template_integration**
   - Setup: Create climate with hvac_mode_template
   - Template: `{{ states('input_select.test_hvac_mode') }}`
   - Action: Change input_select
   - Expected: Climate HVAC mode updates
   - Validates: Mode template integration

3. **test_hvac_action_template_integration**
   - Setup: Create climate with hvac_action_template
   - Template: Conditional based on heater/cooler state
   - Action: Turn on heater
   - Expected: Climate shows 'heating' action
   - Validates: Action template integration

4. **test_fan_mode_template_integration**
   - Setup: Create climate with fan_mode_template
   - Template: `{{ states('input_select.test_fan_mode') }}`
   - Action: Change fan mode
   - Expected: Climate fan_mode updates
   - Validates: Fan mode template

5. **test_preset_mode_template_integration**
   - Setup: Create climate with preset_mode_template
   - Template: `{{ states('input_select.test_preset_mode') }}`
   - Action: Change preset
   - Expected: Climate preset_mode updates
   - Validates: Preset template

#### Action Script Integration Tests

6. **test_set_temperature_action_integration**
   - Setup: Climate with set_temperature action script
   - Action: Call climate.set_temperature service
   - Expected: Action script executes, target_temp updates
   - Validates: Temperature action integration

7. **test_set_hvac_mode_action_integration**
   - Setup: Climate with set_hvac_mode action script
   - Action: Call climate.set_hvac_mode service
   - Expected: Action script executes, mode changes
   - Validates: HVAC mode action integration

8. **test_set_fan_mode_action_integration**
   - Setup: Climate with set_fan_mode action script
   - Action: Call climate.set_fan_mode service
   - Expected: Action script executes, fan mode changes
   - Validates: Fan mode action integration

9. **test_set_preset_mode_action_integration**
   - Setup: Climate with set_preset_mode action script
   - Action: Call climate.set_preset_mode service
   - Expected: Action script executes, preset changes
   - Validates: Preset action integration

10. **test_action_with_multiple_targets**
    - Setup: Action script that controls multiple entities
    - Action: Call climate service
    - Expected: All target entities update
    - Validates: Multi-target actions

#### State Management Tests

11. **test_template_state_persistence**
    - Setup: Climate with templates
    - Action: Restart Home Assistant
    - Expected: Last state restored correctly
    - Validates: State restoration

12. **test_optimistic_vs_template_mode**
    - Setup: Climate with set action but no read template
    - Action: Set temperature
    - Expected: Optimistic update, then template read
    - Validates: Optimistic state handling

13. **test_template_dependency_tracking**
    - Setup: Climate with template
    - Action: Update dependent entity
    - Expected: Climate updates automatically
    - Validates: Entity dependency tracking

14. **test_template_error_recovery**
    - Setup: Climate with template
    - Action: Make template fail, then recover
    - Expected: Climate shows unavailable, then recovers
    - Validates: Error recovery

---

### 3.2 Test File: `tests/test_mode_migration.py`

**Purpose:** Test migration from Simple to Advanced mode

**Test Cases:**

1. **test_simple_to_advanced_migration**
   - Setup: Create Simple mode climate
   - Action: Reconfigure to Advanced mode via options flow
   - Expected: Configuration migrated, templates pre-populated
   - Validates: Basic migration

2. **test_migration_preserves_state**
   - Setup: Simple mode climate with specific state
   - Action: Migrate to Advanced mode
   - Expected: Target temperature, HVAC mode preserved
   - Validates: State preservation

3. **test_migration_generates_equivalent_templates**
   - Setup: Simple mode with sensor.test_room_temperature
   - Action: Migrate to Advanced
   - Expected: Template generated: `{{ states('sensor.test_room_temperature') }}`
   - Validates: Template generation

4. **test_migration_action_script_generation**
   - Setup: Simple mode with heater entity
   - Action: Migrate to Advanced
   - Expected: Action scripts generated for turn_on/turn_off
   - Validates: Action generation

5. **test_migration_preserves_options**
   - Setup: Simple mode with fan modes, presets
   - Action: Migrate to Advanced
   - Expected: All options preserved
   - Validates: Option preservation

6. **test_advanced_to_simple_warning**
   - Setup: Advanced mode with complex templates
   - Action: Try to migrate to Simple mode
   - Expected: Warning about data loss
   - Validates: Downgrade protection

7. **test_migration_unique_id_preservation**
   - Setup: Simple mode climate
   - Action: Migrate to Advanced
   - Expected: Unique ID unchanged
   - Validates: Entity ID stability

---

### 3.3 Test File: `tests/test_simple_mode.py`

**Purpose:** Integration tests for Simple Mode (existing functionality)

**Test Cases:**

1. **test_simple_mode_basic_operation**
   - Setup: Create Simple mode climate
   - Action: Set temperature, change mode
   - Expected: Heater turns on/off appropriately
   - Validates: Basic thermostat functionality

2. **test_simple_mode_ac_mode**
   - Setup: Simple mode with AC mode enabled
   - Action: Set temperature below current
   - Expected: Cooler turns on
   - Validates: AC mode operation

3. **test_simple_mode_tolerance**
   - Setup: Simple mode with cold/hot tolerance
   - Action: Temperature fluctuates within tolerance
   - Expected: Heater doesn't cycle unnecessarily
   - Validates: Tolerance handling

4. **test_simple_mode_preset_modes**
   - Setup: Simple mode with presets
   - Action: Change preset
   - Expected: Preset changes, can set preset temperatures
   - Validates: Preset functionality

---

## 4. UI/E2E Tests (Playwright)

### 4.1 Test File: `tests/test_config_flow_ui.py`

**Purpose:** End-to-end UI tests for configuration flow

**Test Cases:**

#### Initial Setup Tests

1. **test_config_flow_appears_in_integrations**
   - Action: Navigate to Integrations page
   - Expected: "Climate Template" appears in integration list
   - Validates: Integration visibility

2. **test_mode_selection_radio_buttons**
   - Action: Start config flow
   - Expected: Radio buttons for Simple/Advanced mode appear
   - Validates: Mode selection UI

3. **test_simple_mode_shows_entity_selectors**
   - Action: Select Simple mode
   - Expected: Entity selector dropdowns appear
   - Validates: Simple mode UI

4. **test_advanced_mode_shows_template_fields**
   - Action: Select Advanced mode
   - Expected: Template text fields with editor appear
   - Validates: Advanced mode UI

#### Template Field UI Tests

5. **test_template_field_three_modes**
   - Field: current_temperature_template
   - Expected: Three options visible: Entity | Template | None
   - Validates: Field mode selection

6. **test_template_field_entity_mode**
   - Action: Select "Entity" mode for temperature
   - Expected: Entity selector dropdown appears
   - Validates: Entity selector mode

7. **test_template_field_template_mode**
   - Action: Select "Template" mode for temperature
   - Expected: Code editor with Jinja2 syntax highlighting appears
   - Validates: Template editor mode

8. **test_template_field_none_mode**
   - Action: Select "None" mode for optional field
   - Expected: Field disabled, no value required
   - Validates: None mode handling

#### Template Validation UI Tests

9. **test_template_validation_error_display**
   - Action: Enter invalid template syntax
   - Expected: Red error message appears below field
   - Validates: Validation error UI

10. **test_template_preview_shows_current_value**
    - Action: Enter valid template
    - Expected: Preview shows "Current value: 21.5°C"
    - Validates: Template preview

11. **test_template_preview_updates_on_change**
    - Action: Modify template
    - Expected: Preview updates in real-time
    - Validates: Live preview

12. **test_template_syntax_highlighting**
    - Action: Type template code
    - Expected: Keywords, filters, variables highlighted
    - Validates: Syntax highlighting

#### Action Script UI Tests

13. **test_action_script_editor_button**
    - Action: Click "Edit Action" button
    - Expected: Action script editor dialog opens
    - Validates: Editor dialog

14. **test_action_script_visual_mode**
    - Action: Select "Visual" mode in editor
    - Expected: Service selector and data fields appear
    - Validates: Visual editor

15. **test_action_script_yaml_mode**
    - Action: Select "YAML" mode in editor
    - Expected: YAML code editor appears
    - Validates: YAML editor

16. **test_action_script_yaml_visual_toggle**
    - Action: Switch between YAML and Visual modes
    - Expected: Content converts between formats
    - Validates: Mode switching

17. **test_action_script_variable_hints**
    - Action: Open action editor for set_temperature
    - Expected: Hint shows "Available: temperature, hvac_mode"
    - Validates: Variable documentation

18. **test_action_script_validation**
    - Action: Enter invalid YAML
    - Expected: Validation error appears
    - Validates: Action validation

#### Complete Flow Tests

19. **test_complete_simple_mode_setup**
    - Action: Complete entire Simple mode setup
    - Expected: Climate entity created successfully
    - Validates: End-to-end Simple mode flow

20. **test_complete_advanced_mode_setup**
    - Action: Complete entire Advanced mode setup with templates
    - Expected: Climate entity created successfully
    - Validates: End-to-end Advanced mode flow

21. **test_form_field_validation**
    - Action: Try to submit with missing required fields
    - Expected: Form shows validation errors
    - Validates: Required field validation

22. **test_help_text_displays**
    - Action: Hover over help icons
    - Expected: Helpful tooltips appear
    - Validates: User help

---

### 4.2 Test File: `tests/test_options_flow_ui.py`

**Purpose:** UI tests for options/reconfiguration flow

**Test Cases:**

1. **test_open_options_flow**
   - Action: Click "Configure" on existing climate
   - Expected: Options dialog opens with current values
   - Validates: Options flow access

2. **test_options_show_current_values**
   - Setup: Climate with specific configuration
   - Action: Open options
   - Expected: All current values pre-populated
   - Validates: Value population

3. **test_change_simple_to_advanced_ui**
   - Action: Switch mode from Simple to Advanced
   - Expected: Warning dialog, then template fields appear
   - Validates: Mode change UI

4. **test_template_prepopulation_on_migration**
   - Setup: Simple mode with sensor
   - Action: Switch to Advanced mode
   - Expected: Templates pre-populated with equivalent values
   - Validates: Migration assistance

5. **test_modify_existing_templates**
   - Setup: Advanced mode climate
   - Action: Modify template in options
   - Expected: Changes saved, climate updates
   - Validates: Template modification

6. **test_modify_action_scripts**
   - Setup: Climate with action scripts
   - Action: Modify action in options
   - Expected: Action updated, works correctly
   - Validates: Action modification

7. **test_options_validation**
   - Action: Enter invalid configuration in options
   - Expected: Validation errors prevent save
   - Validates: Options validation

8. **test_cancel_options_flow**
   - Action: Make changes, then click Cancel
   - Expected: Changes discarded, original config remains
   - Validates: Cancel handling

---

## 5. Performance Tests

### 5.1 Test File: `tests/test_performance.py`

**Purpose:** Performance and load testing

**Test Cases:**

1. **test_template_rendering_speed**
   - Action: Render complex template 1000 times
   - Expected: Average render time < 10ms
   - Validates: Template performance

2. **test_multiple_climates_performance**
   - Setup: Create 50 climate entities
   - Action: Update all sensor values
   - Expected: All climates update within 1 second
   - Validates: Scalability

3. **test_action_script_execution_speed**
   - Action: Execute action script 100 times
   - Expected: Average execution < 50ms
   - Validates: Action performance

4. **test_memory_usage**
   - Setup: Create climates with templates
   - Action: Monitor memory over 1 hour
   - Expected: No memory leaks detected
   - Validates: Memory management

5. **test_template_caching**
   - Action: Render same template multiple times
   - Expected: Subsequent renders faster (cached)
   - Validates: Template caching

---

## 6. Error Handling Tests

### 6.1 Test File: `tests/test_error_handling.py`

**Purpose:** Error scenarios and edge cases

**Test Cases:**

1. **test_template_syntax_error_handling**
   - Setup: Climate with invalid template
   - Expected: Error logged, entity shows unavailable
   - Validates: Syntax error handling

2. **test_missing_entity_in_template**
   - Template: References non-existent entity
   - Expected: Template returns 'unknown', logs warning
   - Validates: Missing entity handling

3. **test_action_failure_recovery**
   - Action: Script fails due to service error
   - Expected: Error logged, climate remains functional
   - Validates: Action error recovery

4. **test_circular_template_dependency**
   - Setup: Templates that reference each other
   - Expected: Detects circular dependency, prevents loop
   - Validates: Circular dependency protection

5. **test_template_timeout**
   - Template: Extremely complex calculation
   - Expected: Times out gracefully after 5 seconds
   - Validates: Timeout protection

6. **test_invalid_template_return_type**
   - Template: Returns list instead of number
   - Expected: Type conversion error handled gracefully
   - Validates: Type validation

7. **test_entity_state_unavailable**
   - Setup: Template reading unavailable entity
   - Expected: Climate shows unavailable, recovers when entity returns
   - Validates: Unavailable state handling

8. **test_home_assistant_restart_recovery**
   - Action: Restart HA while climate active
   - Expected: Climate restores state correctly
   - Validates: Restart handling

---

## 7. Accessibility Tests

### 7.1 Test File: `tests/test_accessibility.py`

**Purpose:** Ensure UI is accessible

**Test Cases:**

1. **test_screen_reader_labels**
   - Expected: All form fields have proper ARIA labels
   - Validates: Screen reader compatibility

2. **test_keyboard_navigation**
   - Action: Navigate form using only keyboard
   - Expected: All fields accessible, logical tab order
   - Validates: Keyboard accessibility

3. **test_color_contrast**
   - Expected: All text meets WCAG AA contrast requirements
   - Validates: Visual accessibility

4. **test_error_announcements**
   - Action: Trigger validation error
   - Expected: Error announced to screen reader
   - Validates: Error accessibility

---

## 8. Regression Tests

### 8.1 Test File: `tests/test_regression.py`

**Purpose:** Ensure existing functionality not broken

**Test Cases:**

1. **test_yaml_configuration_still_works**
   - Setup: YAML-configured climate
   - Expected: Still functions correctly
   - Validates: Backward compatibility

2. **test_existing_simple_climates_unchanged**
   - Setup: Existing Simple mode climate
   - Action: Update HA
   - Expected: No changes to behavior
   - Validates: Upgrade compatibility

3. **test_entity_id_stability**
   - Setup: Existing climate
   - Action: Modify via options
   - Expected: Entity ID unchanged
   - Validates: Entity ID preservation

---

## 9. Test Execution Strategy

### 9.1 Test Execution Order

1. **Pre-commit:** Unit tests (fast, < 1 minute)
2. **CI Pipeline:** All unit + integration tests (< 5 minutes)
3. **Nightly:** Full suite including E2E and performance (< 30 minutes)
4. **Pre-release:** Complete regression suite (< 1 hour)

### 9.2 Test Environment Matrix

**Python Versions:**
- Python 3.11 (minimum supported)
- Python 3.12 (recommended)
- Python 3.13 (latest)

**Home Assistant Versions:**
- Latest stable
- Latest beta
- Latest dev

**Browsers (for E2E):**
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### 9.3 Test Data Management

- **Fixtures:** Stored in `tests/fixtures/`
- **Mock Data:** Generated dynamically in test setup
- **Test Entities:** Defined in configuration YAML
- **Test Isolation:** Each test uses fresh HA instance

### 9.4 Continuous Integration

**GitHub Actions Workflow:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/test_*.py -v

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: pytest tests/ -m integration -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Playwright tests
        run: pytest tests/ -m e2e -v
```

---

## 10. Test Metrics and Reporting

### 10.1 Coverage Requirements

- **Overall Code Coverage:** > 90%
- **Critical Paths:** 100% coverage
- **Template Rendering:** 100% coverage
- **Action Execution:** 100% coverage
- **UI Flows:** > 80% coverage

### 10.2 Test Reports

**Generated Reports:**
- HTML coverage report (pytest-cov)
- JUnit XML for CI integration
- Allure test report for visualization
- Performance benchmark results

### 10.3 Quality Gates

**Required for PR Merge:**
- All unit tests pass
- All integration tests pass
- Code coverage > 90%
- No new linting errors
- E2E tests pass (on main branch)

---

## 11. Test Maintenance

### 11.1 Test Review Schedule

- **Weekly:** Review failed tests, update flaky tests
- **Monthly:** Review test coverage, add missing tests
- **Quarterly:** Refactor tests, improve test architecture

### 11.2 Test Documentation

- Keep this testing plan updated
- Document new test patterns
- Maintain test fixture documentation
- Update test entity configurations

---

## 12. Known Issues and Limitations

### 12.1 Current Limitations

1. **Template Validation:** Cannot validate entity existence at config time
2. **Action Testing:** Difficult to test actual hardware control
3. **UI Testing:** Playwright tests may be flaky on CI
4. **Performance:** Template rendering performance varies by complexity

### 12.2 Future Improvements

1. Implement static template analysis
2. Add mutation testing for critical paths
3. Improve test isolation and speed
4. Add visual regression testing
5. Implement property-based testing for templates

---

## Appendix A: Test Scenario Definitions

### Scenario A: Simple Mode (Entity Selectors)

**Configuration:**
```yaml
name: Test Simple Climate
temperature_sensor: sensor.test_room_temperature
heater: input_boolean.test_heater
ac_mode: false
min_temp: 7
max_temp: 35
temp_step: 0.5
hvac_modes: [off, heat, cool]
```

**Test Steps:**
1. Create climate via UI with entity selectors
2. Set target temperature to 22°C
3. Verify heater turns on when room temp < 22°C - tolerance
4. Verify heater turns off when room temp > 22°C + tolerance
5. Change HVAC mode to 'off'
6. Verify heater remains off regardless of temperature

---

### Scenario B: Advanced Mode (Templates)

**Configuration:**
```yaml
name: Test Advanced Climate
current_temperature_template: |
  {{ (states('sensor.test_room_temperature') | float +
      states('sensor.test_outdoor_temperature') | float) / 2 }}
hvac_mode_template: |
  {{ states('input_select.test_hvac_mode') }}
hvac_action_template: |
  {% if is_state('input_boolean.test_heater', 'on') %}
    heating
  {% elif is_state('input_boolean.test_ac', 'on') %}
    cooling
  {% else %}
    idle
  {% endif %}
set_temperature_action:
  - service: input_number.set_value
    target:
      entity_id: input_number.test_target_temp
    data:
      value: "{{ temperature }}"
```

**Test Steps:**
1. Create climate with templates
2. Verify current temperature shows average of room + outdoor
3. Change input_select.test_hvac_mode to 'heat'
4. Verify climate HVAC mode updates to 'heat'
5. Call climate.set_temperature with 23°C
6. Verify input_number.test_target_temp updates to 23
7. Turn on input_boolean.test_heater
8. Verify HVAC action shows 'heating'

---

### Scenario C: Mixed Mode Migration

**Test Steps:**
1. Create Simple mode climate (as in Scenario A)
2. Let it run for 10 minutes, establish state
3. Reconfigure to Advanced mode via options flow
4. Verify templates pre-populated with equivalent logic:
   - `current_temperature_template: "{{ states('sensor.test_room_temperature') }}"`
5. Verify target temperature preserved
6. Verify HVAC mode preserved
7. Modify templates to add outdoor temperature average
8. Verify climate works with new templates
9. Verify entity ID unchanged
10. Verify history preserved

---

## Appendix B: Mock Data Structures

### Mock Home Assistant State

```python
MOCK_STATES = {
    'sensor.test_room_temperature': State(
        entity_id='sensor.test_room_temperature',
        state='21.5',
        attributes={
            'unit_of_measurement': '°C',
            'device_class': 'temperature',
        }
    ),
    'sensor.test_outdoor_temperature': State(
        entity_id='sensor.test_outdoor_temperature',
        state='-5.0',
        attributes={
            'unit_of_measurement': '°C',
            'device_class': 'temperature',
        }
    ),
    # ... more states
}
```

### Mock Config Entry

```python
MOCK_CONFIG_ENTRY = {
    'entry_id': 'test_climate_1',
    'domain': 'climate_template',
    'title': 'Test Climate',
    'data': {},
    'options': {
        'name': 'Test Climate',
        'temperature_sensor': 'sensor.test_room_temperature',
        'heater': 'input_boolean.test_heater',
        'min_temp': 7,
        'max_temp': 35,
        'temp_step': 0.5,
        'hvac_modes': ['off', 'heat'],
    },
}
```

---

## Appendix C: Test Command Reference

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/test_template_fields.py tests/test_action_scripts.py -v
```

### Run Integration Tests Only
```bash
pytest tests/test_advanced_mode.py tests/test_mode_migration.py -v
```

### Run E2E Tests Only
```bash
pytest tests/test_config_flow_ui.py tests/test_options_flow_ui.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=custom_components.climate_template --cov-report=html
```

### Run Performance Tests
```bash
pytest tests/test_performance.py -v --benchmark-only
```

### Run Specific Test
```bash
pytest tests/test_template_fields.py::test_simple_entity_state_template -v
```

---

## Summary

This comprehensive testing plan ensures the Climate Template integration's new template support features are thoroughly validated across all layers:

1. **60% Unit Tests** - Fast, isolated component testing
2. **30% Integration Tests** - End-to-end feature validation
3. **10% E2E Tests** - Complete user journey validation

**Total Test Count:** ~150 test cases covering:
- Template rendering and validation
- Action script execution
- Mode switching and migration
- UI/UX flows
- Error handling and edge cases
- Performance and scalability
- Accessibility and compatibility

**Expected Outcomes:**
- 90%+ code coverage
- Comprehensive feature validation
- Confidence in deployment
- Regression protection
- Excellent user experience
