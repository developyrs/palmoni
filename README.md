# Palmoni

A developer productivity tool that delivers instant code snippets and text expansions anywhere you type. Built with DuckDB for lightning-fast performance and powered by a curated snippet database.

## Why Palmoni?

Stop context-switching to look up syntax. Type `py::class` and instantly get a Python class template. Type `git::cm` and get `git commit -m`. Works everywhere - terminal, browser, IDE, anywhere you type.

**Performance-first architecture:** DuckDB backend loads all snippets into memory at startup for O(1) expansion times. No file I/O during text expansion means zero latency.

## Installation

```bash
pip install palmoni
```

## Quick Start

```bash
# Initialize configuration
palmoni config --init

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
- **Zero Configuration** - Ships with curated snippet database
- **Smart Expansion** - Triggers on word boundaries (space, tab, enter)
- **Cross-platform** - macOS, Linux, Windows support

## Architecture

Palmoni uses DuckDB to store and manage snippets efficiently:
- **Startup**: All snippets loaded from database into memory hash table
- **Runtime**: O(1) snippet lookups with no database queries during expansion  
- **Database**: Read-only DuckDB file ships with the package
- **Memory**: Optimized for thousands of snippets without performance degradation

## Snippet Categories

**Python & Development**
- `py::main` - Main function template
- `py::class` - Class template  
- `pip::r` - Install requirements
- `doc::run` - Docker run command

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

### Initialize Configuration
```bash
palmoni config --init
```
Sets up configuration directory and verifies database access.

### Start the Expander
```bash
palmoni start
```
Runs in the background, listening for snippet triggers. Loads all snippets into memory for instant access.

### List All Snippets
```bash
palmoni list
```
Shows all available snippets and their expansions from the DuckDB database.

### Show Configuration
```bash
palmoni config --show
```
Displays current configuration including database path and performance settings.

### Stop the Expander
Press `Ctrl+C` in the terminal where it's running.

## How It Works

1. **Database Loading**: At startup, all snippets are loaded from DuckDB into a memory hash table
2. **Keystroke Monitoring**: Background process monitors all keystrokes across applications
3. **Pattern Matching**: When you type a trigger (like `pip::r`), it's recognized instantly
4. **Smart Expansion**: On word boundary (space, tab, enter), trigger is replaced with expansion
5. **Zero Latency**: All lookups happen in memory - no file or database I/O during expansion

## Performance

- **Startup time**: <100ms to load entire snippet database thanks to DuckDB's efficient columnar storage
- **Expansion time**: <1ms lookup and replacement
- **Memory usage**: ~10MB for thousands of snippets
- **Scalability**: Tested with 10,000+ snippets without performance impact

## Requirements

- Python 3.11+
- DuckDB (automatically installed)
- Works on macOS, Linux, Windows

## Database Technology

Palmoni leverages DuckDB for optimal performance:
- **Fast startup**: Columnar storage enables rapid full-table scans
- **Memory efficiency**: Only active data loaded into Python memory
- **Reliability**: ACID transactions prevent data corruption
- **Portability**: Single file database ships with package

## Coming Soon

- Custom snippet management via CLI
- Team snippet sharing capabilities
- Premium snippet packs for specialized domains
- Performance analytics and usage tracking
- More programming languages and frameworks

## License

MIT License - see LICENSE file for details.

## Support

Having issues? [Open an issue](https://github.com/developyrs/palmoni/issues) or email daniel@developyr.com