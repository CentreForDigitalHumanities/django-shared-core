"""
Creates one million bs data entries for testing

Not a fixture because it would be a very large file full of bs
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import make_aware
from faker import Faker
from random import choice

from dev_vue.models import ExampleData

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("Sit back, this will take a while. Up to half an hour depending on your PC.")
        faker = Faker()

        # The transaction is not needed, but does speed up SQLite performance
        # as everything is done in the one connection, reducing overhead
        with transaction.atomic():
            for i in range(1, 1000000):
                progress(i, 1000000)
                ExampleData.objects.create(**{
                        'project_name':     faker.bs(),
                        'project_owner':    faker.name(),
                        'reference_number': i,
                        'created':          make_aware(faker.date_time_between()),
                        'project_type':     choice(ExampleData.TypeOptions.values),
                        'status':           choice(ExampleData.StatusOptions.values)
                    })


def progress(iteration, total, width=80, start="\r", newline_on_complete=True):
    width = width - 2
    tally = f" {iteration}/{total}"
    width -= len(tally)
    filledLength = int(width * iteration // total)
    bar = "█" * filledLength + "-" * (width - filledLength)
    print(f"{start}|{bar}|{tally}", end="")
    # Print New Line on Complete
    if newline_on_complete and iteration == total:
        print()
