import re

from datetime import datetime
from lxml import etree
from ._utils import BasePage, int_or_none


class TeamPage(BasePage):

    URL_TEMPLATE = "http://www.eloratings.net/{path}"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def country(self):
        elem = self.tree.xpath('//h1')[0]
        match = re.match(r'World Football Elo Ratings: (?P<country>.+)',
                         elem.text)
        return match.group('country')

    @property
    def entries(self):
        get_texts = etree.XPath('./text()')
        for row in self.tree.xpath('//table[@class="results"]'
                                   '/tr[@class="nh"]'):
            dt_str = " ".join(get_texts(row[0]))
            try:
                dt = datetime.strptime(dt_str, "%B %d %Y").date()
            except:
                try:
                    dt = datetime.strptime(dt_str, "%B %Y").date()
                except:
                    dt = datetime.strptime(dt_str, "%Y").date()
            names = list(map(str, get_texts(row[1])))
            score = list(map(int, get_texts(row[2])))
            competition = " ".join(get_texts(row[3]))
            rating_diffs = list(map(int_or_none, get_texts(row[4])))
            ratings = list(map(int_or_none, get_texts(row[5])))
            rank_diffs = list(map(int_or_none, get_texts(row[6])))
            ranks = list(map(int_or_none, get_texts(row[7])))
            match_info = {
                'date': dt,
                'competition': competition,
            }
            for i, key in enumerate(('team1', 'team2')):
                match_info[key] = {
                    'name': names[i],
                    'goals': score[i],
                    'rating_diff': rating_diffs[i],
                    'rating': ratings[i],
                    'rank_diff': rank_diffs[i],
                    'rank': ranks[i]
                }
            yield match_info

    @classmethod
    def from_name(cls, name):
        path = "{}.htm".format(name)
        return cls.from_url(TeamPage.absolute_url(path))

    @staticmethod
    def absolute_url(path):
        return URL_TEMPLATE.format(path=path)


class HomePage(BasePage):

    URL = "http://www.eloratings.net/"

    RATINGS_KEYS = ['rank', 'team', 'rating', 'highest_rank', 'highest_rating',
                    '1yr_change_rank', '1yr_change_rating', 'matches_total',
                    'matches_home', 'matches_away', 'matches_neutral',
                    'matches_wins', 'matches_losses', 'matches_draws',
                    'goals_for', 'goals_against']

    def __init__(self, data):
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def date(self):
        elem = self.tree.xpath('//td[@class="mh"][@colspan="16"]')[0]
        match = re.match(r'Ratings and Statistics as of (?P<date>.+)',
                         elem.text)
        dt = datetime.strptime(match.group('date'), "%A %B %d %Y")
        return dt.date()

    @property
    def ratings(self):
        for row in self.tree.xpath('//table[@rules="groups"][not(@class)]'
                                   '/tr[not(@class)]'):
            country_info = dict()
            for key, cell in zip(HomePage.RATINGS_KEYS, row.iter('td')):
                if key == 'team':
                    val = cell[0].text
                    country_info['href'] = cell[0].get('href')
                else:
                    val = int_or_none(cell.text)
                country_info[key] = val
            yield country_info

    @classmethod
    def load(cls):
        return cls.from_url(HomePage.URL)
