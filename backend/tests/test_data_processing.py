from app.services.data_processing import (
    dataframe_to_markdown,
    process_head_to_head,
    process_player_fixtures,
    process_player_season_stats,
    process_standings,
    process_team_stats,
    process_top_scorers,
)


class TestProcessPlayerFixtures:
    def test_returns_correct_row_count(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        assert len(df) == 3

    def test_columns_present(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        assert list(df.columns) == ["Date", "Opponent", "Result", "Goals", "Assists", "Minutes"]

    def test_goals_summed_correctly(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        assert df["Goals"].sum() == 3  # 2 + 1 + 0

    def test_win_result_computed_correctly(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        # Most recent fixture (Feb 22): Liverpool won 2-0 at home → W
        assert df.iloc[0]["Result"] == "W 2-0"

    def test_loss_result_computed_correctly(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        # Feb 15: Man City 3-1 Liverpool → Liverpool lost → L
        assert df.iloc[1]["Result"] == "L 1-3"

    def test_draw_result_computed_correctly(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        # Feb 8: Liverpool 1-1 Brentford → D
        assert df.iloc[2]["Result"] == "D 1-1"

    def test_opponent_is_the_other_team(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        assert df.iloc[0]["Opponent"] == "Arsenal"
        assert df.iloc[1]["Opponent"] == "Manchester City"
        assert df.iloc[2]["Opponent"] == "Brentford"

    def test_sorted_by_date_descending(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=306)
        dates = list(df["Date"])
        assert dates == sorted(dates, reverse=True)

    def test_unknown_player_id_returns_empty(self, player_fixtures_response):
        df = process_player_fixtures(player_fixtures_response, player_id=999)
        assert df.empty


class TestProcessPlayerSeasonStats:
    def test_returns_one_row(self, player_season_stats_response):
        df = process_player_season_stats(player_season_stats_response)
        assert len(df) == 1

    def test_correct_goals_and_assists(self, player_season_stats_response):
        df = process_player_season_stats(player_season_stats_response)
        assert df.iloc[0]["Goals"] == 18
        assert df.iloc[0]["Assists"] == 8

    def test_player_name(self, player_season_stats_response):
        df = process_player_season_stats(player_season_stats_response)
        assert df.iloc[0]["Player"] == "Mohamed Salah"


class TestProcessStandings:
    def test_returns_correct_row_count(self, standings_response):
        df = process_standings(standings_response)
        assert len(df) == 3

    def test_first_place_team(self, standings_response):
        df = process_standings(standings_response)
        assert df.iloc[0]["Team"] == "Liverpool"
        assert df.iloc[0]["Pts"] == 65

    def test_columns_present(self, standings_response):
        df = process_standings(standings_response)
        for col in ["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]:
            assert col in df.columns

    def test_goal_diff_correct(self, standings_response):
        df = process_standings(standings_response)
        assert df.iloc[0]["GD"] == 42

    def test_empty_response_returns_empty_df(self):
        df = process_standings({"response": []})
        assert df.empty


class TestProcessTopScorers:
    def test_returns_correct_row_count(self, top_scorers_response):
        df = process_top_scorers(top_scorers_response)
        assert len(df) == 2

    def test_rank_ordering(self, top_scorers_response):
        df = process_top_scorers(top_scorers_response)
        assert df.iloc[0]["Rank"] == 1
        assert df.iloc[0]["Player"] == "Erling Haaland"
        assert df.iloc[0]["Goals"] == 24

    def test_second_place(self, top_scorers_response):
        df = process_top_scorers(top_scorers_response)
        assert df.iloc[1]["Player"] == "Mohamed Salah"
        assert df.iloc[1]["Goals"] == 18


class TestProcessTeamStats:
    def test_returns_dict(self, team_stats_response):
        result = process_team_stats(team_stats_response)
        assert isinstance(result, dict)

    def test_correct_values(self, team_stats_response):
        result = process_team_stats(team_stats_response)
        assert result["team"] == "Arsenal"
        assert result["wins"] == 16
        assert result["draws"] == 7
        assert result["losses"] == 5
        assert result["goals_for"] == 54
        assert result["goals_against"] == 30
        assert result["clean_sheets"] == 9
        assert result["form"] == "WDWWL"

    def test_empty_response_returns_empty_dict(self):
        result = process_team_stats({"response": {}})
        assert result == {}


class TestProcessHeadToHead:
    def test_returns_correct_row_count(self, head_to_head_response):
        df = process_head_to_head(head_to_head_response)
        assert len(df) == 2

    def test_sorted_by_date_descending(self, head_to_head_response):
        df = process_head_to_head(head_to_head_response)
        dates = list(df["Date"])
        assert dates == sorted(dates, reverse=True)

    def test_winner_computed_correctly(self, head_to_head_response):
        df = process_head_to_head(head_to_head_response)
        assert df.iloc[0]["Winner"] == "Liverpool"   # 2-0 win
        assert df.iloc[1]["Winner"] == "Draw"         # 1-1

    def test_score_format(self, head_to_head_response):
        df = process_head_to_head(head_to_head_response)
        assert df.iloc[0]["Score"] == "2-0"


class TestDataframeToMarkdown:
    def test_outputs_markdown_table(self, standings_response):
        df = process_standings(standings_response)
        md = dataframe_to_markdown(df)
        assert "|" in md
        assert "Liverpool" in md
        assert "Pts" in md
