import time
import logging
from typing import Dict, Optional, Callable, TYPE_CHECKING
from pynput import keyboard
from pynput.keyboard import Controller, Key

if TYPE_CHECKING:
    from .config import PalmoniConfig

from .database import SnippetDatabase

logger = logging.getLogger(__name__)


class TextExpander:
    def __init__(self, config: Optional['PalmoniConfig'] = None):
        if config is None:
            from .config import load_config
            config = load_config()
            
        self.config = config
        self.db = SnippetDatabase(self.config.database_file)
        self.snippets: Dict[str, str] = {}
        self.typed_buffer = ""
        self.keyboard_controller = Controller()
        self.keyboard_listener: Optional[keyboard.Listener] = None
        
        self.load_snippets()
    
    def load_snippets(self) -> None:
        try:
            self.snippets = self.db.load_all_snippets()
            logger.info(f"Loaded {len(self.snippets)} snippets into memory")
        except Exception as e:
            logger.error(f"Failed to load snippets from database: {e}")
            self.snippets = {}
    
    def get_snippets(self) -> Dict[str, str]:
        return self.snippets.copy()
    
    def get_snippet_count(self) -> int:
        return len(self.snippets)
    
    def _expand_trigger(self, trigger: str, expansion: str, boundary_char: Optional[str] = None) -> None:
        try:
            delete_count = len(trigger) + (1 if boundary_char else 0)
            
            for _ in range(delete_count):
                self.keyboard_controller.press(Key.backspace)
                self.keyboard_controller.release(Key.backspace)
                time.sleep(0.01)
            
            self.keyboard_controller.type(expansion)
            
            if boundary_char == "\n":
                self.keyboard_controller.press(Key.enter)
                self.keyboard_controller.release(Key.enter)
            elif boundary_char == "\t":
                self.keyboard_controller.press(Key.tab)
                self.keyboard_controller.release(Key.tab)
            elif boundary_char == " ":
                self.keyboard_controller.type(" ")
            
            logger.debug(f"Expanded '{trigger}'")
            
        except Exception as e:
            logger.error(f"Error during expansion: {e}")
    
    def _on_key_press(self, key) -> None:
        try:
            if hasattr(key, 'char') and key.char is not None:
                ch = key.char
                self.typed_buffer += ch
                
                for trigger, expansion in self.snippets.items():
                    if self.typed_buffer.endswith(trigger):
                        self._expand_trigger(trigger, expansion)
                        self.typed_buffer = ""
                        return
                
                if ch in self.config.boundary_chars:
                    buf_no_boundary = self.typed_buffer[:-1]
                    for trigger, expansion in self.snippets.items():
                        if buf_no_boundary.endswith(trigger):
                            self._expand_trigger(trigger, expansion, boundary_char=ch)
                            self.typed_buffer = ""
                            return
                    self.typed_buffer = ""
            
            else:
                if key == Key.backspace:
                    self.typed_buffer = self.typed_buffer[:-1] if self.typed_buffer else ""
                elif key in (Key.enter, Key.tab):
                    boundary_char = "\n" if key == Key.enter else "\t"
                    self.typed_buffer += boundary_char
                    
                    buf_no_boundary = self.typed_buffer[:-1]
                    for trigger, expansion in self.snippets.items():
                        if buf_no_boundary.endswith(trigger):
                            self._expand_trigger(trigger, expansion, boundary_char=boundary_char)
                            self.typed_buffer = ""
                            return
                    self.typed_buffer = ""
                    
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
            self.typed_buffer = ""
    
    def start(self, on_started: Optional[Callable] = None) -> None:
        try:
            logger.info(f"Starting text expander with {len(self.snippets)} snippets")
            
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
            
            if on_started:
                on_started()
            
            logger.info("Text expander running. Press Ctrl+C to quit.")
            
            try:
                self.keyboard_listener.join()
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                
        except Exception as e:
            logger.error(f"Error starting text expander: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self) -> None:
        logger.info("Stopping text expander")
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        logger.info("Text expander stopped")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        with TextExpander() as expander:
            expander.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()