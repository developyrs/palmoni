import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class PalmoniConfig:
    database_file: Path
    user_config_dir: Path
    poll_interval: float = 0.3
    boundary_chars: set = None
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.boundary_chars is None:
            self.boundary_chars = {" ", "\n", "\t"}


def get_default_config_dir() -> Path:
    home = Path.home()
    
    if os.name == "posix":
        if "darwin" in os.uname().sysname.lower():
            return home / "Library" / "Application Support" / "palmoni"
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / "palmoni"
            return home / ".config" / "palmoni"
    else:
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "palmoni"
        return home / ".palmoni"


def get_bundled_database_file() -> Path:
    return Path(__file__).parent.parent / "data" / "snippets.db"


def load_config(config_file: Optional[Path] = None) -> PalmoniConfig:
    config_dir = get_default_config_dir()
    
    if config_file is None:
        config_file = config_dir / "config.yml"
    
    config = PalmoniConfig(
        database_file=get_bundled_database_file(),
        user_config_dir=config_dir
    )
    
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
            
            if "poll_interval" in config_data:
                config.poll_interval = float(config_data["poll_interval"])
            if "log_level" in config_data:
                config.log_level = config_data["log_level"]
            
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration.")
    
    return config


def save_config(config: PalmoniConfig, config_file: Optional[Path] = None) -> None:
    if config_file is None:
        config_file = config.user_config_dir / "config.yml"
    
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    config_data = {
        "poll_interval": config.poll_interval,
        "log_level": config.log_level,
    }
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False)
    except Exception as e:
        print(f"Warning: Could not save config file {config_file}: {e}")


def ensure_user_setup() -> Path:
    config = load_config()
    config.user_config_dir.mkdir(parents=True, exist_ok=True)
    
    if not config.database_file.exists():
        raise FileNotFoundError(f"Bundled database not found: {config.database_file}")
    
    print(f"Using bundled database with snippets")
    return config.database_file