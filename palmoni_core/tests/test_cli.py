import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

from palmoni_core.cli.commands import app
from palmoni_core.core.config import PalmoniConfig


class TestCLIList:
    def test_list_command_with_snippets(self):
        runner = CliRunner()
        
        mock_config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        mock_snippets = {
            "py::class": "class Test:\n    pass",
            "git::st": "git status",
            "test::long": "a" * 60  # Long expansion to test truncation
        }
        
        with patch('palmoni_core.cli.commands.ensure_user_setup'):
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_load_config.return_value = mock_config
                
                with patch('palmoni_core.cli.commands.TextExpander') as mock_expander_class:
                    mock_expander = Mock()
                    mock_expander.get_snippets.return_value = mock_snippets
                    mock_expander_class.return_value = mock_expander
                    
                    result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "Loaded 3 snippets" in result.stdout
        assert "py::class" in result.stdout
        assert "git::st" in result.stdout
        assert "git status" in result.stdout
        assert "class Test:\\n    pass" in result.stdout  # Newlines should be escaped
        assert "..." in result.stdout  # Long expansion should be truncated
    
    def test_list_command_no_snippets(self):
        runner = CliRunner()
        
        mock_config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch('palmoni_core.cli.commands.ensure_user_setup'):
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_load_config.return_value = mock_config
                
                with patch('palmoni_core.cli.commands.TextExpander') as mock_expander_class:
                    mock_expander = Mock()
                    mock_expander.get_snippets.return_value = {}
                    mock_expander_class.return_value = mock_expander
                    
                    result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "No snippets found" in result.stdout
        assert "Check your snippets file" in result.stdout
    
    def test_list_command_with_verbose(self):
        runner = CliRunner()
        
        mock_config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch('palmoni_core.cli.commands.ensure_user_setup'):
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_load_config.return_value = mock_config
                
                with patch('palmoni_core.cli.commands.TextExpander') as mock_expander_class:
                    mock_expander = Mock()
                    mock_expander.get_snippets.return_value = {"test": "value"}
                    mock_expander_class.return_value = mock_expander
                    
                    with patch('logging.getLogger') as mock_logger:
                        result = runner.invoke(app, ["list", "--verbose"])
        
        assert result.exit_code == 0
        assert mock_logger.called


class TestCLIStart:
    def test_start_command_keyboard_interrupt(self):
        runner = CliRunner()
        
        mock_config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch('palmoni_core.cli.commands.ensure_user_setup'):
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_load_config.return_value = mock_config
                
                with patch('palmoni_core.cli.commands.TextExpander') as mock_expander_class:
                    mock_expander = Mock()
                    mock_expander_class.return_value = mock_expander
                    mock_expander.__enter__ = Mock(return_value=mock_expander)
                    mock_expander.__exit__ = Mock(return_value=None)
                    
                    # Mock the start method to raise KeyboardInterrupt
                    mock_expander.start.side_effect = KeyboardInterrupt()
                    
                    result = runner.invoke(app, ["start"])
        
        assert result.exit_code == 0
        assert "Starting palmoni text expander" in result.stdout
        assert "Shutting down gracefully" in result.stdout
    
    def test_start_command_with_config_file(self):
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "custom_config.yml"
            
            with patch('palmoni_core.cli.commands.ensure_user_setup'):
                with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                    mock_config = PalmoniConfig(
                        snippets_file=Path("test.yml"),
                        user_config_dir=Path("test_dir")
                    )
                    mock_load_config.return_value = mock_config
                    
                    with patch('palmoni_core.cli.commands.TextExpander') as mock_expander_class:
                        mock_expander = Mock()
                        mock_expander_class.return_value = mock_expander
                        mock_expander.__enter__ = Mock(return_value=mock_expander)
                        mock_expander.__exit__ = Mock(return_value=None)
                        mock_expander.start.side_effect = KeyboardInterrupt()
                        
                        result = runner.invoke(app, ["start", "--config", str(config_file)])
            
            # Should have called load_config with the custom file
            mock_load_config.assert_called_once_with(config_file)
            assert result.exit_code == 0


class TestCLIConfig:
    def test_config_init_command(self):
        runner = CliRunner()
        
        with patch('palmoni_core.cli.commands.ensure_user_setup') as mock_ensure:
            mock_ensure.return_value = Path("/test/snippets.yml")
            
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_config = PalmoniConfig(
                    snippets_file=Path("/test/snippets.yml"),
                    user_config_dir=Path("/test/config")
                )
                mock_load_config.return_value = mock_config
                
                result = runner.invoke(app, ["config", "--init"])
        
        assert result.exit_code == 0
        assert "Palmoni configuration initialized!" in result.stdout
        assert "/test/config" in result.stdout
        assert "/test/snippets.yml" in result.stdout
        assert "Then run: palmoni start" in result.stdout
    
    def test_config_show_command(self):
        runner = CliRunner()
        
        mock_config = PalmoniConfig(
            snippets_file=Path("/test/snippets.yml"),
            user_config_dir=Path("/test/config"),
            poll_interval=0.5,
            log_level="DEBUG"
        )
        
        with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
            mock_load_config.return_value = mock_config
            
            result = runner.invoke(app, ["config", "--show"])
        
        assert result.exit_code == 0
        assert "Current Palmoni Configuration:" in result.stdout
        assert "/test/config" in result.stdout
        assert "/test/snippets.yml" in result.stdout
        assert "0.5s" in result.stdout
        assert "DEBUG" in result.stdout
    
    def test_config_no_options(self):
        runner = CliRunner()
        
        result = runner.invoke(app, ["config"])
        
        assert result.exit_code == 0
        assert "Use --show to display configuration or --init to initialize" in result.stdout


class TestCLIErrorHandling:
    def test_list_command_error(self):
        runner = CliRunner()
        
        with patch('palmoni_core.cli.commands.ensure_user_setup'):
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_load_config.side_effect = Exception("Test error")
                
                result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 1
    
    def test_start_command_error(self):
        runner = CliRunner()
        
        with patch('palmoni_core.cli.commands.ensure_user_setup'):
            with patch('palmoni_core.cli.commands.load_config') as mock_load_config:
                mock_load_config.side_effect = Exception("Test error")
                
                result = runner.invoke(app, ["start"])
        
        assert result.exit_code == 1
    
    def test_config_init_error(self):
        runner = CliRunner()
        
        with patch('palmoni_core.cli.commands.ensure_user_setup') as mock_ensure:
            mock_ensure.side_effect = Exception("Test error")
            
            result = runner.invoke(app, ["config", "--init"])
        
        assert result.exit_code == 1
        assert "Error initializing configuration" in result.stdout