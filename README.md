# Yasb Tauri Rewrite

## Getting started:
```bash
cd yasb
npm install
npm run tauri dev
```

## TODO 
1. add bar configuration via config.yaml in src or $HOME/.yasb/
    - top, bottom bar configurations
    - window flags and properties
    - screen specific configurations
    - padding
    - centering
    - percentage widths
    - left, center, right widget configuration
    - blur and opacity
2. add bar stylesheet via styles.scss in src or $HOME/.yasb/
3. add file watcher for config.yaml and styles.scss
4. resgister bar(s) as an [application desktop toolbar](https://docs.microsoft.com/en-us/windows/win32/shell/application-desktop-toolbars)
6. hide always-on-top when fullscreen active
7. documentation


## TODO Widgets
1. timezone and calendar options for datetime widget
2. fix clickable href for text widget
3. active window
4. battery
5. cpu / memory profile(s)
6. custom widgets
7. media player
8. komorebi workspace and active layout widgets
9. system tray
10. bluetooth