import pandas as pd


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def process_player_fixtures(raw_json: dict, player_id: int) -> pd.DataFrame:
    """Extract per-match stats for a specific player from fixture responses."""
    rows = []
    for fixture in raw_json.get("response", []):
        date = fixture["fixture"]["date"][:10]
        home = fixture["teams"]["home"]["name"]
        away = fixture["teams"]["away"]["name"]
        home_goals = fixture["goals"]["home"]
        away_goals = fixture["goals"]["away"]

        # Find the player's stats within this fixture
        player_stats = None
        for team_block in fixture.get("players", []):
            for p in team_block.get("players", []):
                if p["player"]["id"] == player_id:
                    player_stats = p["statistics"][0]
                    player_team_id = team_block["team"]["id"]
                    break
            if player_stats:
                break

        if not player_stats:
            continue

        # Determine opponent and result from the player's team perspective
        home_team_id = fixture["teams"]["home"]["id"]
        if player_team_id == home_team_id:
            opponent = away
            gf, ga = home_goals, away_goals
        else:
            opponent = home
            gf, ga = away_goals, home_goals

        result = "W" if gf > ga else ("D" if gf == ga else "L")

        rows.append({
            "Date": date,
            "Opponent": opponent,
            "Result": f"{result} {gf}-{ga}",
            "Goals": player_stats["goals"]["total"] or 0,
            "Assists": player_stats["goals"]["assists"] or 0,
            "Minutes": player_stats["games"]["minutes"] or 0,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Date", ascending=False).reset_index(drop=True)
    return df


def process_player_season_stats(raw_json: dict) -> pd.DataFrame:
    """Extract season aggregate stats for a player."""
    rows = []
    for entry in raw_json.get("response", []):
        player = entry["player"]
        for stat in entry.get("statistics", []):
            rows.append({
                "Player": player["name"],
                "Team": stat["team"]["name"],
                "League": stat["league"]["name"],
                "Appearances": stat["games"].get("appearences") or 0,
                "Goals": stat["goals"].get("total") or 0,
                "Assists": stat["goals"].get("assists") or 0,
                "Minutes": stat["games"].get("minutes") or 0,
                "Yellow Cards": stat["cards"].get("yellow") or 0,
                "Red Cards": stat["cards"].get("red") or 0,
            })
    return pd.DataFrame(rows)


def process_standings(raw_json: dict) -> pd.DataFrame:
    """Extract league standings table."""
    rows = []
    try:
        standings = raw_json["response"][0]["league"]["standings"][0]
    except (KeyError, IndexError):
        return pd.DataFrame()

    for entry in standings:
        all_stats = entry["all"]
        rows.append({
            "Pos": entry["rank"],
            "Team": entry["team"]["name"],
            "P": all_stats["played"],
            "W": all_stats["win"],
            "D": all_stats["draw"],
            "L": all_stats["lose"],
            "GF": all_stats["goals"]["for"],
            "GA": all_stats["goals"]["against"],
            "GD": entry["goalsDiff"],
            "Pts": entry["points"],
            "Form": entry.get("form", ""),
        })
    return pd.DataFrame(rows)


def process_top_scorers(raw_json: dict) -> pd.DataFrame:
    """Extract top scorers list."""
    rows = []
    for i, entry in enumerate(raw_json.get("response", []), start=1):
        player = entry["player"]
        stat = entry["statistics"][0]
        rows.append({
            "Rank": i,
            "Player": player["name"],
            "Team": stat["team"]["name"],
            "Goals": stat["goals"].get("total") or 0,
            "Assists": stat["goals"].get("assists") or 0,
            "Appearances": stat["games"].get("appearences") or 0,
        })
    return pd.DataFrame(rows)


def process_team_stats(raw_json: dict) -> dict:
    """Extract team season summary as a plain dict."""
    r = raw_json.get("response", {})
    if not r:
        return {}

    fixtures = r.get("fixtures", {})
    goals = r.get("goals", {})
    return {
        "team": r["team"]["name"],
        "league": r["league"]["name"],
        "played": fixtures.get("played", {}).get("total", 0),
        "wins": fixtures.get("wins", {}).get("total", 0),
        "draws": fixtures.get("draws", {}).get("total", 0),
        "losses": fixtures.get("loses", {}).get("total", 0),
        "goals_for": goals.get("for", {}).get("total", {}).get("total", 0),
        "goals_against": goals.get("against", {}).get("total", {}).get("total", 0),
        "clean_sheets": r.get("clean_sheet", {}).get("total", 0),
        "form": r.get("form", ""),
    }


def process_head_to_head(raw_json: dict) -> pd.DataFrame:
    """Extract recent head-to-head results."""
    rows = []
    for fixture in raw_json.get("response", []):
        date = fixture["fixture"]["date"][:10]
        home = fixture["teams"]["home"]["name"]
        away = fixture["teams"]["away"]["name"]
        home_goals = fixture["goals"]["home"]
        away_goals = fixture["goals"]["away"]

        if fixture["teams"]["home"]["winner"]:
            winner = home
        elif fixture["teams"]["away"]["winner"]:
            winner = away
        else:
            winner = "Draw"

        rows.append({
            "Date": date,
            "Home": home,
            "Away": away,
            "Score": f"{home_goals}-{away_goals}",
            "Winner": winner,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Date", ascending=False).reset_index(drop=True)
    return df
