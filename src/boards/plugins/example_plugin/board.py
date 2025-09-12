"""
Example board plugin implementation.
"""
from boards.base_plugin import BoardPlugin
import datetime


class ExamplePlugin(BoardPlugin):
    """
    Example board plugin that displays the current time and a custom message.
    
    This demonstrates:
    - Inheriting from BoardPlugin
    - Using plugin configuration
    - Basic matrix rendering
    - Standard plugin interface
    """
    
    def __init__(self, data, matrix, sleepEvent):
        super().__init__(data, matrix, sleepEvent)
        
        # Plugin metadata
        self.plugin_name = "Example Plugin"
        self.plugin_version = "1.0.0"
        self.plugin_description = "Demonstrates the plugin system with time display"
        
        # Get configuration values with defaults
        self.display_message = self.plugin_config.get("message", "Hello World!")
        self.text_color = self.plugin_config.get("text_color", "white")
        self.display_seconds = self.plugin_config.get("display_seconds", 5)
        
        # Access standard application config
        self.font = data.config.layout.font
        self.font_large = data.config.layout.font_large
    
    def render(self):
        """
        Render the example board content.
        """
        self.matrix.clear()
        
        # Get current time
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%m/%d/%Y")
        
        # Draw custom message
        self.matrix.draw_text_centered(8, self.display_message, self.font, self.text_color)
        
        # Draw current time
        self.matrix.draw_text_centered(20, time_str, self.font_large, self.text_color)
        
        # Draw current date
        self.matrix.draw_text_centered(32, date_str, self.font, self.text_color)
        
        # Draw plugin info
        info_text = f"Plugin: {self.plugin_name} v{self.plugin_version}"
        self.matrix.draw_text_centered(44, info_text, self.font, "gray")
        
        # Render to display
        self.matrix.render()
        
        # Wait for configured display time
        self.sleepEvent.wait(self.display_seconds)