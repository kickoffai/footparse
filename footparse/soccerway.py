"""Soccerway scraping module.

Note: on soccerway, a competition is divided in multiple phases, which
itself contains multiple games.

TODO Explain the following types of pages:

- person
- player (needless - person is more refined)
- team
- match
- competition (needless - season is more refined)
- season
- round
- group (needless - just a filter on `round`)
"""

import itertools
import re

from datetime import datetime
from lxml import etree
from ._utils import BasePage, int_or_none


class SoccerwayPage(BasePage):

    @classmethod
    def make_url(cls, swid):
        return cls.URL_TEMPLATE.format(swid=swid)


class MatchPage(SoccerwayPage):

    URL_TEMPLATE = "http://www.soccerway.mobi/?page=match&id={swid}"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def swid(self):
        elem = self.tree.xpath('//div[@data-match_id]')[0]
        return int(elem.get("data-match_id"))

    @property
    def info(self):
        mapping = { # Maps description string to dict key.
            'Competition': 'competition',
            'Date': 'date',
            'Kick-off': 'timestamp',
            'Venue': 'venue',
            'Attendance': 'attendance',
            'Half-time': 'score_ht',
            'Full-time': 'score_ft',
            'Extra-time': 'score_et',
            'Penalties': 'score_kfpm',
        }
        attr = dict()
        for elem in self.tree.xpath('//dt'):
            if elem.text in mapping:
                key = mapping[elem.text]
                desc = elem.getnext()
                if key == 'date':
                    attr[key] = datetime.strptime(desc[0][0].text,
                                                  "%d %B %Y").date()
                elif key == 'timestamp':
                    attr[key] = int(desc[0].get('data-value'))
                elif key == 'attendance':
                    attr[key] = int(desc.text)
                elif key.startswith('score_'):
                    val1, val2 = map(int, desc.text.split(' - '))
                    attr[key + "_team1"] = val1
                    attr[key + "_team2"] = val2
                else:
                    attr[key] = desc[0].text
        for i, elem in zip((1, 2), self.tree.xpath(
                '//h3[not(contains(@class, "scoretime"))]/a')):
            attr['team{}_name'.format(i)] = elem.text
            match = re.match(r'.*page=team&id=(?P<swid>\d+)&', elem.get('href'))
            attr['team{}_swid'.format(i)] = int(match.group('swid'))
        return attr

    def _parse_player_item(self, li):
        attr = dict()
        # Shirt number.
        elems = li.xpath('./span/span[@class="shirt-number"]')
        if len(elems) > 0:
            attr['shirt_number'] = int(elems[0].text)
        # Nationality.
        elems = li.xpath('./span/span[contains(@class,"nationality")]')
        if len(elems) > 0:
            attr['nationality'] = elems[0].get('title')
        # Display name and Soccerway ID.
        elems = li.xpath('./span//span[@class="name"]/a')
        if len(elems) > 0:
            attr['display_name'] = elems[0].text
            match = re.match(r'.*&id=(?P<swid>\d+)&', elems[0].get('href'))
            attr['swid'] = int(match.group('swid'))
        # Position (i.e., whether GK or not).
        elems = li.xpath('./span//span[@class="position"]')
        if len(elems) > 0:
            attr['position'] = elems[0].get('title')
        # Substitute out.
        elems = li.xpath('./span//span[@class="player-events"]'
                         '/span/span[contains(@class,"evt-icon-SO")]')
        if len(elems) > 0:
            match = re.match(r'Substitute out - (?P<when>\d+).+',
                             elems[0].get('title'))
            attr['subst_out'] = int(match.group('when'))
        # Substitute in.
        elems = li.xpath('./span//span[@class="player-events"]'
                         '/span/span[contains(@class,"evt-icon-SI")]')
        if len(elems) > 0:
            match = re.match(r'Substitute in - (?P<when>\d+).+',
                             elems[0].get('title'))
            attr['subst_in'] = int(match.group('when'))
        # Game events (goals, cards, etc.).
        attr['events'] = list()
        elems = li.xpath('./span/span[@class="match-events"]/span')
        for elem in elems:
            match = re.match(r'(?P<when>\d+).+', elem[1].text)
            attr['events'].append({
                'type': elem[0].get('title'),
                'minute': int(match.group('when')),
            })
        return attr

    @property
    def starters(self):
        starters = {'team1': list(), 'team2': list()}
        for i, cls in ((1, "team-a"), (2, "team-b")):
            for li in self.tree.xpath('//div[@class="lineups"]'
                                      '/div[contains(@class, "{}")]'
                                      '/ul/li'.format(cls)):
                attr = self._parse_player_item(li)
                starters['team{}'.format(i)].append(attr)
        return starters

    @property
    def substitutes(self):
        substitutes = {'team1': list(), 'team2': list()}
        for i, cls in ((1, "team-a"), (2, "team-b")):
            for li in self.tree.xpath('//div[@class="substitutes"]'
                                      '/div[contains(@class, "{}")]'
                                      '/ul/li'.format(cls)):
                attr = self._parse_player_item(li)
                substitutes['team{}'.format(i)].append(attr)
        return substitutes

    @property
    def coaches(self):
        coaches = dict()
        for i, cls in ((1, "team-a"), (2, "team-b")):
            elems = self.tree.xpath('//div[contains(@class, "{}")]'
                                    '/div[contains(@class, "team-coach")]/span'
                                    '/span[@class="name"]/a'.format(cls))
            if len(elems) > 0:
                match = re.match(r'.*page=person&id=(?P<swid>\d+)&',
                                 elems[0].get('href'))
                coaches['team{}'.format(i)] = {
                    'display_name': elems[0].text,
                    'swid': int(match.group('swid'))
                }
        return coaches


