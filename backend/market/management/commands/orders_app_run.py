from django.core.management.base import BaseCommand, CommandError
from services.oredes_auto_close import main


class Command(BaseCommand):

    def handle(self, *args, **options):
        main()