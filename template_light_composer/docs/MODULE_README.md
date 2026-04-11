# Template Light Composer

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-repo/template-light-composer)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-green.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> A powerful Home Assistant custom integration that allows you to create template-based light entities with dynamic state management, brightness control, and color temperature adjustment.

## 🌟 Overview

Template Light Composer enables you to combine multiple Home Assistant entities into a single, intelligent light entity using Jinja2 templates. Perfect for creating virtual lights that represent complex lighting systems, aggregate multiple devices, or provide custom lighting behaviors.

## ✨ Key Features

### 🎛️ **Comprehensive Light Control**
- **State Management**: Dynamic on/off control based on any entity
- **Brightness Control**: 0-255 brightness levels with template-based calculation
- **Color Temperature**: Kelvin-based temperature control (2500K-6500K)
- **Real-time Updates**: Automatic state synchronization with source entities

### 🔧 **Flexible Configuration**
- **Visual Config Flow**: User-friendly setup interface in Home Assistant UI
- **Template-Based**: Leverage the power of Jinja2 templates for complex logic
- **Entity Selection**: Easy picker for source entities
- **Custom Actions**: Define turn on/off behaviors with service calls

### 🚀 **Advanced Features**
- **State Restoration**: Remembers state across Home Assistant restarts
- **Transition Support**: Smooth transitions for brightness and color temperature
- **Debug Logging**: Comprehensive logging for troubleshooting
- **Error Handling**: Robust template error handling and fallbacks

## 📦 Installation

### Method 1: Manual Installation

1. **Download the Integration**
   ```bash
   cd /path/to/your/homeassistant/config
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/your-repo/template-light-composer.git
   ```

2. **Copy to Custom Components**
   ```bash
   cp -r template-light-composer/custom_components/template_light_composer ./
   ```

3. **Restart Home Assistant**
   - Restart your Home Assistant instance
   - The integration will be available in the integrations page

### Method 2: HACS (Recommended)

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Go to Integrations
   - Click the three dots menu and select "Custom repositories"
   - Add this repository URL
   - Select "Integration" as the category

2. **Install via HACS**
   - Search for "Template Light Composer"
   - Click "Install"
   - Restart Home Assistant

## ⚙️ Configuration

### Quick Setup

1. **Navigate to Integrations**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Template Light Composer"

2. **Basic Configuration**
   - **Name**: Give your light a unique name
   - **State Entity**: Choose entity that controls on/off state
   - **Level Entity**: Select entity for brightness control
   - **Temperature Entity**: Pick entity for color temperature

3. **Advanced Options**
   - Set minimum/maximum temperature values
   - Configure transition support
   - Add availability templates

### Test Entity Setup

To test the integration, add these entities to your `configuration.yaml`:

```yaml
# Test entities for Template Light Composer
input_number:
  # Brightness control (0-255)
  test_brightness:
    name: "Test Brightness"
    min: 0
    max: 255
    step: 1
    initial: 100
    mode: slider

  # Color temperature control (2500K-6500K)
  test_color_temp:
    name: "Test Color Temperature (Kelvin)"
    min: 2500
    max: 6500
    step: 100
    initial: 4000
    mode: slider
    unit_of_measurement: "K"

input_boolean:
  # Light on/off state
  test_light_state:
    name: "Test Light State"
    initial: false
```

See [example_configuration.yaml](example_configuration.yaml) for a complete configuration example with automations.

## 🎯 Usage Examples

### Example 1: Simple Room Light
Create a virtual light that represents multiple physical lights:

```yaml
# Configuration through UI:
# - Name: "Living Room Main Light"
# - State Entity: input_boolean.living_room_lights
# - Level Entity: input_number.living_room_brightness
# - Temperature Entity: input_number.living_room_color_temp
```

### Example 2: Adaptive Lighting
Use templates to create adaptive lighting based on time and conditions:

```yaml
# State based on motion and time
# State Entity: binary_sensor.living_room_motion
# State Operator: "=="
# State Threshold: "on"

# Brightness based on ambient light
# Level Entity: sensor.ambient_light_lux
# (Automatically converted to 0-255 range)

# Color temperature based on time of day
# Temperature Entity: sensor.circadian_color_temp
```

### Example 3: Aggregate Multiple Lights
Combine several lights into one unified control:

