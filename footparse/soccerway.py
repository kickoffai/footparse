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
import json
import re

from datetime import datetime
from lxml import etree
from ._utils import BasePage, int_or_none


class SoccerwayPage(BasePage):

    @classmethod
    def make_url(cls, swid):
        return cls.URL_TEMPLATE.format(swid=swid)


class MatchPage(SoccerwayPage):

    URL_TEMPLATE = "https://int.soccerway.com/matches/0000/00/00/-/-/-/-/{swid}/"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def swid(self):
        elem = self.tree.xpath('//div[@data-match-id]')[0]
        return int(elem.get("data-match-id"))

    @property
    def competition_swid(self):
        elem = self.tree.xpath('//div[@data-competitionids]')[0]
        return int(elem.get("data-competitionids"))

    @property
    def info(self):
        attr = dict()
        div = self.tree.xpath('//div[contains(@class, "details")]')[0]
        elems = div.xpath('./a//text()')
        # Date.
        attr['date'] = datetime.strptime(elems[0], '%d/%m/%Y').date()
        # Competition.
        attr['competition'] = elems[1]
        # Kick-off time.
        elems = div.xpath('./span[text()="KO"]')
        if len(elems) > 0:
            span = elems[0].getnext().getchildren()[0]
            attr["timestamp"] = int(span.get('data-value'))
        # Venue.
        elems = div.xpath('./span[text()="Venue"]')
        if len(elems) > 0:
            attr["venue"] = "".join(elems[0].getnext().itertext())
        # Teams.
        for i, elem in zip((1, 2), self.tree.xpath('//a[@class="team-title"]')):
            attr['team{}_name'.format(i)] = elem.text
            match = re.match(r'.*/(?P<swid>\d+)/', elem.get('href'))
            attr['team{}_swid'.format(i)] = int(match.group('swid'))
        return attr

    @property
    def scores(self):
        elems = self.tree.xpath('//h3[contains(@class,"scoretime")]')
        if len(elems) == 0:
            return {}  # No score information (e.g., match cancelled).
        text = etree.tostring(elems[0], method='text').decode()
        text = text.replace("&nbsp", "")  # Get rid of invalid HTML.
        text = re.sub(r'\s+', ' ', text).strip()  # Collapse multiple white space.
        # Examples:
        #
        #     AET E 2 - 1 E (FT 1 - 1)
        #     FT 1 - 1
        #     AET P 1 - 1 P (FT 1 - 1) (PEN 6 - 5)
        #     FT 2 - 1 (HT 1 - 0)
        match = re.match(
            r'(?P<t1>FT|AET) (?:(?:E|P) )?'  #  Score 1: FT or ET
            r'(?P<s1a>\d+) - (?P<s1b>\d+)(?: (?:E|P))?'  # Actual score 1.
            r'(?: \((?P<t2>HT|FT) (?P<s2a>\d+) - (?P<s2b>\d+)\))?'  # Score 2.
            r'(?: \(PEN (?P<s3a>\d+) - (?P<s3b>\d+)\))?',  # Score 3.
            text)
        attr = dict()
        # Score 1
        if match.group('t1') == 'FT':
            attr['score_ft_team1'] = int(match.group('s1a'))
            attr['score_ft_team2'] = int(match.group('s1b'))
        else:  # match.group('t1') == "AET":
            attr['score_et_team1'] = int(match.group('s1a'))
            attr['score_et_team2'] = int(match.group('s1b'))
        # Score 2
        if match.group('t2') == 'FT':
            attr['score_ft_team1'] = int(match.group('s2a'))
            attr['score_ft_team2'] = int(match.group('s2b'))
        elif match.group('t2') == 'HT':
            attr['score_ht_team1'] = int(match.group('s2a'))
            attr['score_ht_team2'] = int(match.group('s2b'))
        # Score 3
        if match.group('s3a') is not None:
            attr['score_kfpm_team1'] = int(match.group('s3a'))
            attr['score_kfpm_team2'] = int(match.group('s3b'))
        return attr

    def _parse_player_item(self, tr):
        attr = dict()
        # Shirt number.
        elems = tr.xpath('./td[@class="shirtnumber"]')
        if len(elems) > 0 and elems[0].text is not None:
            attr['shirt_number'] = int(elems[0].text)
        # Display name and Soccerway ID.
        elems = tr.xpath('./td[contains(@class,"player")]//a')
        if len(elems) > 0:
            attr['display_name'] = elems[0].text
            match = re.match(r'.*/(?P<swid>\d+)/', elems[0].get('href'))
            attr['swid'] = int(match.group('swid'))
        else:
            # Not a player (maybe a coach, an empty row, ...)
            return None
        # Substitution.
        elems = tr.xpath(
            './td[contains(@class,"player")]//img[@title="Substituted"]')
        if len(elems) > 0:
            match = re.match(r'.*/(?P<what>S[IO]).png', elems[0].get('src'))
            if match.group("what") == "SO":
                # Substitute out.
                attr['subst_out'] = -1  # For legacy reasons (used to be minute).
            elif match.group("what") == "SI":
                # Substitute in.
                attr['subst_in'] = -1  # For legacy reasons (used to be minute).
        # Game events (goals, cards, etc.).
        attr['events'] = list()
        mapping = {
            'G': 'Goal',
            'OG': 'Own goal',
            'PG': 'Penalty goal',
            'PM': 'Penalty missed',
            'YC': 'Yellow card',
            'Y2C': 'Yellow 2nd/RC',
            'RC': 'Red card',
        }
        elems = tr.xpath('./td[@class="bookings"]/span/img')
        for elem in elems:
            match = re.match(r'.*events/(?P<what>.+).png', elem.get('src'))
            event = {'type': mapping[match.group('what')]}
            match = re.match(r'(?P<when>\d+).+', elem.tail.strip())
            if match is not None:
                event['minute'] = int(match.group('when'))
            attr['events'].append(event)
        return attr

    @property
    def starters(self):
        starters = {'team1': list(), 'team2': list()}
        for team, cls in (("team1", "left"), ("team2", "right")):
            for tr in self.tree.xpath(
                    '//div[@class="container {}"]'
                    '/table[@class="playerstats lineups table"]'
                    '/tbody/tr'.format(cls)):
                attr = self._parse_player_item(tr)
                if attr is not None:
                    starters[team].append(attr)
        return starters

    @property
    def substitutes(self):
        substitutes = {'team1': list(), 'team2': list()}
        for team, cls in (("team1", "left"), ("team2", "right")):
            for tr in self.tree.xpath(
                    '//div[@class="container {}"]'
                    '/table[contains(@class, "substitutions")]'
                    '/tbody/tr'.format(cls)):
                attr = self._parse_player_item(tr)
                substitutes[team].append(attr)
        return substitutes

    @property
    def coaches(self):
        coaches = {'team1': list(), 'team2': list()}
        for team, cls in (("team1", "left"), ("team2", "right")):
            for elem in self.tree.xpath(
                    '//div[@class="container {}"]'
                    '/table[@class="playerstats lineups table"]'
                    '/tbody/tr/td/strong[text()="Coach:"]'.format(cls)):
                a = elem.getnext()
                match = re.match(r'.*/(?P<swid>\d+)/', a.get('href'))
                coaches[team].append({
                    'display_name': a.text,
                    'swid': int(match.group('swid'))
                })
        return coaches


