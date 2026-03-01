import asyncio
import pandas as pd
from langchain_core.tools import tool

from app.services.football_api import FootballAPIClient, FootballAPIError
from app.services.data_processing import (
    dataframe_to_markdown,
    process_head_to_head,
    process_team_fixtures,
    process_player_season_stats,
    process_standings,
    process_team_stats,
    process_top_scorers,
)

LEAGUE_IDS = {
    "premier league": 39,
    "pl": 39,
    "epl": 39,
    "la liga": 140,
    "bundesliga": 78,
    "serie a": 135,
    "ligue 1": 61,
    "champions league": 2,
    "ucl": 2,
}

CURRENT_SEASON = 2024  # Free tier max; covers the 2024-25 season
DEFAULT_LEAGUE_ID = 39


def _resolve_league(league_name: str) -> int:
    return LEAGUE_IDS.get(league_name.lower().strip(), DEFAULT_LEAGUE_ID)


def _run(coro):
    """Run an async function from a sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@tool
def search_player(name: str, league_name: str = "Premier League") -> str:
    """Search for a player by name. Returns their ID, team, and position.
    Use league_name to search in a specific league (e.g. 'La Liga' for Spanish players).
    """
    client = FootballAPIClient()
    league_id = _resolve_league(league_name)
    try:
        data = _run(client.search_player(name, league_id=league_id, season=CURRENT_SEASON))
    except FootballAPIError as e:
        return f"API error: {e}"

    results = data.get("response", [])
    if not results:
        return f"No player found matching '{name}'."

    lines = []
    for entry in results[:5]:
        p = entry["player"]
        teams = [s["team"]["name"] for s in entry.get("statistics", [])]
        team = teams[0] if teams else "Unknown"
        lines.append(f"- {p['name']} (ID: {p['id']}) — {team}")
    return "Players found:\n" + "\n".join(lines)


@tool
def get_player_recent_matches(player_name: str, last_n: int = 5, league_name: str = "Premier League") -> str:
    """Get a player's individual stats (goals, assists, minutes) for their last N matches (default 5).
    Shows per-match breakdown with date, opponent, goals, assists, and minutes played.
    Use league_name to specify the league if the player is not in the Premier League.
    """
    client = FootballAPIClient()
    league_id = _resolve_league(league_name)
    try:
        search_data = _run(client.search_player(player_name, league_id=league_id, season=CURRENT_SEASON))
        results = search_data.get("response", [])
        if not results:
            return f"No player found matching '{player_name}' in {league_name}."

        player = results[0]["player"]
        player_id = player["id"]
        team_id = results[0]["statistics"][0]["team"]["id"]
        team_name = results[0]["statistics"][0]["team"]["name"]

        fixture_data = _run(
            client.get_team_fixtures(team_id, league_id, CURRENT_SEASON)
        )
    except FootballAPIError as e:
        return f"API error: {e}"

    df = process_team_fixtures(fixture_data, team_id)
    if df.empty:
        return f"No match data found for {team_name} this season."
    # Get fixture IDs for the last N matches
    fixtures_sorted = sorted(
        fixture_data.get("response", []),
        key=lambda f: f["fixture"]["date"],
        reverse=True,
    )
    recent_fixtures = fixtures_sorted[:last_n]

    # Fetch per-match player stats
    rows = []
    for fix in recent_fixtures:
        fix_id = fix["fixture"]["id"]
        date = fix["fixture"]["date"][:10]
        home_id = fix["teams"]["home"]["id"]
        home_name = fix["teams"]["home"]["name"]
        away_name = fix["teams"]["away"]["name"]
        home_goals = fix["goals"].get("home") or 0
        away_goals = fix["goals"].get("away") or 0

        if team_id == home_id:
            opponent = away_name
            venue = "H"
            gf, ga = home_goals, away_goals
        else:
            opponent = home_name
            venue = "A"
            gf, ga = away_goals, home_goals
        result = "W" if gf > ga else ("D" if gf == ga else "L")

        # Get individual player stats for this fixture
        p_goals, p_assists, p_minutes = 0, 0, 0
        try:
            fix_players = _run(client.get_fixture_players(fix_id))
            for team_data in fix_players.get("response", []):
                for p in team_data.get("players", []):
                    if p["player"]["id"] == player_id:
                        stat = p["statistics"][0]
                        p_goals = stat.get("goals", {}).get("total") or 0
                        p_assists = stat.get("goals", {}).get("assists") or 0
                        p_minutes = stat.get("games", {}).get("minutes") or 0
                        break
        except FootballAPIError:
            pass

        rows.append({
            "Date": date,
            "H/A": venue,
            "Opponent": opponent,
            "Result": f"{result} {gf}-{ga}",
            "Goals": p_goals,
            "Assists": p_assists,
            "Minutes": p_minutes,
        })

    match_df = pd.DataFrame(rows)
    total_goals = match_df["Goals"].sum()
    total_assists = match_df["Assists"].sum()

    return (
        f"**{player['name']} ({team_name}) — last {len(match_df)} matches**\n\n"
        f"{dataframe_to_markdown(match_df)}\n\n"
        f"**Totals: {total_goals} goals, {total_assists} assists in {len(match_df)} matches**"
    )


@tool
def get_player_season_stats(player_name: str, league_name: str = "Premier League") -> str:
    """Get a player's full season aggregate stats (goals, assists, appearances, etc.)."""
    client = FootballAPIClient()
    league_id = _resolve_league(league_name)
    try:
        search_data = _run(client.search_player(player_name, league_id=DEFAULT_LEAGUE_ID, season=CURRENT_SEASON))
        results = search_data.get("response", [])
        if not results:
            return f"No player found matching '{player_name}'."

        player_id = results[0]["player"]["id"]
        player_name_resolved = results[0]["player"]["name"]

        stats_data = _run(
            client.get_player_stats(player_id, league_id, CURRENT_SEASON)
        )
    except FootballAPIError as e:
        return f"API error: {e}"

    df = process_player_season_stats(stats_data)
    if df.empty:
        return f"No season stats found for {player_name_resolved}."

    return f"**{player_name_resolved} — {CURRENT_SEASON} season stats**\n\n{dataframe_to_markdown(df)}"


