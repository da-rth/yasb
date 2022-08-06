![Yet Another Status Bar](img/logo.png)


<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  </a>
  <a href="https://github.com/denBot/yasb/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/github/contributors/denBot/yasb" /></a>
  <a href="https://github.com/denBot/yasb">
    <img src="https://img.shields.io/github/languages/top/denBot/yasb">
  </a>
  <a href="https://discord.gg/HjJCwm5">
    <img src="https://img.shields.io/discord/898554690126630914" alt="chat on Discord">
  </a>
  <br/>
</p>

---

### A highly configurable status bar written in Rust for Windows.

Yasb aims to bring a feature-rich configurable status bar to Windows. Inspired by [waybar](https://github.com/Alexays/Waybar) and [polybar](https://github.com/polybar/polybar), yasb enables users to build advanced user interfaces for a real linux ricing experience.

----
## Configuration

Yasb can be configured by editing the following files:
- [config.yaml](src-tauri/config.yaml) - Config file for creating and managing bars
- [styles.scss](src-tauri/styles.scss) - SCSS Stylesheet used to style bar(s)

Useful guides:
- [Sass CSS Pre-processor Documentation](https://sass-lang.com/documentation/)
- [YAML Syntax Documentation](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html)

Yasb spawns two file watchers which automatically re-render bar(s) when changes are detected:
- Stylesheets changes are loaded immediately into all bar(s)
- Configuration changes result in all bar(s) being reinitialised.

## Installation
1. Generate a release build (see [contribution](#contribution)) or install via MSI
2. Ensure config.yaml and styles.css are in the same directory as `yasb.exe` or in `$HOME/.yasb/`
2. Run yasb.exe to start application

**Note:** Binaries, assets and installers can be found in `src-tauri/target`. Once built, an executable will be generated. Additionally, an MSI installer will be created in `src-tauri/target/bundle/msi/`.

---

## Contribution:
If you wish to contribute to yasb, setting it up locally is very simple:
```bash
git clone https://github.com/denBot/yasb.git
cd yasb/src
npm install
```
To run a development server:
```
npm run tauri dev
```
To build a release:
```
npm run tauri build
```
To build a release with debugging enabled:
```
npm run tauri -- --debug
```

---

## Widgets Todo List
1. timezone and calendar options for datetime widget
2. text widget
3. active window
4. battery
5. cpu / memory profile(s)
6. custom widgets
7. media player
8. komorebi workspace and active layout widgets
9. system tray
10. bluetooth