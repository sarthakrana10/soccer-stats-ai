import asyncio
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
def search_player(name: str) -> str:
    """Search for a player by name. Returns their ID, team, and position.
    Use this first whenever you need a player's ID for other tools.
    """
    client = FootballAPIClient()
    try:
        data = _run(client.search_player(name))
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
def get_player_recent_matches(player_name: str, last_n: int = 5) -> str:
    """Get a player's team results from their last N matches (default 5) plus season totals.
    Shows date, home/away, opponent, and result for each game.
    """
    client = FootballAPIClient()
    try:
        search_data = _run(client.search_player(player_name, league_id=DEFAULT_LEAGUE_ID, season=CURRENT_SEASON))
        results = search_data.get("response", [])
        if not results:
            return f"No player found matching '{player_name}'."

        player = results[0]["player"]
        player_id = player["id"]
        team_id = results[0]["statistics"][0]["team"]["id"]
        team_name = results[0]["statistics"][0]["team"]["name"]

        fixture_data = _run(
            client.get_team_fixtures(team_id, DEFAULT_LEAGUE_ID, CURRENT_SEASON)
        )
        stats_data = _run(
            client.get_player_stats(player_id, DEFAULT_LEAGUE_ID, CURRENT_SEASON)
        )
    except FootballAPIError as e:
        return f"API error: {e}"

    df = process_team_fixtures(fixture_data, team_id)
    if df.empty:
        return f"No match data found for {team_name} this season."
    df = df.head(last_n)

    season_df = process_player_season_stats(stats_data)
    season_line = ""
    if not season_df.empty:
        row = season_df.iloc[0]
        season_line = (
            f"\n\n**{player['name']} 2024-25 season totals:** "
            f"{int(row['Goals'])} goals, {int(row['Assists'])} assists in {int(row['Appearances'])} appearances"
        )

    return (
        f"**{player['name']} ({team_name}) — last {len(df)} matches**\n\n"
        f"{dataframe_to_markdown(df)}"
        f"{season_line}"
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
