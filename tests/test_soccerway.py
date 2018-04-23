from datetime import date
from footparse import soccerway
from testutils import data_path


def test_teampage_country():
    path = data_path('soccerway_team.html')
    page = soccerway.TeamPage.from_file(path)
    assert page.country == 'Chile'


def test_teampage_name():
    path = data_path('soccerway_team.html')
    page = soccerway.TeamPage.from_file(path)
    assert page.name == 'CD Universidad Cat\u00F3lica'


def test_teampage_swid():
    path = data_path('soccerway_team.html')
    page = soccerway.TeamPage.from_file(path)
    assert page.swid == 418


def test_personpage_passport():
    truth = {
        'display_name': 'Jordi Alba',
        'first_name': 'Jordi',
        'last_name': 'Alba Ramos',
        'nationality': 'Spain',
        'birthdate': date(1989, 3, 21),
        'age': 27,
        'birthcountry': 'Spain',
        'birthplace': 'L\'Hospitalet de Llobregat',
        'position': 'Defender',
        'height': 170,
        'weight': 68,
        'foot': 'Left',
    }
    path = data_path('soccerway_person.html')
    page = soccerway.PersonPage.from_file(path)
    assert page.passport == truth


def test_personpage_swid():
    path = data_path('soccerway_person.html')
    page = soccerway.PersonPage.from_file(path)
    assert page.swid == 60883


