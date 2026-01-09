from django.apps import AppConfig

class DrugappConfig(AppConfig):
    name = 'drugapp'

    def ready(self):
        import drugapp.signals  # connect signals
