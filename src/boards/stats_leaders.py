from PIL import Image, ImageDraw
from utils import get_file
from nhl_api.data import get_skater_stats_leaders
import debug
import traceback

class StatsLeaders:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.team_colors = data.config.team_colors
        self.layout = data.config.layout

    def render(self):
        try:
            # Use the imported function directly
            leaders_data = get_skater_stats_leaders(category='goals', limit=10)
            
            if not leaders_data or 'goals' not in leaders_data:
                debug.error("Stats leaders board unavailable due to missing information from the API")
                return

            # Calculate image height (header + 10 players * 7 pixels per row)
            im_height = (11 * 7)  # 11 rows total (1 header + 10 players)
            
            # Create and draw the image
            image = self.draw_leaders(leaders_data['goals'], im_height, self.matrix.width)
            
            # Initial position (start at top)
            i = 0
            self.matrix.draw_image((0, i), image)
            self.matrix.render()
            self.sleepEvent.wait(5)  # Show top for 5 seconds

            # Scroll the image if it's taller than the matrix
            while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                i -= 1
                self.matrix.draw_image((0, i), image)
                self.matrix.render()
                self.sleepEvent.wait(0.2)  # Scroll speed

            # Show bottom for 5 seconds
            self.sleepEvent.wait(5)

        except Exception as e:
            debug.error(f"Error rendering stats leaders: {str(e)}")
            debug.error(f"Stack trace: {traceback.format_exc()}")

    def draw_leaders(self, leaders_data, img_height, width):
        """Draw an image showing the top goal scorers"""
        
        # Create a new image
        image = Image.new('RGB', (width, img_height))
        draw = ImageDraw.Draw(image)

        # Start position
        row_pos = 0
        row_height = 7
        top = row_height - 1

        # Draw header
        draw.text((1, 0), "NHL GOAL LEADERS", font=self.layout.font)
        row_pos += row_height

        # Draw each player's stats
        for player in leaders_data:
            # Get player info
            last_name = player['lastName']['default']
            abbrev = player['teamAbbrev']
            goals = str(player['value'])
            rank = str(leaders_data.index(player) + 1)
            
            # Get team colors
            team_id = self.data.teams_info_by_abbrev[abbrev].details.id
            team_colors = self.data.config.team_colors
            bg_color = team_colors.color(f"{team_id}.primary")
            txt_color = team_colors.color(f"{team_id}.text")

            # Draw rank (white)
            draw.text((1, row_pos), rank + ".", font=self.layout.font)
            
            # Calculate name width for background rectangle
            name_width = self.layout.font.getlength(last_name)
            
            # Draw background rectangle for name
            draw.rectangle(
                [14, row_pos, 14 + name_width, row_pos + row_height - 1],
                fill=(bg_color['r'], bg_color['g'], bg_color['b'])
            )
            
            # Draw last name (in team text color)
            draw.text((14, row_pos), last_name, 
                     fill=(txt_color['r'], txt_color['g'], txt_color['b']), 
                     font=self.layout.font)
            
            # Right-align goals count (white)
            goals_width = self.layout.font.getlength(goals)
            draw.text((width - goals_width - 1, row_pos), goals, font=self.layout.font)

            row_pos += row_height

        return image 