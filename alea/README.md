# Alea Password Generator

A simple command-line password generator that creates secure passwords based on your configuration preferences.

## Features

- Configurable password length
- Customizable character sets (uppercase, lowercase, numbers, special characters)
- Option to exclude similar-looking characters
- Automatic clipboard copying
- JSON-based configuration
- Command-line shortcut for quick access

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the command-line shortcut (Windows):
   - Copy the `alea.bat` file to a directory that is in your system PATH, or
   - Add the directory containing `alea.bat` to your system PATH:
     1. Search Windows settings for "Environment Variables"
     2. Under "System variables", find and select the "Path" variable, then click "Edit"
     3. Click "New" and add the full path to the directory containing `alea.bat`
     4. Click "OK" on all dialogs to save the changes
   - Restart any open command prompt windows for the changes to take effect

## Usage

1. Configure your password preferences in `config.json`:
```json
{
    "length": 16,
    "use_uppercase": true,
    "use_lowercase": true,
    "use_numbers": true,
    "use_special_chars": true,
    "special_chars": "@#$%^&*-_+=[]{}|\\:;?/`~\"()",
    "exclude_similar_chars": true
}
```

2. Run the password generator:
```bash
# Using the Python script directly
python alea.py

# Or using the command-line shortcut (after setup)
alea
```

The generated password will be displayed and automatically copied to your clipboard.

## Configuration Options

- `length`: Password length (default: 16)
- `use_uppercase`: Include uppercase letters (default: true)
- `use_lowercase`: Include lowercase letters (default: true)
- `use_numbers`: Include numbers (default: true)
- `use_special_chars`: Include special characters (default: true)
- `special_chars`: String of allowed special characters
- `exclude_similar_chars`: Exclude similar-looking characters like 'l', '1', 'O', '0' (default: true)

## Running Tests

To run the unit tests:
```bash
python -m unittest test_alea.py
``` 

## Team
Cursor
Thom Rommens
