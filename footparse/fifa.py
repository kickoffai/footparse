from ._utils import BasePage
from lxml import etree
from datetime import datetime

class RankingPage(BasePage):

    URL = "http://www.fifa.com/fifa-world-ranking/ranking-table/men/"

    def __init__(self, data):
        data = data.replace(r'&nbsp;', " ")
        self.tree = etree.HTML(data)
        super().__init__(data)

    @property
    def date(self):
        ranking_date = self.tree.xpath('//*[@id="content-wrap"]/div/div[2]/div/div[2]/div/div[1]/div[2]/ul/li')[0].text
        return datetime.strptime(ranking_date, "%d %B %Y").date()

    @property
    def ratings(self):
        teams = self.tree.xpath('//table[contains(@class, "tbl-ranking")]/tbody/tr')

        for row in teams:
            team = {
                "rank": int(row[1][0].text),
                "team_name": row[2][1].text,
                "country_code": row[4][0].text.lower(),
                "points": int(row[5].text),
                "team_url": "http://www.fifa.com" + row[2][1].get("href")
            }
            yield team
