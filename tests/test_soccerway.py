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
    starters = page.starters
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
        'team1': {'display_name': 'J. Löw', 'swid': 33477},
        'team2': {'display_name': 'A. Conte', 'swid': 105100},
    }
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.coaches == truth


def test_matchpage_swid():
    path = data_path('soccerway_match.html')
    page = soccerway.MatchPage.from_file(path)
    assert page.swid == 2024887