@tool
def get_league_standings(league_name: str = "Premier League") -> str:
    """Get the current standings table for a league."""
    client = FootballAPIClient()
    league_id = _resolve_league(league_name)
    try:
        data = _run(client.get_standings(league_id, CURRENT_SEASON))
    except FootballAPIError as e:
        return f"API error: {e}"

    df = process_standings(data)
    if df.empty:
        return f"No standings data found for {league_name}."

    return f"**{league_name} Standings — {CURRENT_SEASON} season**\n\n{dataframe_to_markdown(df)}"


@tool
def get_top_scorers(league_name: str = "Premier League") -> str:
    """Get the top scorers in a league for the current season."""
    client = FootballAPIClient()
    league_id = _resolve_league(league_name)
    try:
        data = _run(client.get_top_scorers(league_id, CURRENT_SEASON))
    except FootballAPIError as e:
        return f"API error: {e}"

    df = process_top_scorers(data)
    if df.empty:
        return f"No top scorer data found for {league_name}."

    return f"**{league_name} Top Scorers — {CURRENT_SEASON} season**\n\n{dataframe_to_markdown(df)}"


@tool
def get_team_statistics(team_name: str, league_name: str = "Premier League") -> str:
    """Get a team's season statistics (wins, losses, goals, form, clean sheets)."""
    client = FootballAPIClient()
    league_id = _resolve_league(league_name)
    try:
        team_data = _run(client.get_team_id(team_name))
        teams = team_data.get("response", [])
        if not teams:
            return f"No team found matching '{team_name}'."

        team_id = teams[0]["team"]["id"]
        team_name_resolved = teams[0]["team"]["name"]

        stats_data = _run(
            client.get_team_stats(team_id, league_id, CURRENT_SEASON)
        )
    except FootballAPIError as e:
        return f"API error: {e}"

    stats = process_team_stats(stats_data)
    if not stats:
        return f"No stats found for {team_name_resolved}."

    return (
        f"**{stats['team']} — {stats['league']} {CURRENT_SEASON} season**\n\n"
        f"| Stat | Value |\n|------|-------|\n"
        f"| Played | {stats['played']} |\n"
        f"| Wins | {stats['wins']} |\n"
        f"| Draws | {stats['draws']} |\n"
        f"| Losses | {stats['losses']} |\n"
        f"| Goals For | {stats['goals_for']} |\n"
        f"| Goals Against | {stats['goals_against']} |\n"
        f"| Clean Sheets | {stats['clean_sheets']} |\n"
        f"| Form (last 5) | {stats['form'][-5:] if stats['form'] else 'N/A'} |"
    )


@tool
def get_head_to_head(team1: str, team2: str) -> str:
    """Get recent head-to-head results between two teams."""
    client = FootballAPIClient()
    try:
        t1_data = _run(client.get_team_id(team1))
        t2_data = _run(client.get_team_id(team2))

        t1_results = t1_data.get("response", [])
        t2_results = t2_data.get("response", [])

        if not t1_results:
            return f"No team found matching '{team1}'."
        if not t2_results:
            return f"No team found matching '{team2}'."

        t1_id = t1_results[0]["team"]["id"]
        t1_name = t1_results[0]["team"]["name"]
        t2_id = t2_results[0]["team"]["id"]
        t2_name = t2_results[0]["team"]["name"]

        h2h_data = _run(client.get_head_to_head(t1_id, t2_id))
    except FootballAPIError as e:
        return f"API error: {e}"

    df = process_head_to_head(h2h_data)
    if df.empty:
        return f"No head-to-head data found for {t1_name} vs {t2_name}."

    return (
        f"**{t1_name} vs {t2_name} — Recent Head-to-Head**\n\n"
        f"{dataframe_to_markdown(df)}"
    )


ALL_TOOLS = [
    search_player,
    get_player_recent_matches,
    get_player_season_stats,
    get_league_standings,
    get_top_scorers,
    get_team_statistics,
    get_head_to_head,
]
