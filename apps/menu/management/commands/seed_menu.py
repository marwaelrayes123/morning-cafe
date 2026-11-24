from django.core.management.base import BaseCommand

from apps.menu.seed import seed_menu


class Command(BaseCommand):
    help = "Load (or refresh) the starter coffee menu, milk options and sizes."

    def handle(self, *args, **options):
        seed_menu()
        self.stdout.write(self.style.SUCCESS("Menu loaded."))
