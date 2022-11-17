import requests


USER_AGENT = ("Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) "
    "AppleWebKit/602.1.50 (KHTML, like Gecko) "
    "Version/10.0 Mobile/19A346 Safari/602.1")


class BasePage:

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            raw = f.read()
        return cls(raw)

    @classmethod
    def from_url(cls, url):
        headers = {"User-Agent": USER_AGENT}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return cls(res.text)


def int_or_none(blob):
    try:
        return int(blob)
    except ValueError:
        return None


def float_or_none(blob):
    try:
        return float(blob)
    except TypeError:
        return None