class PersonPage(SoccerwayPage):

    URL_TEMPLATE = "http://www.soccerway.mobi/?page=person&id={swid}"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def swid(self):
        elem = self.tree.xpath('//div[@id]/ul/li[2]/a[2]')[0]
        match = re.match(r'.*page=person&id=(?P<swid>\d+).+', elem.get('href'))
        return int(match.group("swid"))

    @property
    def passport(self):
        attr = dict()
        elem = self.tree.xpath('//title')[0]
        match = re.match(r'(?P<disp>.+) - Soccer - Soccerway mobi', elem.text)
        attr['display_name'] = match.group('disp')
        mapping = { # Maps description string to dict key.
            'First name': 'first_name',
            'Last name': 'last_name',
            'Nationality': 'nationality',
            'Date of birth': 'birthdate',
            'Age': 'age',
            'Country of birth': 'birthcountry',
            'Place of birth': 'birthplace',
            'Position': 'position',
            'Height': 'height',
            'Weight': 'weight',
            'Foot': 'foot',
        }
        for elem in self.tree.xpath('//dt'):
            if elem.text in mapping:
                key = mapping[elem.text]
                val = elem.getnext().text
                if key in ('height', 'weight'):
                    val = int(val.split(" ")[0])
                elif key == 'age':
                    val = int(val)
                elif key == 'birthdate':
                    val = datetime.strptime(val, "%d-%m-%y").date()
                attr[key] = val
        return attr


class TeamPage(SoccerwayPage):

    URL_TEMPLATE = "http://www.soccerway.mobi/?page=team&id={swid}"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def swid(self):
        elem = self.tree.xpath('//h2[1]/a')[0]
        match = re.match(r'.*page=team&id=(?P<swid>\d+).+', elem.get('href'))
        return int(match.group("swid"))

    @property
    def country(self):
        # Pattern: `<dt>Country</dt><dd>Chile</dd>`.
        elem = self.tree.xpath('//dt[text()="Country"]')[0]
        return elem.getnext().text

    @property
    def name(self):
        attr = self.tree.xpath('//div[@class="logo"]/img/@alt')[0]
        return str(attr)


class MatchListPage(SoccerwayPage):

    def __init__(self, data):
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def rounds(self):
        for option in self.tree.xpath('//select[@name="round_id"]/option'):
            match = re.match(r'.*page=round&id=(?P<swid>\d+).+',
                             option.get("value"))
            yield {
                'name': option.text,
                'swid': int(match.group('swid')),
            }

    @property
    def seasons(self):
        for option in self.tree.xpath('//select[@name="season_id"]/option'):
            match = re.match(r'.*page=season&id=(?P<swid>\d+).+',
                             option.get("value"))
            yield {
                'name': option.text,
                'swid': int(match.group('swid')),
            }

    @property
    def matches(self):
        for tr in self.tree.xpath('//table[contains(@class, "matches")]'
                                  '/tbody/tr[contains(@class, "match")]'):
            match_info = dict()
            # Get the timestamp.
            match_info['timestamp'] = int(tr.get("data-timestamp"))
            # Get the Soccerway ID.
            elem = tr.xpath('./td[contains(@class, "score")]/a')[0]
            match = re.match(r'.*page=match&id=(?P<swid>\d+).+',
                             elem.get("href"))
            match_info['swid'] = int(match.group('swid'))
            # Try to get the score.
            elems = tr.xpath('./td//span[@class="scoring"]')
            if len(elems) > 0:
                scores = list(map(int, elems[0].text.split(" - ")))
            else:
                scores = None
            # Process each team.
            for i, cls in ((1, "team-a"), (2, "team-b")):
                elem = tr.xpath('./td[contains(@class, "{}")]/a'.format(cls))[0]
                match = re.match(r'.*page=team&id=(?P<swid>\d+).+',
                                 elem.get("href"))
                match_info['team{}'.format(i)] = {
                    'name': elem.text.strip(),
                    'swid': int(match.group('swid')),
                }
                if scores is not None:
                    match_info['team{}'.format(i)]['goals'] = scores[i-1]
            yield match_info

    @property
    def is_last(self):
        """Returns true if page is at end of pagination."""
        elems = self.tree.xpath('//div[contains(@class, "match-pagination")]'
                                '/span/a[contains(@class, "previous")]')
        return len(elems) == 0 or "disabled" in elems[0].get("class")

    @classmethod
    def paginated_urls(cls, swid):
        # TODO Documentation.
        template = cls.URL_TEMPLATE + "&params={{%22p%22%3A{}}}"
        for i in itertools.count(-1, -1):
            yield template.format(i, swid=swid)


class SeasonPage(MatchListPage):

    URL_TEMPLATE = "http://www.soccerway.mobi/?page=season&id={swid}"

    @property
    def swid(self):
        attr = self.tree.xpath('//select[@name="season_id"]'
                               '/option[@selected]/@value')[0]
        match = re.match(r'.*page=season&id=(?P<swid>\d+).+', attr)
        return int(match.group('swid'))


class RoundPage(MatchListPage):

    URL_TEMPLATE = "http://www.soccerway.mobi/?page=round&id={swid}"

    @property
    def swid(self):
        elem = self.tree.xpath('//div[@data-round_id]')[0]
        return int(elem.get("data-round_id"))
