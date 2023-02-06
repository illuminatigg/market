from django.core.management.base import BaseCommand, CommandError
from bot.handlers import run


class Command(BaseCommand):

    def handle(self, *args, **options):
        run()