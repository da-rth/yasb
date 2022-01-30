<p align="center"><img src="https://raw.githubusercontent.com/denBot/yasb/main/img/yasb_icon.png" width="120"></p>
<h2 align="center">Yasb - Yet Another Status Bar</h2>
<p align="center">
  A highly configurable cross-platform (Windows) status bar written in Python.
  <br><br>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://github.com/denBot/yasb"><img src="https://img.shields.io/github/languages/top/denBot/yasb"></a>
  <a href="https://github.com/denBot/yasb/issues"><img src="https://img.shields.io/github/issues/denBot/yasb"></a>
</p>

### What is it?
**Yasb** (Yet Another Status Bar) is a highly configurable status bar written in Python using the Qt6 GUI Framework. The current goal of yasb is to bring a [polybar](https://github.com/polybar/polybar)/[waybar](https://github.com/Alexays/Waybar)-style status bar to the Windows platform. However, as yasb is written in Python + Qt6, it is cross-platform capable. With some minor adjustments and OS-specific widgets, yasb can also be configured to run on both Linux and Mac OSX.

### What can it look like?
Although yasb comes with **default stylesheet and configuration files**, the user is given complete control over how their status bar is structured and how it will look.

The config file allows for extensive configuration of one or more taskbars, whereas, the stylesheet used by yasb allows for complete control over how the bar and its nested widgets should look. Change everything from font and colours to rounded corners, padding and opacity. 

For an example of the default bar configuration, see the image below:
![](img/yasb_bar.png)

### Some interesting features:
- Multi-monitor and monitor-exclusive taskbars
- Multiple bars per monitor
- Top, bottom and centred bar alignment
- Full UI customisation via user-defined stylesheet
- Extensive configuration via a user-defined configuration file
- Config and stylesheet validation
- Configurable taskbar widgets
  - Active Window Title (and other window information)
  - Battery Widget with customisable 
  - Clock Widget with multi-time zone support
  - Custom (command line) Widgets with JSON parsing
  - Memory & CPU Monitor Widgets
  - [Komorebi WM](https://github.com/LGUG2Z/komorebi) Workspace Widget
  - and more...

### How do you run it?
- Install [Python 3.9](https://www.python.org/doc/versions/) or above
- Install required Python Modules:
  - pip install -r [requirements.txt](requirements.txt)
- Create the directory `C:/Users/{username}/.yasb/` and copy [styles.css](src/styles.css) and [config.yaml](src/config.yaml) into folder.
  - Configure [styles.css](src/styles.css) and [config.yaml](src/config.yaml) to your liking.
- Start the application:
  - run `python src/main.py` in your terminal (or create a startup shortcut)

### What do I do if I've spotted a bug?
**This project is still in early development... If you encounter any bugs, please submit an [issue](https://github.com/denBot/yasb/issues) :bug:**

*Note: Please include a log file along with steps to reproduce when submitting a bug report, it helps!*

### How do you configure it?
All taskbars can be configured in a user-defined YAML config file [config.yaml](src/config.yaml) located in either of the following directories:
- `C:/Users/{username}/.yasb/config.yaml`
- `/path/to/yasb/src/config.yaml`

All taskbars can also be styled using a configurable stylesheet [styles.css](src/styles.css):
- `C:/Users/{username}/.yasb/styles.css`
- `/path/to/yasb/src/styles.css`

NOTE: If either configuration file is not present in the user's `$HOME/.yasb` directory (or if they contain errors), the default config and stylesheet will be loaded instead. You may also be prompted with a popup error dialog showing which lines of code contain linting errors.

## Troubleshooting

#### Why aren't icons being displayed correctly in my taskbar?
By default, yasb uses the [Font Awesome 5 Free]((https://fontawesome.com/v5.15/how-to-use/on-the-desktop/setup/getting-started)) icon font. If this is not installed on your system, this is likely the reason why icons are not appearing correctly in your taskbar.

If you would like to use a different icon font, simply change the wildcard font-family CSS rule in the stylesheet file to your prefered icon font:
```css
* {
    font-family: 'Courier New', 'Font Awesome 5 Free';
    font-size: 16px;
    ...
}
```

#### Why is the Komorebi Workspaces widget not working?
The Komorebi Workspace widget bundled with Yasb requires that you are running [komorebi v0.18.0](https://github.com/LGUG2Z/komorebi/releases/tag/v0.1.8) or above. This is because previous komorebi versions do not support socket-based communication with external applications via Windows Named Pipes.
If you are running an older version of komorebi, yasb will not be able to query komorebi for workspace information.

**Note**: Yasb executes komorebic.exe commands directly via the [subprocess](https://docs.python.org/3/library/subprocess.html) module. For this to work, you MUST have `komoreb.exe` and `komorebic.exe` [added to your system PATH](https://medium.com/@kevinmarkvi/how-to-add-executables-to-your-path-in-windows-5ffa4ce61a53). 


## Contributions
Contributions to yasb are more than welcome. This project was started as an experiment and has blossomed into something I use every day. If you find good use out of this software but believe there are areas for improvement (of which there are likely many), please feel free to submit a Pull Request.

#### Development Environment
All you will need to get started is Python 3.9 or above.

#### Linting
The project is linted using [pylama](https://github.com/klen/pylama):
```
pip install pylama
python -m pylama
# or just  run 'pylama'
```
- The linting tool is configured in [pylama.ini](pylama.ini)
- If you choose to contribute, **please lint your code beforehand.**

#### Commit Formatting and Pull Requests
- Commit messages should ideally follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
- Pull Requests should be submitted [here](https://github.com/denBot/yasb/pulls)
