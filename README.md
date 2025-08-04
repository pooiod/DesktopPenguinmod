# Penguinmod Desktop (Unofficial)

![](cover.png)

**Penguinmod Desktop** is an unofficial wrapper for [PenguinMod](https://penguinmod.com), designed to run the site in a minimal desktop browser environment with persistent file caching.

> This project is a work in progress, expect it to crash a lot

## Features
- Works offline, even url based extension
- Cache whitelist editor (press ctrl + m)

## Platform Support
This project is developed for Windows. Compatibility on Linux or macOS is untested

## How It Works
Penguinmod Desktop embeds PenguinMod in a PyQt5-based web browser. Any resources loaded through the browser are cached if they are from a whitelisted domain.

## Dependencies
```bash
pip install PyQt5 PyQtWebEngine requests
```

<sub>- This project is not affiliated with PenguinMod or Scratch</sub>
