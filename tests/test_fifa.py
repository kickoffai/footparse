from footparse import fifa
from testutils import data_path
from datetime import date


def test_homepage_date():
    path = data_path('fifa_home.html')
    page = fifa.RankingPage.from_file(path)
    assert page.date == date(2016, 9, 15)


def test_homepage_ratings():
    truth = {
        "rank": 16,
        "team_name": "Switzerland",
        "country_code": "sui",
        "points": 1020,
        "team_url": "http://www.fifa.com/fifa-world-ranking/associations/association=sui/men/index.html"
    }
    path = data_path('fifa_home.html')
    page = fifa.RankingPage.from_file(path)
    ratings = list(page.ratings)
    assert len(ratings) == 210
    assert ratings[15] == truth
