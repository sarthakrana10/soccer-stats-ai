import pytest


@pytest.fixture
def player_fixtures_response():
    """Realistic API-Football /fixtures?player= response for Salah (player_id=306)."""
    return {
        "results": 3,
        "errors": [],
        "response": [
            {
                "fixture": {"id": 1001, "date": "2025-02-22T20:00:00+00:00"},
                "teams": {
                    "home": {"id": 40, "name": "Liverpool", "winner": True},
                    "away": {"id": 42, "name": "Arsenal", "winner": False},
                },
                "goals": {"home": 2, "away": 0},
                "players": [
                    {
                        "team": {"id": 40},
                        "players": [
                            {
                                "player": {"id": 306, "name": "Mohamed Salah"},
                                "statistics": [
                                    {
                                        "games": {"minutes": 90},
                                        "goals": {"total": 2, "assists": 0},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            {
                "fixture": {"id": 1002, "date": "2025-02-15T15:00:00+00:00"},
                "teams": {
                    "home": {"id": 50, "name": "Manchester City", "winner": True},
                    "away": {"id": 40, "name": "Liverpool", "winner": False},
                },
                "goals": {"home": 3, "away": 1},
                "players": [
                    {
                        "team": {"id": 40},
                        "players": [
                            {
                                "player": {"id": 306, "name": "Mohamed Salah"},
                                "statistics": [
                                    {
                                        "games": {"minutes": 90},
                                        "goals": {"total": 1, "assists": 0},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            {
                "fixture": {"id": 1003, "date": "2025-02-08T15:00:00+00:00"},
                "teams": {
                    "home": {"id": 40, "name": "Liverpool", "winner": False},
                    "away": {"id": 35, "name": "Brentford", "winner": False},
                },
                "goals": {"home": 1, "away": 1},
                "players": [
                    {
                        "team": {"id": 40},
                        "players": [
                            {
                                "player": {"id": 306, "name": "Mohamed Salah"},
                                "statistics": [
                                    {
                                        "games": {"minutes": 72},
                                        "goals": {"total": 0, "assists": 1},
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        ],
    }


@pytest.fixture
def player_season_stats_response():
    """Realistic API-Football /players?id=&season=&league= response."""
    return {
        "results": 1,
        "errors": [],
        "response": [
            {
                "player": {"id": 306, "name": "Mohamed Salah"},
                "statistics": [
                    {
                        "team": {"id": 40, "name": "Liverpool"},
                        "league": {"id": 39, "name": "Premier League"},
                        "games": {"appearences": 28, "minutes": 2340},
                        "goals": {"total": 18, "assists": 8},
                        "cards": {"yellow": 1, "red": 0},
                    }
                ],
            }
        ],
    }


@pytest.fixture
def standings_response():
    """Realistic API-Football /standings response (top 3 rows)."""
    return {
        "results": 1,
        "errors": [],
        "response": [
            {
                "league": {
                    "standings": [
                        [
                            {
                                "rank": 1,
                                "team": {"id": 40, "name": "Liverpool"},
                                "points": 65,
                                "goalsDiff": 42,
                                "form": "WWWDW",
                                "all": {
                                    "played": 28,
                                    "win": 20,
                                    "draw": 5,
                                    "lose": 3,
                                    "goals": {"for": 68, "against": 26},
                                },
                            },
                            {
                                "rank": 2,
                                "team": {"id": 42, "name": "Arsenal"},
                                "points": 55,
                                "goalsDiff": 24,
                                "form": "WDWWL",
                                "all": {
                                    "played": 28,
                                    "win": 16,
                                    "draw": 7,
                                    "lose": 5,
                                    "goals": {"for": 54, "against": 30},
                                },
                            },
                            {
                                "rank": 3,
                                "team": {"id": 50, "name": "Manchester City"},
                                "points": 50,
                                "goalsDiff": 18,
                                "form": "DWLWW",
                                "all": {
                                    "played": 28,
                                    "win": 15,
                                    "draw": 5,
                                    "lose": 8,
                                    "goals": {"for": 52, "against": 34},
                                },
                            },
                        ]
                    ]
                }
            }
        ],
    }


@pytest.fixture
def top_scorers_response():
    """Realistic API-Football /players/topscorers response."""
    return {
        "results": 2,
        "errors": [],
        "response": [
            {
                "player": {"id": 1100, "name": "Erling Haaland"},
                "statistics": [
                    {
                        "team": {"name": "Manchester City"},
                        "goals": {"total": 24, "assists": 5},
                        "games": {"appearences": 27},
                    }
                ],
            },
            {
                "player": {"id": 306, "name": "Mohamed Salah"},
                "statistics": [
                    {
                        "team": {"name": "Liverpool"},
                        "goals": {"total": 18, "assists": 8},
                        "games": {"appearences": 28},
                    }
                ],
            },
        ],
    }


@pytest.fixture
def team_stats_response():
    """Realistic API-Football /teams/statistics response."""
    return {
        "results": 1,
        "errors": [],
        "response": {
            "team": {"id": 42, "name": "Arsenal"},
            "league": {"id": 39, "name": "Premier League"},
            "fixtures": {
                "played": {"total": 28},
                "wins": {"total": 16},
                "draws": {"total": 7},
                "loses": {"total": 5},
            },
            "goals": {
                "for": {"total": {"total": 54}},
                "against": {"total": {"total": 30}},
            },
            "clean_sheet": {"total": 9},
            "form": "WDWWL",
        },
    }


@pytest.fixture
def head_to_head_response():
    """Realistic API-Football /fixtures/headtohead response."""
    return {
        "results": 2,
        "errors": [],
        "response": [
            {
                "fixture": {"id": 2001, "date": "2025-01-10T17:30:00+00:00"},
                "teams": {
                    "home": {"id": 40, "name": "Liverpool", "winner": True},
                    "away": {"id": 50, "name": "Manchester City", "winner": False},
                },
                "goals": {"home": 2, "away": 0},
            },
            {
                "fixture": {"id": 2002, "date": "2024-09-22T14:00:00+00:00"},
                "teams": {
                    "home": {"id": 50, "name": "Manchester City", "winner": False},
                    "away": {"id": 40, "name": "Liverpool", "winner": False},
                },
                "goals": {"home": 1, "away": 1},
            },
        ],
    }
