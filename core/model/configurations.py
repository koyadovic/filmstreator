from typing import Any


class Configuration:
    key: str
    data: Any

    def __init__(self, **kwargs):
        self.key = kwargs.pop('key', '')
        self.data = kwargs.pop('data', None)

    @classmethod
    def get_configuration(cls, key):
        from core import services
        return services.get_configuration(key)

    @classmethod
    def get_or_create_configuration(cls, key):
        from core import services
        configuration = services.get_configuration(key)
        if configuration is None:
            configuration = Configuration(key=key, data={})
            configuration.save()
        return configuration

    def save(self):
        from core import services
        services.save_configuration(self)

    def delete(self):
        from core import services
        return services.delete_configuration(self)
