import requests


USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/39.0.2171.95 Safari/537.36')


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
