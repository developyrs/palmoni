import pytest
import tempfile
import yaml
import platform
from pathlib import Path
from unittest.mock import patch, mock_open

from palmoni_core.core.config import (
    PalmoniConfig,
    get_default_config_dir,
    get_default_snippets_file,
    get_bundled_snippets_file,
    load_config,
    save_config,
    ensure_user_setup
)


class TestPalmoniConfig:
    def test_config_defaults(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        assert config.poll_interval == 0.3
        assert config.log_level == "INFO"
        assert config.boundary_chars == {" ", "\n", "\t"}
    
    def test_config_custom_values(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir"),
            poll_interval=0.5,
            log_level="DEBUG"
        )
        
        assert config.poll_interval == 0.5
        assert config.log_level == "DEBUG"


class TestConfigPaths:
    def test_get_default_config_dir_current_platform(self):
        result = get_default_config_dir()
        assert isinstance(result, Path)
        assert "palmoni" in str(result)
    
    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_get_default_config_dir_macos_real(self):
        result = get_default_config_dir()
        expected_parts = ["Library", "Application Support", "palmoni"]
        result_parts = result.parts
        assert all(part in result_parts for part in expected_parts)
    
    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux-specific test")
    def test_get_default_config_dir_linux_real(self):
        result = get_default_config_dir()
        assert ".config" in str(result) or "XDG_CONFIG_HOME" in str(result)
        assert "palmoni" in str(result)
    
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_get_default_config_dir_windows_real(self):
        result = get_default_config_dir()
        assert "palmoni" in str(result)
        # On Windows, should be in AppData or similar
        assert any(part in str(result).lower() for part in ["appdata", "palmoni"])


class TestLoadConfig:
    def test_load_config_no_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yml"
            
            config = load_config(config_file)
            
            assert isinstance(config, PalmoniConfig)
            assert config.poll_interval == 0.3
            assert config.log_level == "INFO"
    
    def test_load_config_with_file(self):
        config_data = {
            "poll_interval": 0.5,
            "log_level": "DEBUG",
            "snippets_file": "/custom/path/snippets.yml"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yml"
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config = load_config(config_file)
            
            assert config.poll_interval == 0.5
            assert config.log_level == "DEBUG"
            assert config.snippets_file == Path("/custom/path/snippets.yml")
    
    def test_load_config_corrupted_file(self, capsys):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yml"
            
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            config = load_config(config_file)
            
            captured = capsys.readouterr()
            assert "Warning: Could not load config file" in captured.out
            assert config.poll_interval == 0.3


class TestSaveConfig:
    def test_save_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config = PalmoniConfig(
                snippets_file=Path("/test/snippets.yml"),
                user_config_dir=config_dir,
                poll_interval=0.5,
                log_level="DEBUG"
            )
            
            config_file = config_dir / "config.yml"
            save_config(config, config_file)
            
            assert config_file.exists()
            
            with open(config_file, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data["poll_interval"] == 0.5
            assert saved_data["log_level"] == "DEBUG"
            assert saved_data["snippets_file"] == "/test/snippets.yml"


class TestEnsureUserSetup:
    def test_ensure_user_setup_creates_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('palmoni_core.core.config.get_default_config_dir') as mock_config_dir:
                mock_config_dir.return_value = Path(temp_dir) / "palmoni"
                
                with patch('palmoni_core.core.config.get_default_snippets_file') as mock_snippets:
                    mock_snippets.return_value = Path(temp_dir) / "palmoni" / "snippets.yml"
                    
                    with patch('palmoni_core.core.config.get_bundled_snippets_file') as mock_bundled:
                        bundled_file = Path(temp_dir) / "bundled.yml"
                        bundled_file.write_text("snippets:\n  test: 'value'")
                        mock_bundled.return_value = bundled_file
                        
                        result_path = ensure_user_setup()
                        
                        assert Path(temp_dir) / "palmoni" / "snippets.yml" == result_path
                        assert result_path.exists()