# AutoFillForm V4

AutoFillForm V4 combines the powerful automation capabilities of V2 with the modern GUI architecture of V3.

## Features

- **YAML Rule Configuration** - Flexible rule-based form filling with YAML files
- **Multiple Question Types** - Support for radio, multiple choice, matrix, and text input questions
- **Probability-based Selection** - Weighted random selection based on configured probabilities
- **Verification Handling** - Intelligent verification and slider captcha bypass
- **GUI Interface** - User-friendly tabbed interface with Tkinter
- **Survey Analysis** - Parse and analyze questionnaire structure
- **Rule Editor** - Built-in YAML editor with syntax validation
- **Session History** - JSON-based session storage and log viewer
- **Windows DPI Support** - Properly handles Windows display scaling

## Directory Structure

```
V4_selenium_gui_tkinter/
├── app.py                      # Main entry point
├── models/                     # MVC - Data layer
│   ├── survey_model.py         # Survey link and config persistence
│   ├── rule_model.py           # YAML rule file management
│   └── history_model.py        # Session history storage
├── views/                      # MVC - Presentation layer
│   ├── main_view.py            # Main tabbed window
│   ├── fill_view.py            # Form filling tab (V2 features)
│   ├── analyze_view.py         # Survey analysis tab (V3 features)
│   ├── rule_editor_view.py     # YAML rule editor
│   ├── history_view.py         # Session history and logs
│   └── loading_window.py       # Loading indicator dialog
├── controllers/                # MVC - Business logic layer
│   ├── main_controller.py      # Main coordination
│   ├── fill_controller.py      # Form filling logic (V2 automation)
│   ├── analyze_controller.py   # Survey analysis logic (V3)
│   ├── rule_editor_controller.py  # Rule editor logic
│   └── history_controller.py   # History management
├── automation/                 # Core automation functions
│   ├── form_filler.py          # Question filling functions
│   ├── verification.py         # Verification handling
│   └── browser_setup.py        # Browser configuration
├── tools/                      # Utility modules
│   ├── windows_resolution.py   # Windows DPI scaling
│   ├── url_change_judge.py     # URL change detection
│   └── read_list_data_from_file.py  # YAML file reader
├── utils/                      # Additional utilities
│   ├── yaml_validator.py       # YAML syntax validation
│   └── logger.py               # Logger with GUI callback
├── rules/                      # YAML rule files
│   └── example.yaml            # Example configuration
├── history/                    # Session history storage
│   └── sessions.json           # Auto-generated
└── Materials/                  # Test resources
```

## Requirements

- Python 3.7+
- selenium
- pyautogui
- pywin32
- webdriver-manager
- beautifulsoup4
- pyyaml

Install dependencies:

```bash
pip install selenium pyautogui pywin32 webdriver-manager beautifulsoup4 pyyaml
```

## Usage

### Running the Application

```bash
cd Codes/V4_selenium_gui_tkinter
python app.py
```

### Using the Form Fill Tab

1. Click "浏览..." to select a YAML rule file from the `rules/` directory
2. The URL and fill count will be automatically loaded from the rule file
3. Adjust the fill count if needed
4. Click "开始填写" to start filling forms
5. Click "停止" to stop the filling process
6. View real-time logs in the log display

### Using the Survey Analysis Tab

1. Enter a survey URL in the link field
2. Click "分析问卷" to analyze the questionnaire structure
3. View the parsed questions and options
4. Click "导出为YAML模板" to generate a rule file from the analysis

### Using the Rule Editor Tab

1. Click "从模板新建" to create a rule from template
2. Or click "打开" to load an existing rule file
3. Edit the YAML content
4. Click "验证语法" to check for errors
5. Click "保存" or "另存为" to save your changes

### Using the History Tab

1. View all past fill sessions
2. Select a session to view detailed logs
3. Click "导出选中" to export logs to a file
4. Click "清空历史" to clear all history

## YAML Rule Format

```yaml
url: "https://www.wjx.cn/vm/XXXXXXXX"
number_of_questionnaires_to_be_filled_out: 5
rules:
  # Single choice - probability weights
  - radio_selection: [50, 50, 0, 0]

  # Multiple choice - percentage for each option
  - multiple_selection: [50, 50, 50]

  # Matrix single choice - one probability list per sub-question
  - matrix_radio_selection:
      - [50, 50, 0, 0, 0]  # Sub-question 1
      - [50, 50, 0, 0, 0]  # Sub-question 2

  # Text input - [text options, probabilities]
  - blank_filling: [["Option1", "Option2"], [50, 50]]
```

## Key Differences from V2 and V3

### From V2 (V2_selenium_pyautogui)
- Added GUI interface with Tkinter
- Added YAML rule editor with validation
- Added session history and logging
- Removed command-line interface
- Removed ESC key exit (now uses Stop button)

### From V3 (V3_selenium_gui_tkinter)
- Added full form filling automation
- Added batch processing with progress tracking
- Added verification bypass handling
- Added YAML rule configuration
- Added rule editor

## License

This project is a continuation of the AutoFillForm project, combining features from V2 and V3.
