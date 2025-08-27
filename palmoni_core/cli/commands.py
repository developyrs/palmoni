import logging
import sys
import os
import subprocess
import signal
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

PIDFILE = Path.home() / ".palmoni" / "palmoni.pid"


def write_pidfile():
    """Write current process PID to file"""
    PIDFILE.parent.mkdir(exist_ok=True)
    PIDFILE.write_text(str(os.getpid()))


def read_pidfile() -> Optional[int]:
    """Read PID from file"""
    try:
        if PIDFILE.exists():
            return int(PIDFILE.read_text().strip())
    except (ValueError, OSError):
        pass
    return None


def cleanup_pidfile():
    """Remove PID file"""
    try:
        PIDFILE.unlink()
    except OSError:
        pass


def daemonize():
    """Cross-platform daemon implementation"""
    if os.name == 'nt':  # Windows
        subprocess.Popen([
            sys.executable, '-m', 'palmoni_core.cli.commands', 'start', '--no-daemon'
        ], creationflags=subprocess.DETACHED_PROCESS)
        print("Palmoni started in background")
        sys.exit(0)
    else:  # Unix-like (macOS, Linux)
        # Use subprocess instead of fork to preserve session context for accessibility
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen([
                sys.executable, '-m', 'palmoni_core.cli.commands', 'start', '--no-daemon'
            ], stdout=devnull, stderr=devnull, stdin=None)
        print("Palmoni started in background")
        sys.exit(0)


@app.command()
def start(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    no_daemon: bool = typer.Option(False, "--no-daemon", help="Run in foreground")
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('palmoni_core').setLevel(logging.DEBUG)
    
    # Check if already running
    existing_pid = read_pidfile()
    if existing_pid:
        try:
            os.kill(existing_pid, 0)  # Check if process exists
            print(f"Palmoni is already running (PID: {existing_pid})")
            print("Use 'palmoni stop' to stop it first")
            sys.exit(1)
        except OSError:
            # Process doesn't exist, clean up stale pidfile
            cleanup_pidfile()
    
    if not no_daemon:
        daemonize()
    
    # Write PID file for daemon processes
    write_pidfile()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        cleanup_pidfile()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        ensure_user_setup()
        config = load_config(config_file)
        
        if no_daemon:
            print("Starting palmoni text expander...")
            print(f"Configuration: {config.user_config_dir}")
            print(f"Database: {config.database_file}")
            print("Press Ctrl+C to stop")
        
        with TextExpander(config) as expander:
            expander.start()
            
    except KeyboardInterrupt:
        if no_daemon:
            print("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Failed to start expander: {e}")
        if verbose:
            raise
        sys.exit(1)
    finally:
        cleanup_pidfile()


@app.command()
def stop():
    """Stop the running palmoni daemon"""
    pid = read_pidfile()
    if not pid:
        print("Palmoni is not running")
        return
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
        else:  # Unix-like
            os.kill(pid, signal.SIGTERM)
        
        print(f"Stopped palmoni (PID: {pid})")
        cleanup_pidfile()
        
    except OSError as e:
        print(f"Failed to stop palmoni: {e}")
        cleanup_pidfile()  # Clean up stale pidfile
    except subprocess.CalledProcessError:
        print("Failed to stop palmoni process")
        cleanup_pidfile()


@app.command()
def status():
    """Check if palmoni is running"""
    pid = read_pidfile()
    if not pid:
        print("Palmoni is not running")
        return
    
    try:
        if os.name == 'nt':
            # Windows process check
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                  capture_output=True, text=True)
            if str(pid) in result.stdout:
                print(f"Palmoni is running (PID: {pid})")
            else:
                print("Palmoni is not running")
                cleanup_pidfile()
        else:
            # Unix process check
            os.kill(pid, 0)
            print(f"Palmoni is running (PID: {pid})")
    except OSError:
        print("Palmoni is not running")
        cleanup_pidfile()


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