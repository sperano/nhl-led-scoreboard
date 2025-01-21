from PIL import Image, ImageFont, ImageDraw
from utils import get_file
from renderer.screen_config import screenConfig
from nhl_api.player import PlayerStats
from renderer.logos import LogoRenderer
import debug

class OviTrackerRenderer:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.teams_info = data.teams_info
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.layout = self.get_layout()

        self.team_colors = data.config.team_colors
        self.font = data.config.layout.font
        
        # Gretzky's career goals record
        self.GRETZKY_GOALS = 894
        self.OVI_ID = "8471214"  # Ovechkin's NHL ID
        self.team_id = 15
        
    def get_layout(self):
        """Get the layout for Ovechkin goal tracker display"""
        layout = self.data.config.config.layout.get_board_layout('ovi_tracker')
        return layout

    def render(self):
        """Render Ovechkin's goal tracking statistics"""
        try:
            # Get Ovi's stats using the PlayerStats class
            stats = PlayerStats.from_api(self.OVI_ID)
            if not stats:
                debug.error("Could not get stats for Ovechkin")
                return

            team_id = self.team_id
            team = self.teams_info[team_id]
            team_colors = self.data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))

            # Clear the matrix
            self.matrix.clear()

            # Draw text over rectangles
            self.matrix.draw_text_centered(1, "OVI TRACKER", self.font, backgroundColor=(bg_color['r'], bg_color['g'], bg_color['b']))
            
            # Draw stats inside box
            self.matrix.draw_text(
                (4, 14),
                f"Career: {stats.career_goals}",
                font=self.font
            )

            # Calculate and draw goals needed
            goals_needed = self.GRETZKY_GOALS - stats.career_goals + 1
            self.matrix.draw_text(
                (4, 20),
                f"To Go: {goals_needed}",
                font=self.font
            )

            # Render to matrix
            self.matrix.render()
            self.sleepEvent.wait(15)
        except Exception as e:
            debug.error(f"Error rendering Ovi tracker: {str(e)}") 