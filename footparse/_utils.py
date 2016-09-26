import requests


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
        res = requests.get(url)
        return cls(res.text)


def int_or_none(blob):
    try:
        return int(blob)
    except ValueError:
        return None
