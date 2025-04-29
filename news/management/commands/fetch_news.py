from django.core.management.base import BaseCommand
from news.models import Article, Source, Category, UserProfile
import requests
from datetime import datetime
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fetches latest news from NewsAPI and stores them in the database'

    def handle(self, *args, **kwargs):
        API_KEY = '076c98997f964d5588dcf5f87b7667ad'  # Replace with your NewsAPI key
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'country': 'us',
            'apiKey': API_KEY
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data['articles']:
                # Get or create Source
                source, _ = Source.objects.get_or_create(name=item['source']['name'])

                # Get or create Category (default to 'General')
                category, _ = Category.objects.get_or_create(name='General')

                # Parse published_at safely
                published_at = item['publishedAt']
                if published_at.endswith('Z'):
                    published_at = published_at[:-1]
                try:
                    dt = datetime.fromisoformat(published_at)
                    published_at = timezone.make_aware(dt, timezone.utc)
                except Exception:
                    published_at = timezone.now()

                # Create Article if not already present
                Article.objects.get_or_create(
                    title=item['title'],
                    defaults={
                        'content': item['description'] or item['title'],
                        'url': item['url'],
                        'source': source,
                        'category': category,
                        'published_at': published_at
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"Fetched {len(data['articles'])} articles"))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch news'))
