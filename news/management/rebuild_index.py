from django.core.management.base import BaseCommand
from news.ir_utils import InvertedIndex


class Command(BaseCommand):
    help = "Rebuilds the inverted index for boolean search"

    def handle(self, *args, **kwargs):
        self.stdout.write("Building inverted index...")
        index = InvertedIndex()
        self.stdout.write(
            self.style.SUCCESS(
                f"Index built successfully with {len(index.index)} terms"
            )
        )
