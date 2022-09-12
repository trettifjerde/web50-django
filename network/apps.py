from django.apps import AppConfig


class NetworkConfig(AppConfig):
    name = 'network'

    def ready(self):
        from home import signals
        from network import signals
