# 🍌 BananaText

A rich terminal text editor themed after bananas!

## Features

- 🍌 Banana-themed colors (yellow, gold, brown, cream)
- 📁 Visual file picker - browse and select files
- ✂️ Select text with Shift+arrows, copy with Ctrl+C, paste with Ctrl+V
- 📖 Viewer mode for read-only viewing
- ⌨️ Keyboard shortcuts displayed at bottom
- 💾 Save, load, and create new files

## Run

```bash
python3 BananaText.py
```

### Options

```bash
# Open a file
python3 BananaText.py filename.txt

# Open as viewer (read-only)
python3 BananaText.py --view filename.txt
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Arrows | Move cursor |
| Shift+Arrows | Select text |
| Enter | New line |
| Backspace | Delete character left |
| Del | Delete character at cursor |
| Ctrl+C | Copy selected text |
| Ctrl+V | Paste clipboard |
| Ctrl+S | Save file |
| Ctrl+N | New file |
| Ctrl+O | Open file picker |
| Ctrl+F | Open as viewer |
| Ctrl+Q | Quit |
| F1 | Copy (alternative) |
| F2 | Paste (alternative) |
| F5 | Show help |
| q | Quit (in viewer mode) |
| Esc | Clear selection |

## Install Desktop Shortcut (Linux)

```bash
# Copy to your desktop
cp BananaText.desktop ~/

# Or to applications
cp BananaText.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications
```

## Requirements

- Python 3.6+
- curses (included in Python)


## Issues
Post any issues, ill try to fix it and you can create a branch and fix it and ask for a pull request if you want to
