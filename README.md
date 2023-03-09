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

Yasb aims to bring a feature-rich configurable status bar replacement to Windows. Inspired by [waybar](https://github.com/Alexays/Waybar) and [polybar](https://github.com/polybar/polybar), yasb enables users to build advanced user interfaces for a linux-like experience.


## Installation
1. Generate a release build (see [contribution](#contribution)) or install via MSI
2. Run yasb.exe to start application
3. Configure yasb accordingly by updating `config.yaml` and `styles.scss` in `$HOME/.config/yasb`

**Note:** Binaries, assets and installers can be found in `src-tauri/target`. Once built, an executable will be generated. Additionally, an MSI installer will be created in `src-tauri/target/bundle/msi/`.

---
## Configuration
Yasb can be configured by editing the following configuration files:
- [config.yaml](src-tauri/config.yaml) - Config file for creating and managing bars
- [styles.scss](src-tauri/styles.scss) - SCSS Stylesheet used to style bar(s)

On startup, Yasb will attempt to create a configuration directory if none exists and copy the above configuration files into it:
- If set, use `$XDG_CONFIG_HOME/yasb`. Otherwise, use `$HOME/.config/yasb` a.k.a `C:\Users\Username\.config\yasb`

- **Note #1**: If the `.config/yasb` directory cannot be created, it will fallback to the program directory e.g. `C:\Users\Program Files\yasb` and log to the `$HOME/yasb.log`.
- **Note #2**: it is possible to edit the default configuration files directly. However, we recommended editing the *copied* configuration files in the configuration directory instead.


### Debugging configurations
When updating `config.yaml` or `styles.scss`, it is possible that your config may include illegal syntax which yasb cannot parse.
Currently, yasb will simply log error information and quit if it cannot parse a config.

- In order to debug why your config isn't working, run `yasb.exe --verbose` for a full console log.
- Or view the program log output in `.config/yasb/yasb.log` for more information.
- Check out these resources for configuring `yaml` and `scss` files:
  - [Sass CSS Pre-processor Documentation](https://sass-lang.com/documentation/)
  - [YAML Syntax Documentation](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html)

### Configuration Watcher
In the setup phase, the main process will spawn two file watchers which automatically re-render bar(s) when changes are detected:
- Stylesheets changes are loaded immediately into all bar(s)
- Configuration changes result in all bar(s) being reinitialised.

---

## CLI Interface
Yasb currently supports some basic command-line arguments:
```
USAGE:
    yasb.exe [OPTIONS]

OPTIONS:
    -c, --config <config>
            The path to a configuration file

    -h, --help
            Print help information

    -s, --styles <styles>
            The path to a SCSS stylehseet

    -v, --verbose
            Show verbose logging information

    -V, --version
            Print version information
```
**Note**: Both absolute and relative paths are accepted when specifying a configuration or stylesheet.

---


## Contribution:
If you wish to contribute to yasb, ruuning it locally is very simple:
```bash
git clone https://github.com/denBot/yasb.git
cd yasb/src
npm install
npm run tauri dev
```
To build a release run:
```
npm run tauri build
```
To build a release with debugging enabled run:
```
npm run tauri -- --debug
```
To manually lint [[eslint](https://eslint.org/)] `src` and format [[rustfmt](https://github.com/rust-lang/rustfmt)] `src-tauri` directories run:
```
npm run format
```
To generate [TypeScript Bindings](https://docs.rs/ts-rs/latest/ts_rs/) from `src-tauri/` to `src/bindings/` run:
```
npm run cargo:test
```
Development Requirements:
- [NodeJS](https://nodejs.org/en/download/) 16.x or above
- [Rustup](https://doc.rust-lang.org/cargo/getting-started/installation.html) for rustup, rust and cargo
- [Rustfmt](https://github.com/rust-lang/rustfmt) for rust formatting