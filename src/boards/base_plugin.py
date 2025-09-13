"""
Base class for board plugins to ensure consistent interface and enable dynamic loading.
"""
import debug
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from pathlib import Path
from config.files.layout import LayoutConfig
from config.file import ConfigFile


class PluginLayoutConfig(LayoutConfig):
    """
    Extended LayoutConfig that loads layout files from plugin directories.
    """
    def __init__(self, size, fonts, plugin_dir):
        self.plugin_dir = plugin_dir
        
        # Create ConfigFile instances that point to plugin layout files
        # Try to load generic layout.json first (may not exist for some plugins)
        generic_layout_path = str(plugin_dir / 'layout.json')
        size_layout_path = str(plugin_dir / f'layout_{size[0]}x{size[1]}.json')
        
        self.layout = ConfigFile(generic_layout_path, size, False)
        self.dynamic_layout = ConfigFile(size_layout_path, size, False)
        
        # If generic layout failed to load but size-specific exists, use size-specific as base
        if not hasattr(self.layout, 'data') and hasattr(self.dynamic_layout, 'data'):
            self.layout = self.dynamic_layout
            # Create empty dynamic_layout to avoid issues with combine
            self.dynamic_layout = ConfigFile('nonexistent_file_path', size, False)
        elif hasattr(self.layout, 'data') and hasattr(self.dynamic_layout, 'data'):
            # Both exist, combine as normal
            self.layout.combine(self.dynamic_layout)
        
        # Use default system colors and logos (plugins don't have their own color schemes)
        self.logo_config = ConfigFile('config/layout/logos.json', size)
        self.dynamic_logo_config = ConfigFile('config/layout/logos_{}x{}.json'.format(size[0], size[1]), size, False)
        self.logo_config.combine(self.dynamic_logo_config)
        
        self.colors = ConfigFile('config/colors/layout.json')
        self.fonts = fonts


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
        
        # Detect display size
        self.display_width, self.display_height = self._detect_display_size()
        
        # Load plugin-specific config and layout
        self.plugin_config = self._load_plugin_config()
        self.plugin_layout = self._create_plugin_layout_config()
    
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
            debug.error("Error loading plugin config")
            pass
        
        return {}
    
    def _detect_display_size(self) -> tuple:
        """
        Detect the display size from matrix or config.
        
        Returns:
            Tuple of (width, height) as integers
        """
        # Try to get size from matrix object first
        if hasattr(self.matrix, 'width') and hasattr(self.matrix, 'height'):
            return (self.matrix.width, self.matrix.height)
        
        # Try to get from data config
        if hasattr(self.data, 'config'):
            # Look for common config patterns
            if hasattr(self.data.config, 'matrix'):
                if hasattr(self.data.config.matrix, 'width') and hasattr(self.data.config.matrix, 'height'):
                    return (self.data.config.matrix.width, self.data.config.matrix.height)
            
            # Look for layout config that might contain size info
            if hasattr(self.data.config, 'layout'):
                if hasattr(self.data.config.layout, 'width') and hasattr(self.data.config.layout, 'height'):
                    return (self.data.config.layout.width, self.data.config.layout.height)
        
        # Default to most common size if detection fails
        return (128, 64)
    
    def _create_plugin_layout_config(self) -> Optional[LayoutConfig]:
        """
        Create a LayoutConfig instance for this plugin using the system layout infrastructure.
        
        This allows plugins to use the same layout system as the main application,
        with support for size-specific layouts, relative positioning, etc.
        
        Returns:
            LayoutConfig instance if plugin has layout files, None otherwise
        """
        try:
            # Get plugin directory path
            plugin_module = self.__class__.__module__
            if 'plugins.' in plugin_module:
                plugin_name = plugin_module.split('.')[-2] if plugin_module.split('.')[-1] == 'board' else plugin_module.split('.')[-1]
                plugin_dir = Path(__file__).parent / 'plugins' / plugin_name
                
                # Check if plugin has layout files
                size_layout_path = plugin_dir / f'layout_{self.display_width}x{self.display_height}.json'
                generic_layout_path = plugin_dir / 'layout.json'
                
                if size_layout_path.exists() or generic_layout_path.exists():
                    # Create a temporary LayoutConfig that points to plugin layout files
                    # We'll monkey-patch the paths to point to our plugin directory
                    layout_config = PluginLayoutConfig(
                        size=(self.display_width, self.display_height),
                        fonts=self.data.config.config.fonts,
                        plugin_dir=plugin_dir
                    )
                    return layout_config
                    
        except Exception as e:
            debug.error("Error loading plugin layout")
            print(e)
            pass
        
        return None
    
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
    
    # Layout helper methods
    
    def get_board_layout(self, board_name: str = None):
        """
        Get the layout configuration for this plugin's board.
        
        Args:
            board_name: Name of the board layout to get (defaults to plugin name)
            
        Returns:
            Layout object compatible with matrix renderer, or None if no layout
        """
        if not self.plugin_layout:
            return None
            
        if board_name is None:
            # Use plugin class name as board name
            board_name = self.__class__.__name__.lower().replace('plugin', '')
            
        return self.plugin_layout.get_board_layout(board_name)
    
    def has_layout(self) -> bool:
        """
        Check if plugin has a layout configuration loaded.
        
        Returns:
            True if layout config exists, False otherwise
        """
        return self.plugin_layout is not None


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