```yaml
# Use input_boolean that controls multiple lights via automation
# Level Entity tracks the average brightness of all lights
# Temperature Entity represents the current color temperature
```

## 🔍 Template Details

### State Template
Controls when the light is considered "on" or "off":

```jinja2
# For input_boolean entities (automatic):
{{ states('input_boolean.test_light_state') == 'on' }}

# For other entities (customizable):
{{ state_attr('sensor.light_level', 'state')|int(0) > 10 }}
```

### Level Template
Calculates brightness (0-255):

```jinja2
# Direct state value:
{{ states('input_number.test_brightness')|int(0) }}

# Complex calculation:
{{ (states('sensor.ambient_light')|int(0) * 2.55)|int }}
```

### Temperature Template
Determines color temperature in Kelvin:

```jinja2
# Direct Kelvin value:
{{ states('input_number.test_color_temp')|int(0) }}

# Time-based calculation:
{% set hour = now().hour %}
{{ 2700 if hour < 8 or hour > 20 else 5500 }}
```

## 🐛 Debugging

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.template_light_composer: debug
```

### Common Issues

1. **Light Not Updating**
   - Check if source entities exist and have valid states
   - Verify template syntax in logs
   - Ensure entity tracking is working

2. **Template Errors**
   - Look for `Invalid brightness/temperature value` warnings
   - Check that entities return numeric values
   - Add `|int(0)` filters for safety

3. **Config Flow Issues**
   - Restart Home Assistant after installation
   - Check integration is properly loaded
   - Verify entity IDs are correct

### Debug Information

Check these log entries for troubleshooting:

```
# Template generation
Generated state template: {{ states('input_boolean.test') == 'on' }}
Generated level template: {{ states('input_number.brightness')|int(0) }}

# State updates
State template result: True (type: <class 'bool'>)
Set light is_on to: True
Level template result: 150
Set brightness to: 150
```

## 🧪 Development

### Project Structure

```
custom_components/template_light_composer/
├── __init__.py              # Integration setup
├── manifest.json           # Integration metadata
├── const.py                # Constants and templates
├── config_flow.py          # Configuration UI
├── light.py                # Light entity implementation
├── example_configuration.yaml
├── README.md
└── .gitignore
```

### Key Components

- **`config_flow.py`**: Handles the UI configuration flow
- **`light.py`**: Implements the `TemplateComposerLight` entity
- **`const.py`**: Contains template strings and constants
- **`__init__.py`**: Sets up the integration and forwards to light platform

### Running Tests

1. **Setup Development Environment**
   ```bash
   # Clone Home Assistant core for development
   git clone https://github.com/home-assistant/core.git
   cd core

   # Setup development container
   script/setup
   ```

2. **Install Integration**
   ```bash
   # Copy integration to custom_components
   cp -r /path/to/template_light_composer custom_components/
   ```

3. **Start Home Assistant**
   ```bash
   # Run in development mode
   script/server
   ```

4. **Test Configuration**
   - Add test entities from `example_configuration.yaml`
   - Navigate to Integrations and add Template Light Composer
   - Test all functionality with debug logging enabled

### Code Style

- Follow Home Assistant's coding standards
- Use type hints for all functions
- Add comprehensive docstrings
- Include debug logging for troubleshooting

## 🤝 Contributing

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Submit Pull Request**

### Feature Requests

Have an idea for improving Template Light Composer?

- Open an issue with the "enhancement" label
- Describe your use case and proposed solution
- Include examples if applicable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Home Assistant](https://www.home-assistant.io/) team for the excellent platform
- The community for inspiration and feedback
- Contributors who helped improve this integration

## 📊 Version History

### v1.0.0 (Current)
- ✅ Initial release
- ✅ Config flow UI
- ✅ Template-based state management
- ✅ Brightness and color temperature control
- ✅ State restoration
- ✅ Debug logging

### Planned Features
- 🔄 RGB color support
- 🔄 Effect templates
- 🔄 Advanced action configurations
- 🔄 YAML configuration support
- 🔄 Custom attribute templates

---

## 🆘 Support

If you encounter issues or need help:

1. **Check the [Issues](https://github.com/your-repo/template-light-composer/issues)** section
2. **Enable debug logging** and check Home Assistant logs
3. **Review the [example_configuration.yaml](example_configuration.yaml)** file
4. **Create a new issue** with detailed information about your setup

---

**Made with ❤️ for the Home Assistant community**