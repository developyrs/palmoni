import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from palmoni_core.core.expander import TextExpander
from palmoni_core.core.config import PalmoniConfig


class TestTextExpander:
    def test_init_with_config(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            
        assert expander.config == config
        assert expander.snippets == {}
        assert expander.typed_buffer == ""
    
    def test_init_without_config(self):
        with patch('palmoni_core.core.expander.load_config') as mock_load_config:
            mock_config = Mock()
            mock_load_config.return_value = mock_config
            
            with patch.object(TextExpander, 'load_snippets'):
                expander = TextExpander()
                
            assert expander.config == mock_config
    
    def test_load_snippets_from_file(self):
        snippets_data = {
            "snippets": {
                "test::trigger": "test expansion",
                "py::class": "class Test:\n    pass"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            snippets_file = Path(temp_dir) / "snippets.yml"
            with open(snippets_file, 'w') as f:
                yaml.dump(snippets_data, f)
            
            config = PalmoniConfig(
                snippets_file=snippets_file,
                user_config_dir=Path(temp_dir)
            )
            
            expander = TextExpander(config)
            
            assert len(expander.snippets) == 2
            assert expander.snippets["test::trigger"] == "test expansion"
            assert expander.snippets["py::class"] == "class Test:\n    pass"
    
    def test_load_snippets_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = PalmoniConfig(
                snippets_file=Path(temp_dir) / "missing.yml",
                user_config_dir=Path(temp_dir)
            )
            
            with patch('palmoni_core.core.expander.get_bundled_snippets_file') as mock_bundled:
                mock_bundled.return_value = Path(temp_dir) / "also_missing.yml"
                
                expander = TextExpander(config)
                
            assert expander.snippets == {}
    
    def test_load_snippets_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            snippets_file = Path(temp_dir) / "invalid.yml"
            with open(snippets_file, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            config = PalmoniConfig(
                snippets_file=snippets_file,
                user_config_dir=Path(temp_dir)
            )
            
            expander = TextExpander(config)
            
            assert expander.snippets == {}
    
    def test_get_snippets(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.snippets = {"test": "value"}
            
            result = expander.get_snippets()
            
            assert result == {"test": "value"}
            assert result is not expander.snippets  # Should be a copy
    
    def test_add_snippet(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            
            expander.add_snippet("test::trigger", "test expansion")
            
            assert expander.snippets["test::trigger"] == "test expansion"
    
    def test_remove_snippet(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.snippets = {"test::trigger": "test expansion"}
            
            result = expander.remove_snippet("test::trigger")
            assert result is True
            assert "test::trigger" not in expander.snippets
            
            result = expander.remove_snippet("nonexistent")
            assert result is False
    
    @patch('palmoni_core.core.expander.Controller')
    def test_expand_trigger(self, mock_controller_class):
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.keyboard_controller = mock_controller
            
            expander._expand_trigger("test", "expansion")
            
            assert mock_controller.press.call_count == 4  # 4 backspaces for "test"
            assert mock_controller.release.call_count == 4
            mock_controller.type.assert_called_once_with("expansion")
    
    @patch('palmoni_core.core.expander.Controller')
    def test_expand_trigger_with_boundary(self, mock_controller_class):
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.keyboard_controller = mock_controller
            
            expander._expand_trigger("test", "expansion", boundary_char=" ")
            
            assert mock_controller.press.call_count == 5  # 5 backspaces (test + space)
            assert mock_controller.release.call_count == 5
            mock_controller.type.assert_called_with(" ")  # Last call should add space back


class TestTextExpanderKeyHandling:
    @patch('palmoni_core.core.expander.Controller')
    def test_on_key_press_exact_match(self, mock_controller_class):
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.keyboard_controller = mock_controller
            expander.snippets = {"test": "expansion"}
            
            # Simulate typing "test"
            for char in "test":
                key = Mock()
                key.char = char
                expander._on_key_press(key)
            
            # Should have triggered expansion
            assert mock_controller.type.called
            assert expander.typed_buffer == ""
    
    @patch('palmoni_core.core.expander.Controller')
    def test_on_key_press_boundary_match(self, mock_controller_class):
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.keyboard_controller = mock_controller
            expander.snippets = {"test": "expansion"}
            
            # Simulate typing "test "
            for char in "test":
                key = Mock()
                key.char = char
                expander._on_key_press(key)
            
            # Add space (boundary character)
            key = Mock()
            key.char = " "
            expander._on_key_press(key)
            
            # Should have triggered expansion
            assert mock_controller.type.called
            assert expander.typed_buffer == ""
    
    def test_on_key_press_no_match(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            expander = TextExpander(config)
            expander.snippets = {"test": "expansion"}
            
            # Simulate typing "hello"
            for char in "hello":
                key = Mock()
                key.char = char
                expander._on_key_press(key)
            
            # Buffer should contain "hello"
            assert expander.typed_buffer == "hello"


class TestTextExpanderContextManager:
    def test_context_manager(self):
        config = PalmoniConfig(
            snippets_file=Path("test.yml"),
            user_config_dir=Path("test_dir")
        )
        
        with patch.object(TextExpander, 'load_snippets'):
            with patch.object(TextExpander, 'stop') as mock_stop:
                with TextExpander(config) as expander:
                    assert isinstance(expander, TextExpander)
                
                mock_stop.assert_called_once()