class PersonPage(SoccerwayPage):

    URL_TEMPLATE = "https://int.soccerway.com/players/-/{swid}/"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def swid(self):
        elem = self.tree.xpath('//table[@data-people_id]')[0]
        return int(elem.get("data-people_id"))

    @property
    def passport(self):
        attr = dict()
        elem = self.tree.xpath('//h1')[0]
        attr['display_name'] = elem.text
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
                    val = datetime.strptime(val, "%d %B %Y").date()
                attr[key] = val
        return attr


class TeamPage(SoccerwayPage):

    URL_TEMPLATE = "https://int.soccerway.com/teams/-/-/{swid}/"

    def __init__(self, data):
        # Getting rid of annoying non-breaking spaces.
        data = data.replace('&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def swid(self):
        elem = self.tree.xpath('//div[@data-teamids]')[0]
        return int(elem.get("data-teamids"))

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
    def matches(self):
        table = self.tree.xpath('//table[contains(@class, "matches")]')[0]
        return MatchesBlock.parse_matches(table)

    @property
    def rounds(self):
        for option in self.tree.xpath('//select[@name="round_id"]/option'):
            match = re.match(r'.*/r(?P<swid>\d+)/',
                             option.get("value"))
            yield {
                'name': option.text,
                'swid': int(match.group('swid')),
            }

    @property
    def seasons(self):
        for option in self.tree.xpath('//select[@name="season_id"]/option'):
            match = re.match(r'.*/s(?P<swid>\d+)/',
                             option.get("value"))
            yield {
                'name': option.text,
                'swid': int(match.group('swid')),
            }

    @property
    def is_paginated(self):
        elems = self.tree.xpath('//div[@class="page-dropdown-container"]')
        return len(elems) > 0

    @property
    def competition_swid(self):
        elem = self.tree.xpath('//div[@data-competitionids]')[0]
        return int(elem.get("data-competitionids"))

    @property
    def season_swid(self):
        attr = self.tree.xpath('//select[@name="season_id"]'
                               '/option[@selected]/@value')[0]
        match = re.match(r'.*/s(?P<swid>\d+)/', attr)
        return int(match.group('swid'))

    @property
    def round_swid(self):
        elems = self.tree.xpath(
            '//select[@name="round_id"]/option[@selected]/@value')
        if len(elems) > 0:
            # This approach seems more robust.
            match = re.match(r'.*/r(?P<swid>\d+)/', elems[0])
            return int(match.group('swid'))
        else:
            # Fallback when there is no selected round.
            elems = self.tree.xpath(
                '//div[@id="submenu"]/ul/li/a[text()="Summary"]/@href')
            match = re.match(r'.*/r(?P<swid>\d+)/', elems[0])
            return int(match.group('swid'))


class CompetitionPage(MatchListPage):

    URL_TEMPLATE = "https://int.soccerway.com/national/-/-/c{swid}/"

    @property
    def swid(self):
        return self.competition_swid


class SeasonPage(MatchListPage):

    URL_TEMPLATE = "https://int.soccerway.com/national/-/-/-/s{swid}/"

    @property
    def swid(self):
        return self.season_swid


class RoundPage(MatchListPage):

    URL_TEMPLATE = "https://int.soccerway.com/national/-/-/-/-/r{swid}/"

    @property
    def swid(self):
        return self.round_swid


class MatchesBlock(BasePage):

    URL_TEMPLATE = (
        'https://int.soccerway.com/a/block_competition_matches_summary?block_id='
        '&callback_params={{'
            '"page":0,'
            '"block_service_id":"competition_summary_block_competitionmatchessummary",'
            '"round_id":{swid},'
            '"outgroup":false,'
            '"view":0,'
            '"competition_id":0'
        '}}&action=changePage&params={{"page":{page}}}'
    )

    def __init__(self, data):
        self.json = json.loads(data)
        super().__init__(data)

    @property
    def matches(self):
        content = self.json["commands"][0]["parameters"]["content"]
        table = etree.HTML(content)
        return MatchesBlock.parse_matches(table)

    @property
    def round_swid(self):
        params = self.json["commands"][2]["parameters"]["params"]
        return int(params["round_id"])

    @property
    def page(self):
        params = self.json["commands"][2]["parameters"]["params"]
        return int(params["page"])

    @property
    def has_previous(self):
        attr = self.json["commands"][1]["parameters"]["attributes"]
        return attr["has_previous_page"] == "1"

    @property
    def has_next(self):
        attr = self.json["commands"][1]["parameters"]["attributes"]
        return attr["has_next_page"] == "1"

    @staticmethod
    def parse_matches(table):
        for tr in table.xpath('//tbody/tr[contains(@class, "match")]'):
            match_info = dict()
            # Get the timestamp.
            match_info['timestamp'] = int(tr.get("data-timestamp"))
            # Get the Soccerway ID.
            elem = tr.xpath('./td[contains(@class, "score-time")]/a')[0]
            match = re.match(r'.*/(?P<swid>\d+)/', elem.get("href"))
            match_info['swid'] = int(match.group('swid'))
            # Try to get the score.
            elems = tr.xpath('./td//span[@class="extra_time_score"]')
            if len(elems) > 0:
                scores = list(map(int, elems[0].text.split(" - ")))
            else:
                scores = None
            # Process each team.
            for team, cls in (('team1', 'team-a'), ('team2', 'team-b')):
                elem = tr.xpath('./td[contains(@class, "{}")]/a'.format(cls))[0]
                match = re.match(r'.*/(?P<swid>\d+)/', elem.get("href"))
                match_info[team] = {
                    'name': elem.text.strip(),
                    'swid': int(match.group('swid')),
                }
            if scores is not None:
                match_info['team1']['goals'] = scores[0]
                match_info['team2']['goals'] = scores[1]
            yield match_info

    @classmethod
    def for_round(cls, swid):
        for i in itertools.count(0, -1):
            yield cls.URL_TEMPLATE.format(swid=swid, page=i)
