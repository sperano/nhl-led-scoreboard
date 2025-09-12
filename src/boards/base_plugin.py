"""
Base class for board plugins to ensure consistent interface and enable dynamic loading.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from pathlib import Path


class BoardPlugin(ABC):
    """
    Abstract base class for all board plugins.
    
    All board plugins must inherit from this class and implement the required methods.
    This ensures a consistent interface for the plugin system.
    """
    
    def __init__(self, data, matrix, sleepEvent):
        """
        Initialize the board plugin.
        
        Args:
            data: Application data object containing config and state
            matrix: Display matrix object for rendering
            sleepEvent: Threading event for sleep/wake control
        """
        self.data = data
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        
        # Plugin metadata (should be overridden by subclasses)
        self.plugin_name = self.__class__.__name__
        self.plugin_version = "1.0.0"
        self.plugin_description = "A board plugin"
        
        # Load plugin-specific config if it exists
        self.plugin_config = self._load_plugin_config()
    
    @abstractmethod
    def render(self):
        """
        Render the board content to the matrix.
        
        This method must be implemented by all board plugins.
        It should handle the complete display logic for the board.
        """
        pass
    
    def _load_plugin_config(self) -> Dict[str, Any]:
        """
        Load plugin-specific configuration from config.json in the plugin directory.
        
        Returns:
            Dict containing plugin configuration, or empty dict if no config found.
        """
        try:
            # Try to find config file relative to the plugin module
            plugin_module = self.__class__.__module__
            if 'plugins.' in plugin_module:
                # Extract plugin name from module path (e.g., boards.plugins.nfl_team.board -> nfl_team)
                plugin_name = plugin_module.split('.')[-2] if plugin_module.split('.')[-1] == 'board' else plugin_module.split('.')[-1]
                config_path = Path(__file__).parent / 'plugins' / plugin_name / 'config.json'
                
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        return json.load(f)
        except Exception:
            pass
        
        return {}
    
    def get_plugin_info(self) -> Dict[str, str]:
        """
        Get plugin metadata information.
        
        Returns:
            Dict containing plugin name, version, and description.
        """
        return {
            'name': self.plugin_name,
            'version': self.plugin_version,
            'description': self.plugin_description,
        }
    
    def validate_config(self) -> bool:
        """
        Validate plugin configuration.
        
        Override this method to implement custom configuration validation.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        return True
    
    def cleanup(self):
        """
        Cleanup resources when plugin is unloaded.
        
        Override this method to implement custom cleanup logic.
        """
        pass


class LegacyBoardAdapter(BoardPlugin):
    """
    Adapter class to wrap existing non-plugin boards.
    
    This allows existing boards to work with the plugin system without modification.
    """
    
    def __init__(self, data, matrix, sleepEvent, board_class, *args, **kwargs):
        """
        Initialize the legacy board adapter.
        
        Args:
            data: Application data object
            matrix: Display matrix object  
            sleepEvent: Threading event
            board_class: The legacy board class to wrap
            *args, **kwargs: Additional arguments to pass to the legacy board
        """
        super().__init__(data, matrix, sleepEvent)
        
        # Create instance of the legacy board
        self.board_instance = board_class(data, matrix, sleepEvent, *args, **kwargs)
        
        # Set plugin metadata based on the legacy board
        self.plugin_name = board_class.__name__
        self.plugin_description = f"Legacy board: {board_class.__name__}"
    
    def render(self):
        """
        Delegate rendering to the legacy board instance.
        
        Handles different legacy board interfaces (render() method vs direct execution).
        """
        if hasattr(self.board_instance, 'render'):
            self.board_instance.render()
        elif hasattr(self.board_instance, 'draw'):
            self.board_instance.draw()
        else:
            # Some legacy boards execute in their constructor
            # In this case, the board has already been "rendered"
            pass