from django.apps import AppConfig
from django.apps import AppConfig 

class MusicNationConfig(AppConfig):
    name = 'music_nation'



class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import signals


