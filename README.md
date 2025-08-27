# Palmoni

A developer productivity tool that delivers instant code snippets and text expansions anywhere you type.

## Why Palmoni?

Stop context-switching to look up syntax. Type `pip::r` and instantly get `pip install -r requirements.txt`. Type `git::cm` and get `git commit -m`. Works everywhere - terminal, browser, IDE, anywhere you type.

## Installation

```bash
pip install palmoni
```

## Quick Start

```bash
# List available snippets  
palmoni list

# Start the text expander (runs in background)
palmoni start
```

Now type any trigger followed by a space, tab, or enter:
- `pip::r` → `pip install -r requirements.txt`
- `py::main` → Complete Python main function
- `git::st` → `git status` 
- `::ty` → `Thank you`

## Features

- **40+ Built-in Snippets** - Python, Git, SQL, Docker, communication shortcuts
- **Works Everywhere** - Terminal, browser, any text field
- **Hot Reload** - Edit snippets while running
- **Word Boundaries** - Smart expansion on whitespace
- **Zero Configuration** - Works out of the box

## Snippet Categories

**Python & Development**
- `py::main` - Main function template
- `py::class` - Class template  
- `pip::r` - Install requirements
- `docker::run` - Docker run command

**Git Shortcuts**
- `git::st` - Status
- `git::add` - Add all files
- `git::cm` - Commit with message

**Communication**
- `::ty` - Thank you
- `::lmk` - Let me know
- `email::meeting` - Meeting follow-up template

**And many more...** Run `palmoni list` to see all snippets.

## Usage

### Start the Expander
```bash
palmoni start
```
Runs in the background, listening for snippet triggers.

### List All Snippets
```bash
palmoni list
```
Shows all available snippets and their expansions.

### Stop the Expander
Press `Ctrl+C` in the terminal where it's running.

## How It Works

1. Type a snippet trigger (like `pip::r`)
2. Press space, tab, or enter  
3. The trigger gets replaced with the full expansion
4. Continue typing normally

## Requirements

- Python 3.11+
- Works on macOS, Linux, Windows

## Coming Soon

- Custom snippet management
- Team snippet sharing  
- Premium snippet packs for specialized domains
- More programming languages

## License

MIT License - see LICENSE file for details.

## Support

Having issues? [Open an issue](https://github.com/your-username/palmoni/issues) or email wallace.danielk@gmail.com