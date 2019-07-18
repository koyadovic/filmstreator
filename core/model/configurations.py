

class Configuration:
    key: str
    data: dict

    def __init__(self, **kwargs):
        self.key = kwargs.pop('key', '')
        self.data = kwargs.pop('data', '')
