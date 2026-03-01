import httpx

from app.config import settings

BASE_URL = "https://v3.football.api-sports.io"


class FootballAPIError(Exception):
    pass


class FootballAPIClient:
    def __init__(self):
        self._headers = {
            "x-apisports-key": settings.api_football_key,
        }

    async def _get(self, endpoint: str, params: dict) -> dict:
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.get(
                endpoint, headers=self._headers, params=params
            )
            response.raise_for_status()
            data = response.json()
            if data.get("errors"):
                raise FootballAPIError(str(data["errors"]))
            return data

    async def search_player(self, name: str, league_id: int = 39, season: int = 2024) -> dict:
        return await self._get("/players", {"search": name, "league": league_id, "season": season})

    async def get_team_fixtures(
        self, team_id: int, league_id: int, season: int
    ) -> dict:
        return await self._get(
            "/fixtures",
            {"team": team_id, "league": league_id, "season": season},
        )

    async def get_player_stats(
        self, player_id: int, league_id: int, season: int
    ) -> dict:
        return await self._get(
            "/players",
            {"id": player_id, "league": league_id, "season": season},
        )

    async def get_standings(self, league_id: int, season: int) -> dict:
        return await self._get(
            "/standings", {"league": league_id, "season": season}
        )

    async def get_top_scorers(self, league_id: int, season: int) -> dict:
        return await self._get(
            "/players/topscorers",
            {"league": league_id, "season": season},
        )

    async def get_team_id(self, team_name: str) -> dict:
        return await self._get("/teams", {"search": team_name})

    async def get_team_stats(
        self, team_id: int, league_id: int, season: int
    ) -> dict:
        return await self._get(
            "/teams/statistics",
            {"team": team_id, "league": league_id, "season": season},
        )

    async def get_fixture_players(self, fixture_id: int) -> dict:
        return await self._get(
            "/fixtures/players", {"fixture": fixture_id}
        )

    async def get_head_to_head(self, team1_id: int, team2_id: int) -> dict:
        return await self._get(
            "/fixtures/headtohead",
            {"h2h": f"{team1_id}-{team2_id}"},
        )
