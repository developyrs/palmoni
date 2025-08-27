import logging
import sys
from pathlib import Path
import typer
from typing import Optional

from ..core import TextExpander, load_config, ensure_user_setup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="palmoni",
    help="Developer productivity snippet tool",
    add_completion=False
)


@app.command()
def start(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v")
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('palmoni_core').setLevel(logging.DEBUG)
    
    try:
        ensure_user_setup()
        config = load_config(config_file)
        
        print("Starting palmoni text expander...")
        print(f"Configuration: {config.user_config_dir}")
        print(f"Database: {config.database_file}")
        print("Press Ctrl+C to stop")
        
        with TextExpander(config) as expander:
            expander.start()
            
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Failed to start expander: {e}")
        if verbose:
            raise
        sys.exit(1)


@app.command()
def list(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v")
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('palmoni_core').setLevel(logging.DEBUG)
    
    try:
        ensure_user_setup()
        config = load_config(config_file)
        expander = TextExpander(config)
        snippets = expander.get_snippets()
        
        if not snippets:
            print("No snippets found.")
            print(f"Check your database: {config.database_file}")
            return
            
        print(f"Loaded {len(snippets)} snippets from database:")
        print("-" * 60)
        
        for trigger in sorted(snippets.keys()):
            expansion = snippets[trigger]
            
            if len(expansion) > 50:
                display_expansion = expansion[:47] + "..."
            else:
                display_expansion = expansion
            
            display_expansion = display_expansion.replace('\n', '\\n')
            print(f"{trigger:<25} → {display_expansion}")
            
    except Exception as e:
        logger.error(f"Failed to list snippets: {e}")
        if verbose:
            raise
        sys.exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show"),
    init: bool = typer.Option(False, "--init")
):
    if init:
        try:
            database_file = ensure_user_setup()
            config = load_config()
            
            print("✓ Palmoni configuration initialized!")
            print(f"Config directory: {config.user_config_dir}")
            print(f"Database: {database_file}")
            print(f"\nDatabase initialized with default snippets")
            print("Then run: palmoni start")
            
        except Exception as e:
            print(f"Error initializing configuration: {e}")
            sys.exit(1)
    
    if show:
        try:
            config = load_config()
            
            print("Current Palmoni Configuration:")
            print(f"Config directory: {config.user_config_dir}")
            print(f"Database: {config.database_file}")
            print(f"Poll interval: {config.poll_interval}s")
            print(f"Log level: {config.log_level}")
            print(f"Boundary chars: {sorted(config.boundary_chars)}")
            
        except Exception as e:
            print(f"Error showing configuration: {e}")
            sys.exit(1)
    
    if not show and not init:
        print("Use --show to display configuration or --init to initialize")


def main():
    app()


if __name__ == "__main__":
    main()