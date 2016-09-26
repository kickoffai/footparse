from datetime import date
from footparse import eloratings
from testutils import data_path


def test_homepage_date():
    path = data_path('eloratings_home.html')
    page = eloratings.HomePage.from_file(path)
    assert page.date == date(2016, 9, 18)


def test_homepage_ratings():
    truth = {
        'rank': 234,
        'team': 'Northern Mariana Islands',
        'href': 'N_Marianas.htm',
        'rating': 451,
        'highest_rank': None,
        'highest_rating': None,
        '1yr_change_rank': -1,
        '1yr_change_rating': -58,
        'matches_total': 23,
        'matches_home': 3,
        'matches_away': 8,
        'matches_neutral': 12,
        'matches_wins': 3,
        'matches_losses': 19,
        'matches_draws': 1,
        'goals_for': 29,
        'goals_against': 103,
    }
    path = data_path('eloratings_home.html')
    page = eloratings.HomePage.from_file(path)
    ratings = list(page.ratings)
    assert len(ratings) == 234
    assert ratings[233] == truth


def test_teampage_country():
    path = data_path('eloratings_germany.html')
    page = eloratings.TeamPage.from_file(path)
    assert page.country == 'Germany'


def test_teampage_entries():
    truth = {
        'date': date(1972, 6, 18),
        'competition': 'European Championship in Belgium',
        'team1': {
            'name': 'West Germany',
            'goals': 3,
            'rating_diff': 31,
            'rating': 2098,
            'rank_diff': 0,
            'rank': 2,
        },
        'team2': {
            'name': 'Soviet Union',
            'goals': 0,
            'rating_diff': -31,
            'rating': 1931,
            'rank_diff': -1,
            'rank': 4,
        },
    }
    path = data_path('eloratings_germany.html')
    page = eloratings.TeamPage.from_file(path)
    entries = list(page.entries)
    assert len(entries) == 919
    assert entries[372] == truth
