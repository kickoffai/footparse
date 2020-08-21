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
        'age': 31,
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


def test_matchpage_swid():
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.swid == 2024887


def test_matchpage_info():
    truth = {
        'team1_name': 'Germany',
        'team1_swid': 1037,
        'team2_name': 'Italy',
        'team2_swid': 1318,
        'competition': 'European Championship',
        'date': date(2016, 7, 2),
        'timestamp': 1467486000,
        'venue': 'Stade Matmut-Atlantique (Bordeaux)',
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.info == truth


def test_matchpage_no_kickoff_time():
    """Sometimes there is no kick-off time indicated."""
    truth = {
        'team1_name': 'Italy',
        'team1_swid': 1318,
        'team2_name': 'USSR',
        'team2_swid': 2823,
        'competition': 'Friendlies',
        'date': date(1991, 6, 16),
    }
    path = data_path('soccerway_match_notime.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.info == truth


def test_matchpage_scores():
    data = (
        ('soccerway_match.html', {
            'score_ft_team1': 1,
            'score_ft_team2': 1,
            'score_et_team1': 1,
            'score_et_team2': 1,
            'score_kfpm_team1': 6,
            'score_kfpm_team2': 5,
        }),
        ('soccerway_match2.html', {
            'score_ft_team1': 3,
            'score_ft_team2': 1,
            'score_ht_team1': 1,
            'score_ht_team2': 0,
        }),
        ('soccerway_match_notime.html', {
            'score_ft_team1': 1,
            'score_ft_team2': 1,
        }),
    )
    for path, res in data:
        page = soccerway.MatchPage.from_file(data_path(path))
        assert page.scores == res


def test_matchpage_competition_swid():
    data = (
        ('soccerway_match.html', 25),
        ('soccerway_match2.html', 90),
    )
    for path, cid in data:
        page = soccerway.MatchPage.from_file(data_path(path))
        assert page.competition_swid == cid


def test_matchpage_starters():
    oezil = {  # Scored a goal during the game.
        'display_name': 'M. \u00D6zil',
        'events': [{
            'type': 'Goal',
            'minute': 65
        }],
        'swid': 1986,
        'shirt_number': 8
    }
    buffon = {  # A goalkeeper.
        'events': [],
        'swid': 53,
        'shirt_number': 1,
        'display_name': 'G. Buffon',
    }
    chiellini = {  # Got substituted at 120+1'.
        'events': [],
        'swid': 17684,
        'shirt_number': 3,
        'subst_out': -1,
        'display_name': 'G. Chiellini'
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    starters = page.starters
    assert starters["team1"][5] == oezil
    assert starters["team2"][0] == buffon
    assert starters["team2"][3] == chiellini
    for team in ("team1", "team2"):
        assert len(starters[team]) == 11


def test_matchpage_multiple_events():
    # One of the players, D. Buonanotte, got booked and scored a goal.
    truth = [
        {'type': 'Yellow card', 'minute': 33,},
        {'type': 'Goal', 'minute': 52,}
    ]
    path = data_path('soccerway_match2.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.starters["team1"][5]["events"] == truth


def test_matchpage_substitutes():
    schweinsteiger = {
        'shirt_number': 7,
        'display_name': 'B. Schweinsteiger',
        'swid': 35,
        'subst_in': -1,
        'events': [{
            'minute': 112,
            'type': 'Yellow card'
        }],
    }
    sirigu = {
        'shirt_number': 12,
        'display_name': 'S. Sirigu',
        'swid': 58378,
        'events': [],
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    substitutes = page.substitutes
    assert substitutes["team1"][0] == schweinsteiger
    assert substitutes["team2"][5] == sirigu


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


def test_matchpage_no_minutes():
    """Sometimes the time of events isn't available."""
    path = data_path('soccerway_match_nodetails.html')
    page = soccerway.MatchPage.from_file(path)
    cichero = page.starters['team1'][3]
    assert cichero['events'] == [{'type': 'Yellow card'}]


def test_matchpage_subst():
    """Sometimes the time of substitutions is not indicated."""
    path = data_path('soccerway_match_subst.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.starters["team1"][8]["subst_out"] == -1
    assert page.substitutes["team1"][0]["subst_in"] == -1


def test_seasonpage_rounds():
    truth = [
        {'name': 'Final', 'swid': 31064},
        {'name': 'Semi-finals', 'swid': 31063},
        {'name': 'Quarter-finals', 'swid': 31062},
        {'name': '8th Finals', 'swid': 31061},
        {'name': 'Group Stage', 'swid': 31060}
    ] 
    path = data_path('soccerway_season_euro16.html')
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
    path = data_path('soccerway_season_euro16.html')
    page = soccerway.SeasonPage.from_file(path)
    seasons = list(page.seasons)
    assert len(seasons) == 16
    assert seasons[3] == euro08


def test_seasonpage_matches():
    match_future = {
        'swid': 3288329,
        'timestamp': 1598209200,
        'team1': {
            'swid': 886,
            'name': 'PSG',
        },
        'team2': {
            'swid': 961,
            'name': 'Bayern Munich',
        },
    }
    match_past = {
        'swid': 3288327,
        'timestamp': 1597777200,
        'team1': {
            'swid': 13410,
            'name': 'RB Leipzig',
            'goals': 0,
        },
        'team2': {
            'swid': 886,
            'name': 'PSG',
            'goals': 3,
        },
    }
    path = data_path('soccerway_season_cl.html')
    page = soccerway.SeasonPage.from_file(path)
    matches = list(page.matches)
    assert matches[0] == match_future
    assert matches[1] == match_past


def test_seasonpage_swid_euro():
    path = data_path('soccerway_season_euro16.html')
    page = soccerway.SeasonPage.from_file(path)
    assert page.swid == 7576


def test_seasonpage_swid_superlig():
    path = data_path('soccerway_season_superlig.html')
    page = soccerway.SeasonPage.from_file(path)
    assert page.swid == 12658


def test_roundpage_swid():
    path = data_path('soccerway_round4.html')
    page = soccerway.RoundPage.from_file(path)
    assert page.swid == 54137


def test_roundpage_matches():
    # Timestamp is not part of <span class="timestamp"> element.
    path = data_path('soccerway_round2.html')
    page = soccerway.RoundPage.from_file(path)
    list(page.matches)
    # Some rows in the matches table contain aggregate results.
    path = data_path('soccerway_round3.html')
    page = soccerway.RoundPage.from_file(path)
    list(page.matches)


def test_matchlistpage_is_paginated():
    path = data_path('soccerway_season_euro16.html')
    page = soccerway.SeasonPage.from_file(path)
    assert not page.is_paginated
    path = data_path('soccerway_season_superlig.html')
    page = soccerway.SeasonPage.from_file(path)
    assert page.is_paginated


def test_matchesblock_info():
    path = data_path('soccerway_matchesblock1.json')
    block = soccerway.MatchesBlock.from_file(path)
    assert block.round_swid == 54142
    assert block.page == 0
    assert block.has_previous
    assert not block.has_next


def test_matchesblock_matches():
    path = data_path('soccerway_matchesblock1.json')
    block = soccerway.MatchesBlock.from_file(path)
    matches = list(block.matches)
    assert len(matches) == 10
    assert matches[3] == {
        'timestamp': 1576086900,
        'swid': 3160589,
        'team1': {
            'name': 'Shakhtar Donetsk',
            'swid': 2254,
            'goals': 0,
        },
        'team2': {
            'name': 'Atalanta',
            'swid': 1255,
            'goals': 3,
        },
    }


def test_matchesblock_empty():
    path = data_path('soccerway_matchesblock2.json')
    block = soccerway.MatchesBlock.from_file(path)
    assert block.round_swid == 54138
    assert block.page == 50
    assert block.has_previous
    assert not block.has_next
    matches = list(block.matches)
    assert len(matches) == 0
