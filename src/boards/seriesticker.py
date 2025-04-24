"""
    Shows list of series summary (Table with each result of game).
"""
from time import sleep
from utils import center_obj
from data.playoffs import Series
from data.scoreboard import Scoreboard
from renderer.matrix import MatrixPixels, Matrix
import debug
import nhlpy

class Seriesticker:
    def __init__(self, data, matrix: Matrix, sleepEvent):
        self.data = data
        self.rotation_rate = 5
        self.matrix = matrix
        self.spacing = 3 # Number of pixel between each dot + 1
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        
        self.layout = self.data.config.config.layout.get_board_layout('seriesticker')
        self.team_colors = self.data.config.team_colors

        self.top_seed_scores = [
            self.layout.top_seed_score_1,
            self.layout.top_seed_score_2,
            self.layout.top_seed_score_3,
            self.layout.top_seed_score_4,
            self.layout.top_seed_score_5,
            self.layout.top_seed_score_6,
            self.layout.top_seed_score_7,
        ]
        self.top_seed_scores_bg = [
            self.layout.top_seed_score_1_bg,
            self.layout.top_seed_score_2_bg,
            self.layout.top_seed_score_3_bg,
            self.layout.top_seed_score_4_bg,
            self.layout.top_seed_score_5_bg,
            self.layout.top_seed_score_6_bg,
            self.layout.top_seed_score_7_bg,
        ]

        self.bottom_seed_scores = [
            self.layout.bottom_seed_score_1,
            self.layout.bottom_seed_score_2,
            self.layout.bottom_seed_score_3,
            self.layout.bottom_seed_score_4,
            self.layout.bottom_seed_score_5,
            self.layout.bottom_seed_score_6,
            self.layout.bottom_seed_score_7,
        ]
        self.bottom_seed_scores_bg = [
            self.layout.bottom_seed_score_1_bg,
            self.layout.bottom_seed_score_2_bg,
            self.layout.bottom_seed_score_3_bg,
            self.layout.bottom_seed_score_4_bg,
            self.layout.bottom_seed_score_5_bg,
            self.layout.bottom_seed_score_6_bg,
            self.layout.bottom_seed_score_7_bg,
        ]

    def render(self):
        if not self.data.current_round:
            debug.log("No Playoff to render on seriesticker")
            return
        self.allseries = self.data.series
        self.index = 0
        self.num_series = len(self.allseries)

        for series in self.allseries:
            self.matrix.clear()
            banner_text = "STANLEY CUP"
            color_banner_bg = (200,200,200)
            color_banner_text = (0,0,0)
            round_name = "FINAL" 

            if not self.data.current_round == 4:
                try:
                    color_conf = self.team_colors.color("{}.primary".format(series.conference))
                    banner_text = series.conference[:4].upper()
                except:
                    color_conf = self.team_colors.color("{}.primary".format("Western"))
                    banner_text = "WEST"
                color_banner_bg = (color_conf['r'], color_conf['g'], color_conf['b'])
                round_name = self.data.current_round_name.replace("-"," ").upper()
                self.show_indicator(self.index, self.num_series)
            
            top_team_wins = series.top_team.series_wins
            bottom_team_wins = series.bottom_team.series_wins

            if top_team_wins > bottom_team_wins:
                series_overview = f"{series.top_team.abbrev} LEADS SERIES {top_team_wins} - {bottom_team_wins}"
            else:
                series_overview = f"{series.bottom_team.abbrev} LEADS SERIES {bottom_team_wins} - {top_team_wins}"

            # Conference banner, Round Title
            self.matrix.draw_text_layout(
                self.layout.header,
                f"{banner_text} - {round_name}", 
                align="left",
                fillColor=(0,0,0,),
                backgroundColor=color_banner_bg,
                backgroundOffset=[2,2,2,2]
            )

            self.index += 1
            
            self.draw_series_table(series)

            self.matrix.draw_text_layout(
                self.layout.overview,
                series_overview
            )

            self.matrix.render()
            self.sleepEvent.wait(self.data.config.seriesticker_rotation_rate)

    def draw_series_table(self, series):

        color_top_bg = self.team_colors.color("{}.primary".format(series.top_team.id))
        color_top_team = self.team_colors.color("{}.text".format(series.top_team.id))

        color_bottom_bg = self.team_colors.color("{}.primary".format(series.bottom_team.id))
        color_bottom_team = self.team_colors.color("{}.text".format(series.bottom_team.id))

        # Table
        self.grid_row_y = self.layout.seperator.position[1]
        self.matrix.draw.line([(0,self.grid_row_y),(self.matrix.width,self.grid_row_y)], width=1, fill=(150,150,150))

        # use rectangle because I want to keep symmetry for the background of team's abbrev
        self.matrix.draw_rectangle_layout(
            self.layout.top_seed_bg,
            fillColor=(color_top_bg['r'], color_top_bg['g'], color_top_bg['b'])
        )
        self.matrix.draw_text_layout(
            self.layout.top_seed,
            series.top_team.abbrev, 
            fillColor=(color_top_team['r'], color_top_team['g'], color_top_team['b'])
        )

        self.matrix.draw_rectangle_layout(
            self.layout.bottom_seed_bg,
            fillColor=(color_bottom_bg['r'], color_bottom_bg['g'], color_bottom_bg['b'])
        )
        self.matrix.draw_text_layout(
            self.layout.bottom_seed,
            series.bottom_team.abbrev, 
            fillColor=(color_bottom_team['r'], color_bottom_team['g'], color_bottom_team['b'])
        )
        
        loosing_color = (150,150,150)
        loosing_color_bg = (0,0,0)

        game_count = 0
        for game in series.games:
            game_count += 1
            attempts_remaining = 5
            while attempts_remaining > 0:
                try:
                    if game["id"] in series.game_overviews:
                        # Look if the game data is already stored in the game overviews from the series
                        overview = series.game_overviews[game["id"]]
                    else:
                        # Request and store the game overview in the series instance
                        overview = series.get_game_overview(game["id"])
                    
                    # get the scoreboard
                    try:
                        scoreboard = Scoreboard(overview, self.data)
                    except:
                        break
                    if (self.data.status.is_final(overview["gameState"]) or self.data.status.is_game_over(overview["gameState"])) and hasattr(scoreboard, "winning_team_id"):
                        if scoreboard.winning_team_id == series.top_team.id:
                            winning_layout = self.top_seed_scores[game_count - 1]
                            winning_layout_bg = self.top_seed_scores_bg[game_count - 1]
                            loosing_layout = self.bottom_seed_scores[game_count - 1]
                            loosing_layout_bg = self.bottom_seed_scores_bg[game_count - 1]
                            winning_team_color = color_top_team
                            winning_bg_color = color_top_bg
                        else:
                            winning_layout = self.bottom_seed_scores[game_count - 1]
                            winning_layout_bg = self.bottom_seed_scores_bg[game_count - 1]
                            loosing_layout = self.top_seed_scores[game_count - 1]
                            loosing_layout_bg = self.top_seed_scores_bg[game_count - 1]
                            winning_team_color = color_bottom_team
                            winning_bg_color = color_bottom_bg

                        self.matrix.draw_rectangle_layout(
                            loosing_layout_bg,
                            fillColor=loosing_color_bg
                        )

                        self.matrix.draw_rectangle_layout(
                            winning_layout_bg,
                            fillColor=(winning_bg_color['r'], winning_bg_color['g'], winning_bg_color['b']), 
                        )

                        self.matrix.draw_text_layout(
                            loosing_layout,
                            str(scoreboard.losing_score),  
                            fillColor=loosing_color
                        )

                        self.matrix.draw_text_layout(
                            winning_layout,
                            str(scoreboard.winning_score),  
                            fillColor=(winning_team_color['r'], winning_team_color['g'], winning_team_color['b']), 
                        )

                    break

                except ValueError as error_message:
                    self.data.network_issues = True
                    debug.error("Failed to get the Games for the {} VS {} series: {} attempts remaining".format(series.top_team.abbrev, series.bottom_team.abbrev, attempts_remaining))
                    debug.error(error_message)
                    attempts_remaining -= 1
                    self.sleepEvent.wait(1)
                except KeyError as error_message:
                    debug.error("Failed to get the overview for game id {}. Data unavailable or is TBD".format(game["gameId"]))
                    debug.error(error_message)
                    break
            # If one of the request for player info failed after 5 attempts, return an empty dictionary
            if attempts_remaining == 0:
                return False


    def show_indicator(self, index, slides):
        """
            TODO: This function need to be coded a better way. but it works :D

            Carousel indicator.
        """
        align = 0
        spacing = 3

        # if there is more then 11 games, reduce the spacing of each dots
        if slides > 10:
            spacing = 2

            # Move back the indicator by 1 pixel if the number of games is even.
            if slides % 2:
              align = -1

        pixels = []

        # Render the indicator
        for i in range(slides):
            dot_position = ((spacing * i) - 1) + 1

            color = (70, 70, 70)
            if i == index:
                color = (255, 50, 50)

            pixels.append(
              MatrixPixels(
                ((align + dot_position), 0), 
                color
              )
            )

        self.matrix.draw_pixels_layout(
            self.layout.indicator_dots,
            pixels,
            (pixels[-1].position[0] - pixels[0].position[0], 1)
        )
