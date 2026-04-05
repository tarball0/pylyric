# PyLyric

PyLyric is a lightweight, terminal-based utility written in Python for searching and managing song lyrics. It provides a clean terminal user interface (TUI) powered by `curses`, allowing you to find lyrics online and save them for offline access.

## Features

- **Terminal User Interface (TUI):** Navigate through menus easily using arrow keys or Vim-style (`j`/`k`) bindings.
- **Online Search:** Instantly fetch lyrics from [AZLyrics](https://www.azlyrics.com/).
- **Offline Viewing:** Lyrics are automatically saved to your local storage for viewing without an internet connection.
- **Cache Management:** Easily clear your saved lyrics directly from the application menu.

## Prerequisites

- **Python 3.x**
- **pip** (Python package manager)
- **Unix-like OS:** Linux or macOS (uses standard `curses`).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pylyric.git
   cd pylyric
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To start the application, run:

```bash
python src/lyric.py
```

### Controls
- **Arrow Keys / J, K:** Navigate the menu.
- **Enter:** Select an option.

## Local Storage

PyLyric saves your lyrics in a directory named `Bard` located in your home directory (`~/Bard/`).

## License

This project is licensed under the terms of the [LICENCE](LICENCE) file.