def test_matchpage_info():
    truth = {
        'team1_name': 'Germany',
        'team1_swid': 1037,
        'team2_name': 'Italy',
        'team2_swid': 1318,
        'competition': 'European Championship',
        'date': date(2016, 7, 2),
        'timestamp': 1467486000,
        'score_ht_team1': 0,
        'score_ht_team2': 0,
        'score_ft_team1': 1,
        'score_ft_team2': 1,
        'score_et_team1': 1,
        'score_et_team2': 1,
        'score_kfpm_team1': 6,
        'score_kfpm_team2': 5,
        'venue': 'Stade Matmut-Atlantique (Bordeaux)',
        'attendance': 38764,
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.info == truth


def test_matchpage_starters():
    oezil = {  # Scored a goal during the game.
        'display_name': 'M. \u00D6zil',
        'nationality': 'Germany',
        'events': [{
            'type': 'Goal',
            'minute': 65
        }],
        'swid': 1986,
        'shirt_number': 8
    }
    buffon = {  # A goalkeeper.
        'nationality': 'Italy',
        'events': [],
        'swid': 53,
        'shirt_number': 1,
        'display_name': 'G. Buffon',
        'position': 'Goalkeeper'
    }
    chiellini = {  # Got substituted at 120+1'.
        'nationality': 'Italy',
        'events': [],
        'swid': 17684,
        'shirt_number': 3,
        'subst_out': 120,
        'display_name': 'G. Chiellini'
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    starters = page.starters
    assert starters["team1"][5] == oezil
    assert starters["team2"][0] == buffon
    assert starters["team2"][2] == chiellini


def test_matchpage_multiple_events():
    # One of the players, D. Buonanotte, got booked and scored a goal.
    truth = [
        {'type': 'Yellow card', 'minute': 33,},
        {'type': 'Goal', 'minute': 52,}
    ]
    path = data_path('soccerway_match2.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.starters["team1"][7]["events"] == truth


def test_matchpage_substitutes():
    schweinsteiger = {
        'nationality': 'Germany',
        'shirt_number': 7,
        'display_name': 'B. Schweinsteiger',
        'swid': 35,
        'subst_in': 16,
        'events': [{
            'minute': 112,
            'type': 'Yellow card'
        }]
    }
    sirigu = {
        'nationality': 'Italy',
        'shirt_number': 12,
        'display_name': 'S. Sirigu',
        'swid': 58378,
        'position': 'Goalkeeper',
        'events': []
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    substitutes = page.substitutes
    assert substitutes["team1"][3] == schweinsteiger
    assert substitutes["team2"][1] == sirigu


def test_matchpage_coaches():
    truth = {
        'team1': [{'display_name': 'J. L\u00F6w', 'swid': 33477}],
        'team2': [{'display_name': 'A. Conte', 'swid': 105100}],
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.coaches == truth


def test_matchpage_swid():
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.swid == 2024887


def test_matchpage_no_shirt_numbers():
    """Some pages don't have shirt numbers."""
    path = data_path('soccerway_match_nonum.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.starters is not None


def test_seasonpage_rounds():
    truth = [
        {'name': 'Final', 'swid': 13557},
        {'name': 'Semi-finals', 'swid': 13556},
        {'name': 'Quarter-finals', 'swid': 13555},
        {'name': 'Group Stage', 'swid': 13552}
    ] 
    path = data_path('soccerway_season_euro12.html')
    page = soccerway.SeasonPage.from_file(path)
    rounds = list(page.rounds)
    assert rounds == truth


def test_seasonpage_no_rounds():
    path = data_path('soccerway_season_superlig.html')
    page = soccerway.SeasonPage.from_file(path)
    rounds = list(page.rounds)
    assert rounds == list()


def test_seasonpage_seasons():
    euro08 = {'swid': 1532, 'name': '2008 Austria/Switzerland'}
    path = data_path('soccerway_season_euro12.html')
    page = soccerway.SeasonPage.from_file(path)
    seasons = list(page.seasons)
    assert len(seasons) == 16
    assert seasons[3] == euro08


def test_seasonpage_matches():
    match_past = {
        'swid': 2291182,
        'timestamp': 1474799400,
        'team1': {
            'swid': 2235,
            'name': 'Kayserispor',
            'goals': 2,
        },
        'team2': {
            'swid': 2224,
            'name': 'Rizespor',
            'goals': 1,
        },
    }
    match_future = {
        'swid': 2291192,
        'timestamp': 1475337600,
        'team1': {
            'swid': 2216,
            'name': 'Gaziantepspor',
        },
        'team2': {
            'swid': 2227,
            'name': 'Bursaspor',
        },
    }
    path = data_path('soccerway_season_superlig.html')
    page = soccerway.SeasonPage.from_file(path)
    matches = list(page.matches)
    assert matches[0] == match_past
    assert matches[-1] == match_future


def test_seasonpage_swid_euro():
    path = data_path('soccerway_season_euro12.html')
    page = soccerway.SeasonPage.from_file(path)
    assert page.swid == 4943


def test_seasonpage_swid_superlig():
    path = data_path('soccerway_season_superlig.html')
    page = soccerway.SeasonPage.from_file(path)
    assert page.swid == 12658


def test_roundpage_swid():
    path = data_path('soccerway_round.html')
    page = soccerway.RoundPage.from_file(path)
    assert page.swid == 6910


def test_roundpage_matches():
    # Timestamp is not part of <span class="timestamp"> element.
    path = data_path('soccerway_round2.html')
    page = soccerway.RoundPage.from_file(path)
    list(page.matches)
    # Some rows in the matches table contain aggregate results.
    path = data_path('soccerway_round3.html')
    page = soccerway.RoundPage.from_file(path)
    list(page.matches)


def test_matchlistpage_is_last():
    path = data_path('soccerway_season_euro12.html')
    page = soccerway.SeasonPage.from_file(path)
    assert page.is_last
    path = data_path('soccerway_season_superlig.html')
    page = soccerway.SeasonPage.from_file(path)
    assert not page.is_last


def test_seasonpage_paginated_urls():
    gen = soccerway.SeasonPage.paginated_urls(12658)
    assert next(gen) == ("http://www.soccerway.mobi/?page=season&id=12658"
                         "&params={%22p%22%3A-1}")
    assert next(gen) == ("http://www.soccerway.mobi/?page=season&id=12658"
                         "&params={%22p%22%3A-2}")
