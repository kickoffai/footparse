import pytest

from footparse.betexplorer import CompetitionPage, MatchPage, OddsPage
from testutils import data_path
from datetime import date


@pytest.mark.skip(reason="BetExplorer layout has changed")
def test_competitionpage_matches():
    # It should retrieve the list of all the match ids
    path = data_path('betexplorer_euro_2016.html')
    page = CompetitionPage.from_file(path)
    matches = list(page.matches_ids)

    assert len(matches) == 319


@pytest.mark.skip(reason="BetExplorer layout has changed")
def test_matchpage_odds():
    # It should retrieve the odds for Switzerland - France during the Euro 2016
    # Match ID: UB0TAndB
    path = data_path('betexplorer_euro_2016_swi_fra.html')
    page = MatchPage.from_file(path)
    odds_ids = list(page.odds_ids)
    odds = []
    for odds_id in odds_ids:
        odds_url = OddsPage.get_url_from_ids(page.match_id, odds_id)
        odds_page = OddsPage.from_url(odds_url)
        for odd in odds_page.odds:
            odds.append(odd)

    assert len(odds) == 85


def test_matchpage_info():
    # The true info about Switzerland - France during the Euro 2016
    # Match ID: UB0TAndB
    truth = {
        'date': date(2016, 6, 19),
        'team1': "Switzerland",
        'team2': "France"
    }
    path = data_path('betexplorer_euro_2016_swi_fra.html')
    page = MatchPage.from_file(path)

    assert page.info == truth


def test_oddspage():
    path = data_path('betexplorer_euro_2016_swi_fra_odds_1x2.html')
    page = OddsPage.from_file(path)
    odds = list(page.odds)

    truth = {
        "company_name": "10Bet",
        "odds": [5.7, 2.85, 1.95],
        "type": "1X2 Odds",
        "odds_id": "1x2"
    }

    assert page.odds_id == "1x2"
    assert page.type == "1X2 Odds"
    assert len(odds) == 25
    assert odds[0] == truth
