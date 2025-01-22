from PIL import ImageFont
from utils import get_file
from renderer.screen_config import screenConfig
from nhl_api.player import PlayerStats
import debug

class PlayerStatsRenderer:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.teams_info = data.teams_info
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        self.team_colors = data.config.team_colors
        self.font = self.data.config.layout.font

        self.layout = self.get_layout()

        #FIX THIS
        self.player_id = "8471214"
        
    def get_layout(self):
        """Get the layout for player stats display"""
        layout = self.data.config.config.layout.get_board_layout('player_stats')
        return layout

    def render(self, player_id="8471214"):
        """Render player statistics on the board"""
        try:
            # Get player stats using the new PlayerStats class
            stats = PlayerStats.from_api(player_id)
            if not stats:
                debug.error(f"Could not get stats for player {player_id}")
                return
            
            team_id = stats.team_id
            team_colors = self.data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))

            # Clear the matrix
            self.matrix.clear()

            # Draw player name
            self.matrix.draw_text_centered(
                1, 
                f"{stats.name}", 
                self.font,
                fill=(txt_color['r'], txt_color['g'], txt_color['b']),
                backgroundColor=(bg_color['r'], bg_color['g'], bg_color['b'])
                )

            # Draw team and position
            team_pos = f"{stats.team} - {stats.position}"
            self.matrix.draw_text_layout(
                self.layout.team,
                team_pos
            )

            # Draw stats based on position
            if stats.position == 'G':
                # Goalie stats
                stats_text = [
                    f"GP: {stats.games_played}",
                    f"GAA: {stats.goals_against_avg:.2f}",
                    f"SV%: {stats.save_percentage:.3f}",
                    f"SO: {stats.shutouts}"
                ]
            else:
                # Skater stats
                stats_text = [
                    f"GP: {stats.games_played}",
                    f"G: {stats.goals}",
                    f"A: {stats.assists}",
                    f"PTS: {stats.points}",
                    f"+/-: {stats.plus_minus}"
                ]

            # Draw each stat line
            for i, stat in enumerate(stats_text):
                self.matrix.draw_text_layout(
                    getattr(self.layout, f'stat_{i+1}'),
                    stat
                )

            # Render to matrix
            self.matrix.render()
            self.sleepEvent.wait(15)

        except Exception as e:
            debug.error(f"Error rendering player stats: {str(e)}")
