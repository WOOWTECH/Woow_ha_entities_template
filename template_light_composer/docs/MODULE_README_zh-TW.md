# Template Light Composer

[![版本](https://img.shields.io/badge/版本-1.0.0-blue.svg)](https://github.com/your-repo/template-light-composer)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-green.svg)](https://www.home-assistant.io/)
[![授權條款](https://img.shields.io/badge/授權條款-MIT-orange.svg)](LICENSE)

> 一個強大的 Home Assistant 自定義整合套件，讓您能夠創建基於模板的燈光實體，具備動態狀態管理、亮度控制和色溫調整功能。

## 🌟 概述

Template Light Composer 讓您能夠使用 Jinja2 模板將多個 Home Assistant 實體組合成單一的智能燈光實體。非常適合創建代表複雜照明系統的虛擬燈光、聚合多個設備或提供自定義照明行為。

## ✨ 主要功能

### 🎛️ **全面的燈光控制**
- **狀態管理**：基於任何實體的動態開關控制
- **亮度控制**：0-255 亮度等級，支援基於模板的計算
- **色溫控制**：基於 Kelvin 的溫度控制（2500K-6500K）
- **即時更新**：與來源實體的自動狀態同步

### 🔧 **靈活的配置**
- **視覺化配置流程**：Home Assistant UI 中的用戶友好設置界面
- **基於模板**：利用 Jinja2 模板的強大功能處理複雜邏輯
- **實體選擇器**：輕鬆選擇來源實體
- **自定義動作**：使用服務調用定義開關行為

### 🚀 **進階功能**
- **狀態恢復**：Home Assistant 重啟後記住狀態
- **轉場支援**：亮度和色溫的平滑轉場
- **除錯日誌**：全面的日誌記錄，方便故障排除
- **錯誤處理**：強健的模板錯誤處理和後備機制

## 📦 安裝

### 方法一：手動安裝

1. **下載整合套件**
   ```bash
   cd /path/to/your/homeassistant/config
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/your-repo/template-light-composer.git
   ```

2. **複製到自定義組件**
   ```bash
   cp -r template-light-composer/custom_components/template_light_composer ./
   ```

3. **重啟 Home Assistant**
   - 重啟您的 Home Assistant 實例
   - 整合套件將在整合頁面中可用

### 方法二：HACS（推薦）

1. **新增自定義儲存庫**
   - 在 Home Assistant 中開啟 HACS
   - 前往整合套件
   - 點擊三點選單並選擇「自定義儲存庫」
   - 新增此儲存庫 URL
   - 選擇「整合套件」作為類別

2. **通過 HACS 安裝**
   - 搜尋「Template Light Composer」
   - 點擊「安裝」
   - 重啟 Home Assistant

## ⚙️ 配置

### 快速設置

1. **導航至整合套件**
   - 前往設定 → 裝置與服務
   - 點擊「新增整合套件」
   - 搜尋「Template Light Composer」

2. **基本配置**
   - **名稱**：為您的燈光指定唯一名稱
   - **狀態實體**：選擇控制開關狀態的實體
   - **亮度實體**：選擇亮度控制實體
   - **溫度實體**：選擇色溫實體

3. **進階選項**
   - 設定最小/最大溫度值
   - 配置轉場支援
   - 新增可用性模板

### 測試實體設置

要測試整合套件，請將這些實體新增到您的 `configuration.yaml`：

```yaml
# Template Light Composer 的測試實體
input_number:
  # 亮度控制（0-255）
  test_brightness:
    name: "測試亮度"
    min: 0
    max: 255
    step: 1
    initial: 100
    mode: slider

  # 色溫控制（2500K-6500K）
  test_color_temp:
    name: "測試色溫（Kelvin）"
    min: 2500
    max: 6500
    step: 100
    initial: 4000
    mode: slider
    unit_of_measurement: "K"

input_boolean:
  # 燈光開關狀態
  test_light_state:
    name: "測試燈光狀態"
    initial: false
```

參見 [example_configuration.yaml](example_configuration.yaml) 以獲得包含自動化的完整配置範例。

## 🎯 使用範例

### 範例一：簡單房間燈光
創建一個代表多個實體燈光的虛擬燈光：

```yaml
# 通過 UI 配置：
# - 名稱：「客廳主燈」
# - 狀態實體：input_boolean.living_room_lights
# - 亮度實體：input_number.living_room_brightness
# - 溫度實體：input_number.living_room_color_temp
```

### 範例二：自適應照明
使用模板創建基於時間和條件的自適應照明：

```yaml
# 基於動作和時間的狀態
# 狀態實體：binary_sensor.living_room_motion
# 狀態運算子：「==」
# 狀態閾值：「on」

# 基於環境光的亮度
# 亮度實體：sensor.ambient_light_lux
#（自動轉換為 0-255 範圍）

# 基於時間的色溫
# 溫度實體：sensor.circadian_color_temp
```

### 範例三：聚合多個燈光
將數個燈光組合成一個統一控制：

```yaml
# 使用通過自動化控制多個燈光的 input_boolean
# 亮度實體追蹤所有燈光的平均亮度
# 溫度實體代表當前色溫
```

## 🔍 模板詳情

### 狀態模板
控制燈光何時被視為「開啟」或「關閉」：

```jinja2
# 對於 input_boolean 實體（自動）：
{{ states('input_boolean.test_light_state') == 'on' }}

# 對於其他實體（可自定義）：
{{ state_attr('sensor.light_level', 'state')|int(0) > 10 }}
```

### 亮度模板
計算亮度（0-255）：

```jinja2
# 直接狀態值：
{{ states('input_number.test_brightness')|int(0) }}

# 複雜計算：
{{ (states('sensor.ambient_light')|int(0) * 2.55)|int }}
```

### 溫度模板
確定 Kelvin 色溫：

```jinja2
# 直接 Kelvin 值：
{{ states('input_number.test_color_temp')|int(0) }}

# 基於時間的計算：
{% set hour = now().hour %}
{{ 2700 if hour < 8 or hour > 20 else 5500 }}
```

## 🐛 除錯

### 啟用除錯日誌

新增到您的 `configuration.yaml`：

```yaml
logger:
  default: info
  logs:
    custom_components.template_light_composer: debug
```

### 常見問題

1. **燈光未更新**
   - 檢查來源實體是否存在且有有效狀態
   - 驗證日誌中的模板語法
   - 確保實體追蹤正常工作

2. **模板錯誤**
   - 查看「Invalid brightness/temperature value」警告
   - 檢查實體是否返回數值
   - 為安全起見新增 `|int(0)` 過濾器

3. **配置流程問題**
   - 安裝後重啟 Home Assistant
   - 檢查整合套件是否正確載入
   - 驗證實體 ID 是否正確

### 除錯資訊

檢查這些日誌項目進行故障排除：

```
# 模板生成
Generated state template: {{ states('input_boolean.test') == 'on' }}
Generated level template: {{ states('input_number.brightness')|int(0) }}

# 狀態更新
State template result: True (type: <class 'bool'>)
Set light is_on to: True
Level template result: 150
Set brightness to: 150
```

## 🧪 開發

### 專案結構

```
custom_components/template_light_composer/
├── __init__.py              # 整合套件設置
├── manifest.json           # 整合套件元數據
├── const.py                # 常數和模板
├── config_flow.py          # 配置 UI
├── light.py                # 燈光實體實現
├── example_configuration.yaml
├── README.md
└── .gitignore
```

### 核心組件

- **`config_flow.py`**：處理 UI 配置流程
- **`light.py`**：實現 `TemplateComposerLight` 實體
- **`const.py`**：包含模板字串和常數
- **`__init__.py`**：設置整合套件並轉發到燈光平台

### 執行測試

1. **設置開發環境**
   ```bash
   # 克隆 Home Assistant 核心進行開發
   git clone https://github.com/home-assistant/core.git
   cd core

   # 設置開發容器
   script/setup
   ```

2. **安裝整合套件**
   ```bash
   # 複製整合套件到 custom_components
   cp -r /path/to/template_light_composer custom_components/
   ```

3. **啟動 Home Assistant**
   ```bash
   # 以開發模式執行
   script/server
   ```

4. **測試配置**
   - 從 `example_configuration.yaml` 新增測試實體
   - 導航至整合套件並新增 Template Light Composer
   - 在啟用除錯日誌的情況下測試所有功能

### 程式碼風格

- 遵循 Home Assistant 的編碼標準
- 對所有函數使用類型提示
- 新增全面的文件字串
- 包含除錯日誌以便故障排除

## 🤝 貢獻

1. **Fork 儲存庫**
2. **創建功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **進行更改**
   - 遵循現有程式碼風格
   - 為新功能新增測試
   - 根據需要更新文件
4. **提交拉取請求**

### 功能請求

有改進 Template Light Composer 的想法嗎？

- 使用「enhancement」標籤開啟問題
- 描述您的使用案例和建議解決方案
- 如適用，請包含範例

## 📝 授權條款

此專案根據 MIT 授權條款授權 - 詳見 [LICENSE](LICENSE) 文件。

## 🙏 致謝

- [Home Assistant](https://www.home-assistant.io/) 團隊提供的優秀平台
- 社區的靈感和回饋
- 幫助改進此整合套件的貢獻者

## 📊 版本歷史

### v1.0.0（當前）
- ✅ 初始發佈
- ✅ 配置流程 UI
- ✅ 基於模板的狀態管理
- ✅ 亮度和色溫控制
- ✅ 狀態恢復
- ✅ 除錯日誌

### 計劃功能
- 🔄 RGB 顏色支援
- 🔄 效果模板
- 🔄 進階動作配置
- 🔄 YAML 配置支援
- 🔄 自定義屬性模板

---

## 🆘 支援

如果您遇到問題或需要幫助：

1. **檢查 [Issues](https://github.com/your-repo/template-light-composer/issues)** 部分
2. **啟用除錯日誌**並檢查 Home Assistant 日誌
3. **查看 [example_configuration.yaml](example_configuration.yaml)** 文件
4. **創建新問題**並提供有關您設置的詳細資訊

---

**用 ❤️ 為 Home Assistant 社區製作**