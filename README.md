# Yasb: Yet Another Status Bar
**Yasb** is a highly configurable and hackable taskbar written in python with Qt6. This project is still in (very) early development, and the number of available widgets are currently very limited.

The feature set stands as follows:
- Multiple taskbars for each screen
- Fully customisable user interface via CSS stylesheet
- [Komorebi](https://github.com/LGUG2Z/komorebi) workspace navigation (very early development)
- Clock widgets with time-zone cycling and alternate label formatting
- Custom widgets capable of parsing/displaying content from command-line applications and on-click events

## Configuration
All taskbars can be configured in a user-defined YAML config file `config.yaml` located in either of the following directories:
- `C:/Users/{username}/.yasb/config.yaml`
- `/path/to/yasb/src/config.yaml`

All taskbars can also be styled using a configurable stylesheet `styles.css`:
- `C:/Users/{username}/.yasb/styles.css`
- `/path/to/yasb/src/styles.css`

NOTE: If either of these configuration files are not present in the user's `$HOME/.yasb` directory (or if they contain errors), the default config and stylesheet will be loaded instead.

## Development
### Requirements
- Python 3.6 or above (3.9+ recommended)

### Local setup
- Create a virtual python environment
- Enter the venv and `pip install -r requirements.txt`
- Configure `styles.css` and `config.yaml` accordingly
- Run `main.py`

### Linting
To lint the project, simply run the following in the root source directory:
```
pip install pylama
python -m pylama        # or just `pylama`
```
- You can configure the linting tool via `pylama.ini`
- If you choose to contribute, **please lint your code beforehand.**

